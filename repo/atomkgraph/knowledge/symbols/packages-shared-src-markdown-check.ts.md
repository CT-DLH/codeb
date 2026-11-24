---
covers:
  - packages/shared/src/markdown-check.ts
title: Semantic block index: markdown-check.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：markdown-check.ts（第4层）

**源码文件**：`packages/shared/src/markdown-check.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="packages/shared/src/markdown-check.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| MarkdownIssue@26 | interface | L26-54 |  | export interface MarkdownIssue { |
| MarkdownCheckStats@56 | interface | L56-63 |  | export interface MarkdownCheckStats { |
| MarkdownCheckResult@65 | interface | L65-73 |  | export interface MarkdownCheckResult { |
| MarkdownField@76 | interface | L76-79 | 要检查的一个字段（题目有题干/选项/解析等多个 Markdown 字段）。 | export interface MarkdownField { |
| truncate@110 | arrow | L110-110 |  | const truncate = (s: string): string => (s.length > MAX_SOURCE ? s.sli… |
| checkFormula@120 | function | L120-139 | 用 katex 校验一条公式。 | function checkFormula(tex: string, displayMode: boolean): { error?: st… |
| blankInlineCode@142 | function | L142-144 | 行内代码替换成等长空白：既保留列位置，又不会被当成公式分隔符。 | function blankInlineCode(line: string): string { |
| isEscaped@147 | function | L147-151 | 该位置上的 $ 是否被奇数个反斜杠转义。 | function isEscaped(s: string, idx: number): boolean { |
| stripQuote@153 | function | L153-156 |  | function stripQuote(line: string): string { |
| ClosingInfo@158 | interface | L158-164 |  | interface ClosingInfo { |
| findClosing@169 | function | L169-182 | 从 from 行起找块级公式的闭符行（必须独占一行且与开符完全相同）。 | function findClosing(lines: string[], from: number, delim: string): Cl… |
| inTableBody@190 | function | L190-200 | 这一行是否真的处在 GFM 表格里（表头 + 对齐行之后的任意行）。 | function inTableBody(lines: string[], i: number): boolean { |
| emptyStats@202 | function | L202-204 |  | function emptyStats(): MarkdownCheckStats { |
| scan@212 | function | L212-447 | 扫描一段 Markdown，返回问题清单与统计（不含 field 归属）。 | function scan(text: string): { issues: MarkdownIssue[]; stats: Markdow… |
| scan.pushStrictWarnings@221 | arrow | L221-233 |  | const pushStrictWarnings = (warns: string[], line: number, src: string… |
| delimsBothSides@453 | function | L453-458 | $ 或 $$ 独占一行时，是否「上下都有边界」——即它真的能起一个块。 | function delimsBothSides(lines: string[], i: number, delim: string): b… |
| finalize@461 | function | L461-500 | 去重 + 排序 + 分类 + 截断。 | function finalize( |
| finalize.isError@475 | arrow | L475-479 |  | const isError = (k: MarkdownIssue['kind']): boolean => |
| finalize.cap@482 | arrow | L482-492 |  | const cap = (arr: MarkdownIssue[]): MarkdownIssue[] => { |
| lintMarkdown@503 | function | L503-507 | 单字段检查（返回值里的 issue 不带 field 归属）。 | export function lintMarkdown(text: string \| null \| undefined): Markd… |
| checkMarkdownFields@514 | function | L514-531 | 复合检查：一次检查多个 Markdown 字段（题目有题干/选项/解析等）。 | export function checkMarkdownFields(fields: MarkdownField[]): Markdown… |
| checkContentMarkdown@534 | function | L534-536 | 写路径用的便捷入口：检查单个正文字段（知识点正文）。 | export function checkContentMarkdown(content: string \| null \| undefi… |
