---
covers:
  - kb.py
updated: 2026-11-18
---

# Commands

十一个命令。**只有 `kb upsert` 和 `kb plan close` 会写**（后者也经由 `upsert`），
其余全部只读。

所有命令都支持 `--json`（MCP 层依赖它）。**JSON 字段一旦变更，必须同步改 `mcp/server.ts`**——
这是工具层与内核之间唯一的接触面。

## The eleven commands

| 命令 | 作用 |
| :-- | :-- |
| `kb tree [--depth N] [--repo X] [--flat]` | 下行浏览：按目录折叠输出标题与一行提示；`--flat` 忽略 parent |
| `kb read <page> [--section "标题"]` | 读整页，或只读某一节 |
| `kb heads <page>` | 列出一页的所有标题 |
| `kb search <词> [--repo X] [--limit N]` | 全库搜词，带 `路径:行号` |
| `kb where <源码路径> [--repo X]` | 上行反查：哪些页覆盖这个文件 |
| `kb graph [--repo X] [--hub N] [--top N]` | covers 投影成页间图：hub / 孤立页 / 重复覆盖 |
| `kb plan [--repo X] [--only 桶]` | 散落在各页 `## 计划` 的条目，状态按锚点现场算 |
| `kb plan close P-ID --into <页> --section <节> --body-file f` | 关闭一条计划：先写知识，再删条目 |
| `kb pack <scope> [--budget N] [--no-source]` | 现场装订上下文册子：源码 + 相关节 + 大纲，打 stdout 不落盘。`--no-source` 只要知识层（省约 75%） |
| `kb dispatch <scope>...` | 派发检查：写范围互斥 / 共享知识 / 接口面 / 串行点 |
| `kb upsert ...` | 写入：命中即更新、miss 即补充 |
| `kb init` | 初始化骨架 |

前五个与 `graph`、`plan` 全部只读；只有 `upsert` 和 `plan close` 会写，
且两者都经由同一个 `upsert` 实现——写入路径始终只有一条。

全局参数 `--root <目录>` 可显式指定知识库根；默认从当前目录向上找 `.codeb`。

## `--depth` counts from the repo directory

`--depth 1` 只显示仓库根下的页面，`--depth 2` 再展开一层子目录，默认 3。

这个参数曾经完全失效——`--depth 1/2/3` 输出完全相同，因为递归终止条件多算了一层偏移。
**所以它现在被写进冒烟测试**：折叠行为不成立时，整个导航设计就退化成文件清单。

## Path resolution is lenient, but never guesses

这三个写法等价：

```text
kb read l1-primitives
kb read collector/l1-primitives
kb read infohub/collector/l1-primitives.md
```

但**裸名指向多页时报错并列出全部候选，退出码 2**，不猜第一个。

理由：静默选错页是最坏的失败方式。调用方拿到了内容、以为拿到了正确的，
实际是另一个仓库的同名页。它不会报错，只会让后续判断建立在错误前提上。

解析顺序是**精确匹配优先，后缀匹配兜底**：先试 `rel` 全等或去掉仓库前缀的裸名全等，
没有才用后缀匹配。所以 `infohub/overview` 永远指向想指的那页，
不会被 `codeb/overview` 干扰。

## `kb upsert`: three shapes

```bash
# 新建（miss）：topic 决定折叠到哪个子目录
kb upsert --repo infohub --topic collector --title "L1 primitives" \
  --covers collector/kit/ --body-file body.md

# 命中：替换某一节（该节不存在时自动追加）
kb upsert infohub/collector/l1-primitives --section "Testing" --body-file body.md

# 命中：追加到文末
kb upsert infohub/collector/l1-primitives --append --body-file body.md
```

`--replace` 是第四种，整页替换，**慎用**——它会丢掉没写进 body 的所有节。

工具会：建目录、合并并去重 `covers`、写 `updated` 日期、
拒绝空正文（退出码 2）、统一 CRLF→LF 且不写 BOM。

### Why `--body-file` exists

正文一律优先用文件传，不用命令行参数。

原因很具体：Windows 的 PowerShell 会把长命令行截断，被截断的位置看起来像语法错误，
排查方向一开始就会走偏。`--body` 就因此失败过一次。

`--body-file` 让「正文有多长」与「命令有多长」彻底解耦。
MCP 层仍用 `--body`（通过 `spawn` 传 argv，不经过 shell，没有长度问题），
但人和脚本应该用 `--body-file`。

### Idempotent filenames

标题没有 ASCII 字符时，文件名回退到**标题的 sha1 前 10 位**（`page-<hash>`），
而不是时间戳或序号。

同一个标题必须永远映射到同一个文件名。用时间戳或序号，重跑一次同样的 `kb upsert`
就会多建一页，而「多出来的副本」在知识库里极难被发现和清理。

### Duplicate heading guard

`--section X` 且该节不存在时，工具会加一层 `## X` 再放正文。
但如果 body **自己已经以同名标题开头**，它不再加第二层——
否则会得到 `## X` 下面紧跟 `## X`，读起来是空节。

