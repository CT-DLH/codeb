---
covers:
  - packages/core/src/services/knowledge-service.ts
title: Semantic block index: knowledge-service.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：knowledge-service.ts（第4层）

**源码文件**：`packages/core/src/services/knowledge-service.ts`  
**解析器**：`regex-fallback`  
**第5层完整正文**：`read_block(path="packages/core/src/services/knowledge-service.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| MarkdownCheckResult@27 | fallback | L27-27 |  | type MarkdownCheckResult, |
| ItemAdapter@34 | fallback | L34-34 |  | type ItemAdapter, |
| CreateRelationInput@42 | fallback | L42-42 |  | type CreateRelationInput, |
| UpdateRelationInput@43 | fallback | L43-43 |  | type UpdateRelationInput, |
| suggestKnowledgeType@102 | fallback | L102-102 |  | export function suggestKnowledgeType(value: unknown): string { |
| knowledgeTypeHint@108 | fallback | L108-108 |  | export function knowledgeTypeHint(value: unknown): string { |
| normalizeKnowledgeType@117 | fallback | L117-117 |  | export function normalizeKnowledgeType(value: unknown): KnowledgeType … |
| KnowledgeValidationError@127 | fallback | L127-127 |  | export class KnowledgeValidationError extends Error { |
| TagMode@138 | fallback | L138-138 |  | export type TagMode = 'replace' \| 'add' \| 'remove' |
| ContentSearchReplace@141 | fallback | L141-141 |  | export interface ContentSearchReplace { |
| VisualizationSearchReplace@156 | fallback | L156-156 |  | export interface VisualizationSearchReplace { |
| VisualizationUpsert@176 | fallback | L176-176 |  | export interface VisualizationUpsert { |
| VisualizationRemove@190 | fallback | L190-190 |  | export interface VisualizationRemove { |
| UpdateKnowledgePatch@204 | fallback | L204-204 |  | export type UpdateKnowledgePatch = UpdateKnowledgeInput & { |
| dedupe@222 | fallback | L222-222 |  | function dedupe(list: string[]): string[] { |
| translateFieldOp@230 | fallback | L230-230 |  | function translateFieldOp<T>(fn: () => T): T { |
| applySearchReplace@240 | fallback | L240-240 |  | function applySearchReplace(content: string, spec: ContentSearchReplac… |
| applyVisualizationSearchReplace@273 | fallback | L273-273 |  | function applyVisualizationSearchReplace( |
| applyVisualizationUpsert@284 | fallback | L284-284 |  | function applyVisualizationUpsert( |
| applyVisualizationRemove@319 | fallback | L319-319 |  | function applyVisualizationRemove( |
| nextSortOrder@327 | fallback | L327-327 |  | function nextSortOrder(nodes: Knowledge[], parentId: string \| null): … |
| KnowledgeTreeNode@336 | fallback | L336-336 |  | export interface KnowledgeTreeNode { |
| KnowledgeOutlineNode@352 | fallback | L352-352 |  | export interface KnowledgeOutlineNode { |
| KnowledgeOutline@371 | fallback | L371-371 |  | export interface KnowledgeOutline { |
| KnowledgeOutlineOptions@385 | fallback | L385-385 |  | export interface KnowledgeOutlineOptions { |
| KnowledgeBrief@399 | fallback | L399-399 |  | export interface KnowledgeBrief { |
| KnowledgeFeedItem@414 | fallback | L414-414 |  | export interface KnowledgeFeedItem { |
| KnowledgeFeed@434 | fallback | L434-434 |  | export interface KnowledgeFeed { |
| NeighborhoodNode@448 | fallback | L448-448 |  | export interface NeighborhoodNode { |
| Neighborhood@468 | fallback | L468-468 |  | export interface Neighborhood { |
| NeighborhoodOptions@484 | fallback | L484-484 |  | export interface NeighborhoodOptions { |
| CreateKnowledgeWithLayoutInput@491 | fallback | L491-491 |  | export interface CreateKnowledgeWithLayoutInput { |
| ReadResult@533 | fallback | L533-533 |  | export interface ReadResult { |
| KnowledgeMoveError@546 | fallback | L546-546 |  | export class KnowledgeMoveError extends Error { |
| KnowledgeWriteError@565 | fallback | L565-565 |  | export class KnowledgeWriteError extends Error { |
| KnowledgeWithCheck@591 | fallback | L591-591 |  | export type KnowledgeWithCheck = Knowledge & { md_check?: MarkdownChec… |
| assertWriteLanded@606 | fallback | L606-606 |  | function assertWriteLanded( |
| MoveErrorCode@670 | fallback | L670-670 |  | export type MoveErrorCode = |
| MoveResult@680 | fallback | L680-680 |  | export interface MoveResult { |
| ReparentResult@691 | fallback | L691-691 |  | export interface ReparentResult { |
| MigrateRelationsResult@704 | fallback | L704-704 |  | export interface MigrateRelationsResult { |
| CreateRelationsResult@714 | fallback | L714-714 |  | export interface CreateRelationsResult { |
| UpdateRelationServiceResult@723 | fallback | L723-723 |  | export interface UpdateRelationServiceResult { |
| DeleteRelationResult@732 | fallback | L732-732 |  | export interface DeleteRelationResult { |
| RemoveResult@743 | fallback | L743-743 |  | export interface RemoveResult { |
| KnowledgeService@768 | fallback | L768-768 |  | export class KnowledgeService { |
| toExcerpt@1963 | fallback | L1963-1963 |  | export function toExcerpt(markdown: string, maxChars: number): string … |
