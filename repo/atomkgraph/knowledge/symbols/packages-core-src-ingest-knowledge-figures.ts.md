---
covers:
  - packages/core/src/ingest/knowledge-figures.ts
title: Semantic block index: knowledge-figures.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：knowledge-figures.ts（第4层）

**源码文件**：`packages/core/src/ingest/knowledge-figures.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="packages/core/src/ingest/knowledge-figures.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| normalizeImageLinks@42 | function | L42-59 | 模型还会把示例写反：![/api/assets/](placeholder_image) —— 把路径放进 alt、 | export function normalizeImageLinks(content: string): string { |
| SectionFigure@65 | interface | L65-74 |  | export interface SectionFigure { |
| FigureRepairResult@76 | interface | L76-87 |  | export interface FigureRepairResult { |
| figureNo@92 | function | L92-95 |  | function figureNo(text: string): string { |
| keywords@98 | function | L98-109 | 从图注抽中文关键词：连续汉字串，去掉通用词与纯数字/字母。 | function keywords(caption: string): string[] { |
| collectSectionFigures@115 | function | L115-144 | 从一节原文里提取所有图片引用，并把紧邻上一行的 ⟦图N：…⟧ 图注并进来。 | export function collectSectionFigures(body: string): SectionFigure[] { |
| flatten@147 | function | L147-159 | 展平整棵节点树（含 children），区分叶子与容器。 | function flatten(nodes: SplitNode[]): { all: SplitNode[]; leaves: Spli… |
| flatten.walk@150 | arrow | L150-156 |  | const walk = (list: SplitNode[]): void => { |
| score@162 | function | L162-175 | 图对某个节点的归属打分：图号 10 分/次，标题关键词 3 分，正文 1 分。 | function score(fig: SectionFigure, node: SplitNode): number { |
| urlsInNodes@178 | function | L178-191 | 已补进任意节点正文的 URL（整节去重，避免同一张图挂到多个节点）。 | function urlsInNodes(nodes: SplitNode[]): Set<string> { |
| urlsInNodes.walk@180 | arrow | L180-188 |  | const walk = (list: SplitNode[]): void => { |
| repairKnowledgeFigures@199 | function | L199-256 | 抽取完成后，把原文里有、模型输出里没有的图补回节点正文。 | export function repairKnowledgeFigures(nodes: SplitNode[], body: strin… |
| repairKnowledgeFigures.cleanPlaceholders@205 | arrow | L205-221 | 先清掉模型照抄 prompt 示例写出的假引用（xxx.png），否则它会被当成「已有图」挡住真图补回。 | const cleanPlaceholders = (list: SplitNode[]): void => { |
