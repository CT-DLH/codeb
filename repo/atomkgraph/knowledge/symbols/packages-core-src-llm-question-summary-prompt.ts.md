---
covers:
  - packages/core/src/llm/question-summary-prompt.ts
title: Semantic block index: question-summary-prompt.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：question-summary-prompt.ts（第4层）

**源码文件**：`packages/core/src/llm/question-summary-prompt.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="packages/core/src/llm/question-summary-prompt.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| QuestionSummaryContext@23 | interface | L23-31 |  | export interface QuestionSummaryContext { |
| summaryContextOf@34 | function | L34-49 | 由实体构造概述上下文（自动拼装一题多解的多条解析）。 | export function summaryContextOf(q: Question): QuestionSummaryContext … |
| buildQuestionSummaryPrompt@51 | function | L51-63 |  | export function buildQuestionSummaryPrompt(ctx: QuestionSummaryContext… |
| cleanSummary@72 | function | L72-81 | 清洗模型返回的概述： | export function cleanSummary(raw: string): string { |
