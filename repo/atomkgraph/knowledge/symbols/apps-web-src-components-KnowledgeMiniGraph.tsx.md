---
covers:
  - apps/web/src/components/KnowledgeMiniGraph.tsx
title: Semantic block index: KnowledgeMiniGraph.tsx (layer 4)
updated: 2026-11-24
---

# 语义块索引：KnowledgeMiniGraph.tsx（第4层）

**源码文件**：`apps/web/src/components/KnowledgeMiniGraph.tsx`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="apps/web/src/components/KnowledgeMiniGraph.tsx", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| fitTitle@42 | function | L42-47 | 按标题估宽，并在超长时截断加省略号。 | function fitTitle(title: string, maxChars = MAX_CHARS): { label: strin… |
| placeRow@69 | function | L69-80 | 把一行节点按实际宽度从左到右排布，返回每个节点的中心 x。 | function placeRow(row: Array<{ width: number }>, startX: number): { ce… |
| wrapIntoRows@88 | function | L88-106 | 把一列节点折成多行，并返回每行在「本行可用宽度」内的居中标尺。 | function wrapIntoRows<T extends { width: number }>(items: T[], maxWidt… |
| layout@127 | function | L127-214 | 计算所有节点的坐标。 | function layout( |
| layout.toPrep@132 | arrow | L132-135 |  | const toPrep = (item: NeighborhoodItem) => { |
| NodeBox@217 | function | L217-305 | 节点外观：层级不同、样式不同。 | function NodeBox({ |
| KnowledgeMiniGraph@307 | function | L307-588 |  | export function KnowledgeMiniGraph({ |
| KnowledgeMiniGraph.createChild@360 | arrow | L360-378 | 闭环设计：建完立刻跳转到新节点并进入编辑态——因为新建时通常只有个标题， 正文还没来得及写。跳过去直接编辑，省掉「建完再在树里找它」这一步。 故需要 onJump 与 onEdit 都 | const createChild = async (title: string) => { |
| KnowledgeMiniGraph.top@396 | arrow | L396-396 |  | const top = (n: RenderNode): number => n.row * rowH + PAD_Y |
| KnowledgeMiniGraph.bottom@397 | arrow | L397-397 |  | const bottom = (n: RenderNode): number => n.row * rowH + PAD_Y + BOX_H |
