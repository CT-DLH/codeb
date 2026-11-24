---
covers:
  - src/core/pdf.ts
title: Semantic block index: pdf.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：pdf.ts（第4层）

**源码文件**：`src/core/pdf.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="src/core/pdf.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| pdfText@11 | function | L11-21 |  | function pdfText(file: string, mode: PdfMode): string { |
| pdfPages@24 | function | L24-26 | 按页切分：pdftotext 用 \f 分页，每页的字符网格缩放可能不同 | export function pdfPages(file: string, mode: PdfMode = 'layout'): stri… |
| pdfLines@29 | function | L29-34 | 保留缩进的原始行：缩进就是列位置，去掉缩进表格就散了 | function pdfLines(file: string, mode: PdfMode = 'layout'): string[] { |
| pdfParagraphs@37 | function | L37-39 | 去掉首尾空白的紧凑行，供章节/标签类解析用 | export function pdfParagraphs(file: string): string[] { |
