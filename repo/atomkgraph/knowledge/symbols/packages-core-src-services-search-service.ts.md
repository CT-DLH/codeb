---
covers:
  - packages/core/src/services/search-service.ts
title: Semantic block index: search-service.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：search-service.ts（第4层）

**源码文件**：`packages/core/src/services/search-service.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="packages/core/src/services/search-service.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| SearchHit@17 | interface | L17-23 |  | export interface SearchHit { |
| StaleNode@31 | interface | L31-35 | 一条「索引过期」的记录：未索引（从没建过）或已过期（建完之后正文改过）。 | export interface StaleNode { |
| StaleReport@37 | interface | L37-41 |  | export interface StaleReport { |
| SearchService@43 | class | L43-464 |  | export class SearchService { |
| SearchService.migrateMapTable@82 | method | L82-98 | 迁移旧版 vec_map 表结构。 | private migrateMapTable(): void { |
| SearchService.bootstrapState@107 | method | L107-121 | 一次性把已存在的 vec_map 认领为「新鲜」。 | private bootstrapState(): void { |
| SearchService.recordState@124 | method | L124-140 | 记下「这个知识点已按当前正文建好索引」。块数以 vec_map 为准（空正文 → 0）。 | private recordState(knowledgeId: string): void { |
| SearchService.rebuildState@143 | method | L143-154 | 全量重建后重写状态：所有存活知识点都算「刚索引过」，包括空正文的。 | private rebuildState(): void { |
| SearchService.staleReport@163 | method | L163-183 | 谁需要（重新）建索引。 | staleReport(): StaleReport { |
| SearchService.reindexStale@189 | method | L189-219 | 只补过期的：缺失的 + 正文改过的。不全量重算，所以几百个节点的库也只要几秒。 | async reindexStale(opts: { limit?: number } = {}): Promise<{ |
| SearchService.setEmbedder@226 | method | L226-229 | 运行时替换 embedding 后端（设置页切换 provider / 模型后调用）。 | setEmbedder(embed: EmbeddingFn, batchEmbed?: EmbeddingBatchFn): void { |
| SearchService.hasTable@236 | method | L236-241 | 表是否存在（向量表是懒创建的，用前必须先问一句）。 | private hasTable(name: string): boolean { |
| SearchService.getDim@243 | method | L243-248 |  | private getDim(): number \| null { |
| SearchService.setDim@250 | method | L250-256 |  | private setDim(d: number): void { |
| SearchService.ensureTable@258 | method | L258-275 |  | private ensureTable(dim: number): boolean { |
| SearchService.nextRowId@277 | method | L277-282 |  | private nextRowId(): number { |
| SearchService.clearKnowledge@285 | method | L285-298 | 删除某知识点的全部旧向量与映射。 | private clearKnowledge(knowledgeId: string): void { |
| SearchService.collectChunks@301 | method | L301-313 | 收集指定知识点（省略则全部）的分块列表。 | private collectChunks(ids?: string[]): Array<{ kid: string; text: stri… |
| SearchService.embedChunks@316 | method | L316-340 | 分批 embed 分块列表；有 batchEmbed 时一次请求多块，否则逐条兜底。 | private async embedChunks( |
| SearchService.writeVectors@343 | method | L343-358 | 把向量写入索引表（从 startRow 起分配 rowid，事务保证一致性）。 | private writeVectors(vectors: Array<{ kid: string; vec: number[] }>, s… |
| SearchService.indexKnowledge@361 | method | L361-363 | 为单个知识点建/更新向量索引（分块 → 多向量）。 | async indexKnowledge(knowledgeId: string): Promise<number> { |
| SearchService.indexMany@369 | method | L369-389 | 增量更新指定知识点的向量索引（写入后自动调用）。 | async indexMany(ids: string[]): Promise<number> { |
| SearchService.removeKnowledge@392 | method | L392-396 | 删除某知识点的向量索引（删除知识点后调用）。 | removeKnowledge(id: string): void { |
| SearchService.reindexAll@407 | method | L407-421 | 批量重建全部知识点的向量索引，返回总块数。 | async reindexAll(): Promise<number> { |
| SearchService.search@424 | method | L424-463 | 语义检索：chunk 级命中后按知识点去重（保留最近距离）。 | async search(query: string, limit = 10): Promise<SearchHit[]> { |
