---
covers:
  - packages/core/src/services/relink-service.ts
title: Semantic block index: relink-service.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：relink-service.ts（第4层）

**源码文件**：`packages/core/src/services/relink-service.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="packages/core/src/services/relink-service.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| RelinkTarget@37 | interface | L37-45 | 一道待重挂的题。 | export interface RelinkTarget { |
| RelinkOptions@47 | interface | L47-67 |  | export interface RelinkOptions { |
| RelinkItemResult@70 | interface | L70-81 | 单题的重挂结果。 | export interface RelinkItemResult { |
| RelinkResult@83 | interface | L83-102 |  | export interface RelinkResult { |
| findRelinkTargets@111 | function | L111-164 | 找出所有「没有活关联」的题。 | export function findRelinkTargets( |
| relinkQuestions@173 | function | L173-270 | 重挂一批题。 | export async function relinkQuestions(opts: RelinkOptions): Promise<Re… |
| pruneStaleLinks@283 | function | L283-345 | 清理失效关联（维护命令，默认干跑）。 | export function pruneStaleLinks( |
