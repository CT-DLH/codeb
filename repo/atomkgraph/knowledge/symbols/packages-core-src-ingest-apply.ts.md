---
covers:
  - packages/core/src/ingest/apply.ts
title: Semantic block index: apply.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：apply.ts（第4层）

**源码文件**：`packages/core/src/ingest/apply.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="packages/core/src/ingest/apply.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| ApplyOptions@19 | interface | L19-45 |  | export interface ApplyOptions { |
| ApplyItemResult@47 | interface | L47-56 |  | export interface ApplyItemResult { |
| ApplyResult@58 | interface | L58-73 |  | export interface ApplyResult { |
| makeBatchId@83 | function | L83-87 | 批次号。传了 sourceHash 就把它编进前缀，让「同一份文件导过几次」可以直接用 | function makeBatchId(sourceHash?: string): string { |
| applyQuestions@89 | function | L89-268 |  | export function applyQuestions( |
| applyQuestions.nextOrder@115 | arrow | L115-118 |  | const nextOrder = (): number => { |
| applyQuestions.placeInPaper@127 | arrow | L127-136 | 匹配策略：按 q.paper_part（大题标题）找；找不到（模型没给 / 标题不在预建列表里） 就落到没有 part 的段位（paper_part_id=''），仍算挂在卷上—— 宁 | const placeInPaper = (q: ExtractedQuestion): { |
| applyQuestions.run@138 | arrow | L138-249 |  | const run = (): void => { |
