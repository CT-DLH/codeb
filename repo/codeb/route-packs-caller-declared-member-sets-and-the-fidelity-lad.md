---
title: Route packs: caller-declared member sets and the fidelity ladder
covers:
  - kb.py
  - distill/agent/codeb_agent.py
  - distill/agent/spawn.py
---

# Route packs: caller-declared member sets and the fidelity ladder

一句话：`kb pack` 的装订单位是**范围**（一个文件，或一个目录里所有文件平分预算）；
路由包的装订单位是**leader 显式点名的成员集**，每个成员单独声明保真度（全文 / 索引 / 大纲）。

这不是给 pack 加一个参数。两者的失败方式不同：pack 怕「知识层被挤光」，
路由包怕「leader 点的文件被摊平或删掉」——那是另一种残缺，而且更像完整。

## 现状为什么不够（实测，不是推测）

改 `apps/web/src/components/Sidebar.tsx`，leader 知道真正要碰的是 6 个文件。
用现有两种写法装订，都对不上这个认知：

| 写法 | 结果 | 问题 |
| :-- | :-- | :-- |
| `kb pack <Sidebar.tsx>` | 6,228 tok，落点文件**全文** 5,383 + 知识 845 | 只装一个文件，`api.ts` / `button.tsx` 完全不在场 |
| `kb pack <components/>` | 22 块 7,428 tok，**全是大纲**，精度 none | 22 个文件平分预算，落点文件的全文反而没了 |
| 显式 7 成员 + 各自 role | **5,550 tok / 15 块** | 3 全文 + 1 索引 + 3 大纲 + 知识 2,546 tok（原型实测） |

关键点：**默认预算下 `pack` 单文件本来就会给全文**（5,383 tok ≤ 13k×0.6=7.8k）。
所以这次增强不是「让 pack 吐全文」，而是：

1. 让 leader 能声明**一组**文件（不是一个）；
2. 让**每个成员**的保真度由 leader 定，而不是由「预算 ÷ 文件数」定；
3. 让这份声明在预算压力下**不被静默抹掉**。

### 1-hop import 闭包的真实大小：19,166 tok

`Sidebar.tsx` 深度 1 的 import 闭包：

| 文件 | tok | 占比 |
| :-- | --: | --: |
| `apps/web/src/api.ts` | 12,218 | **64%** |
| `Sidebar.tsx` | 5,383 | 28% |
| `ImportPanel.tsx` | 735 | 4% |
| `ui/button.tsx` / `ui/tooltip.tsx` / `lib/utils.ts` | 474 / 278 / 78 | 4% |

一个 import 吃掉三分之二预算。**所以「把框架相关的文件都装原文」不成立**——
必须分档：落点文件全文、调用面只给索引、样式约定给全文（它小）、无关邻居给大纲。
这正是「路由」要表达的东西：不是文件集合，是**每份文件给到什么程度**。

## 三个必须先修的缺陷（blocking）

### 1. 带仓库前缀的目录 → 0 块 0 tok，退出码 0

```text
$ python kb.py pack atomkgraph/apps/web/src/components/ --json
blocks 0  total 0  precision none        ← rc=0，没有报错
$ python kb.py pack apps/web/src/components/ --json
blocks 22 total 7428                     ← 同一个目录，只差前缀
```

根因在 `cmd_pack` 的目录分支：`target` 用的是剥了前缀的 `rel_scope`（所以单文件正常），
但 `src_files(base, scope, root)` 传的是**带前缀的 `scope`**，恒返回空列表。
于是「目录 + 前缀」这条路径装出一份整齐的空册子。

这是本项目点名过的最危险失败模式：**安静地交出一份残缺但整齐的册子**。
而 leader 天然会写带前缀的路径——`kb where` / `kb pack` 的文档示例都带前缀。

判据：装订结果 `total == 0` 时必须非零退出并说明原因（是范围空？还是路径没解析？），
不能 rc=0。

