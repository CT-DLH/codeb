---
covers:
  - packages/graph-engine/src/layout.ts
title: Semantic block index: layout.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：layout.ts（第4层）

**源码文件**：`packages/graph-engine/src/layout.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="packages/graph-engine/src/layout.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| TreeLayout@24 | interface | L24-29 |  | export interface TreeLayout { |
| LayoutOptions@31 | interface | L31-44 |  | export interface LayoutOptions { |
| Rect@46 | interface | L46-51 |  | interface Rect { |
| squarify@63 | function | L63-129 | Squarified treemap：把 rect 按权重切成近方形的小块。 | function squarify( |
| squarify.Item@72 | interface | L72-75 |  | interface Item { |
| squarify.inset@79 | arrow | L79-85 |  | const inset = (r: Rect): Rect => { |
| squarify.rowWorst@87 | arrow | L87-96 |  | const rowWorst = (row: Item[], shortSide: number, area: number): numbe… |
| computeTreeLayout@136 | function | L136-295 | 计算树布局（确定性）。 | export function computeTreeLayout(nodes: GraphNode[], opts: LayoutOpti… |
| computeTreeLayout.sizeDfs@172 | arrow | L172-185 |  | const sizeDfs = (id: string, seen: Set<string>): number => { |
| computeTreeLayout.place@206 | arrow | L206-257 |  | const place = (id: string, rect: Rect, rootLevel = false): { sx: numbe… |
