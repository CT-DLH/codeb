---
covers:
  - packages/shared/src/field-ops.ts
title: Semantic block index: field-ops.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：field-ops.ts（第4层）

**源码文件**：`packages/shared/src/field-ops.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="packages/shared/src/field-ops.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| FieldOpError@22 | class | L22-30 | 字段级操作的错误。 | export class FieldOpError extends Error { |
| TextSearchReplace@33 | interface | L33-40 | 文本局部替换的规格。 | export interface TextSearchReplace { |
| applyTextAppend@43 | function | L43-47 | 追加一节内容：抹平尾部换行后，用恰好一个空行分隔。 | export function applyTextAppend(existing: string, addition: string): s… |
| applyTextSearchReplace@55 | function | L55-80 | 外科手术式替换：找不到 old 时报错而不是静默不动。 | export function applyTextSearchReplace( |
| ItemSearchReplace@83 | interface | L83-89 | search_replace 的规格：定位一条（按键），只改它某个文本字段里的一处。 | export interface ItemSearchReplace { |
| ItemRemove@92 | interface | L92-94 | remove 的规格：按键删掉一条。 | export interface ItemRemove { |
| ItemAdapter@105 | interface | L105-120 | 「按键定位的数组条目」这类字段的操作适配器。 | export interface ItemAdapter<T> { |
| keyOrThrow@122 | function | L122-138 |  | function keyOrThrow<T>(list: T[], id: string \| undefined, adapter: It… |
| applyItemSearchReplace@141 | function | L141-165 | 对某一条的文本字段做 search/replace；找不到键或 old 都报错（不静默）。 | export function applyItemSearchReplace<T>( |
| applyItemRemove@168 | function | L168-171 | 按键删掉一条；找不到键报错（不静默）。 | export function applyItemRemove<T>(list: T[], spec: ItemRemove, adapte… |
| ItemUpsertAdapter@174 | interface | L174-183 | upsert 用到的额外回调：怎么从入参取键、怎么并入已有条目 / 造一条新的。 | export interface ItemUpsertAdapter<T, U> { |
| applyItemUpsert@186 | function | L186-213 | 按键新增或替换一条，其余不动；到上限再追加会报错（而不是被静默丢弃）。 | export function applyItemUpsert<T, U>( |
