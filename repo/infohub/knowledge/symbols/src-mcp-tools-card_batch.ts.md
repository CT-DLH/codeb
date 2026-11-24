---
covers:
  - src/mcp/tools/card_batch.ts
title: Semantic block index: card_batch.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：card_batch.ts（第4层）

**源码文件**：`src/mcp/tools/card_batch.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="src/mcp/tools/card_batch.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| BatchOp@45 | interface | L45-60 |  | interface BatchOp { |
| fail@62 | function | L62-67 |  | function fail(errors: string[], extra: Record<string, unknown> = {}) { |
| readText@69 | function | L69-71 |  | function readText(path: string): string { |
| parseOpsFile@73 | function | L73-96 |  | function parseOpsFile(path: string): BatchOp[] { |
| resolveRef@98 | function | L98-102 |  | function resolveRef(ref: string \| undefined, aliases: Map<string, str… |
| registerCardBatch@104 | function | L104-354 |  | export function registerCardBatch(server: McpServer): void { |
| registerCardBatch.finish@163 | arrow | L163-173 |  | const finish = (ok: boolean) => { |
