---
covers:
  - kb.py
  - distill/agent/codeb_agent.py
  - distill/agent/spawn.py
  - mcp/server.ts
  - mcp/smoke.ts
  - distill/agent/tools_fs.py
  - distill/agent/route_ask.py
title: Route packs: whole-directory raw source, 200k budgets, and what questions they can actually answer
updated: 2026-11-24
---

# Route packs: whole-directory raw source, 200k budgets, and what questions they can actually answer

装订单位从「一个范围」扩到**一条路由**：entry + 显式成员集 + 每成员保真度 + 一组预设问题。
预算可到 200k。但**装得下不等于答得对**——这一页最重要的部分不是怎么装，
而是实测出「哪些问题路由包能答、哪些必须配工具」。

一句话结论：**语义题靠装订，定位/计数题必须靠工具，而且工具要给「已算好的答案」而不是原料。**

## 装订单位：范围 → 路由

`kb pack` 的装订单位是**范围**（一个文件，或一个目录里所有文件平分预算）。
路由的装订单位是**leader 显式点名的成员集**，每个成员单独声明保真度。

这两种不是同一件事的粗细两档，失败方式相反：pack 怕「知识层被挤光」，
路由怕「leader 点的文件被摊平或删掉」——那是另一种残缺，而且更像完整。

### 整目录装订实测：200k 装得下，但平分预算仍然会降级

`apps/web` 全量源码实测：

| 项 | 值 |
| :-- | :-- |
| 文件数 | 43 个 `.ts/.tsx`（排除锁文件/生成清单） |
| 全量全文 | **154,895 tok** |
| 与前端的 200k 预算 | 装得下，余 45k 给知识层 |

但**直接给 `kb pack <目录> --budget 200000` 仍然不对**，因为预算按文件数平分：

```text
share = 200000 × 0.6 / 43 = 2,790 tok/文件
→ 19 个文件被降级成大纲，其中包括 QuestionPanel(20,111)、App(13,018)、api(12,218)
```

也就是说：**给了 200k，最大的那些文件反而还是只给签名。** 这正是路由要解决的——
保真度由 leader 按「这个文件要看多细」定，不由「预算 ÷ 文件数」定。

## 语义题：装订就够（4/4）

用 13,961 tok 的聚焦包（main + App + Sidebar 大纲）实测，四个语义类问题全对：

| 题目 | 结果 |
| :-- | :-- |
| 组件层次 / 依赖方向 | ✓ 画出 `main.tsx → App.tsx → Sidebar`，指出 Sidebar 是静态 import 不是懒加载 |
| 约束 / 契约 | ✓ drop 请求体 `{before_id}` / `{after_id}`；dragover 不能 `getData()` 的原因说得完整 |
| 改动影响面 | ✓ 只改 App.tsx；**主动指出** `getInitialCollapsed`/`ViewMode` 必须保持静态导入 |
| 归因 / 方案 | ✓ 「App.tsx 是单体上帝组件、无代码分割」+ 两个切入点 |

这类问题的共同点：**答案需要跨多行、多文件综合，但不需要精确计数或行号。**

## 定位 / 计数题：装订没用，工具才行（决定性对比）

同一批题、同一份 155k 全文上下文，**唯一变量是工具**：

| 配置 | 工具 | 定位/计数题 | 观察 |
| :-- | :-- | :-- | :-- |
| M0 | 无 | **0/3** | 答 102 / 14 / 20（真值 106 / 16 / 28） |
| M1 | `grep` 返回命中行 | **1/3** | 只有「首次出现行号」对；计数题烧满 6 轮仍答不出 |
| M2 | `grep` + `grep_count` | **3/3** | 计数题全部一次或两次调用答对 |
| M3 | `+ find_line` | **3/3** | 定位题一步到位 |

### 什么时候装订完全无效

把上下文从 155k 一路缩到单文件，正确率**没有变化**：

| 上下文规模 | 定位题正确率 |
| --: | --: |
| 154,895 tok（43 文件全文） | 1/4 |
| 39,830 tok（5 文件聚焦） | 1/4 |
| 5,383 tok（单文件 Sidebar） | 1/5 |
| **20 tok（3 行玩具）** | **1/1** ✓ |

