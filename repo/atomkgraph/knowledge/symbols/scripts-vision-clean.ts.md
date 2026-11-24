---
covers:
  - scripts/vision-clean.ts
title: Semantic block index: vision-clean.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：vision-clean.ts（第4层）

**源码文件**：`scripts/vision-clean.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="scripts/vision-clean.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| Args@21 | interface | L21-39 |  | interface Args { |
| get@41 | function | L41-44 |  | function get(argv: string[], name: string): string \| undefined { |
| parsePages@46 | function | L46-62 |  | function parsePages(spec?: string): number[] \| undefined { |
| parseArgs@64 | function | L64-90 |  | function parseArgs(argv: string[]): Args { |
| main@92 | function | L92-243 |  | async function main(): Promise<void> { |
| main.extractNativeTextLengths@123 | function | L123-152 | 取每页文本层的长度，供覆盖率校验做基准。 | async function extractNativeTextLengths( |
