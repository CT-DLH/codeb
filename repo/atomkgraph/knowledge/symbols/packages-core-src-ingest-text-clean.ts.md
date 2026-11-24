---
covers:
  - packages/core/src/ingest/text-clean.ts
title: Semantic block index: text-clean.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：text-clean.ts（第4层）

**源码文件**：`packages/core/src/ingest/text-clean.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="packages/core/src/ingest/text-clean.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| isSentenceEnd@28 | function | L28-39 | 行尾算不算「话已说完」。 | function isSentenceEnd(line: string): boolean { |
| isHardWrap@60 | function | L60-63 | 两行之间是不是「排版换行」而非「真换行」。 | function isHardWrap(prev: string, next: string): boolean { |
| joinTwo@66 | function | L66-73 | 拼接两行：只有「英文/数字挨着英文/数字」才补空格，中文一律直接连 | function joinTwo(a: string, b: string): string { |
| joinHardWraps@81 | function | L81-102 | 合并硬换行。空行代表「真的分段」，但只在前一句已经说完时才保留—— | export function joinHardWraps(input: string): string { |
| dropCaptionBeforeImage@129 | function | L129-146 | 删掉题干末尾的图注残片。 | export function dropCaptionBeforeImage(input: string): string { |
| stripFigureTail@148 | function | L148-168 |  | export function stripFigureTail(input: string): string { |
| fixBrackets@176 | function | L176-181 | 括号配对归一：（) / ( ） 这类混用统一成全角。 | export function fixBrackets(input: string): string { |
| tidySpaces@184 | function | L184-190 | 零宽字符、不换行空格、行尾空白 | export function tidySpaces(input: string): string { |
| isRunningHeaderLine@227 | function | L227-229 |  | export function isRunningHeaderLine(line: string): boolean { |
| isPageNumberLine@232 | function | L232-234 | 独立成行的页码。它在正文里也可能是数据，故只在书眉行相邻位置删。 | export function isPageNumberLine(line: string): boolean { |
| stripPageChrome@236 | function | L236-261 |  | export function stripPageChrome(input: string): string { |
| stripMarkdownMarks@271 | function | L271-276 | 剥掉 Markdown 的强调与标题标记。 | export function stripMarkdownMarks(input: string): string { |
| normalizeStem@284 | function | L284-287 | 题干：去尾部图注 → 合并硬换行 → 括号/空白归一。 | export function normalizeStem(input: string): string { |
| normalizeProse@290 | function | L290-292 | 解析/解答：只做换行与空白归一，不删任何行（解析里没有图注） | export function normalizeProse(input: string): string { |
| normalizeOption@295 | function | L295-297 | 单个选项：已经是一行了，只收拾空白与括号 | export function normalizeOption(input: string): string { |
