# Shared conventions

跨仓库复用的知识放这里。任何单个仓库的细节都不应该出现在这个目录——那些属于各自的仓库目录。

## Toolchain baseline

- Python 3.13，虚拟环境一律 `.venv/`，不进版本库。
- TypeScript 侧 Node 24 + pnpm，锁文件必须提交。
- 格式化：Python 用 `ruff format`，TS 用 `prettier`。每个仓库不各配一份规则，统一继承这里。

## Error handling and exit codes

- 库代码抛异常，不吞异常。只有进程边界（CLI 入口、HTTP handler）才 catch 并转成退出码。
- 退出码：`0` 正常、`1` 可预期的业务失败、`2` 用法错误、`3` 内部错误。
- 日志走 stderr，stdout 只留给机器可读输出（JSON、管道数据）。

## Commits and branches

- 提交信息用动词开头的一句话；正文解释"为什么"，不解释"改了什么"。
- 一个提交只做一件事。重构与功能改动分开，便于单独 revert。

## Environment gotchas

- Windows 的 PowerShell 默认不是 UTF-8。写文件、读文件都显式指定 `encoding="utf-8"`。
  控制台打印中文变成乱码**通常只是显示问题**，判断文件有没有坏要直接读文件内容，不要看控制台。
- PowerShell 里过长的命令行会被截断，导致命令语法错误。复杂的多步操作写成脚本文件再执行。
- 通过管道把中文喂给子进程时，编码会按本地代码页转换。稳妥做法是让子进程显式 reconfigure 成 UTF-8。
- **`Get-Content` + `-replace` + `Set-Content` 会摧毁中文文件**（实测踩过，代价是重写整页）：
  PowerShell 按本地代码页（GBK）读 UTF-8 文件，写回时内容已成乱码。
  改文件内容一律走 Python 或专门的编辑工具，**不要用 PowerShell 做文本替换**。
- **`Set-Content -Encoding UTF8` 在 Windows PowerShell 5.x 会写 BOM**。
  BOM 会让「文件第一行是不是 `---`」这类判断失效，frontmatter 解析直接错位。
  用 `write_bytes(text.encode("utf-8"))` 写，不用 `write_text` 的默认编码。
- **CRLF 会破坏按行切片的逻辑**。Windows 上手工编辑常留下 CRLF，
  而按行号切 markdown 小节时，CRLF 不会报错、只会静默切错位置。
  读文件后统一 `replace("\r\n", "\n")`，写文件时统一用 `\n`。
- **`python -c "...长字符串..."` 在 PowerShell 里极易被截断**，报出看起来像语法错误、
  实际是命令被切断的错误。超过三行的逻辑一律写临时脚本文件。

## Verifying a change actually took effect

- 写完文件后**回读一次**再报告成功。控制台输出不能作为证据：
  它可能乱码，也可能来自上一次运行的残留。
- 端到端测试要启动真实进程、走真实协议，**不要 mock 掉边界**。
  本次 MCP 构建中，三个真实缺陷（根路径算错、小节拼接破坏结构、位置参数被忽略）
  全都只在真实进程下才暴露，单元级 mock 一个都抓不到。
- 测试用例本身也可能写错。当断言失败时，先确认**预期**是否成立，
  再判断实现是否有 bug——否则会去「修」一个本来就是正确的东西。
