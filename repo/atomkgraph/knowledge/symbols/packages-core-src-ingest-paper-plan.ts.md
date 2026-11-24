---
covers:
  - packages/core/src/ingest/paper-plan.ts
title: Semantic block index: paper-plan.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：paper-plan.ts（第4层）

**源码文件**：`packages/core/src/ingest/paper-plan.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="packages/core/src/ingest/paper-plan.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| PaperPlanOptions@29 | interface | L29-53 |  | export interface PaperPlanOptions { |
| PaperContext@56 | interface | L56-62 | 落库时用的一份「卷上下文」：目标卷 + 各大题的目标 part_id。 | export interface PaperContext { |
| PaperPlanner@64 | class | L64-181 |  | export class PaperPlanner { |
| PaperPlanner.plan@81 | method | L81-155 | 建（或复用）卷，并按需建大题。 | plan(opts: PaperPlanOptions, partTitles: string[] = []): PaperContext … |
| PaperPlanner.makeOrderAllocator@169 | method | L169-175 | 按卷分配卷内序号（全局递增，不按 part 分段重置）。 | makeOrderAllocator(paperId: string): () => number { |
| PaperPlanner.count@178 | method | L178-180 | 卷内题数（供落库后汇报）。 | count(paperId: string): number { |
| makePaperOrder@190 | function | L190-192 | 把 paper_order 编成「大题序号 × 10000 + 大题内序号」的全局排序键。 | export function makePaperOrder(partSortOrder: number, indexInPart: num… |
