---
covers:
  - packages/core/src/services/question-service.ts
title: Semantic block index: question-service.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：question-service.ts（第4层）

**源码文件**：`packages/core/src/services/question-service.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="packages/core/src/services/question-service.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| createLlmSummaryFn@28 | function | L28-44 | 基于 LLM 的默认概述器。 | export function createLlmSummaryFn(cfg?: LLMConfig): QuestionSummaryFn… |
| SummaryResult@46 | interface | L46-51 |  | export interface SummaryResult { |
| BatchSummaryResult@53 | interface | L53-62 |  | export interface BatchSummaryResult { |
| QuestionService@64 | class | L64-193 |  | export class QuestionService { |
| QuestionService.generateSummary@75 | method | L75-86 | 为单道题生成概述并落库；题目不存在返回 null。 | async generateSummary(questionId: string): Promise<SummaryResult \| nu… |
| QuestionService.generateSummaries@95 | method | L95-126 | 批量为题目生成概述。 | async generateSummaries( |
| QuestionService.findSimilar@145 | method | L145-192 | 查找与「待录入题目」相似的已有题目（题库查重，R12 精简版）。 | findSimilar(input: { |
| SimilarQuestion@196 | interface | L196-209 | findSimilar 的一条候选。 | export interface SimilarQuestion { |
| bigramSet@212 | function | L212-214 | 归一后的 bigram 集合（去重后用于 Dice 系数）。 | function bigramSet(text: string): Set<string> { |