只有缩到 3 行才对。所以瓶颈不是注意力被稀释，而是**模型在任何真实规模下都数不准**。

一个典型误答：问 `let dragSource` 第几行，答 **526**——那是 Sidebar.tsx 的**总行数**，
就印在包的标题行 `526 行 全文` 里。它抓了邻近的显著数字，而不是说「不确定」。

两个模型（`lightning-30b` / `super-vl-120b`）都是 1/4，只是错得不一样（526/11 vs 100/103）。
提问方式也全排除：合并问、拆开问、同一会话多轮，都是 1/4 或 0/3。

## 工具要给「答案」，不要给「原料」

这是本轮最有操作价值的结论，也是本项目既有教训的加强版。

| 工具返回 | 模型的行为 |
| :-- | :-- |
| `grep` → 30 行命中 | 自己数，数错（答 23，真值 27/28） |
| `grep_count` → 「命中 16 条」 | 直接采纳，答对 |

原教训是「**算出来的信息不给，等于没算**」（`kb_dispatch` 说「6 个文件」却不列出，
被同一参数重复调用 3 次）。这里是它的加强版：

> **让模型自己数，等于没算。**

所以路由该配的工具形态，不是 `grep` 这种原料型，而是**已归约好的答案**：

```text
grep_count(pattern)      → "命中 16 条" + 前 20 个位置
find_line(literal)       → "apps/web/src/components/Sidebar.tsx:106"
grep(pattern)            → 命中行（只在模型要「看内容」时用，不是用来数）
read_block(path, key)    → 单块正文（虚拟内存的缺页调入，已有）
```

这条同时解释了 M1 为什么只救回 1/3：`grep` 让模型拿到了原料，但**把唯一的算术留给了它**。

### 真值口径必须写死——我为此错过一次

题面「App.tsx 里 `from './` 开头的 import 几条」，我先后写过 27 和 28：

- **27**：`^import.*from './'` 单行匹配（跨行的 `import {` 单独一行，看不到）
- **28**：跨行合并成语句后匹配（含 L11-L17 那个多行 import）

模型答 27，我按 28 判它错。**是我错**。真值必须先核（`_tmp/truth_imports.py`），
判分接受两个口径。否则「模型答错」里混着自己的错题。

## leader 的提问模式：一次装订，多问

用户要的形态是「组装好路由后确定好需要提的问题，一次性拿到需要的上下文」。
实测支持这个形态，但要按题型分工：

| 阶段 | 做什么 | 实测成本 |
| :-- | :-- | :-- |
| 1 装订 | 全量原文一次装入（154,895 tok） | 27s / 一次调用 |
| 2 语义提问 | 一次问 N 个语义题 | 各 3–17s，上下文不动 |
| 3 定位核实 | 用 `find_line` / `grep_count` 逐条核 | 1–3 轮工具调用 |

关键收益不是省钱，而是**装订成本只付一次**：后续每问只加几百 tok（`prompt` 从
155,383 涨到 155,469，三次问总共 +86 tok）。

两条边界：

- **同一会话多轮对语义题有效，对计数题无效**（E 实验 0/3）。多轮救不了算术。
- **路由变了就开新会话**。旧会话残留旧成员原文，追加一条「新增 X」会让两代上下文同时在场。
  `SQLiteSession(session_id, db_path)` 已验证可用（0.25.0，见 `_kbwork/agvenv`）。

## 路由规格

```json
{
  "repo": "atomkgraph",
  "entry": "apps/web/src/main.tsx",
  "budget": 200000,
  "members": [
    {"path": "apps/web/src/App.tsx", "role": "full", "why": "首屏入口，冷启动归因主体"},
    {"path": "apps/web/src/components/Sidebar.tsx", "role": "full"},
    {"path": "apps/web/src/api.ts", "role": "index", "why": "只要接口签名"}
  ],
  "questions": [
    "首屏为什么这么大？最直接的两个切入点是什么？",
    "把 Sidebar 改成 lazy 要动哪些文件、注意什么？"
  ],
  "tools": ["grep_count", "find_line", "read_block"]
}
```

