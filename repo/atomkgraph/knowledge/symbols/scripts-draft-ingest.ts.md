---
covers:
  - scripts/draft-ingest.ts
title: Semantic block index: draft-ingest.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：draft-ingest.ts（第4层）

**源码文件**：`scripts/draft-ingest.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="scripts/draft-ingest.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| flag@29 | function | L29-31 |  | function flag(name: string): boolean { |
| opt@32 | function | L32-35 |  | function opt(name: string): string \| undefined { |
| num@36 | function | L36-40 |  | function num(name: string, dflt: number): number { |
| need@41 | function | L41-48 |  | function need(name: string): string { |
| usage@49 | function | L49-67 |  | function usage(): never { |
| makeSearch@70 | function | L70-101 | 尽量接上语义检索；没配 embedding key 时降级为标题字面召回，并明确告知。 | function makeSearch(db: DB): { |
| main@106 | function | L106-367 | 索引新鲜度的判断统一在 SearchService.staleReport() 里：它比「数 vec_map 有没有行」更准， 能区分「从未索引」和「索引后正文改过」，也不会把空正文节点永久算作未 | async function main(): Promise<void> { |
