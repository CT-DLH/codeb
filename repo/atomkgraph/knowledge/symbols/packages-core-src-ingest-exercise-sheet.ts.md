---
covers:
  - packages/core/src/ingest/exercise-sheet.ts
title: Semantic block index: exercise-sheet.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：exercise-sheet.ts（第4层）

**源码文件**：`packages/core/src/ingest/exercise-sheet.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="packages/core/src/ingest/exercise-sheet.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| SheetItem@27 | interface | L27-32 |  | export interface SheetItem { |
| SheetGroup@34 | interface | L34-39 |  | export interface SheetGroup { |
| ParsedSheet@41 | interface | L41-49 |  | export interface ParsedSheet { |
| isRunningHeader@74 | function | L74-76 | 页眉判据：页码+书名，或 第N章 章名+页码。 | function isRunningHeader(line: string): boolean { |
| kindOfGroup@79 | function | L79-85 | 分组标题 → 题型。认不出就按 choice（有选项）还是 short 由调用方按内容再判。 | export function kindOfGroup(title: string): SheetQuestionKind { |
| parseSheet@93 | function | L93-176 | 切一段「习题精选」或「答案与解析」。 | export function parseSheet(text: string, opts: { maxSkip?: number } = … |
| parseSheet.closeItem@104 | arrow | L104-111 |  | const closeItem = (): void => { |
| parseSheet.closeGroup@112 | arrow | L112-116 |  | const closeGroup = (): void => { |
| pairKey@179 | function | L179-181 | 配对键：题型 + 题号。两侧分组标题常不一致（一、单项选择题 vs 单项选择题），用题型更稳。 | function pairKey(kind: SheetQuestionKind, no: string): string { |
| seqKey@184 | function | L184-186 | 顺序键：题型 + 该题型内的出现序（1 起）。题目与答案两侧按同一规则各自编号。 | function seqKey(kind: SheetQuestionKind, ordinal: number): string { |
| AnswerBinding@188 | interface | L188-200 |  | export interface AnswerBinding { |
| bindAnswers@214 | function | L214-271 | 把答案册对到习题上。 | export function bindAnswers(sheet: ParsedSheet, answers: ParsedSheet):… |
| bindAnswers.bump@220 | arrow | L220-225 |  | const bump = (kind: SheetQuestionKind): number => { |
| BuiltQuestion@279 | interface | L279-294 |  | export interface BuiltQuestion { |
| Marker@296 | interface | L296-300 |  | interface Marker { |
| collectMarkers@310 | function | L310-326 | 找选项标记（A. / B、 / C。 / D．）。 | function collectMarkers(text: string): Marker[] { |
| atLineOrWideGap@329 | function | L329-333 | 这个位置是不是「行首 / 宽间距之后」（判 、 。 分隔符用）。 | function atLineOrWideGap(text: string, index: number): boolean { |
| collectRuns@341 | function | L341-363 | 把标记切成若干段「A/B/C/D 递增序列」。 | function collectRuns(markers: Marker[]): Marker[][] { |
| collectRuns.flush@345 | arrow | L345-348 |  | const flush = (): void => { |
| splitOptions@370 | function | L370-389 | 拆题干与选项。 | export function splitOptions(text: string): { stem: string; options: s… |
| figureBlockStart@396 | function | L396-401 | 从 from 之后第一个「配图行」的位置（⟦图…⟧ / ![…](…) / <!-- fig:… -->）。 | function figureBlockStart(text: string, from: number): number { |
| splitChoiceAnswer@404 | function | L404-409 | 答案行的「字母部分」与「解析部分」。B\n计算机网络是… → letters=B, rest=解析。 | export function splitChoiceAnswer(raw: string): { letters: string; res… |
| splitBlankAnswers@430 | function | L430-439 | 多空题的答案：只取答案行原样保留（A、A、A、C 比 AAAC 更能看出第几空选什么）， | export function splitBlankAnswers(raw: string): { answer: string; rest… |
| BuildMeta@441 | interface | L441-444 |  | export interface BuildMeta { |
| stripAnswerLabel@447 | function | L447-449 | 剥掉答案册里的 【解答】/【解析】/【答案】 标签——那是对版面的标注，不是答案内容。 | function stripAnswerLabel(s: string): string { |
| typeOfKind@451 | function | L451-456 |  | function typeOfKind(kind: SheetQuestionKind): SheetQuestionType { |
| buildQuestions@464 | function | L464-553 | 习题 + 已配对答案 → 题目实体。 | export function buildQuestions(sheet: ParsedSheet, binding: AnswerBind… |