落盘的是**意图**（成员、保真度、问题、工具），源码正文永远现场读：

- 册子落盘 → 内容会和代码分叉，然后照着旧内容开工；
- 意图落盘 → 内容变了重新装订就是新的；文件被删了**立刻报错**。

`questions` 是这一版新增的核心字段：leader 把要问的一次写清楚，
装订完就跑完这些问，**不必等装订结果再决定问什么**。这正是「一次性拿到上下文」。

### 保真度三档

| role | 装什么 | 复用 |
| :-- | :-- | :-- |
| `full` | 全文 | `_read_text_robust`（**不要**用 `render_source(allowance=0)`，见下） |
| `index` | 语义块索引 | `kb._source_index_block` |
| `outline` | 签名大纲 | `kb.file_outline` |

`render_source(allowance=0)` 不是「不限」，是「按 400 行启发式」：
526 行的文件给大纲（809 tok），传 100000 才给全文（5,383 tok）。
**默认值有语义时，省略参数就是一次误表达。**

### 不变式：成员清单永不丢

预算不够只降档（full→index→outline→一行路径），不删成员。实测反例：
7 成员包压到 5,000 tok 时，5,383 tok 的落点文件被**整块删掉**，只剩 830 tok 的小文件；
而 5,000 和 2,500 的结果完全一样——现有 prio 阶梯在这个区间不连续。

### 超预算默认拒绝

打印溢出表（超多少 / 每成员多少 / 降档能省多少），非零退出。
要 `--degrade` 或逐个 `--drop <path>` 才继续。**悄悄降一档，答案就基于大纲而不是原文，
而它长得像装订成功。**

## 三个必须先修的缺陷（blocking）

### 1. 带仓库前缀的目录 → 0 块 0 tok，`rc=0`

```text
$ python kb.py pack atomkgraph/apps/web/src/components/ --json
blocks 0  total 0  precision none        ← rc=0，没有报错
$ python kb.py pack apps/web/src/components/ --json
blocks 22 total 7428                     ← 同一个目录，只差前缀
```

根因在 `cmd_pack` 目录分支：`target` 用剥了前缀的 `rel_scope`（所以单文件正常），
但 `src_files(base, scope, root)` 传的是**带前缀的 `scope`**，恒返回空列表。

这是本项目点名过最危险的失败模式：安静地交出一份残缺但整齐的册子。
而 leader 天然写带前缀路径——`kb where` / `kb pack` 的文档示例都带前缀。

### 2. 同一根因：落点文件被当成自己的兄弟

```text
pack atomkgraph/.../ui/button.tsx  → prio5 全文 + prio1 同名文件大纲（重复）
pack apps/web/.../ui/button.tsx    → 只有 prio5 全文
```

一重一轻，不报错只白付 token。修法：兄弟比较用 `r != rel_scope`，
且 `render_source` 的 `rel` 统一传裸路径（现在前缀从 `scope` 漏进 label，
两种写法输出不逐字节一致，「带前缀 == 裸路径」没法断言）。

### 3. `dispatch` 带前缀目录报错，且指向错误修法

```text
$ python kb.py dispatch atomkgraph/apps/web/src/components/ atomkgraph/apps/server/src/
atomkgraph/apps/web/src/components 定位不到（先在仓库 overview 页写 root: <磁盘路径>）
```

`scope_repo` 其实解析成功了，错在下一行 `target = base / scope` 又拼一次前缀。
但错误文案和「root 没写」共用一句，把人指向完全不相关的修法。

判据：**带前缀与裸路径必须产出相同的 `files` / `conflicts` / `shared_pages`**。

## 冷启动案例的实测事实

顺手把这条真实需求摸清了（`_tmp/coldstart.py`）：

| 项 | 值 |
| :-- | :-- |
| `main.tsx` 深度 1 | 3 文件 13,434 tok |
| `main.tsx` **深度 2** | **29 文件 130,257 tok** ← 首屏 chunk 全部内容 |
| `main.tsx` 深度 3 | 40 文件 152,596 tok |
| App.tsx 的 import 语句 | 31 条，其中 **28 条**指向 `./` |
| App.tsx 里 `lazy(` / `Suspense` | **0 次** |

