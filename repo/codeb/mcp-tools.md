---
covers:
  - mcp/
  - kb.py
  - README.md
updated: 2026-11-17
---

# MCP tools for maintaining this KB

模型通过这组工具维护知识库，而不是手工改文件。
**所有规则只有一份实现，在 `kb.py`**；`mcp/server.ts` 只声明工具、校验参数、调用内核。

## Why the split exists

每条规则必须只有一个实现。如果 TypeScript 层也懂怎么解析页面路径、怎么匹配 `covers`，
两份实现就会分叉，而分叉的表现形式是「页面明明存在，却永远查不到」——最难排查的一类问题。

所以 `server.ts` 是**刻意做笨的**：

- 它自己从不读页、从不写页；
- 它不判断路径有没有歧义；
- 它不做任何知识格式化。

它只做一件事：`spawn python kb.py <cmd> --json`，解析结果并原样返回。
工具层需要的任何结论，都必须由内核给出。

## The six MCP tools

| 工具 | 方向 | 成本 |
| :-- | :-- | :-- |
| `kb_tree` | 下行浏览，按目录折叠 | 全库约几十 tok |
| `kb_read` | 读一页，或只读一节 | 一节约 150 tok |
| `kb_heads` | 先看结构，再决定读哪节 | 约 40 tok |
| `kb_search` | 知道关键词、不知道在哪页时用 | 每页一行 |
| `kb_where` | **上行反查**：哪些页覆盖了这个源文件 | 几行 |
| `kb_upsert` | 唯一的写入口 | 返回实际动作 |

`kb_init` 只在 CLI，不暴露给 MCP——建骨架是一次性动作，不需要模型在会话中途调用。

`kb_upsert` 是**唯一**的写入口，这一点是刻意的。开第二个写入路径，就意味着第二套
关于 frontmatter、小节合并、幂等的规则，而两套规则迟早不一致。

### `kb_upsert` 的四种模式

| 模式 | 参数 | 改什么 | 危险 |
| :-- | :-- | :-- | :-- |
| 新建 | `repo` + `title` + `body` + `covers` | 造一张新页 | 低 |
| 替换某节 | `page` + `section` + `body` | 该节整段（标题保留） | 中 |
| 追加 | `page` + `append` + `body` | 只在文末加内容 | 低 |
| 细粒度替换 | `page` + `find` + `body` | **只换命中的字面文本**，其余逐字节保留 | 低 |
| 整页替换 | `page` + `replace` + `body` | 整段正文，**未写进 body 的节全丢** | 高 |

前四种里，改一个数字、一句话、一个词应该用 `find`，不要用 `section` 或 `replace`。
`section` 要求整节重写（容易顺手删掉半节），`replace` 会丢掉所有没写进 body 的节。

### `find` 的三个细节

**字面匹配，不认正则、不忽略空白。** `find` 用 `str.count` 与 `str.replace`，所以
空格、全角半角、换行都必须与原文逐字符一致。要改的东西跨行时，把换行写进 `find`。
这条不是限制而是安全设计：正则替换在中文正文上极易一次改坏一大片。

**`expect` 是护栏，强烈建议给。** 命中数与 `expect` 不符时**整体中止、不写入**。
没有它，`find: "20"` 可能一次改掉七处（`200`、`2020`、`20 个` 全都命中）。
这是这类编辑最危险的失败方式：它不报错，只是悄悄多改了几处。

**`body` 传空串才是删除。** 「没给 body」与「给了空串」是两件事：
前者报错（多半是漏了参数），后者才执行删除。这个区分是必要的——
把两者合并，漏传一次参数就会静默删掉正文里的一段。

`find` 还要求目标页**必须已存在**：页不存在时它会直接报错，而不是落到新建分支
（否则「替换值」会被当成正文写进一张只含一个词的新页，这个坑实际踩过）。

### 为什么 `find` 值得单独存在

没有它之前，清理漂移数字只能靠 Python 脚本直接改文件——那等于**绕过唯一写入口**，
而绕过写入路径就绕过了 `_write_page` 的 UTF-8 无 BOM、LF 统一、frontmatter 重写。
`find` 把「改一处字面文本」这件高频小事收回到了内核里。

它同时解决了 `--section` 的一个老问题：子串匹配。`--section` 传错一个词（写 `five`
而原文是 `six`）会**静默追加一个新节**；`find` 传错则直接报「没找到」。前者哑、后者响。