### 2. 同一个根因的第二种症状：落点文件被当成自己的兄弟

```text
$ python kb.py pack atomkgraph/apps/web/src/components/ui/button.tsx
  prio 5  474  atomkgraph/.../button.tsx  40 行  全文      ← 目标
  prio 1   43  apps/web/.../button.tsx    40 行           ← 同一个文件，又给了一份大纲
$ python kb.py pack apps/web/src/components/ui/button.tsx
  prio 5  474  atomkgraph/.../button.tsx  40 行  全文      ← 目标（没有重复项）
```

一重一轻，所以它不报错、只是白付 token；目录那条路径则是整份册子为空。
修法：兄弟比较改用 `r != rel_scope`，且 `render_source` 的 `rel` 参数也统一传裸路径
（现在前缀从 `scope` 漏进了 label，两种写法输出不逐字节一致，
「带前缀 == 裸路径」这条断言没法直接写）。

### 3. `dispatch` 对带前缀目录报错，且错误信息指向错误的修法

```text
$ python kb.py dispatch atomkgraph/apps/web/src/components/ atomkgraph/apps/server/src/
atomkgraph/apps/web/src/components 定位不到（先在仓库 overview 页写 root: <磁盘路径>）
```

`scope_repo` 其实**已经解析成功**（返回了 repo 和磁盘根），
错在下一行 `target = base / scope`——又拼了一次前缀。
但错误文案和 `pack` 的「root 没写」共用一句，于是把用户指向了完全不相关的修法。

这条要有单测：**带前缀与裸路径必须产出相同的 `files` / `conflicts` / `shared_pages`**。
`dispatch` 和 `pack` 对同一个 scope 给出不同结论，是 `kb where` 与 `kb pack` 打脸那次的同型缺陷。

另外：`kb pack <components/>` 报 `precision: none`（没有页 covers 那个目录），
这本身是对的。但组合上缺陷 1 之后，**前缀写法的 none 和路径没解析的 none 长得一模一样**。
修 1 的时候要顺手把两者分开报。

## 路由规格：只落「意图」，不落「内容」

```json
{
  "repo": "atomkgraph",
  "entry": "apps/web/src/components/Sidebar.tsx",
  "budget": 13000,
  "members": [
    {"path": "apps/web/src/components/Sidebar.tsx", "role": "full",    "why": "改动落点"},
    {"path": "apps/web/src/components/ui/button.tsx", "role": "full",  "why": "样式约定必须照抄"},
    {"path": "apps/web/src/api.ts",                 "role": "index",   "why": "只关心 moveKnowledge 的签名"},
    {"path": "apps/web/src/components/ImportPanel.tsx", "role": "outline"}
  ]
}
```

这份 JSON 可以落盘，落的是**意图**（哪些文件、各自多细、为什么）；
源码正文永远现场读。这与「册子不落盘」不冲突：

- 册子落盘 → 内容会和代码分叉，然后照着旧内容开工；
- 意图落盘 → 内容变了，重新装订就是新的；文件被删了则**立刻报错**。

`why` 不是注释，它进成员索引（见下），是 agent 判断「这个文件我该看到多少」的唯一依据。

## 保真度三档 + 一条不变式

| role | 装什么 | 复用哪个现成函数 |
| :-- | :-- | :-- |
| `full` | 全文 | `_read_text_robust` 或 `render_source(..., allowance=大值)` |
| `index` | 语义块索引（`函数名@行号  L起-止  签名`） | `kb._source_index_block` |
| `outline` | 签名大纲 | `kb.file_outline` |

### `render_source` 的 allowance 语义坑

`allowance=0` 不是「不限」，而是「按 400 行参考线判」：

```text
allowance=      0     809 tok  大纲     ← 想要全文却拿到大纲
allowance=   3000     809 tok  大纲
allowance= 100000   5,383 tok  全文
```