`main.tsx` 只 134 tok，但它 import 的 App.tsx 静态拉进 24 个组件，
所以 depth=2 就是整个首屏。**「首屏为什么大」的答案是确定的、可从源码读出的**——
这也解释了为什么 S4 语义题答得准。

## 落地顺序（每步配一个会红的断言）

| # | 改动 | 断言 |
| :-: | :-- | :-- |
| 1 | 前缀归一：`src_files(base, rel_scope)`、`dispatch` 的 `target`、兄弟比较 | 带前缀与裸路径输出**逐字节相同**；`total==0` 必须非零退出 |
| 2 | `kb route --spec`（装订 + 跑 `questions`） | 成员数 == 规格成员数（**降预算也不许少**）；源文本真在包里（`"export function Sidebar" in out`） |
| 3 | `kb route --around <entry> --depth 1` 提议器 | 闭包对 `Sidebar.tsx` 能找到 `api.ts`；tok 与直接读一致 |
| 4 | 工具集 `grep_count` / `find_line` | 同一批定位题从 0/3 升到 3/3（**这是本页的核心断言**） |
| 5 | `Task.route` + `kb agent --route` | `context_tokens` 落在规格 ±10%；`index` 成员正文不在上下文里 |
| 6 | 多轮 `ask`（session 复用） | turn 2 输入只增 < 200 tok；语义题仍引用得到原文标识符 |

**别用「端到端跑通」验收第 2、4 步**——agent 可以靠 `read_file` 自给自足跑通，
管道坏了看不出来（`with_source` 那个 bug 就是这么漏过的）。

## 提议器：`kb route --around <entry> --depth 1`

leader 说「根据项目框架找到可能会用到的文件」，这一步必须**只提议、不装订**，
输出 `path / 行数 / tok / 建议 role / 被谁 import`。建议 role 按体量：

| 成员 tok | 建议 |
| --: | :-- |
| ≤ 1,500 | `full` |
| ≤ 6,000 | `index` |
| 更大 | `outline` |

解析器分语言：TS/TSX 正则抽 `from '...'` 再试 `.ts/.tsx/.js/.jsx`
（项目里 import 写 `.js`、实体是 `.ts`）；Python 用 `ast`。
**不引入新依赖，不建索引文件。**

`--depth` 默认 1 且只对 `entry` 展开：`Sidebar.tsx` 1-hop 已 19,166 tok
（`api.ts` 一人占 64%），2-hop 会拉进整个 API 表面。需要更远处时 leader 显式加成员。

**必须把 tok 打出来**：`api.ts` 占 64% 这个事实，只有看到数字才让人改主意。

## 与硬契约的关系

不新增任何一条：

1. 唯一写入口仍是 `kb upsert`——`route` 全只读。
2. 无状态：不建索引、不缓存正文；路由规格是**输入**，不是派生真源。
3. 规则一份实现：复用 `render_source` / `_source_index_block` / `file_outline` /
   `claiming_pages` / `page_sections`。原型 60 行、0 行新抽取逻辑。
4. 自报精度：每个成员报 `exact / dir / none`。`none` 是待办——
   「这个文件没有知识页，改了没人记得为什么」。

## 计划

- [ ] P-route-prefix 修 pack/dispatch 的仓库前缀归一（带前缀目录曾装出 0 块 0 tok 且 rc=0） — done: grep kb.py `src_files\(base, rel_scope`
- [ ] P-route-cmd 加 kb route：成员集 + 保真度 + questions 一次跑完，成员清单永不丢 — done: grep kb.py `def cmd_route`
- [ ] P-route-around 提议器：1-hop 闭包，只提议不装订 — done: grep kb.py `def cmd_route_around`
- [ ] P-route-tools 给路由配 grep_count / find_line（原料型 grep 救不回计数题） — done: grep distill/agent/tools_fs.py `def grep_count`
- [ ] P-route-agent Task.route 接进 assemble/render — done: grep distill/agent/codeb_agent.py `route:`
- [ ] P-route-ask 一次装订、逐条提问，**每问都是全新会话**（不走 SQLiteSession：历史与包体相比是噪声，且会让前缀缓存失效、答案无法单独判定） — done: grep distill/agent/route_ask.py `def ask_one`
- [ ] P-route-noise 知识层按共同点名降噪（`api` 这种短 stem 会带进 1,232 tok 无关小节） — done: none

