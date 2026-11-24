---
covers:
  - scripts/test-figures.ts
title: Semantic block index: test-figures.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：test-figures.ts（第4层）

**源码文件**：`scripts/test-figures.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="scripts/test-figures.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| assert@23 | function | L23-27 |  | function assert(cond: unknown, msg: string): void { |
| eq@28 | function | L28-35 |  | function eq(msg: string, actual: unknown, expected: unknown): void { |
| mkQ@37 | function | L37-50 |  | function mkQ(no: string, stem: string, pageFrom = 1, pageTo = 1): Layo… |
| mkRegion@52 | function | L52-66 |  | function mkRegion(page: number, png: string, above = '', below = ''): … |
| tmpPng@68 | function | L68-72 |  | function tmpPng(dir: string, name: string, body: string): string { |
| caseAnchorNo@74 | function | L74-80 |  | function caseAnchorNo(): void { |
| caseByNo@82 | function | L82-105 |  | async function caseByNo(): Promise<void> { |
| caseByText@107 | function | L107-117 |  | async function caseByText(): Promise<void> { |
| caseSingleQuestionPage@119 | function | L119-128 |  | async function caseSingleQuestionPage(): Promise<void> { |
| caseMultiQuestionPage@130 | function | L130-153 |  | async function caseMultiQuestionPage(): Promise<void> { |
| caseMissingPng@155 | function | L155-164 |  | async function caseMissingPng(): Promise<void> { |
| caseContentAddressed@166 | function | L166-182 |  | async function caseContentAddressed(): Promise<void> { |
| caseCollectByQuestion@186 | function | L186-201 | ---- 7. 抽题后的「图有没有被模型丢掉」核对 ---- | function caseCollectByQuestion(): void { |
| caseRepairDropped@203 | function | L203-212 |  | function caseRepairDropped(): void { |
| caseRepairKept@214 | function | L214-225 |  | function caseRepairKept(): void { |
| caseRepairUnmapped@227 | function | L227-239 |  | function caseRepairUnmapped(): void { |
| caseRepairIdempotent@241 | function | L241-249 |  | function caseRepairIdempotent(): void { |
| caseDiagnostics@252 | function | L252-264 | 整页位图页产出 0 张图时，必须报出来（过去是完全静默的成功）。 | function caseDiagnostics(): void { |
| main@266 | function | L266-281 |  | async function main(): Promise<void> { |