所以 `full` 这一档必须显式给大 allowance，或者干脆直接读文本。
**不能靠「不传 allowance」表达「要全文」**——那个默认值的意思是「用行数启发式」，
和调用方的意图正好相反。这与 `--with-source` 那次 CLI 默认值把 dataclass 默认值静默压掉，
是同一类错误：**默认值有语义时，省略参数就是一次误表达。**

### 不变式：成员清单永不丢

预算不够只降保真度，不删成员：

```text
full → index → outline → 只留一行路径 + 取回命令
```

理由用实测数字说。同一份 7 成员包，只压预算不降档：

| 预算 | 留下 | 丢了什么 |
| --: | :-- | :-- |
| 9,000 | 7/7 块 7,578 tok | — |
| 5,000 | 3/7 块 830 tok | `ImportPanel` 大纲、`i18n` 大纲、**`api.ts` 索引 1,184**、**`Sidebar.tsx` 全文 5,383** |
| 2,500 | 同上 | 同上 |

两个数字值得记住：

1. **5,000 → 2,500 时留下的东西完全一样**。prio 阶梯是先丢整档，
   prio 5 一丢就直接到 830 tok，深压无意义——降预算在这个区间里不是连续的。
2. 落点文件（5,383 tok，占包 97%）**一步到位被整块删掉**，留下的 830 tok 全是别的小文件。
   agent 会以为「这个范围只有这些」。

这条与 pack 的「目标源码最后才丢」方向一致（都是保源码），但判据不同：
pack 按 prio 全局排序，路由包**按成员的 role 降级**，因为 leader 的点名本身就是最强的相关性信号。

## 超预算必须大声

默认**拒绝装订**：打印溢出表（超了多少 / 每个成员各自多少 / 降档能省多少），
退出码非零，让 leader 决定。两个显式开关才允许继续：

- `--degrade`：按阶梯降档（full→index→outline），并在包顶写警告
- `--drop <path>`：点名删成员（必须逐个写出，不接受「自动挑最小的丢」）

不做默认降级，因为**悄悄降一档，答案就会基于大纲而不是原文**——
而长得像「装订成功」的结果最难被发现。上表那种 830 tok 的包就是活例。

## 知识层：跨成员去重，但会带噪音

路由包的知识层 = 每个成员各自反查后**按 (页, 节) 去重**的并集。实测有污染：

| 成员 | 命中 | tok | 其中可疑 |
| :-- | --: | --: | :-- |
| `Sidebar.tsx` | 5 节 | 845 | — |
| `api.ts` | 6 节 | 2,048 | `page-5bb3b9f185 :: 挂载题目不可删除（挂题守卫，R63）` **1,232 tok** |

匹配判据是「正文里出现文件 stem」（`kb.py:1620`），`api` 这种短 stem 会大面积误命中。
路由包因为成员多、每成员都可能带进这类小节，噪音会累加，
所以需要降噪规则（按「被几个成员共同点名」排序，取前 N 节），而不是简单并集。

## 输出形态

```text
# 路由包：<entry>   （仓库/预算/实装/成员数）
## 成员索引                          ← **永不丢**，agent 的页表
   apps/web/src/components/Sidebar.tsx   full     526 行  5,383 tok   改动落点
   apps/web/src/api.ts                   index   1,094 行  1,188 tok   只关心 moveKnowledge
   apps/web/src/components/ImportPanel.tsx outline    71 行     57 tok
## 成员正文 …                        ← 每个成员按自己的 role
## 共享知识层 …                      ← 去重后的小节
## 有意省略
   降档：api.ts full→index（省 11,030 tok）
   未装：Sidebar 里 `TreeNodeView` 之外的 12 个块 —— read_block(...)
```

成员索引放最前，是因为它同时回答两个问题：**我手上有哪些原文**、
**哪些只给了目录**。现在 `pack` 的「有意省略」只在文末回答后者，agent 得读到底才知道。

## 提议器：`kb route --around <entry> --depth 1`

leader 说「根据项目框架找到可能会用到的文件」，这一步必须**只提议、不装订**：