## 实测数字汇总

| 项 | 值 |
| :-- | :-- |
| `apps/web` 全量源码 | 43 文件 **154,895 tok**（200k 装得下） |
| `main.tsx` depth=2 闭包 | 29 文件 130,257 tok（首屏全部） |
| App.tsx import | 31 语句，28 条指向 `./`，lazy/Suspense **0** |
| `pack <Sidebar.tsx>` 默认预算 | 6,228 tok（全文 5,383 + 知识 845） |
| `pack <目录> --budget 200000` | 仍降级 19 个文件（share=2,790/文件） |
| `pack <atomkgraph/目录/>` | **0 块 0 tok，rc=0**（缺陷 1） |
| 语义题（4 类） | **4/4** ✓ |
| 定位/计数题 · 无工具 | **0/3** |
| 定位/计数题 · grep | **1/3** |
| 定位/计数题 · grep_count + find_line | **3/3** |
| 155k 装订耗时 | 27s / 一次调用 |
| 后续每问增量 | +86 tok（三次问合计） |
| `est_tokens` vs tiktoken | 1.00–1.17 倍（偏保守） |

## 落地结果（已实现，实测数字都是跑出来的）

## 落地结果（已实现，实测数字都是跑出来的）

四个 blocking 缺陷已全部修掉，`kb route` 与四个工具已进内核与 MCP 层。回归：`node mcp/smoke.ts` **97 通过 / 0 失败**（原 75，新增 22 条都在断言路由的不变式）；`_tmp/test_tools_calibration.py` **10/10**。

涉及文件：`kb.py`（前缀归一三处 + `cmd_route` / `cmd_route_around` / `_route_member_block` / `_imports_of` / `_resolve_import`）、`distill/agent/route_ask.py`（新增，逐问全新会话）、`distill/agent/tools_fs.py`（`grep_count` / `find_line` / `resolve_loose`）、`mcp/server.ts`（`kb_route`）、`mcp/smoke.ts`（22 条新断言）。

### 已修的三条前缀缺陷

`cmd_pack` 的目录分支现在传 `rel_scope` 而不是 `scope`；单文件的兄弟比较改成 `r != rel_scope`；`cmd_dispatch` 的 `target` 也改成剥过前缀的 `rel`。三个命令现在对「带前缀」和「裸路径」给出**逐字节相同**的内容（只有标题行回显的 scope 不同，那是元信息）。

另外加了一条硬错误：`total == 0` 且不是 `--no-source` 时**退出码 2**。理由就是那个 bug 的形态——0 块 0 tok 且 `rc=0` 让它伪装成「这个目录没东西」。错误信息要分开报「文件存在但抽不出内容」和「目录里扫不到源码」，否则实现 bug 会继续藏在「范围给错了」后面。

### `kb route --spec` / `--around`

- `--spec` 装订：成员集 + 每成员 `full`/`index`/`outline` + `questions` 一次装订。
- `--around` 提议：1-hop import 闭包，给 tok / 行数 / 建议 role / 被谁 import，**只提议不装订**。
- `--ask`：装订后逐条提问，**每问都是全新会话**。

实测 `route --around Sidebar.tsx --depth 1`：6 个候选 19,649 tok，其中 `api.ts` 12,531 tok 占 64%，自动建议 `outline`；落点 `Sidebar.tsx` 5,533 tok 建议 `index`。这正是「按体量给 role」该有的样子。

冷启动案例装 6 个成员：**23,538 tok**（App.tsx 全文 13,018 + Sidebar 全文 5,383 + api.ts 索引 1,184 + 知识层 10 节 3,221），200k 预算下**零降档**。

### 不变式是怎么保住的

