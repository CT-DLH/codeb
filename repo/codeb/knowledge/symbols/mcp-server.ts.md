---
covers:
  - mcp/server.ts
title: Semantic block index: server.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：server.ts（第4层）

**源码文件**：`mcp/server.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="mcp/server.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| RunResult@28 | interface | L28-32 |  | interface RunResult { |
| runKb@38 | function | L38-58 | 调用 Python 内核。参数一律走 argv，不拼 shell 字符串—— | function runKb(args: string[]): Promise<RunResult> { |
| kbJson@61 | function | L61-72 | 取 JSON 结果；非 0 退出码时把 stderr 作为错误抛出。 | async function kbJson<T = any>(args: string[]): Promise<T> { |
| text@81 | function | L81-84 |  | function text(value: unknown): ToolResult { |
| fail@86 | function | L86-88 |  | function fail(message: string): ToolResult { |
| ToolDef@90 | interface | L90-95 |  | interface ToolDef { |
| RpcRequest@371 | interface | L371-376 |  | interface RpcRequest { |
| send@378 | function | L378-380 |  | function send(obj: unknown): void { |
| reply@382 | function | L382-384 |  | function reply(id: RpcRequest["id"], result: unknown): void { |
| replyError@386 | function | L386-388 |  | function replyError(id: RpcRequest["id"], code: number, message: strin… |
| handle@390 | function | L390-440 |  | async function handle(req: RpcRequest): Promise<void> { |
| main@442 | function | L442-469 |  | function main(): void { |
