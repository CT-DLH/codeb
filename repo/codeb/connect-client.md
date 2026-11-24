---
covers:
  - .mcp.json
updated: 2026-11-17
---

# Connecting a client to codeb

工具写好了不等于用得上——**中间还差一步：让客户端知道这个 server 存在**。
这一步没有代码可读，所以必须写下来。

## Registration

项目根有 `.mcp.json`：

```json
{
  "mcpServers": {
    "codeb": {
      "command": "node",
      "args": ["D:/work/project/codeb/mcp/server.ts"],
      "env": { "PYTHONIOENCODING": "utf-8" }
    }
  }
}
```

三个字段的含义：

- `command` + `args`：客户端用 `spawn` 起一个子进程，**通过 stdin/stdout 通信**。
  没有端口、没有常驻服务、没有健康检查。
- `env`：必须带 `PYTHONIOENCODING=utf-8`，否则内核输出的中文在 Windows 下会乱码，
  而乱码导致 JSON 解析失败后的表现是「工具返回了奇怪的东西」——很难联想到编码。
- 路径用正斜杠：Windows 的反斜杠在 JSON 里要转义成 `\\`，容易写错，正斜杠两边都认。

不同客户端的配置位置与键名不同（`mcpServers` / settings UI / 项目级 vs 用户级），
但**上面这个结构是通用的**。

## Verifying without the client

```bash
node mcp/inspect.ts      # 握手结果 + 六个工具的入参 + 一段可粘贴的 tools/call 原文
node mcp/smoke.ts        # 32 项真实协议断言
```

`inspect.ts` 存在的理由：注册失败的表现通常是**客户端里根本看不到这些工具**，
而那时没有任何报错可查。先脱离客户端验证 server 本身是通的，能把问题范围砍一半。

判断「是 server 的问题还是客户端配置的问题」，看这两个脚本的结果就够了：

- 两个都通过 → server 没问题，去查客户端配置。
- `smoke.ts` 通过但 `inspect.ts` 失败 → 几乎不可能，两者走同一协议。
- `smoke.ts` 失败 → server 有问题，先修这里。

## The actual call sequence

真实会话里不需要手写 JSON-RPC，模型直接调用工具。但**调用顺序**有讲究：

```text
1. kb_tree                          看清全库（约 140 tok）
2. kb_where <源码路径>               这次要改的东西归谁管？
3. 有命中 → kb_read <页> --section    确认现有内容
   无命中 → kb_read <最相关的页>       看邻近主题怎么写的
4. kb_upsert                        按上一步结果更新或新建
```

第 2 步是最容易跳过、也最不该跳过的。跳过它就会产出重复页，
而**重复页一旦出现，两页都不再权威**——读者不知道信哪个，之后也没人会去合并。

第 3 步里「无命中时先读最相关的页」同样重要：新页要和邻居保持同样的详细程度和术语。
否则同一库里会出现两种语气，读起来像两批人写的。

## One write per fact

一次 `kb_upsert` 只写一节，不要在一次调用里塞进三个不相干的主题。

理由是可回退性：`--section` 替换的粒度为节，一次写进三节时，
其中一节写错要重写，另外两节也会被一起覆盖。

## What the model should NOT do

- **不要绕开 `kb_upsert` 直接改 md 文件。** 会漏掉 `covers` 合并、`updated` 日期、
  CRLF/BOM 归一——这些正是手工编辑最容易破坏的东西。
- **不要把源码贴进知识库。** 代码会变，库里的副本不会跟着变，于是它从「知识」
  退化成「过期的副本」。要引用就写路径。
- **不要为「以后可能有用」而写。** 判据见 `codeb/design/where-knowledge-goes`。
  不确定就不写——没人读的页和没有页，维护成本完全不同。
- **不要在页里写「本文介绍……」这类开场。** `kb tree` 的提示行取的是正文首句，
  空话会把那一行浪费掉。

## 在 DSH 里注册（与 `.mcp.json` 不是同一处）

这是最容易卡住的一步：**`.mcp.json` 是给 Claude Desktop / Cursor 那类客户端看的，
DSH 不读它。** 在 DSH 里注册要改：

```text
~/.dsh/profiles/desktop/cordis.patch.yml
```

条目长这样（与 `mcp-infohub` / `mcp-viscode` 同构）：

```yaml
- id: mcp-codeb
  name: "@deepseek-ai/dsh-mcp-client"
  config:
    serverName: codeb            # 工具名变成 mcp__codeb__kb_where
    transport: stdio
    command: "C:\\Program Files\\nodejs\\node.exe"
    args:
      - "D:\\work\\project\\codeb\\mcp\\server.ts"
    cwd: "D:\\work\\project\\codeb"
    env:
      PYTHONIOENCODING: "utf-8"
    toolCallTimeoutMs: 900000
    failOnStartupError: true
```

四个字段值得单独说：

**`cwd` 要给全。** codeb 靠 `.codeb` 标记文件向上找根，理论上不依赖 cwd；
但显式给出更稳——cwd 不明确时，`kb.py` 可能静默解析到别的目录。

**`failOnStartupError: true` 必须开。** 设成 `false` 时连接失败会被完全吞掉
（配置层叫 `registrationFailure: "contain"`），界面上一点提示都没有，
表现就是「工具列表里没有这些工具」，而你无从知道是哪个环节断了。

**`toolCallTimeoutMs` 要放大。** 默认 60s 对读改整页 Markdown 不够：
一张几万 tok 的大页，`kb_upsert` 的读写往返可能超过一分钟。

**codeb 不需要 `tsx`。** 另外两个 server 用 `node_modules/tsx` 起 `.ts`，
而 codeb 是零依赖的：Node 24 原生类型剥离能直接跑 `server.ts`。
换机器时若启动失败，先查 `node --version`。

### 注册不等于立刻可用

改完 `cordis.patch.yml` 后，**当前会话的工具列表不会变**——MCP 连接在会话启动时建立，
要新开一个会话才会出现 `mcp__codeb__*`。

这一点值得先记住，否则会反复怀疑配置写错了。判断办法很简单：
直接脱离客户端验证 server 本身通不通

```bash
node mcp/inspect.ts
```

通了就说明 server 没问题，剩下的纯粹是「有没有重新建连接」。
