---
covers:
  - src/core/parsers/docx.ts
title: Semantic block index: docx.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：docx.ts（第4层）

**源码文件**：`src/core/parsers/docx.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="src/core/parsers/docx.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| DocxText@9 | interface | L9-16 |  | export interface DocxText { |
| unescapeXml@18 | arrow | L18-19 |  | const unescapeXml = (s: string): string => |
| collectText@22 | function | L22-41 | 一个 XML 片段（单元格或段落外部）内的全部 w:t，按 w:p 分组后拼回文本 | function collectText(fragment: string): string { |
| readDocxText@43 | function | L43-64 |  | export function readDocxText(file: string): DocxText { |
| stripSpace@67 | function | L67-69 | 去掉空白与常见标点，只留语义骨架——题目对账用 | export function stripSpace(value: string): string { |