「成员清单永不丢」的敌人不只预算，还有一个我没想到的：`_source_index_block` 在子进程失败时**返回 None**，于是成员整块消失，而 `members[]` 里它还在、只显示 0 tok。实测发生过——同一份规格，CLI 跑出 3 个成员，MCP 跑出来只有 2 个块。现在 index 档失败会退回大纲并在块头写明「语义块索引抽取失败，退大纲」，任何一档都不返回 None。

降档实现也改了：不是「按顺序挨个降」，而是每轮挑**省得最多**的那个降一档。按顺序降会先把 57 tok 的小文件降成大纲（省 20 tok），而 13k 的大文件还占着位置。

预算是 800 tok 时全部降到 outline 仍要 1,804 —— 这时**报错**，并给出「预算至少要给到 1804，或用 `--drop` 明确去掉成员」。不硬塞，因为硬塞出去的包看着完整、实际全是签名。

### 工具：三个都必须宽容

`grep_count` / `find_line` 之外，这轮最重要的改动是 `grep_text` 的两个「宽容」：

1. **`path` 接受裸文件名**。实测模型写 `path: "Sidebar.tsx"` 意思是「那个文件」，严格按目录解析返回「目录不存在」，它就开始瞎猜路径——连试 `/app` `/root` `/home` `/tmp` `/workspace` 五个，7 轮烧完仍答不出。这是**工具把文件当成了目录**，不是模型的错。现在按 basename 找（`resolve_loose`），并在返回里注明「按文件名匹配到哪个文件」。
2. **`pattern` 支持正则**。模型天然写 `^export function|^function`，只做字面匹配会让它「每次都没命中」然后不断换写法。非法正则退回字面子串（`let x = (a` 这类含元字符的字面量不能报错）。

这条教训值得单独记：**「模型不会用工具」的结论，有两次实际是我的工具坏了**（第一次是 `do_grep` 用字面匹配，这次是裸文件名）。下这个结论前必须先看 trace 里工具收到了什么、回了什么。

### 提问：每问全新会话，实测代价为零

`route --ask` 三问的 prompt 分别是 24,830 / 25,764 / 25,718 tok。**包体 23,538 tok 是每问的全部成本，历史为 0**。第 3 问只多花 2.8 秒。

每问独立换来三件事：前缀缓存每次命中（前缀逐字节相同）、答案可并行可重跑、单独判定（第 3 问答错时不必怀疑是第 2 问带偏的）。代价是没有「追问」——想问「刚才第三点展开」必须重组成自足的问题。这是刻意的。

### `tool_choice="required"` 在这个端点上不可用

这是本轮最意外的发现，且完全没有替代方案：

| tool_choice | finish_reason | content | tool_calls |
| :-- | :-- | :-- | :-- |
| `auto` | `stop` | 正常 | 按需 |
| `required` | **`length`** | **空** | **无** |

`max_tokens` 给 2000 和 4000 都被烧光，`reasoning_content` 也是空的——它吐了 2000 个不可见 token 然后停。所以「强制模型去查」只能靠提示词，不能靠 `tool_choice`。

### 模型选型是硬约束，不是偏好

同一份包、同一套提示词、同一批题，只换模型：

| 模型 | 两道事实题 | 是否调工具 |
| :-- | :-- | :-- |
| `nemotron-3.5-super-vl-120b-a12b` | **2/2**（28 / 106） | 都调了 `grep_count` / `find_line` |
| `nemotron-3.5-lightning-30b-a3b` | **0/2**（11 / 163） | 一次都没调 |

30b 不只是答错，它还给出了精确的错数字、不带任何不确定表示。所以 `route_ask` 的 `DEFAULT_MODEL` 固定成 120b，**不跟随 `.env` 的 `ZHIHU_LLM_MODEL`**；要换用 `KB_ROUTE_MODEL` 显式指定。

### 事实题的提示词要防「自己发明 pattern」

即使模型愿意调工具，它仍会糟蹋机会。真实发生的一次：问「App.tsx 里指向 `./` 的 import 有多少条」，它连调 6 次 `grep_count`、每次换一个自己发明的 pattern，最后报 **2**；而工具用 `from './` 第一次就返回 28。

