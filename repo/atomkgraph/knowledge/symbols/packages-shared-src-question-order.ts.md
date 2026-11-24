---
covers:
  - packages/shared/src/question-order.ts
title: Semantic block index: question-order.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：question-order.ts（第4层）

**源码文件**：`packages/shared/src/question-order.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="packages/shared/src/question-order.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| questionTier@42 | function | L42-45 | 活关联数 → 层级。≤0 一律 unlinked（负数在数据里不存在，防御性处理）。 | export function questionTier(liveLinks: number): QuestionTier { |
| OrderableQuestion@48 | interface | L48-62 | compareQuestions 需要的最小字段集。Question 与 SQL 投影都能满足。 | export interface OrderableQuestion { |
| compareQuestions@90 | function | L90-111 | 排序比较器：基础题 → 综合题（按关联数升序）→ 未关联。 | export function compareQuestions(a: OrderableQuestion, b: OrderableQue… |
| tierOf@114 | function | L114-117 | 层级：优先用显式 tier，否则由 live_links 推。 | function tierOf(q: OrderableQuestion): QuestionTier { |
| linksOf@120 | function | L120-131 | 活关联数：优先用显式值，否则由 tier 给一个同序的代表值。 | function linksOf(q: OrderableQuestion): number { |
| isQuestionSort@150 | function | L150-152 |  | export function isQuestionSort(v: unknown): v is QuestionSort { |
| ownerSubquery@231 | function | L231-237 | 「归属节点」子查询的唯一生成器——正文只写一遍。 | function ownerSubquery(questionIdExpr: string): string { |
| knowledgeSubtreeCteSql@291 | function | L291-298 | 「从某个节点往下展开子树」的递归 CTE（别名默认 sub，单列 id）。 | export function knowledgeSubtreeCteSql(anchorSql: string, alias = 'sub… |
| OrderKey@340 | interface | L340-348 | 一个排序键：SQL 表达式 + 方向 + 游标字段名。 | export interface OrderKey { |
| questionOrderKeys@359 | function | L359-419 | 排序键列表（唯一真相源）。 | export function questionOrderKeys(sort: QuestionSort = 'priority'): Or… |
| questionOrderSql@427 | function | L427-431 | 排序模式 → SQL ORDER BY 片段。 | export function questionOrderSql(sort: QuestionSort = 'priority'): str… |
| toComparable@436 | function | L436-440 |  | function toComparable(v: unknown): string \| number { |
| questionCursorPredicate@460 | function | L460-498 | 生成 keyset 分页的 WHERE 谓词（字典序比较），返回 { sql, params }。 | export function questionCursorPredicate( |
| encodeQuestionCursor@501 | function | L501-503 | 把一行排序值编码成游标（前端原样回传，不做解释）。 | export function encodeQuestionCursor(row: QuestionCursor): string { |
| cursorFromRow@519 | function | L519-525 | 把一行排序值编码成游标（前端原样回传，不做解释）。 | export function cursorFromRow(sort: QuestionSort, row: QuestionCursor)… |
