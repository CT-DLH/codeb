---
covers:
  - packages/core/src/ingest/extract.ts
title: Semantic block index: extract.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：extract.ts（第4层）

**源码文件**：`packages/core/src/ingest/extract.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="packages/core/src/ingest/extract.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| ExtractedSubQuestion@19 | interface | L19-27 |  | export interface ExtractedSubQuestion { |
| ExtractedQuestion@29 | interface | L29-58 |  | export interface ExtractedQuestion { |
| ExtractIssue@60 | interface | L60-73 |  | export interface ExtractIssue { |
| ExtractResult@75 | interface | L75-89 |  | export interface ExtractResult { |
| ExtractOptions@103 | interface | L103-129 |  | export interface ExtractOptions { |
| normalizeDifficulty@134 | function | L134-138 | 难度收敛到 0-1；非数字回落 0.6（与难度系数的既有口径一致：越界收敛不抛错）。 | function normalizeDifficulty(v: unknown): number { |
| parseQuestions@140 | function | L140-158 |  | function parseQuestions(content: string, truncated: boolean): Array<Re… |
| normalizeExtracted@161 | function | L161-218 | 逐题归一：缺字段补默认、类型非法回落 short（安全终态）、答案来源以「有没有答案」为准。 | export function normalizeExtracted(raw: Record<string, unknown>, fallb… |
| isFaithfulContent@234 | function | L234-245 | 题干保真度：模型有没有把原文改写掉。 | export function isFaithfulContent(content: string, source: string): bo… |
| stemKey@259 | function | L259-266 | 题干归一化后的前缀键。用于比对「两块抽出来的到底是不是同一道题」。 | function stemKey(content: string, len = 24): string { |
| DedupeResult@268 | interface | L268-272 |  | interface DedupeResult { |
| dedupeAcrossBlocks@284 | function | L284-324 | 跨块去重。 | export function dedupeAcrossBlocks(questions: ExtractedQuestion[], iss… |
| extractQuestions@331 | function | L331-521 | 抽取题目。只产出预览，不落库——抽完直接入库会把编造的答案固化进 SM-2 复习队列。 | export async function extractQuestions( |
