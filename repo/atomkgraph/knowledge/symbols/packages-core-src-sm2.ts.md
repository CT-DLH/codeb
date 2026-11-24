---
covers:
  - packages/core/src/sm2.ts
title: Semantic block index: sm2.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：sm2.ts（第4层）

**源码文件**：`packages/core/src/sm2.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="packages/core/src/sm2.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| SM2State@6 | interface | L6-11 |  | export interface SM2State { |
| sm2Update@21 | function | L21-50 | 一次复习后返回新的 SM-2 状态 | export function sm2Update( |
| deriveMastery@53 | function | L53-84 | 由 SM-2 状态派生掌握度（0-100），不存储（计划书 5.1） | export function deriveMastery( |
| isDue@87 | function | L87-92 | 是否到期需要复习 | export function isDue(state: SM2State, now: Date = new Date()): boolea… |