```bash
kb route --around apps/web/src/components/Sidebar.tsx --depth 1 --json
```

输出每个候选的 `path / 行数 / tok / 建议 role / 被谁 import`。建议 role 按体量给：

| 成员 tok | 建议 |
| --: | :-- |
| ≤ 1,500 | `full` |
| ≤ 6,000 | `index` |
| 更大 | `outline` |

解析器分语言：TS/TSX 用正则抽 `from '...'` + 试 `.ts/.tsx/.js/.jsx` 后缀
（项目里 import 写 `.js`、实体是 `.ts`，这是实测踩到的）；
Python 用 `ast` 的 Import/ImportFrom。**不引入新依赖，不建索引文件。**

为什么把 tok 打出来：`api.ts` 占闭包 64% 这个事实，只有看到数字才会让人改主意。
「算出来的信息不给，等于没算」——`kb_dispatch` 不列文件清单那次，同一参数重复调用了 3 次。

### 关于 1-hop 而不是 2-hop

实测 `Sidebar.tsx` 1-hop 已经 19,166 tok，其中 `api.ts` 一个人 12,218（64%）。
2-hop 会经由 `api.ts` 拉进整个 API 客户端表面，几千到上万 tok 且几乎全是无关端点。

所以 `--depth` 默认 1、且**只对 `entry` 展开**，不对成员递归。
需要更远处的东西时，leader 显式往 `members` 里加一行——那是他的职责，不是解析器的推断。

反方向（谁 import 了我）先不做，但要知道缺了它 UI 改动的**调用方**
（如 `App.tsx` 渲染 `Sidebar`）不会被提议出来。

## agent 侧：`--route` 与「先装原文，再问」

### 一次性任务：`kb agent --route r.json`

`Task.scope` 换成 `Task.route`，`assemble()` 调 `kb route` 而不是 `kb pack`；
`render()` 的五层顺序、`_shared_instructions()`、`COMMON_WORLD` 全部不动——
**cache 布局是既有资产，路由包只是在「知识层」那一层换了内容来源。**

### 多轮询问：`kb agent ask --route r.json`

「先装入原文，再问有原文的 agent」要求 agent 活着。0.25.0 的 `Runner.run` 收 `session=`，
`SQLiteSession(session_id, db_path)` + `add_items` / `get_items` 已在 `_kbwork/agvenv` 里核对过签名。
形态：

```text
turn 1：注入完整路由包 + 第一个问题     ← 装订成本只付这一次
turn 2+：只发新问题                      ← 会话里已有原文，cache 前缀不动
```

这比「每问一次重新装订」省的不只是组装时间（~0.2s），更是**整段前缀的 cache**。
同一条线也被实测过：注入式（0 次工具调用、7.4s）比让 agent 自己调 `kb_pack`（14.8s）快一倍。

两条边界：

- **路由变了就开新会话**，不要在旧会话里追加差异。旧会话里残留的是旧成员的原文，
  追加一条「新增 X」会让两代上下文同时在场，模型无从判断哪份是当前的。
- `ask` 模式的工具集**不给** `kb route` / `kb pack`：组装是 leader 的活、执行是 worker 的活，
  这条分界在 `spawn.py` 里已经立过。

## 路由表即派发表

路由规格是机器可读的，于是它在 leader 侧有第二种用法：**哪个 agent 手上有哪份原文**。
leader 派 N 个 codeb agent、各持一条路由后，「这个问题该问谁」变成查表而不是猜：

```text
问「button 的样式约定」  → agent-B（路由里有 ui/button.tsx, full）
问「moveKnowledge 签名」 → agent-A（路由里有 api.ts, index → 需要它先 read_block）
问「拖拽语义」           → agent-A（full 原文在它手上）
```

索引档的成员要标出来（`index` 不是原文，问细节要它先 `read_block`），
否则 leader 会把「有索引」当成「有原文」去问，然后得到一个基于签名的回答。

## 与硬契约的关系

不新增任何一条：

