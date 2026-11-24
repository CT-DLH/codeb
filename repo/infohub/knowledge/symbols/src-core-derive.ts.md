---
covers:
  - src/core/derive.ts
title: Semantic block index: derive.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：derive.ts（第4层）

**源码文件**：`src/core/derive.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="src/core/derive.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| DeriveSkipped@17 | interface | L17-21 |  | export interface DeriveSkipped { |
| DeriveOutcome@23 | interface | L23-28 |  | export interface DeriveOutcome { |
| deriveRules@31 | function | L31-44 | 递归收集领域包里声明了 derive 的字段（含 object 子字段与数组 item） | export function deriveRules(spec: DomainSpec): Array<{ path: string; r… |
| deriveRules.walk@33 | arrow | L33-40 |  | const walk = (fields: Record<string, FieldSpec>, prefix: string): void… |
| sourceText@46 | function | L46-54 |  | function sourceText(card: Record<string, any>, from: string): string { |
| captured@57 | function | L57-62 | 命中的片段：命名组 value → 第 1 组 → 整段匹配 | function captured(match: RegExpMatchArray): string { |
| extract@64 | function | L64-75 |  | function extract(rule: DeriveRule, text: string): { value?: string; re… |
| DeriveOptions@77 | interface | L77-84 |  | export interface DeriveOptions { |
| applyDerives@90 | function | L90-136 | 就地填充派生字段。 | export function applyDerives( |
