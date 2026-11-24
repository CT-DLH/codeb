---
covers:
  - kb.py
  - mcp/server.ts
updated: 2026-11-18
---

# Defects found while building this

每一条都是实际踩到的，不是设想。记录格式统一：**症状 → 原因 → 处理**。
症状写「怎么发现的」，因为这类缺陷的共同点是不报错。

## The failure mode they all share

除了编码类问题，下面所有缺陷都有同一个特征：**静默返回了错误的结果，而不是报错。**

- 翻页判错 → 报告写「翻页 12 页」，实际只有 20 条数据；
- 歧义选错页 → 调用方拿到另一个仓库的同名页，内容看起来完全正常；
- 小节拼接破坏结构 → 第一次写入看起来成功，第二次写入读错位置；
- 跨仓库归属错 → `kb where` 返回了不相关的页，让人以为这块已经有说明。

**「看起来成功」比「失败」危险得多**，因为失败会立刻被处理，而看起来成功会被下游继续使用。

## Kernel defects

| 症状 | 原因 | 处理 |
| :-- | :-- | :-- |
| `--depth 1/2/3` 输出完全相同，深层页面永远不展开 | 递归终止条件多算了一层偏移 | 改为按目录层级比较，`level=1` 即仓库自身 |
| 读一个裸名页码，得到另一个仓库的同名页，且无任何提示 | 工具挑了第一个匹配 | **歧义时不猜**：列出全部候选，退出码 2 |
| 从 PowerShell 管道送入中文，写入时 `UnicodeEncodeError: surrogates not allowed` | 标准流未转 UTF-8 | stdin/stdout 都 `reconfigure`，写入前兜底处理代理字符 |
| 搜「软404」0 结果，文中写的是「软 404」 | 逐字匹配，空格差异导致漏命中 | 查询与正文**都去掉全部空白**再比 |
| 替换小节后，下一节标题直接拼在正文末行，再写入一次内容就错位 | 重建时未在插入内容后补空行 | 插入内容后强制补空行；仅当后面还有内容时 |
| 页面已存在却报「需要 --repo」，导致重复建页 | 新建分支只认 `--rel`，忽略位置参数 | 路径优先级改为 `--rel` > `page` > `repo+topic+title` |
| 用 `--body-file` 传自带标题的正文，读回来是空节 | 又加了一层同名标题 | 检测 body 首行是否已是该标题，是则不重复加 |
| 首页 `kb tree` 提示行显示成 `---` | `Set-Content -Encoding UTF8` 在 Windows PowerShell 5.x 写入 BOM，frontmatter 的 `---` 判断失效 | 读用 `utf-8-sig`；写用 `write_bytes(text.encode("utf-8"))` |
| Windows 手工编辑后，按行号切小节静默错位，不报错 | 文件是 CRLF，按 `\n` 切行后每行残留 `\r` | 读后统一 `\r\n → \n`，写时统一 LF |
| `--section "Pipeline and the five statuses"` 打错一个词（写 five 实为 six），页面末尾凭空多出一节，且**不报错不警告** | `--section` 是**子串匹配**（`q in 小节名.lower()`），没命中就走「该节不存在→追加新节」分支 | 写前用 `kb heads <page>` 复制准确节名；发现重复节用 `--replace` 整页重写 |
| `kb upsert --rel <已存在页>` 报错退出码是 **1**，不是文档说的 2 | 该路径走「页面已存在」分支而非参数校验分支 | 更新已有页改用位置参数 `kb upsert <rel> --section/--append`，此时 `--rel` 被忽略 |

## MCP layer defects

| 症状 | 原因 | 处理 |
| :-- | :-- | :-- |
| `initialize` 超时，客户端连不上 | `PROJECT_ROOT` 多向上算了一级，内核路径指向仓库外 | `server.ts` 在 `mcp/` 下，向上一级即根 |
| 未知工具名被当成工具失败返回 | 误用 `isError` result | MCP 规范里未知工具是协议级错误（`-32602`） |
| 通知（`notifications/initialized`）被回复 | 所有消息一视同仁地回复 | 通知没有 `id`，不回复 |

## Attribution defect

**症状**：`kb where mcp/server.ts` 返回了 `infohub/collector/mcp-tools`。

**原因**：构建时把 codeb 自己的 MCP 文档放进了 `infohub/` 命名空间，
而它的 `covers` 是 `mcp/`、`kb.py`——这些都是 codeb 自己的路径。

**处理**：建 `repo/codeb/` 并把页面移过去；在冒烟测试里加两条断言：
codeb 自身路径的命中必须全在 `codeb/` 下，infohub 路径的命中必须全在 `infohub/` 下。

**为什么值得单独记**：这不是代码 bug，是**归属判断错误**。
它不会让任何测试失败，只会让人在错误前提下继续判断——而且它是我自己造成的，
在写「让模型正确维护知识库」的工具时犯了「知识放错仓库」的错。

## A test error, not a tool error

有一次测试报告「漂移未被检测到」，看起来像工具漏检。实际是我写的替换 pattern
在源码里不存在（源码是 `if hit != invert:`，我写的是 `if invert:`），
文件根本没被改动，工具的行为完全正确。

**教训**：断言失败时，先确认**预期**是否成立，再判断实现是否有 bug。
否则会去「修」一个本来就正确的东西，而且改完之后测试通过，问题被永久掩盖。

## Environment traps (not code defects)

- **PowerShell 的 `-replace` + `Set-Content` 会按 GBK 读 UTF-8 文件**，
  写回时中文变乱码。我因此毁掉过一整页正文，只能重写。
  改文件内容一律走 Python 或专门的编辑工具。
