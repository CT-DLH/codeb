---
covers:
  - packages/core/src/ingest/commit.ts
title: Semantic block index: commit.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：commit.ts（第4层）

**源码文件**：`packages/core/src/ingest/commit.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="packages/core/src/ingest/commit.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| CommitOptions@20 | interface | L20-52 |  | export interface CommitOptions { |
| CommitReport@54 | interface | L54-66 |  | export interface CommitReport { |
| fmtCounts@68 | function | L68-72 |  | function fmtCounts(c: Record<string, number>): string { |
| commitQuestions@74 | function | L74-271 |  | export async function commitQuestions(opts: CommitOptions): Promise<Co… |
| batchPrefix@279 | function | L279-281 | 批次号前缀：上层用它判断「这批导过没有」。 | export function batchPrefix(sourceHash: string): string { |
| priorImports@284 | function | L284-291 | 查这个来源在库里已有的批次（空数组 = 没导过）。 | export function priorImports(db: DB, sourceHash: string): Array<{ batc… |
