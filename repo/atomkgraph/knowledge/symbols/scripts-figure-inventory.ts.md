---
covers:
  - scripts/figure-inventory.ts
title: Semantic block index: figure-inventory.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：figure-inventory.ts（第4层）

**源码文件**：`scripts/figure-inventory.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="scripts/figure-inventory.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| FigureEntry@18 | interface | L18-34 |  | export interface FigureEntry { |
| Inventory@36 | interface | L36-49 |  | export interface Inventory { |
| get@55 | function | L55-58 |  | function get(argv: string[], name: string): string \| undefined { |
| safeAssetPath@61 | function | L61-65 | URL 里只认文件名，防路径穿越（与 server 的 assets 路由同一口径）。 | function safeAssetPath(assetsDir: string, url: string): string { |
| buildInventory@67 | function | L67-182 |  | export function buildInventory(md: string, opts: { source?: string; as… |
| inventoryMarkdown@185 | function | L185-206 | Markdown 表：一页一张地让人工核对「图号 / 图注 / 文件 / 需复核」。 | export function inventoryMarkdown(inv: Inventory): string { |
