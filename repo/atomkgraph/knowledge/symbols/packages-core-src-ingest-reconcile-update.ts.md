---
covers:
  - packages/core/src/ingest/reconcile-update.ts
title: Semantic block index: reconcile-update.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：reconcile-update.ts（第4层）

**源码文件**：`packages/core/src/ingest/reconcile-update.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="packages/core/src/ingest/reconcile-update.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| vecTextForReconcile@36 | function | L36-38 | 向量文本：与 semantic-match 同构（标题权重最高，正文取开头），避免图注稀释相似度。 | function vecTextForReconcile(title: string, content: string): string { |
| ReconcileOptions@40 | interface | L40-49 |  | export interface ReconcileOptions { |
| ReconcileResult@51 | interface | L51-58 |  | export interface ReconcileResult { |
| buildPrompt@78 | function | L78-98 |  | function buildPrompt( |
| reconcileUpdates@108 | function | L108-230 | 对指定节点做增量正文比对。 | export async function reconcileUpdates( |