这个坑是实际踩到的：用 `--body-file` 传一个自带标题的文件，读回来发现内容空了。

## `kb search` ignores whitespace

查询词与每一行**都去掉全部空白**再比。

原因：搜「软404」原本 0 结果，因为正文写的是「软 404」。中英混排时有没有空格
完全看作者习惯，而作者（模型或人）不会记得自己当初写的哪一种。

代价是搜不到「把词拆开」的内容，比如搜 `abcdef` 不会命中 `abc def`。
这个代价可以接受——需要跨词检索时应该用更具体的关键词，而不是靠空格碰运气。

## Exit codes

| 码 | 含义 |
| :-- | :-- |
| 0 | 成功（包括「查不到」这种正常结果） |
| 1 | 未捕获的内部错误 |
| 2 | 用法错误：页面不存在、路径有歧义、正文为空、拒绝覆盖 |

**「查不到」是 0，不是错误。** `kb where` 没命中、`kb search` 没命中，
都是正常结果，不是失败——把空结果当错误会让调用方无法区分「没写过」与「出错了」，
而这两种情况需要的动作完全相反。

## `kb graph`：索引图就是 covers 的投影

不需要新建 `index.md` 或 `graph.json`。图形一直存在：两页共享任一 `covers` 路径即相邻，`kb graph` 每次现场算出来：

```
kb graph [--repo R] [--hub 5] [--top 20] [--json]
```

输出三类信号，各有明确用途：

| 信号 | 含义 | 该怎么用 |
| :-- | :-- | :-- |
| hub | 度数 ≥ `--hub` | 事实上的入口页。它自己可能不知道，值得在正文里加指向邻居的路由 |
| 孤立页 | 有 covers 但没有共享者 | 与其它知识脱节，拆页或补 covers 的首选 |
| 重复覆盖 | 同一路径被多页描述 | 正常（多视角），但要确认说法不互相矛盾 |

实测基线（全库）：59 页 / 114 条 covers 路径 / 57 条页间边 / 8 个 hub / 14 个孤立页 / 29 条重复覆盖 / 1 个无 covers。

**投影结果不是树。** 一个源文件天然被多页描述，把图强行树化会丢知识。所以分工是：**树用 `parent` 表达拆分，关联用 `kb graph` 表达**，两者不互相替代。

`--json` 输出 `{pages, covers_paths, edges, hubs, isolated, no_covers, shared_covers}`，可直接喂给任意渲染器——**不依赖任何后台进程**，这与「每次现场扫目录」的硬契约一致。若渲染工具需要后台 daemon（如 viscode），不要把项目知识的读取依赖在它上面：daemon 挂掉时知识会整体不可读。

## `kb plan`：计划散落在各页，状态现场算

计划不是独立文档，而是散落在各页 `## 计划` 小节里的条目——和知识同构。哪一页描述那块代码，待办就写在那页。

```
- [ ] P-<slug> 一句话说清改什么 — done: <锚点>
```

**只允许 `[ ]` 和 `[-]`，不允许 `[x]`**，写了会被拒收。理由：「已实现」是关于代码的断言，而代码的真值只能来自代码本身。手写 `[x]` 会在功能被回退、重命名或从未落地时静默过期，读者却以为已经有了。这与当年的 `manifest.toml` 是同一类失败——把能现场算的派生状态写进文件。

锚点三种语法：

| 锚点 | 判定 |
| :-- | :-- |
| `done: path a.py, b/` | 全部存在→landed；部分→partial；都不在→no-code |
| ``done: grep kb.py `flock|msvcrt` `` | 匹配到→landed，否则 no-code |
| `done: none` | 恒进 manual，交人判 |

锚点缺失判 manual 而不是 no-code 是刻意的：误报「未实现」会让人重做已完成的事，误报「已实现」会让人以为不必做；两种误报里指向人工复核的代价最小。

四桶与行动：

```
kb plan [--repo R] [--only open|partial|manual|stale|dropped] [--json]
```

- **open**（锚点核不到）→ 真正要干的活
- **partial**（部分路径存在）→ 做了一半
- **manual**（无锚点/看不懂）→ 人看一眼，能自动判就补锚点
- **stale**（锚点已匹配 = 代码里已经有）→ **该收编进知识后删掉条目**
- dropped（已否决）→ 留着防重新提议

ID 同一仓库内必须唯一，重复时 `kb plan` 会报警，`close` 会拒绝而不是猜。

### 关闭 = 先落知识，再删条目

```
kb plan close P-xxx --into codeb/defects --section "某节" --body-file body.md
```

顺序不可颠倒，且由一条命令保证：

- **只删行** → 丢掉最有价值的部分（为什么当初要做它），事后无处可查
- **只写正文** → 条目残留，读者仍以为待办

所以 close 先走 `kb upsert` 写正文，成功后才删条目行；任一步失败都不产生「已完成但知识没落地」的中间状态。

`stale` 桶是**清理提示，不是成就墙**。条目该被 close 收编进正页（背景 + 结论 + 放弃了什么），而不是勾成完成——那会让计划页变成第二个白板。
