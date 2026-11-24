---
covers:
  - scripts/e2e-drag-sort.ts
title: Semantic block index: e2e-drag-sort.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：e2e-drag-sort.ts（第4层）

**源码文件**：`scripts/e2e-drag-sort.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="scripts/e2e-drag-sort.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| ok@7 | arrow | L7-10 |  | const ok = (cond: boolean, label: string) => { |
| j@12 | function | L12-19 |  | async function j<T>(path: string, init?: RequestInit): Promise<T> { |
| childTitles@22 | function | L22-36 | 取某父节点下的子节点，按后端返回的 sort_order 顺序。 | async function childTitles(parentId: string \| null): Promise<Array<{ … |
| childTitles.find@26 | arrow | L26-33 |  | const find = (nodes: any[]): any[] \| null => { |
| main@38 | function | L38-112 |  | async function main() { |
| main.findRaw@89 | arrow | L89-96 |  | const findRaw = (nodes: any[]): any[] \| null => { |
