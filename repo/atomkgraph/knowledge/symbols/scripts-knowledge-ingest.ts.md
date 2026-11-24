---
covers:
  - scripts/knowledge-ingest.ts
title: Semantic block index: knowledge-ingest.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：knowledge-ingest.ts（第4层）

**源码文件**：`scripts/knowledge-ingest.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="scripts/knowledge-ingest.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| Args@22 | interface | L22-31 |  | interface Args { |
| parseArgs@33 | function | L33-54 |  | function parseArgs(argv: string[]): Args { |
| parseArgs.get@34 | arrow | L34-37 |  | const get = (name: string): string \| undefined => { |
| pickTargets@61 | function | L61-63 | --chapter 的判据在 outline.ts（chapterMatches）——那里有回归断言， | function pickTargets(flat: FlatSection[]): FlatSection[] { |
| fmtCounts@65 | function | L65-69 |  | function fmtCounts(c: Record<string, number>): string { |
| main@71 | function | L71-150 |  | async function main(): Promise<void> { |
