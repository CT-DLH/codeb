---
covers:
  - packages/core/src/quiz.ts
title: Semantic block index: quiz.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：quiz.ts（第4层）

**源码文件**：`packages/core/src/quiz.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="packages/core/src/quiz.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| GradeResult@20 | interface | L20-29 |  | export interface GradeResult { |
| normalizeJudge@35 | function | L35-40 | 规范化判断题答案。无法识别时返回原串小写。 | export function normalizeJudge(raw: string): string { |
| normalizeMultiple@43 | function | L43-54 | 拆分多选题答案为集合（按 , ，; ；\| 等分隔，排序去重）。 | export function normalizeMultiple(raw: string): string { |
| normalizeText@57 | function | L57-59 | 规范化单选/简答答案为去空白小写。 | export function normalizeText(raw: string): string { |
| normalizeAnswer@62 | function | L62-71 | 规范化某题型的答案。 | export function normalizeAnswer(type: QuestionType, raw: string): stri… |
| gradeAnswer@78 | function | L78-85 | 批改一题。 | export function gradeAnswer(type: QuestionType, expected: string, got:… |
| toSm2Grade@95 | function | L95-101 | 由批改结果映射为 SM-2 grade（0-5）。 | export function toSm2Grade(correct: boolean \| null, difficulty = DEFA… |
| SubGradeDetail@106 | interface | L106-121 | 单个小问的批改明细（前端逐问回显「对/错 + 得分」用）。 | export interface SubGradeDetail { |
| SubGradeResult@124 | interface | L124-132 | 一题多问的整卷批改结果（在 GradeResult 之上补逐问明细与得分）。 | export interface SubGradeResult extends GradeResult { |
| parseSubAnswers@146 | function | L146-170 | 解析结构化作答：期望 { "(1)": "-1", "(2)": "2x-2" }（前端与 API 的共同约定）。 | function parseSubAnswers(got: string): Record<string, string> \| null … |
| parseSubAnswers.toStr@155 | arrow | L155-156 |  | const toStr = (val: unknown): string => |
| gradeSubQuestions@183 | function | L183-240 | 批改「一题多问」（R41）：逐小问判分 → 按分值折算 → 算得分率。 | export function gradeSubQuestions( |
