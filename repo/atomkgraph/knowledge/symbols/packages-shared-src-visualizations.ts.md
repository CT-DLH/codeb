---
covers:
  - packages/shared/src/visualizations.ts
title: Semantic block index: visualizations.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：visualizations.ts（第4层）

**源码文件**：`packages/shared/src/visualizations.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="packages/shared/src/visualizations.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| KnowledgeVisual@20 | interface | L20-34 | 一条交互可视化。 | export interface KnowledgeVisual { |
| byteLength@49 | function | L49-56 | 用 TextEncoder 数字节（Node 与浏览器都有），而不是 str.length——后者数的是 UTF-16 码元。 | function byteLength(s: string): number { |
| normalizeVisualizations@71 | function | L71-125 | 把任意形状的「可视化」入参归一成规整数组。 | export function normalizeVisualizations(raw: unknown): KnowledgeVisual… |
