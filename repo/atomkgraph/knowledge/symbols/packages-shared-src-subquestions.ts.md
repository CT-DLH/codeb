---
covers:
  - packages/shared/src/subquestions.ts
title: Semantic block index: subquestions.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：subquestions.ts（第4层）

**源码文件**：`packages/shared/src/subquestions.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="packages/shared/src/subquestions.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| normalizeSubScore@33 | function | L33-40 | 归一小问分值：只接受正数（含正数字符串）。 | export function normalizeSubScore(raw: unknown): number \| undefined { |
| normalizeFullScore@52 | function | L52-59 | 归一母题满分（R41）。 | export function normalizeFullScore(raw: unknown): number { |
| subDisplayLabel@68 | function | L68-70 | 小问的显示标号：写了就用写的，没写按位置补 (1) (2)… | export function subDisplayLabel(sub: SubQuestion, index: number): stri… |
| subQuestionType@79 | function | L79-82 | 推断某个小问的题型。 | export function subQuestionType(sub: SubQuestion): QuestionType { |
| isGradableSub@93 | function | L93-96 | 这一小问能否自动判分。 | export function isGradableSub(sub: SubQuestion): boolean { |
| resolveSubScores@111 | function | L111-119 | 解出每个小问的最终分值（与 subs 一一对应）。 | export function resolveSubScores(subs: SubQuestion[], fullScore?: numb… |
| gradableTotalScore@122 | function | L122-125 | 可判分小问的总分（主观小问不计入）。 | export function gradableTotalScore(subs: SubQuestion[], fullScore?: nu… |
| totalSubScore@128 | function | L128-130 | 全部小问的总分（含主观小问，用于展示「本题满分」）。 | export function totalSubScore(subs: SubQuestion[], fullScore?: number)… |
