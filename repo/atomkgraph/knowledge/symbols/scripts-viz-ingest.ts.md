---
covers:
  - scripts/viz-ingest.ts
title: Semantic block index: viz-ingest.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：viz-ingest.ts（第4层）

**源码文件**：`scripts/viz-ingest.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="scripts/viz-ingest.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| Args@21 | interface | L21-34 |  | interface Args { |
| parseArgs@36 | function | L36-57 |  | function parseArgs(argv: string[]): Args { |
| parseArgs.get@37 | arrow | L37-40 |  | const get = (name: string): string \| undefined => { |
| clip@60 | function | L60-63 | 一行里塞不下就截断——报告的价值在「一眼扫过哪些被跳过」，不在完整正文。 | function clip(s: string, n: number): string { |
| pickTargets@65 | function | L65-78 |  | function pickTargets(args: Args): Array<{ id: string; title: string }>… |
| main@80 | function | L80-148 |  | async function main(): Promise<void> { |
| main.count@134 | arrow | L134-134 |  | const count = (s: VisualizeResult['status']): number => results.filter… |
