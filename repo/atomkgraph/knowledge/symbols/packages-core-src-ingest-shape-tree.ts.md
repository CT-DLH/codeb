---
covers:
  - packages/core/src/ingest/shape-tree.ts
title: Semantic block index: shape-tree.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：shape-tree.ts（第4层）

**源码文件**：`packages/core/src/ingest/shape-tree.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="packages/core/src/ingest/shape-tree.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| ShapeEntry@32 | interface | L32-41 |  | export interface ShapeEntry { |
| ShapePlan@43 | interface | L43-47 |  | export interface ShapePlan { |
| ShapeResult@49 | interface | L49-58 |  | export interface ShapeResult { |
| ShapeOptions@60 | interface | L60-66 |  | export interface ShapeOptions { |
| ShapeContext@68 | interface | L68-75 |  | export interface ShapeContext { |
| needsShape@85 | function | L85-88 | 这一节值不值得整形。 | export function needsShape(nodes: SplitNode[], opts: { groupMin?: numb… |
| countNodes@90 | function | L90-97 |  | function countNodes(nodes: SplitNode[]): number { |
| briefOf@100 | function | L100-110 | 一句话提要：模型靠它判断这层到底在讲什么，不需要读全文 | export function briefOf(content: string, max = 60): string { |
| flattenForPrompt@113 | function | L113-131 | 摊平成带编号的缩进清单。编号 = 稳定引用，模型只能回编号，不能自由起名再拿标题去匹配。 | export function flattenForPrompt(nodes: SplitNode[]): { text: string; … |
| flattenForPrompt.walk@117 | arrow | L117-128 |  | const walk = (list: SplitNode[], depth: number): void => { |
| sameAsSectionTitle@187 | function | L187-193 | 节点标题是不是「本节主题换个说法」。 | export function sameAsSectionTitle(title: string, sectionTitle?: strin… |
| sameAsSectionTitle.bare@189 | arrow | L189-189 |  | const bare = (t: string) => titleKey(t.replace(/[（(][^（()）]*[）)]/g, ''… |
| buildShapeUserPrompt@195 | function | L195-207 |  | export function buildShapeUserPrompt(ctx: ShapeContext, nodes: SplitNo… |
| parseShapePlan@210 | function | L210-224 | 解析整形结果。坏 JSON 一律抛错——静默返回空树等于把整节知识点丢掉。 | export function parseShapePlan(raw: string): ShapePlan { |
| applyShapePlan@239 | function | L239-451 | 把整形计划落到树上。 | export function applyShapePlan( |
| applyShapePlan.coverSubtree@256 | arrow | L256-260 |  | const coverSubtree = (n: SplitNode): void => { |
| applyShapePlan.take@262 | arrow | L262-282 |  | const take = (raw: unknown, mode: 'keep' \| 'fold'): SplitNode \| null… |
| applyShapePlan.build@284 | arrow | L284-337 |  | const build = (entries: ShapeEntry[] \| undefined, depth: number): Spl… |
| applyShapePlan.flattenChain@395 | arrow | L395-417 |  | const flattenChain = (nodes: SplitNode[]): SplitNode[] => |
| ShapeCallResult@453 | interface | L453-457 |  | export interface ShapeCallResult extends ShapeResult { |
| shapeSectionTree@465 | function | L465-514 | 整形一节的知识点。 | export async function shapeSectionTree( |
| shapeSectionTree.skip@470 | arrow | L470-478 |  | const skip = (warnings: string[], ms = 0): ShapeCallResult => ({ |
