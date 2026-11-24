---
covers:
  - src/mcp/tools/file_read.ts
title: Semantic block index: file_read.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：file_read.ts（第4层）

**源码文件**：`src/mcp/tools/file_read.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="src/mcp/tools/file_read.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| fail@13 | function | L13-18 |  | function fail(errors: string[], extra: Record<string, unknown> = {}) { |
| isNumericText@22 | function | L22-24 |  | function isNumericText(text: string): boolean { |
| isDateText@26 | function | L26-28 |  | function isDateText(text: string): boolean { |
| profileColumns@31 | function | L31-78 | 每列给一个轻量画像：填了多少、两个样例、类型与风险——映射判断只需要这些 | function profileColumns(columns: string[], rows: Record<string, unknow… |
| clamp@80 | function | L80-83 |  | function clamp(value: number \| undefined, fallback: number, max: numb… |
| registerFileRead@85 | function | L85-208 |  | export function registerFileRead(server: McpServer): void { |
