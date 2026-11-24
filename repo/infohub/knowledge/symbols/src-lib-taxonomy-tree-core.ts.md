---
covers:
  - src/lib/taxonomy/tree-core.ts
title: Semantic block index: tree-core.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：tree-core.ts（第4层）

**源码文件**：`src/lib/taxonomy/tree-core.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="src/lib/taxonomy/tree-core.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| TagId@24 | interface | L24-30 |  | export interface TagId { |
| TaxonomyNodeInput@36 | interface | L36-44 | YAML 里的一条节点。parent 用完整 ID，而不是相对名——跨 namespace 时相对名会撞。 | export interface TaxonomyNodeInput { |
| TaxonomyTreeNode@46 | interface | L46-48 |  | export interface TaxonomyTreeNode extends TaxonomyNodeInput { |
| TaxonomyTree@50 | interface | L50-55 |  | export interface TaxonomyTree { |
| TaxonomyIndex@61 | interface | L61-70 | 节点表预建的索引。祖先/后代判定必须依赖它——因为 ID 已经不含层级， | export interface TaxonomyIndex { |
| TaxonomyProblem@72 | interface | L72-84 |  | export interface TaxonomyProblem { |
| TaggedCard@87 | interface | L87-90 | 只要求有这两个字段，避免把整个卡片类型引进来（纯函数层不依赖 card-store） | export interface TaggedCard { |
| TagCount@92 | interface | L92-99 |  | export interface TagCount { |
| isNamespace@101 | function | L101-103 |  | function isNamespace(value: string): value is Namespace { |
| parseTagId@112 | function | L112-126 | 解析标签 ID。非法输入返回 null 而不是抛异常：标签来自手写 YAML 与旧卡片， | export function parseTagId(id: string): TagId \| null { |
| createIndex@133 | function | L133-153 | 扁平节点 → 索引。重复 ID 只保留第一条（重复项由 validateNodes 报出来）。 | export function createIndex(nodes: readonly TaxonomyNodeInput[]): Taxo… |
| coversWithIndex@156 | function | L156-160 | 选中项是否覆盖某个标签：等于它、或沿 parent 链是它的祖先。需要索引。 | function coversWithIndex(selected: TagId, tag: TagId, index: TaxonomyI… |
| isAncestor@168 | function | L168-183 | 严格祖先关系：从 tag 沿 parent 链上溯，途中遇到 ancestor 才算命中。 | export function isAncestor(ancestorId: string, tagId: string, index: T… |
| coversTag@186 | function | L186-191 | 选中项是否覆盖某个标签：等于它、或是它的祖先。需要索引。 | export function coversTag(selectedId: string, tagId: string, index: Ta… |
| matchesAny@199 | function | L199-214 | 卡片的任一标签命中任一选中项即算命中。 | export function matchesAny( |
| filterCards@225 | function | L225-258 | 按标签筛卡。 | export function filterCards<T extends TaggedCard>( |
| orderKey@260 | function | L260-266 |  | function orderKey(node: TaxonomyTreeNode): number { |
| sortSiblings@268 | function | L268-271 |  | function sortSiblings(nodes: TaxonomyTreeNode[]): void { |
| buildTree@281 | function | L281-344 | 扁平节点 → 树。 | export function buildTree(nodes: readonly TaxonomyNodeInput[]): Taxono… |
| validateNodes@353 | function | L353-470 | 校验节点表，返回问题清单而不是抛错。 | export function validateNodes(nodes: readonly TaxonomyNodeInput[]): Ta… |
| countByTag@480 | function | L480-528 | 每个节点自身 / 含后代的卡数。 | export function countByTag( |
