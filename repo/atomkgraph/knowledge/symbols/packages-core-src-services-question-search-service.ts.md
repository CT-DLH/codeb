---
covers:
  - packages/core/src/services/question-search-service.ts
title: Semantic block index: question-search-service.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：question-search-service.ts（第4层）

**源码文件**：`packages/core/src/services/question-search-service.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="packages/core/src/services/question-search-service.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| QuestionHit@11 | interface | L11-16 | 语义搜题命中。 | export interface QuestionHit { |
| questionText@26 | function | L26-29 | 构造用于检索的题目文本：题干 + 选项（题目短，整题 embed）。 | function questionText(q: { content: string; options: string[] }): stri… |
| QuestionSearchService@31 | class | L31-258 |  | export class QuestionSearchService { |
| QuestionSearchService.setEmbedder@47 | method | L47-50 | 运行时替换 embedding 后端（设置页切换后调用，与 SearchService 保持一致）。 | setEmbedder(embed: EmbeddingFn, batchEmbed?: EmbeddingBatchFn): void { |
| QuestionSearchService.hasTable@57 | method | L57-62 | 表是否存在（向量表是懒创建的，用前必须先问一句）。 | private hasTable(name: string): boolean { |
| QuestionSearchService.getDim@64 | method | L64-69 |  | private getDim(): number \| null { |
| QuestionSearchService.setDim@71 | method | L71-77 |  | private setDim(d: number): void { |
| QuestionSearchService.ensureTable@79 | method | L79-94 |  | private ensureTable(dim: number): boolean { |
| QuestionSearchService.nextRowId@96 | method | L96-99 |  | private nextRowId(): number { |
| QuestionSearchService.clearQuestion@101 | method | L101-114 |  | private clearQuestion(questionId: string): void { |
| QuestionSearchService.collect@117 | method | L117-122 | 收集指定题目（省略则全部）的文本。 | private collect(ids?: string[]): Array<{ qid: string; text: string }> … |
| QuestionSearchService.embedItems@124 | method | L124-143 |  | private async embedItems(items: Array<{ qid: string; text: string }>):… |
| QuestionSearchService.writeVectors@145 | method | L145-158 |  | private writeVectors(vectors: Array<{ qid: string; vec: number[] }>, s… |
| QuestionSearchService.indexQuestion@161 | method | L161-163 | 为单题建/更新向量索引。 | async indexQuestion(questionId: string): Promise<number> { |
| QuestionSearchService.indexMany@166 | method | L166-179 | 增量更新指定题目的向量索引（写入后自动调用）。 | async indexMany(ids: string[]): Promise<number> { |
| QuestionSearchService.removeQuestion@182 | method | L182-185 | 删除题目向量索引（删除题目后调用）。 | removeQuestion(id: string): void { |
| QuestionSearchService.reindexAll@188 | method | L188-199 | 批量重建全部题目的向量索引。 | async reindexAll(): Promise<number> { |
| QuestionSearchService.search@202 | method | L202-222 | 语义搜题：返回最相近的题目（按 distance 升序）。 | async search(query: string, limit = 10): Promise<QuestionHit[]> { |
| QuestionSearchService.autoLinkKnowledge@229 | method | L229-257 | 自动关联：给定一个新知识点的 title+content，找出语义相近的已有题目， | async autoLinkKnowledge( |
