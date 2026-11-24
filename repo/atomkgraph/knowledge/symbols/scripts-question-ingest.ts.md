---
covers:
  - scripts/question-ingest.ts
title: Semantic block index: question-ingest.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：question-ingest.ts（第4层）

**源码文件**：`scripts/question-ingest.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="scripts/question-ingest.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| Args@29 | interface | L29-58 |  | interface Args { |
| parseArgs@60 | function | L60-102 |  | function parseArgs(argv: string[]): Args { |
| parseArgs.get@61 | arrow | L61-64 |  | const get = (name: string): string \| undefined => { |
| pickRoute@111 | function | L111-145 | 自动选路（R41）：先廉价地看一眼原始文本层，再决定用什么引擎解析。 | async function pickRoute(args: Args): Promise<RouteDecision> { |
| fmtCounts@147 | function | L147-151 |  | function fmtCounts(c: Record<string, number>): string { |
| main@153 | function | L153-320 |  | async function main(): Promise<void> { |
