---
covers:
  - README.md
root: D:/work/project/codeb
updated: 2026-11-18
---

# codeb overview

给 LLM 维护的多仓库知识库。目标只有一句：**结构少到不会用错，写入便宜到愿意写。**

## Where to look

| 你要做什么 | 看哪页 |
| :-- | :-- |
| 搞清整体是什么 | 本页 |
| **把知识库接进客户端** | `codeb/connect-client` |
| 用命令 / 写页 | `codeb/commands` |
| 页面格式与 `covers` / `parent` 规则 | `codeb/design/page-format` |
| 一段说明该放代码还是知识库 | `codeb/design/where-knowledge-goes` |
| 写出一页有人读的东西 | `codeb/design/writing-pages` |
| 为什么这么设计、推翻过什么 | `codeb/design/decisions` |
| MCP 工具语义与写入循环 | `codeb/mcp-tools` |
| MCP 协议实现细节 | `codeb/mcp-transport` |
| 踩过的坑 | `codeb/defects` |
| **收割历史会话（在场 agent 没写怎么办）** | `codeb/distill/distill-gates-and-their-silent-failure-modes` |
| 谁该写、什么时候写（角色分工） | `codeb/design/page-ca43d322aa` |
| 待办与缺口 | `codeb/plan`（`kb plan`） |
| 拆页与页间关系（parent / graph） | `codeb/design/page-format` |
| **给一个任务装订上下文 / 派发前查冲突** | `codeb/pack-and-dispatch` |
| **做子 agent 的基座（自己写 loop 还是用 pi）** | `codeb/subagent-base` |
| **9 个基座候选的真实体量与依赖实测** | `codeb/agent-base-survey` |
| **codeb 里派子 agent（openai-agents 只当壳）** | `codeb/spawn-subagents` |

## What it is, in three layers

```text
kb.py              内核。所有规则只有这一份实现，只用标准库，无状态。
mcp/server.ts      薄壳。只声明工具、校验参数、spawn 内核、回传 JSON。
repo/              数据。纯 Markdown，没有索引文件、没有数据库。
```

这个三分的意义在于**改动会落到哪一层是确定性的**：

- 改「怎么解析路径」「怎么匹配 covers」→ 只改 `kb.py`，MCP 层不用动。
- 加一个 MCP 工具 → 只改 `server.ts` 的 `TOOLS` 数组，内核不用动。
- 加知识 → 只写 `repo/` 下的 md，两边都不用动。

如果某次改动需要同时动 `kb.py` 和 `server.ts` 才能让一个功能正确，那是设计被破坏的信号。

## Why no index, no database

`kb tree` 每次现场扫目录，`kb where` 每次现场算 `covers`。

代价是库大了会慢（几十到几百页仍是毫秒级）。
收益是**永远不会出现「索引与实际不一致」**——这是知识库里最致命的一类故障，
因为它让「查不到」与「没写过」变得无法区分，而这两种情况需要的动作完全相反。

上一版设计用过 `manifest.toml` 集中登记页面，作废的原因就是这个：
manifest 一定会和目录漂移，而漂移不报错。

## The four mandatory rules

1. 根下必须有 `.codeb`，所有页面在 `repo/` 之下。
2. `repo/` 第一级目录 = 一个仓库，**英文名**。
3. 文件名**英文小写连字符**（`l1-primitives.md`）。
4. 页面**标题英文**，**正文中文**。

第 2–4 条都是为了压缩导航成本：`kb tree` 与 `kb heads` 的输出会反复进入模型上下文。
中文标题在小样本下更贵，且同一概念容易漂移成多种译法（「写入通道/写入途径/写入方式」），
一旦漂移，`kb read --section` 就再也找不到它。

正文保持中文，因为那是知识的载体、是给人读的。
两者靠 `kb tree` 里那行**中文首句提示**接上：英文标题省 token，提示让人（和模型）看懂这页在讲什么。

## Directory folding is a default, not a rule

`collector/` 折叠在 `infohub/` 之下，而不是五页平铺加「采集-」前缀。

平铺不是「错」，但它会让 `kb tree` 退化成文件清单：页数一多，读的人无法从结构看出归属。
折叠之后前缀也不再需要——目录本身已经表达了归属，文件名只需说清「在这一层里是什么」。

所以规则是「**默认按源码路径折叠**」，而不是强制几层。

## How knowledge gets in

只有一条路径，而且它是幂等的：

```text
kb_where <源码路径>   →  有命中：kb_upsert page=... --section ...
                      →  没命中：kb_upsert --repo ... --topic ... --covers ...
```

`kb_upsert` 是**唯一写入口**。开第二个写入路径，就意味着第二套关于 frontmatter、
小节合并、幂等的规则，而两套规则迟早不一致。

## Where the real cost is

这个项目里最容易做错的不是功能，而是**跨平台文本处理**。
实际踩过、并写进 `_shared/conventions` 的：

- PowerShell 的 `-replace` + `Set-Content` 会按 GBK 读 UTF-8 文件，**直接毁掉中文正文**。
- `Set-Content -Encoding UTF8` 在 Windows PowerShell 5.x 会写 BOM，使 frontmatter 的 `---` 判断失效。
- CRLF 不会报错，只会让按行号切 markdown 小节**静默错位**。

因此读写约束是硬的：读用 `utf-8-sig`，写用 `write_bytes(text.encode("utf-8"))`，
全程 LF，不写 BOM。这三条看起来琐碎，但它们决定 diff 是否干净、小节是否读得对。

## Testing

`node mcp/smoke.ts` 启动真实 server、走真实 stdio 协议、断言 63 项。
**不 mock 边界**——本项目构建中发现的缺陷（根路径算错、小节拼接破坏结构、
位置参数被忽略、bodyFile 重复标题）全部只在真实进程下暴露。

## What is deliberately missing

- **没有自动化漂移检查**（覆盖/孤儿）。将来若要加，必须是独立只读命令，
  绝不参与写入路径，也不要求额外元数据文件。`kb graph`、`kb plan`、
  `kb pack` 与 `kb dispatch` 都是这个形态：全部只读、每次现场算，
  不写索引、不落盘、不要求新元数据。
- **没有删除/重命名命令**。直接用文件系统操作，然后跑 `kb tree` 确认没有断链。
- **没有跨仓库引用检查**。`covers` 写错路径不报错——这是刻意的：`covers` 描述意图，
  不该被当成「引用的文件必须存在」的断言。
- **没有全文检索优化**。`kb search` 是逐行子串匹配（空白不敏感），几百页够用。
- **锁只约束经由 kb.py 的写入**。它是建议锁，直接改 `.md` 文件不受保护。
