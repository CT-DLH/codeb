---
covers:
  - mcp/server.ts
updated: 2026-11-17
---

# MCP over stdio: implementation notes

`server.ts` 约 300 行，手写 JSON-RPC。这一页只记**实现时踩到或容易踩到的协议细节**，
工具的语义在 `codeb/mcp-tools` 里。

## Framing: newline-delimited JSON

MCP over stdio 是**按行分隔的 JSON**，一行一个对象。

**不要加 `Content-Length` 头。** 那是更老的 LSP 分帧方式，两者不兼容：
加了之后客户端会一直等换行符，表现在外面就是「连接成功但没有任何响应」，
而日志里看不到任何错误——因为没有错误，只是在等。

实现要点：把 stdin 的 `data` 事件累积到缓冲区，按 `\n` 切分，剩余部分留到下次。

## Notifications must not be answered

没有 `id` 的消息是通知，**不能回复**。

`notifications/initialized` 是最常见的那个：客户端在 `initialize` 之后发它，
表示握手完成。如果回了一条响应，某些客户端会把它当成协议违规直接断开。

判断方式只有一个：**看有没有 `id`**。有则回，无则处理完就走。

## Three error levels, easy to confuse

| 情况 | 正确做法 | 错误做法的后果 |
| :-- | :-- | :-- |
| 未知方法 / 未知工具名 | JSON-RPC `error`（`-32602` / `-32601`） | 当成工具结果返回 `isError`，客户端以为工具执行了 |
| 工具执行失败（页面不存在等） | 正常 result，`isError: true` | 抛协议错误，客户端以为连接坏了 |
| JSON 解析失败 | `error` `-32700`，`id` 填 `null` | 静默丢弃，客户端永久等待 |

区分标准是**「错在协议层还是业务层」**：
工具名拼错是调用方不懂协议 → 协议错误；页面不存在是业务失败 → 业务结果。
混淆的后果是客户端无法区分「我的调用写错了」和「这次确实没查到」，
而这两者需要的后续动作完全不同。

## Idempotent reads, single writer

七个工具里只有 `kb_upsert` 会改磁盘。其余六个纯读。

这不是为了好看：**只读工具可以随便重试、随便并发**，
而一旦有两个写入口，就得开始考虑顺序、冲突和部分失败。
当前假设单会话维护，所以这个简化成立；多会话时会需要真正的锁。

## Why no SDK

官方 SDK 会带来一棵依赖树，而这个 server 的全部工作是调一个 Python 脚本。

手写的收益不只是「少几个包」，而是**消掉一整类问题**：
「哪个 SDK 版本改了分帧方式」「SDK 与客户端协议版本不匹配」
——这类问题的表现是「客户端连不上」，排查时很难想到是版本问题。

代价明确：将来要用 resources / prompts / sampling 得自己加。
这个代价被接受，因为这个 server 只需要 tools。

## Node 24 runs .ts directly

没有构建步骤、没有 `dist/`、没有 watch 进程。

代价写进 README：**降级到 Node 22 及以下就失效**。
这是一个明确的单版本赌注，换掉「构建产物与源码不同步」这一整类问题——
而后者在 MCP 场景下特别难查，因为客户端读的是构建产物，
改源码不重新构建时，表现为「改了没生效」。

## Kernel invocation: argv, never a shell string

用 `spawn("python", [KB_PY, ...args])`，**不拼 shell 字符串**。

原因：知识库路径里有中文、空格、反斜杠，页面路径里可能有引号。
拼字符串时每加一个参数就多一处转义错误，而转义错误的表现是
「内核收到了错误的参数并给出了合理的结果」——看起来像内核的 bug。

`PYTHONIOENCODING=utf-8` 必须显式设进子进程环境，否则 Windows 下中文输出会乱码。

## What the smoke test covers

`node mcp/smoke.ts` 启动真实 server、走真实 stdio 协议、断言 31 项。

**不 mock 边界。** 本项目构建期间发现的 MCP 层缺陷（根路径算错、未知工具错误分级、
通知被回复）全部只在真实进程下暴露，单元级 mock 一个都抓不到。

测试自己也有清理：跑完删掉临时页与临时正文文件，不留残留。
这一点很重要——残留会让**下一次**运行失败，而失败原因看起来像实现有 bug。
