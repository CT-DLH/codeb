---
covers:
  - src/mcp/lib/run-registry.ts
title: Semantic block index: run-registry.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：run-registry.ts（第4层）

**源码文件**：`src/mcp/lib/run-registry.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="src/mcp/lib/run-registry.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| ActiveRun@12 | interface | L12-22 | 长跑登记表的 TS 侧，契约与 collector/zhihu_pipe/runs.py 逐字一致： | export interface ActiveRun { |
| pidAlive@26 | function | L26-36 |  | export function pidAlive(pid: unknown): boolean { |
| runFile@39 | function | L39-42 | run_id 当文件名用（它来自命令行/请求体），消毒后不能越出 active/ | export function runFile(runId: string): string { |
| registerRun@44 | function | L44-47 |  | export function registerRun(entry: ActiveRun): void { |
| unregisterRun@49 | function | L49-55 |  | export function unregisterRun(runId: string): void { |
| readActiveRuns@57 | function | L57-87 |  | export function readActiveRuns(prune = true): ActiveRun[] { |
