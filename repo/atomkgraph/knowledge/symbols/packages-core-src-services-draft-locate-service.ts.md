---
covers:
  - packages/core/src/services/draft-locate-service.ts
title: Semantic block index: draft-locate-service.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：draft-locate-service.ts（第4层）

**源码文件**：`packages/core/src/services/draft-locate-service.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="packages/core/src/services/draft-locate-service.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| LocateHit@44 | interface | L44-49 | 检索命中的一条（和 SearchHit 同形，只留定位要用的字段）。 | export interface LocateHit { |
| LocateDeps@52 | interface | L52-65 | 定位依赖（都可注入，便于单测和降级）。 | export interface LocateDeps { |
| LocateResult@67 | interface | L67-73 |  | export interface LocateResult { |
| DraftApplyResult@76 | interface | L76-83 | 落库统计。 | export interface DraftApplyResult { |
| ConsistencyResult@86 | interface | L86-104 | 一致性检查（R51）的结果：默认只报告，apply 才动库。 | export interface ConsistencyResult { |
| splitByLength@125 | function | L125-155 | 按段落边界把长材料切块（不切断代码块/表格行）。 | export function splitByLength(text: string, size: number): string[] { |
| clip@200 | function | L200-203 |  | function clip(s: string, n: number): string { |
| asAction@205 | function | L205-208 |  | function asAction(v: unknown): DraftNodeAction \| null { |
| asPolicy@210 | function | L210-213 |  | function asPolicy(v: unknown): DraftContentPolicy { |
| DraftLocateService@215 | class | L215-853 |  | export class DraftLocateService { |
| DraftLocateService.extract@241 | method | L241-286 | 把草稿材料整理成候选节点，写进 draft_node（status=pending）。 | async extract( |
| DraftLocateService.locate@291 | method | L291-364 | 对草稿里还没定位的候选逐条定位（写入 draft_node，不碰 knowledge 表）。 | async locate(draftId: string, opts: LocateDeps = {}): Promise<LocateRe… |
| DraftLocateService.locate.worker@305 | arrow | L305-361 |  | const worker = async (): Promise<void> => { |
| DraftLocateService.fallbackSearch@367 | method | L367-379 | 没配 embedding 时的降级：按标题做字面包含（不求准，只求别把候选清单空着）。 | private fallbackSearch(query: string, limit: number): LocateHit[] { |
| DraftLocateService.childTitles@381 | method | L381-383 |  | private childTitles(id: string): Array<{ knowledge_id: string; title: … |
| DraftLocateService.judge@385 | method | L385-460 |  | private async judge( |
| DraftLocateService.apply@469 | method | L469-589 | 把已定位的候选写进知识库，一个批次一个 batch_id。 | apply( |
| DraftLocateService.consistency@600 | method | L600-771 | 建完新节点之后回头修旧节点里的指代（R51，对应人工流程的最后一步）。 | async consistency( |
| DraftLocateService.snapshot@773 | method | L773-783 |  | private snapshot(k: Knowledge): Record<string, unknown> { |
| DraftLocateService.rollback@796 | method | L796-852 | 整批撤销：按明细逆序执行。 | rollback(batchId: string, opts: { dryRun?: boolean } = {}): { |
| mergeContent@861 | function | L861-874 | 按策略合成新正文。 | export function mergeContent(oldC: string, newC: string, policy: Draft… |
