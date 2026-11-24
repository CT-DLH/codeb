---
covers:
  - packages/core/src/ingest/solve-check.ts
title: Semantic block index: solve-check.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：solve-check.ts（第4层）

**源码文件**：`packages/core/src/ingest/solve-check.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="packages/core/src/ingest/solve-check.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| SolveInput@18 | interface | L18-27 |  | export interface SolveInput { |
| SolveVerdict@29 | interface | L29-43 |  | export interface SolveVerdict { |
| SolveCheckStats@45 | interface | L45-55 |  | export interface SolveCheckStats { |
| buildUserMessage@69 | function | L69-77 |  | function buildUserMessage(batch: SolveInput[]): string { |
| parseJson@79 | function | L79-91 |  | function parseJson(raw: string): Record<string, unknown> \| null { |
| lettersOf@94 | function | L94-97 | 答案里的字母集合：B、b、选 B、A、C、AC 都归一成 AC | function lettersOf(s: string): string { |
| judgeOf@100 | function | L100-105 | 判断题的两种写法：正确/错误 与 A/B（很多教材用 A 表示正确） | function judgeOf(s: string): string { |
| judgeAnswer@112 | function | L112-119 | 判分。返回 null 表示不该自动判（简答题 / 官方答案为空 / 模型没答）。 | export function judgeAnswer(type: string, modelAnswer: string, officia… |
| checkAnswers@126 | function | L126-200 | 批量解题并对照。不修改任何题目——只产出结论，由调用方决定怎么标记。 | export async function checkAnswers( |