修法写在 `FACT_SUFFIX` 里：**关键词从问题里原样抄，不要改写、不要加转义**；**工具的返回值就是答案**，不要因为「看起来太多/太少」就换 pattern 再试；如果怀疑 pattern，把第一次的 pattern 和数字一起写进答案。改完之后同一题只调 1 次、答 28、5.6 秒。

### 最终三题的实测

| # | 问题 | 工具调用 | 结果 |
| :-- | :-- | --: | :-- |
| 1 | 首屏为什么这么大？最直接的两个切入点 | 未用 | 给出结论+依据（包内已够） |
| 2 | 把 Sidebar 改成 React.lazy 要动哪些文件、注意什么 | 9 次（grep_count / read_block / find_line） | 给出改动文件与注意点 |
| 3 | App.tsx 里指向 `./` 的 import 有多少条 | 1 次 `grep_count` | **28**（真值 27/28，两种口径都接受） |

耗时 25.3 秒 / 3 问。

## 选型规则的唯一来源是 git（不是第二份清单）

一次真实任务暴露了双真值的代价：想看「codeb 的目录表怎么放进 web」，`kb route --around webview/server.mjs` 能看见 `webview/` 的依赖闭合，但 `kb dispatch webview/` 报**「写范围 0 个代码文件」**。查下来 `webview/` 8 个文件全部已进 git，却被 `repo/.kbignore` 明确排除（注释写着「知识库自身的工作目录，不是源码」）。两条路径对同一批文件给出相反结论。

按使用者的裁定改了规则：

- **git 可用**：候选全集取「已跟踪 + 未跟踪但未忽略」（`git ls-files --cached --others --exclude-standard -z`）。进了 git 的就是重要的；刚建好还没 add 的也能进包；`.gitignore` 仍然生效。
- **git 不可用 / 没有 `.git`**：扫整个项目，但仍跳过 `node_modules` / `dist` / `.git` / `_kbwork` 这类依赖和产物目录。
- **`.kbignore` 停用**。`IgnoreRules` 保留成兼容层（`load/parse` 返回空、`ignored()` 恒 False），`prune_dir()` 只剩依赖目录兜底，三个下游调用点（kb.py、`distill/tokenstat.py`、`distill/projtree.py`）全部改走 git。

后缀限制也放开了：之前 `_resolve_import` 对 ESM 里原样带后缀的 `import './sqlite.mjs'` 解析失败——`with_suffix("")` 把 `.mjs` 也剥掉，再加 `.js` 永远拼不对，`--around server.mjs` 只报它自己 1 个候选。现在先试原样 spec，再试后缀变体（含 `.mjs`/`.cjs`/`.json`），修完后是 3 个候选 / 9,131 tok。

`mcp/smoke.ts` 加了 4 条断言（现 101 通过 / 0 失败）：dispatch 看得见 webview、写范围不是 0、pack 装得出源码、around 能解析 `.mjs` import。

### 这次任务的路由实测（目录表 → web）

规格 5 成员 / 24,707 tok / 29 知识节：`webview/README.md` full、`server.mjs` index、`data.mjs` index、`app.js` full、`kb.py` index。三问全新会话，29,870 / 29,877 / 29,879 tok，28.8 秒。

模型从包里还原出完整数据通路（`repo/00-projects.md` → `data.mjs` 的 `parseChildren`/`buildTree` → `server.mjs` 的 `/api/data` → `app.js` 的 `renderTree`/`renderNode`），也列出了可复用的现成能力（递归树渲染、节点详情、编辑保存、KPI、三层懒加载）。

**但第 2 问暴露了 index 档的真实局限**：模型说「`server.mjs` 中的 `renderTree`/`renderNode`」，实际这两个函数在 `app.js`——它拿到了 5 个成员的签名列表，却把跨文件的函数归属搞混了。`index` 档给的是「有哪些函数」，不是「函数住在哪个文件里」的可靠证据。以后问「改哪里」这类需要精确文件归属的问题，落点文件要给 `full`，或者问题里点名文件让 `find_line` 去定位。这是提示词修不了的，是装订保真度的边界。
