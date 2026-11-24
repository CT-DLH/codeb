---
covers:
  - scripts/test-commit.ts
title: Semantic block index: test-commit.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：test-commit.ts（第4层）

**源码文件**：`scripts/test-commit.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="scripts/test-commit.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| assert@18 | function | L18-22 |  | function assert(cond: unknown, msg: string): void { |
| eq@23 | function | L23-30 |  | function eq(msg: string, actual: unknown, expected: unknown): void { |
| mkQuestion@34 | function | L34-43 |  | function mkQuestion(content: string): ExtractedQuestion { |
| makeChat@46 | function | L46-67 | 假模型：按 system prompt 分派。查重返回「重复」，挂载返回整批都挂 K2。 | function makeChat(seen: { judge: number; link: number }): ChatFn { |
| edgeCount@69 | function | L69-71 |  | function edgeCount(db: DB, qid: string): number { |
| questionCount@72 | function | L72-74 |  | function questionCount(db: DB): number { |
| seed@76 | function | L76-86 |  | function seed(): { db: DB; algId: string; existingId: string } { |
| caseLinkMapping@95 | function | L95-125 |  | async function caseLinkMapping(): Promise<void> { |
| caseDryRun@127 | function | L127-147 |  | async function caseDryRun(): Promise<void> { |
| caseLinkFailure@149 | function | L149-168 |  | async function caseLinkFailure(): Promise<void> { |
| caseForce@170 | function | L170-189 |  | async function caseForce(): Promise<void> { |
| casePriorImports@191 | function | L191-205 |  | async function casePriorImports(): Promise<void> { |
| caseBackfill@207 | function | L207-268 |  | async function caseBackfill(): Promise<void> { |
| caseJudgeFailureVisible@270 | function | L270-297 |  | async function caseJudgeFailureVisible(): Promise<void> { |
| caseJudgeRetry@299 | function | L299-332 |  | async function caseJudgeRetry(): Promise<void> { |
| main@334 | function | L334-344 |  | async function main(): Promise<void> { |
