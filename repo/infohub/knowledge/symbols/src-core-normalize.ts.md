---
covers:
  - src/core/normalize.ts
title: Semantic block index: normalize.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：normalize.ts（第4层）

**源码文件**：`src/core/normalize.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="src/core/normalize.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| asText@7 | function | L7-9 | 录入通道的统一归一化规则。 | export function asText(value: unknown): string { |
| asList@11 | function | L11-13 |  | export function asList(value: unknown): string[] { |
| nonEmpty@15 | function | L15-17 |  | export function nonEmpty(value: unknown): boolean { |
| toHalfWidth@20 | function | L20-24 | 全角转半角（含全角空格），中文表格里最常见的噪声来源 | export function toHalfWidth(input: string): string { |
| stripParenthetical@27 | function | L27-29 | 剥离括号及其内容：「张三（已毕业）」与「张三」是同一个实体 | export function stripParenthetical(input: string): string { |
| normalizeText@32 | function | L32-36 | 标题/标识归一化：忽略空白与标点，只比较语义骨架 | export function normalizeText(value: unknown): string { |
| normalizeRef@39 | function | L39-41 | 来源标识归一化：保留 URL/ID 内部结构，只统一空白与大小写 | export function normalizeRef(value: unknown): string { |
| readPath@44 | function | L44-46 | 按 ext.a.b 这类路径取值 | export function readPath(obj: Record<string, any> \| undefined, path: … |
| writePath@49 | function | L49-59 | 按 ext.a.b 这类路径写值（中间节点自动建对象） | export function writePath(obj: Record<string, any>, path: string, valu… |
| slugify@62 | function | L62-69 | 文件名安全的 slug：保留中文与字母数字，其余折叠为连字符 | export function slugify(input: unknown, maxLength = 32): string { |
| isBlankValue@72 | function | L72-78 | 值是否「空」：null / "" / [] / {} 一律视为未填（与前端 isBlank 同口径） | export function isBlankValue(value: unknown): boolean { |
