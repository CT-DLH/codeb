---
covers:
  - mcp/server.ts
title: MCP server - component table (layer 3)
updated: 2026-11-22
---

# 模块：MCP 服务层（mcp/server.ts）——部件细页表（第3层）

**项目**：codeb
**源码文件**：`mcp/server.ts`（TypeScript，需 node+typescript 解析器）
**第4层语义块索引**：[mcp/server.ts](../symbols/mcp-server.ts.md)
**写范围**：`mcp/server.ts`（不得碰 `packages/**`、`apps/**`）
**验证命令**：`npx tsc -p mcp/tsconfig.json --noEmit`（或对应 tsconfig）

## 职责
codeb 的 MCP 薄壳服务层：把 `kb.py` 的命令（tree/read/search/where/pack/dispatch/agent…）以 MCP 工具形式暴露给外部宿主。逻辑全部在 `kb.py`，本层只做参数转发与结果封装。

## 适用场景
- 改 MCP 工具签名、增/删暴露的工具、修参数转发。
- 宿主侧调用 MCP 工具失败时，先确认本层路由与 kb.py 命令名一致。
- 确认某工具的参数说明与 kb.py 实际参数一致（避免宿主传错参数）。

## 功能部件

| 部件 key | 类型 | 行号 | 作用 |
|:--|:--|:--|:--|
| `runKb@38` | function | L38-58 | 调 kb.py 子进程 |
| `kbJson@61` | function | L61-72 | kb 输出 JSON 解析 |
| `text@81` | function | L81-84 | 文本结果封装 |
| `fail@86` | function | L86-88 | 错误结果封装 |
| `ToolDef@90` | interface | L90-95 | 工具定义类型 |
| `RpcRequest@371` | interface | L371-376 | MCP RPC 请求类型 |
| `send@378` | function | L378-380 | 发送消息 |
| `reply@382` | function | L382-384 | 回复请求 |
| `replyError@386` | function | L386-388 | 回复错误 |
| `handle@390` | function | L390-440 | MCP 请求分发处理 |
| `main@442` | function | L442-469 | 服务入口 |

## 测试文件
- 全量回归中的 MCP smoke 检查（`run_regression.ps1` 内含）。

## 下沉指引
```
选中部件 → 打开第4层 mcp-server.ts.md → read_block(path="mcp/server.ts", key="...")
```
