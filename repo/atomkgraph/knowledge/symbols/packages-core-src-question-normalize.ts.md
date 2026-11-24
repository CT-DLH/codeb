---
covers:
  - packages/core/src/question-normalize.ts
title: Semantic block index: question-normalize.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：question-normalize.ts（第4层）

**源码文件**：`packages/core/src/question-normalize.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="packages/core/src/question-normalize.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| normalizeQuestionType@79 | function | L79-87 | 题型归一。无法识别一律落到 short： | export function normalizeQuestionType(raw: unknown, fallback: Question… |
| optionLetterIndex@104 | function | L104-112 | 该行是否是选项行；是则返回其字母序号（A→0、B→1…），否则 -1。 | function optionLetterIndex(line: string): number { |
| stripOptionPrefix@115 | function | L115-117 | 剥掉行首标号，返回纯选项内容（无标号则原样返回，只是 trim）。 | export function stripOptionPrefix(line: string): string { |
| normalizeOptions@128 | function | L128-147 | 选项数组归一： | export function normalizeOptions(raw: unknown): string[] { |
| explodeOptionLines@159 | function | L159-183 | 把「一行里塞了多个选项」的题干先拆成多行。 | function explodeOptionLines(content: string): string { |
| splitInlineOptions@199 | function | L199-241 | 从题干中剥离内嵌选项（AI 最常犯的格式错误）。 | export function splitInlineOptions(content: string): { content: string… |
| normalizeQuestionFields@250 | function | L250-287 | 题目三个「互相影响」的字段整体归一：题型 / 题干 / 选项。 | export function normalizeQuestionFields( |
| sameList@290 | function | L290-292 | 逐项比较两个字符串数组（选项顺序即 A/B/C，顺序不能乱）。 | function sameList(a: string[], b: string[]): boolean { |
| normalizeAnalyses@304 | function | L304-321 | 归一化多解析数组（一题多解）。 | export function normalizeAnalyses(raw: unknown): QuestionAnalysis[] { |
| normalizeSubQuestions@340 | function | L340-395 | 归一化一题多问的各小问（R29）。 | export function normalizeSubQuestions(raw: unknown): SubQuestion[] { |
| questionFingerprint@414 | function | L414-423 | 整题指纹（R27）：题干 + 选项 + 答案 一起算 hash。 | export function questionFingerprint(input: { |
| questionSkeleton@446 | function | L446-467 |  | export function questionSkeleton(content: string): string { |
