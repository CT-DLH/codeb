---
covers:
  - apps/server/src/batch.ts
title: Semantic block index: batch.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：batch.ts（第4层）

**源码文件**：`apps/server/src/batch.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="apps/server/src/batch.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| BatchOp@50 | interface | L50-112 |  | export interface BatchOp { |
| BatchItemResult@114 | interface | L114-135 |  | export interface BatchItemResult { |
| questionPatchOf@152 | function | L152-186 | 从 op 上摘出题目字段。没出现的键不进对象，这样 question_update 保持 PATCH 语义。 | function questionPatchOf(op: BatchOp): Record<string, unknown> { |
| questionPatchOf.put@154 | arrow | L154-156 |  | const put = (key: string, value: unknown): void => { |
| resolveRef@189 | function | L189-205 | 把 { "$ref": name } / "$name" 解析成真实 id。 | function resolveRef(value: unknown, refs: Map<string, string>): unknow… |
| BatchHooks@208 | interface | L208-217 | 副作用钩子（向量索引/评论等，都是可重建的缓存，失败不影响主流程）。 | export interface BatchHooks { |
| BatchDeps@220 | interface | L220-228 | 批量执行器的依赖。 | export interface BatchDeps { |
| mdCheckOf@237 | function | L237-241 | R28：把 Markdown/LaTeX 渲染体检挂到逐项结果上。 | function mdCheckOf(md?: MarkdownCheckResult): { md_check?: MarkdownChe… |
| runBatchOps@244 | function | L244-446 | 执行批量操作。返回逐项结果（与输入同序）。 | export function runBatchOps( |
