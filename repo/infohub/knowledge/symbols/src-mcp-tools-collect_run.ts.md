---
covers:
  - src/mcp/tools/collect_run.ts
title: Semantic block index: collect_run.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：collect_run.ts（第4层）

**源码文件**：`src/mcp/tools/collect_run.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="src/mcp/tools/collect_run.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| fail@20 | function | L20-25 |  | function fail(errors: string[], extra: Record<string, unknown> = {}): … |
| runLabel@28 | function | L28-32 | 登记表里的一条正在跑的任务，写成给人看的一行 | function runLabel(run: ActiveRun): string { |
| registerCollectRun@34 | function | L34-216 |  | export function registerCollectRun(server: McpServer): void { |
| registerCollectRun.quote@98 | arrow | L98-98 |  | const quote = (a: string) => (/[\s"]/.test(a) ? `"${a}"` : a); |
| registerCollectRun.tail@175 | arrow | L175-175 | 采集器的输出里可能带链接与标题，但不带 cookie；原样回传，只截尾避免把上下文灌爆 | const tail = (text: string, n = 4000): string => (text.length > n ? `…… |