1. 唯一写入口仍是 `kb upsert`——`route` / `--around` 全只读。
2. 无状态：不建索引、不缓存正文；路由规格是**输入**，不是派生真源。
3. 规则一份实现：复用 `render_source` / `_source_index_block` / `file_outline` /
   `claiming_pages` / `page_sections`。原型 60 行、0 行新抽取逻辑，产出 5,550 tok / 15 块。
4. 自报精度：每个成员都报 `exact / dir / none`。`none` 是待办——
   「这个文件没有知识页，改了没人记得为什么」。

## 落地顺序（每步配一个会红的断言）

| # | 改动 | 断言 |
| :-: | :-- | :-- |
| 1 | 前缀归一：`src_files(base, rel_scope)`、`dispatch` 的 `target`、兄弟比较 `r != rel_scope` | 带前缀与裸路径的输出**逐字节相同**；`total==0` 必须非零退出 |
| 2 | `kb route --spec`（只装订）+ `--json` | 成员数 == 规格里的成员数（**降预算也不许少**）；源文本真的在包里（`"export function Sidebar" in out`） |
| 3 | `--around` 提议器 | 闭包对 `Sidebar.tsx` 能找到 `api.ts`；tok 数字与直接读文件一致 |
| 4 | `Task.route` + `kb agent --route` | `context_tokens` 落在规格预算的 ±10%；`index` 成员的正文**不在**上下文里 |
| 5 | `kb agent ask`（session 复用） | turn 2 的输入长度 < turn 1 的 10%；turn 2 仍引用得到原文里的函数名 |
| 6 | 知识层降噪（按共同点名排序） | 5,550 tok 的样例包降到 4,000 以内且 5 条 Sidebar 契约小节全部保留 |

第 1 步是前置：不修它，第 2 步及之后所有「leader 写带前缀路径」的调用都会装出空包。
**别用「端到端跑通」验收第 2、4 步**——agent 可以靠 `read_file` 自给自足跑通，
管道坏了看不出来（`with_source` 那个 bug 就是这么漏过的）。

## 计划

- [ ] P-route-prefix 修 pack/dispatch 的仓库前缀归一（带前缀目录现在装出 0 块 0 tok 且 rc=0） — done: grep kb.py `src_files\(base, rel_scope`
- [ ] P-route-cmd 加 kb route：显式成员集 + 每成员保真度，成员清单永不丢 — done: grep kb.py `def cmd_route`
- [ ] P-route-around 提议器：1-hop import 闭包，只提议不装订 — done: grep kb.py `def cmd_route_around`
- [ ] P-route-agent Task.route 接进 assemble/render — done: grep distill/agent/codeb_agent.py `route:`
- [ ] P-route-ask 多轮询问（SQLiteSession 复用，路由变了开新会话） — done: grep distill/agent/codeb_agent.py `def ask`
- [ ] P-route-noise 知识层按共同点名降噪 — done: none

## 实测数字

| 项 | 值 |
| :-- | :-- |
| `pack <Sidebar.tsx>` 默认预算 | 6,228 tok（源码全文 5,383 + 知识 845） |
| `pack <Sidebar.tsx> --budget 7000` | 1,654 tok（源码退大纲 809） |
| `pack <components/>`（裸路径） | 22 块 7,428 tok，全大纲，精度 none |
| `pack <atomkgraph/components/>` | **0 块 0 tok，rc=0**（缺陷 1） |
| `Sidebar.tsx` 1-hop import 闭包 | 6 文件 19,166 tok（`api.ts` 占 64%） |
| 路由原型（7 成员 + 知识） | 5,550 tok / 15 块 / 13k 预算（占用 43%） |
| 原型压到 5,000 预算 | 3 块 830 tok（落点文件被整块删掉） |
| `est_tokens` vs tiktoken | 1.00–1.17 倍（偏保守，对预算判定安全） |
| `kb pack --index` 单文件 | 1,595 tok（索引 750 + 知识 845） |