- **`python -c "长字符串"` 在 PowerShell 里极易被截断**，报出看起来像语法错误、
  实际是命令被切断的错误。超过三行的逻辑一律写临时脚本文件。
- **控制台乱码不代表文件坏了**。判断文件是否损坏要直接读文件内容，不要看控制台。
- **并行写同一个库时，编码损坏会同时发生多次**。构建 infohub 那批页面时，
  有一个子代理把整页写成了「UTF-8 被当 GBK 解读」的二次损坏——文件本身是**合法 UTF-8**，
  BOM 与 CRLF 检查全部通过，只有人读正文才看得出。这类损坏**不可逆**（`gbk`/`gb18030`
  还原都失败），只能整页重写。
  检测办法：扫正文里是否成对出现 `杩/涓/鏄/鐨/鍏/鍒` 这类只在乱码里才高频的字。
  `_kbwork/encoding_check.py` 就是这么做的——**BOM/CRLF 检查不够，必须单独查内容**。
- **`Get-Content | Measure-Object -Line` 会静默少算行数**。同一个文件用
  `Get-Content | Measure-Object -Line`、`(Get-Content).Count`、`ReadAllLines().Count`
  得到三个不同的数（实测 450 / 523 / 564，真实 564）。
  统计行数一律用 Python 的 `len(text.splitlines())`。
  这也是「不把行数写进知识库」那条规则的直接起因，见 `infohub/numbers-policy`。

## Verified-correct boundaries

反向确认过的行为（这些「没有 bug」的结论同样需要留档，否则以后会被当成 bug 改掉）：

- `covers: src/` 不会误命中 `src2/a.py` 或 `mysrc/a.py`——前缀匹配按**路径段**判断。
- 正文为空时 `kb upsert` 拒绝写入（退出码 2），不会留下空文件。
- 标题没有 ASCII 字符时，文件名回退到标题哈希，**重跑同一命令不会多建一页**。
- `kb where` 完全未覆盖时返回空列表且退出码 0——「没写过」不是错误。

﻿## The tree nesting defect

**症状**：`kb tree` 输出里，`codeb/design/` 显示在 `infohub/` 那一块下面。
层级是错的，但错得很像对的——缩进、目录名、页面归属全都在，看不出问题。

**原因**：文本输出按「目录深度 + 目录名」排序后平铺打印，
缩进量用 `d.count("/")` 算。这忽略了**父子关系**：所有深度为 1 的子目录
被排在同一个序列里，于是 `codeb/design` 会紧挨着 `infohub` 出现，
读起来像是 infohub 的子目录。

**处理**：改成真正的递归树——先建 `父目录 → 子目录` 结构，再从每个仓库根递归打印。

**为什么值得记**：这是「输出看起来合理但结构是错的」的典型。
没有任何测试会失败，人眼扫一遍也容易滑过去，而它直接损害 `kb tree` 的导航价值——
而导航是这套设计里最贵的部分（每次会话都要读）。

﻿## A guard test that silently checked nothing

**症状**：为了防「tree 层级错位」复发，我加了一条断言解析 `kb tree` 的文本输出。
注入缺陷（删掉递归子目录）后，测试仍然 PASS。

**原因有两层，第二层更隐蔽**：

第一层：断言只检查「出现时父目录是否正确」，不检查「该出现的是否出现」。
所以把递归整段删掉、子目录全部消失时，循环体一次都没进，判定自然是通过。

第二层：修好第一层（增加存在性检查）后，测试**仍然通过**——因为解析正则
`^(\s*)(\S+)\/$` 在 Windows 下永远匹配不到：Python 文本输出是 CRLF，
行尾多一个 `\r`，而正则要求 `/` 后立即结束。
于是 `seenDirs` 始终为空，而「为空 → 没有不匹配项」又被判为通过。

**处理**：正则改为 `\s*$` 兜住行尾空白；并显式断言必须存在 `codeb/design` 与
`infohub/collector` 两个子目录。

**教训**：一个永远不进入循环的检查，和一个永远通过的检查，**在测试报告上无法区分**。
所以凡是「遍历解析输出」的断言，必须同时断言**遍历确实发生了**
（本例：必须找到至少 N 个预期条目）。

这与本项目反对「看起来成功」的整条主线是同一件事，只不过这次栽在测试自己身上。

### 中文标题退化成哈希文件名（实测 2026-11-18）

`kb upsert --repo codeb --topic design --title "知识收割的角色分工"` 产出
`repo/codeb/design/page-ca43d322aa.md`。

原因：`cmd_upsert` 先 `slugify(args.title)`，中文被剥成空串，再试 `slugify(args.section)`
（新建时通常没给）也是空串，最后落到 `fallback_slug()` → `page-<sha1前10位>`。

这与「文件名用英文 slug、页面内容用中文」的约定冲突：`--topic` 明确要求英文，
`--title` 却默认是中文，于是**按约定写中文标题必然得到不可读的文件名**。
`title` 字段本身在 frontmatter 里仍完好，所以只影响人浏览目录和 git diff，不影响 `tree` 的 hint。

处理：新建页时显式给一个英文 `--section` 不合适（语义是节名）。真正的修法要么让
`--name` 可显式指定文件名，要么让 `fallback_slug` 用 `topic` + 短哈希而非 `page-` 前缀。
现阶段先接受不可读文件名，靠 `title` 与 `tree` 的 hint 定位——**不要因为名字难看就重命名**，
`kb` 无索引，重命名安全但 `covers` 反查与外部引用会散。
