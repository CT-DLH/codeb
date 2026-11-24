---
covers:
  - packages/core/src/services/variant-service.ts
title: Semantic block index: variant-service.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：variant-service.ts（第4层）

**源码文件**：`packages/core/src/services/variant-service.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="packages/core/src/services/variant-service.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| VariantFamily@39 | interface | L39-54 | 一个题族：根题 + 它的变式。 | export interface VariantFamily { |
| BackfillResult@59 | interface | L59-72 | 反填结果。 | export interface BackfillResult { |
| parseVariantSource@106 | function | L106-124 | 从 source_detail 解析变式信息。解析不出返回 null。 | export function parseVariantSource(sourceDetail: string): { |
| backfillVariants@143 | function | L143-291 | 变式反填：把 source_detail 里写着「变式」的题关联到它们的原题。 | export function backfillVariants( |
| backfillVariants.run@219 | arrow | L219-277 |  | const run = (): void => { |
| listVariantFamilies@302 | function | L302-358 | 列出所有题族（根 + 变式）。 | export function listVariantFamilies( |
| viaOf@361 | function | L361-365 | 从 source_detail 推断这条变式关联是怎么来的（供 UI 显示来源徽标）。 | export function viaOf(sourceDetail: string): VariantVia { |
| firstLine@368 | function | L368-371 | 题干首行，截断（族列表里只用于识别）。 | function firstLine(content: string): string { |
| dedupeFamilies@396 | function | L396-434 | 出题时的族去重：同一族只保留一道。 | export function dedupeFamilies<T extends { question_id: string; varian… |
| dedupeFamilies.familyKey@409 | arrow | L409-409 | 「根在批次里 + 根不在批次里」两种情形走同一条逻辑。 但要注意：若根的 id 恰好等于另一道无关题的 id，会误并—— 实测不可能（id 唯一），所以不做额外防御。 | const familyKey = (q: T): string => (q.variant_of ? q.variant_of : q.q… |
