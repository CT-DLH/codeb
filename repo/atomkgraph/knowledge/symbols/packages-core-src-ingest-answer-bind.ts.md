---
covers:
  - packages/core/src/ingest/answer-bind.ts
title: Semantic block index: answer-bind.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：answer-bind.ts（第4层）

**源码文件**：`packages/core/src/ingest/answer-bind.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="packages/core/src/ingest/answer-bind.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| BindQuestion@18 | interface | L18-23 |  | export interface BindQuestion { |
| BindItem@25 | interface | L25-29 |  | export interface BindItem { |
| BindResult@31 | interface | L31-38 |  | export interface BindResult { |
| buildUserPrompt@72 | function | L72-78 |  | function buildUserPrompt(questions: BindQuestion[], answerBook: string… |
| stripFence@80 | function | L80-83 |  | function stripFence(s: string): string { |
| RawBind@85 | interface | L85-88 |  | interface RawBind { |
| BindOptions@90 | interface | L90-103 |  | export interface BindOptions { |
| bindAnswersToQuestions@113 | function | L113-173 | 回填 + 校验。 | export async function bindAnswersToQuestions( |
| bindOneBatch@176 | function | L176-219 | 一批就一次调用。批内编号从 1 重新开始，见函数内注释。 | async function bindOneBatch( |
| normalizeBind@222 | function | L222-257 | 把模型的自由输出收敛成可落库的条目，所有不合规点记进 problems。 | export function normalizeBind(questions: BindQuestion[], raw: RawBind)… |
