---
covers:
  - packages/core/src/services/question-query-service.ts
title: Semantic block index: question-query-service.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：question-query-service.ts（第4层）

**源码文件**：`packages/core/src/services/question-query-service.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="packages/core/src/services/question-query-service.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| QuestionScope@52 | interface | L52-60 |  | export interface QuestionScope { |
| QuestionQuery@72 | interface | L72-106 |  | export interface QuestionQuery { |
| QuestionViewRow@109 | interface | L109-128 | 一行查询结果：题目本体 + 派生字段。 | export interface QuestionViewRow extends Question { |
| FacetItem@131 | interface | L131-135 | Facet 计数项。 | export interface FacetItem { |
| QuestionFacets@137 | interface | L137-144 |  | export interface QuestionFacets { |
| QuestionQueryResult@146 | interface | L146-161 |  | export interface QuestionQueryResult { |
| withPrefix@175 | function | L175-178 | 拼一段 WITH 前缀（没有 CTE 时返回空串）。 | function withPrefix(ctes: Array<string \| null \| undefined>): string … |
| DomainRow@181 | interface | L181-185 | 顶级根视为「领域」。is_orphan 的暂存节点不算领域。 | interface DomainRow { |
| QuestionQueryService@187 | class | L187-1059 |  | export class QuestionQueryService { |
| QuestionQueryService.loadDomains@200 | method | L200-216 | 知识点 → 顶级根（一次算完，整个查询复用）。 | private loadDomains(): { byNode: Map<string, DomainRow>; roots: Domain… |
| QuestionQueryService.subtreeQuestionCounts@231 | method | L231-252 | 「节点 → 其子树内的去重活题数」——一次算完全表。 | private subtreeQuestionCounts(): Map<string, number> { |
| QuestionQueryService.scopeCondition@268 | method | L268-324 | 把范围编译成「一段顶层 CTE + 一个作用于 q 的条件」。 | private scopeCondition( |
| QuestionQueryService.scopeCondition.inMaterializedSubtree@275 | arrow | L275-282 |  | const inMaterializedSubtree = (cte: string, params: unknown[]) => ({ |
| QuestionQueryService.filterConditions@327 | method | L327-415 | 把普通过滤条件编译成 SQL 片段列表。 | private filterConditions(q: QuestionQuery): { sql: string[]; params: u… |
| QuestionQueryService.query@423 | method | L423-599 | 主查询。 | query(q: QuestionQuery = {}): QuestionQueryResult { |
| QuestionQueryService.groupsByKnowledge@613 | method | L613-716 | 按知识点分组（「题库 → 按知识点」Tab 的数据源）。 | groupsByKnowledge(q: QuestionQuery = {}): { |
| QuestionQueryService.groupsByKnowledge.infoOf@667 | arrow | L667-677 |  | const infoOf = (id: string): { title: string; path: string } => { |
| QuestionQueryService.groupsByPaper@726 | method | L726-848 | 按卷分组（「题库 → 按卷」Tab 的数据源）。 | groupsByPaper(q: QuestionQuery = {}): { |
| QuestionQueryService.groupsByPaper.Agg@775 | interface | L775-787 |  | interface Agg { |
| QuestionQueryService.toViewRow@851 | method | L851-895 | SQL 行 → 视图行（派生字段在此收口）。 | private toViewRow( |
| QuestionQueryService.repoRowToQuestion@904 | method | L904-953 | SELECT q.* 的行 → Question。 | private repoRowToQuestion(r: Record<string, unknown>): Question { |
| QuestionQueryService.repoRowToQuestion.parseArr@905 | arrow | L905-912 |  | const parseArr = (v: unknown): string[] => { |
| QuestionQueryService.repoRowToQuestion.parseJson@913 | arrow | L913-920 |  | const parseJson = <T,>(v: unknown, fallback: T): T => { |
| QuestionQueryService.facets@962 | method | L962-1058 | Facet 计数。 | facets(q: QuestionQuery = {}): QuestionFacets { |
| QuestionQueryService.facets.countBy@968 | arrow | L968-999 |  | const countBy = ( |
