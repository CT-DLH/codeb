---
covers:
  - packages/core/src/llm/json-repair.ts
title: Semantic block index: json-repair.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：json-repair.ts（第4层）

**源码文件**：`packages/core/src/llm/json-repair.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="packages/core/src/llm/json-repair.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| repairJsonText@12 | function | L12-22 | 机械修复：模型常见的坏法。 | export function repairJsonText(raw: string): string { |
| fixInvalidEscapes@47 | function | L47-94 |  | export function fixInvalidEscapes(s: string): string { |
| salvageJsonObjects@103 | function | L103-144 | 从被截断的 JSON 里救回完整的对象：按花括号平衡扫描， | export function salvageJsonObjects<T = Record<string, unknown>>(text: … |
