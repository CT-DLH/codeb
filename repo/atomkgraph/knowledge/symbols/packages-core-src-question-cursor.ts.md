---
covers:
  - packages/core/src/question-cursor.ts
title: Semantic block index: question-cursor.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：question-cursor.ts（第4层）

**源码文件**：`packages/core/src/question-cursor.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="packages/core/src/question-cursor.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| encodeCursor@13 | function | L13-15 | 编码成 URL 安全的 base64（无 + / =，可直接放 query string）。 | export function encodeCursor(row: QuestionCursor): string { |
| decodeCursor@23 | function | L23-38 | 解码游标。任何异常都返回 null（不抛）。 | export function decodeCursor(raw: string \| undefined \| null): Questi… |