## The update-not-duplicate loop

`kb_where` 存在的意义，是让「命中就更新、没命中才补齐」比「凭印象新建」更省力：

```text
1. kb_where <源文件路径>        → 有命中走 2，没命中走 3
2. kb_upsert page=<命中的页> --section <节名>     替换或追加那一节
3. kb_upsert repo=<仓库> topic=<子目录> title=<英文> covers=[路径]
```

跳过第 1 步，就会产生两页从不同角度描述同一个文件——一旦有两页，就没有一页是权威的。

## Writing must be idempotent

同样参数的 `kb_upsert` 重复执行，不能建出第二页。

所以标题没有 ASCII 字符时，文件名回退到**标题的哈希**，而不是时间戳或序号：
同一个标题必须永远映射到同一个文件名，否则重跑一次就多一页。

## Transport specifics live elsewhere

分帧方式、错误分级、通知为什么不回复、Node 版本约束——这些都在 `codeb/mcp-transport` 里。
放在那页的原因是：它们是**协议层**的问题，与本页的「工具语义」读者不同、修法不同。

## Zero dependencies is a decision, not laziness

官方 SDK 会带来一棵依赖树，而这个项目的全部工作只是调一个 Python 脚本。
手写 stdio JSON-RPC 大约 120 行，直接消掉「哪个 SDK 版本改了分帧」这一整类问题。

代价是：将来要用 resources / prompts / sampling，得自己加。
这个代价可以接受——这个 server 只需要 tools。

## Testing

`node mcp/smoke.ts` 会启动真实 server、走真实协议、断言 24 项行为，
覆盖新建 / 追加 / 替换三条写入路径和错误分支，跑完自己清理残留文件。

冒烟测试在构建过程中抓到三个真实缺陷：

- `PROJECT_ROOT` 多向上算了一级，导致内核永远找不到；
- 替换小节时把下一个小节标题直接拼在正文末行，**破坏 Markdown 结构**，下一次写入会读错；
- 新建时忽略了位置参数 `page`，导致已存在的页被报成「需要 --repo」。

## Windows-specific traps hit while building this

- **PowerShell 的 `-replace` + `Set-Content` 会毁中文**：它按本地编码（GBK）读 UTF-8 文件，
  写回时就变成乱码。改文件内容一律走 Python 或本仓库的 `write` 工具，不要用 PowerShell 做文本替换。
  本次构建就这样毁掉过 `overview.md`，靠重写才恢复。
- **长命令会被截断**：多行 `python -c "..."` 极易被截断成语法错误，
  改用临时脚本文件。
- **控制台乱码不代表文件坏了**：先 `read` 文件确认，再判断是否真损坏。

## Decisions made while building this, and why

这几条是本轮对话里定下来的，改动时不要推翻而不说明理由。

**标题也要用英文。** 最初的版本是「英文文件名 + 中文标题」，导航输出仍是中文。
但 `kb tree` 与 `kb heads` 的结果会反复进入上下文，中文标题在小样本下 token 更贵，
且同一概念容易出现多种译法（「写入通道」/「写入途径」/「写入方式」），
一旦标题漂移，`kb read --section` 就找不到它了。所以标题统一英文，正文仍是中文。

**目录必须折叠，不能平铺。** 采集模块最初是五页平铺在 infohub/ 下，
文件名带「采集-」前缀。页数一多，`kb tree` 就退化成文件清单。
改成 `infohub/collector/` 后，前缀也不再需要——目录本身已经表达了归属。

**仓库目录用英文名。** `通用/` 改成 `repo/_shared/`，`infohub/` 保持英文。
中文目录名在跨工具（git、shell、MCP 客户端）时不断触发编码问题，
而这些问题每次都要花时间确认「是显示问题还是真坏了」。

**MCP 层零依赖。** 不引官方 SDK。理由是：这个 server 的全部工作是调一个 Python 脚本，
而 SDK 会带来一棵依赖树和一整类「哪个版本改了分帧」的问题。手写约 120 行。
代价是将来要用 resources / prompts 得自己加——接受，因为这里只需要 tools。

**Node 24 直接跑 .ts。** 没有构建步骤、没有 `dist/`、没有 watch。
代价是降级 Node 就失效，所以版本要求写进了 README。

## Why `--body-file` exists
