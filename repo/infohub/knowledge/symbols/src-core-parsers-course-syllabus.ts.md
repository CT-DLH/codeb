---
covers:
  - src/core/parsers/course-syllabus.ts
title: Semantic block index: course-syllabus.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：course-syllabus.ts（第4层）

**源码文件**：`src/core/parsers/course-syllabus.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="src/core/parsers/course-syllabus.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| escapeRe@32 | arrow | L32-32 |  | const escapeRe = (s: string) => s.replace(/[.*+?^${}()\|[\]\\]/g, '\\$… |
| clean@49 | arrow | L49-53 |  | const clean = (value: string): string => |
| squeezeNumber@55 | function | L55-58 |  | function squeezeNumber(value: string): string { |
| readLabels@61 | function | L61-84 | 一行里可能挤着多个标签（课程学时：32 讲课学时：24 实验学时：8） | function readLabels(line: string, into: Record<string, string>): boole… |
| tableToMarkdown@87 | function | L87-95 | 表格转 markdown：教学内容表是正文里最有用的部分，不能丢 | function tableToMarkdown(rows: string[][]): string { |
| tableToMarkdown.fmt@91 | arrow | L91-92 |  | const fmt = (row: string[]) => |
| tableSectionName@97 | function | L97-102 |  | function tableSectionName(header: string[]): string { |
| titleFromParagraph@105 | function | L105-115 | 标题兜底：《X》课程教学大纲 / X课程中英文简介 | function titleFromParagraph(paragraph: string): string { |
| buildSections@117 | function | L117-177 |  | function buildSections(paragraphs: string[], tables: string[][][]): { … |
| buildSections.push@120 | arrow | L120-125 |  | const push = (name: string, content: string) => { |
| parseCourseText@179 | function | L179-223 |  | export function parseCourseText( |
| codeFromFileName@226 | function | L226-229 | 文件名里的课程代码与书名号标题（正文没写代码时兜底） | export function codeFromFileName(file: string): string { |
| titleFromFileName@231 | function | L231-236 |  | export function titleFromFileName(file: string): string { |
| parse@241 | method | L241-248 |  | parse(file, sourceFile): ParsedAttachment \| null { |
