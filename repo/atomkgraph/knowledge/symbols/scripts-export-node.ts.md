---
covers:
  - scripts/export-node.ts
title: Semantic block index: export-node.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：export-node.ts（第4层）

**源码文件**：`scripts/export-node.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="scripts/export-node.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| flagOn@24 | function | L24-28 |  | function flagOn(argv: string[], name: string): boolean \| undefined { |
| numOrNull@31 | function | L31-39 | 数字参数：none / all 视为「不限」，缺省返回 undefined。 | function numOrNull(argv: string[], name: string): number \| null \| un… |
| buildOptions@41 | function | L41-70 |  | function buildOptions(argv: string[]): PdfExportOptions { |
| buildOptions.pick@42 | arrow | L42-45 |  | const pick = (n: string): string \| undefined => { |
| main@72 | function | L72-159 |  | async function main(): Promise<void> { |
| main.pick@74 | arrow | L74-77 |  | const pick = (n: string): string \| undefined => { |
