---
covers:
  - packages/core/src/repositories/apply-batch-repo.ts
title: Semantic block index: apply-batch-repo.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：apply-batch-repo.ts（第4层）

**源码文件**：`packages/core/src/repositories/apply-batch-repo.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="packages/core/src/repositories/apply-batch-repo.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| BatchRow@11 | interface | L11-19 |  | interface BatchRow { |
| ItemRow@21 | interface | L21-28 |  | interface ItemRow { |
| parseJson@30 | function | L30-38 |  | function parseJson(raw: string): Record<string, unknown> { |
| asAction@47 | function | L47-53 | R52 起新增了三种体检修复动作（merge/rename/reparent）。 | function asAction(v: string): DraftNodeAction { |
| rowToBatch@55 | function | L55-72 |  | function rowToBatch(r: BatchRow): ApplyBatch { |
| rowToItem@74 | function | L74-83 |  | function rowToItem(r: ItemRow): ApplyBatchItem { |
| CreateBatchInput@85 | interface | L85-89 |  | export interface CreateBatchInput { |
| AddBatchItemInput@92 | interface | L92-97 | 一条动作记录：before 是动作前的整实体快照（create 传空对象）。 | export interface AddBatchItemInput { |
| ApplyBatchRepository@99 | class | L99-176 |  | export class ApplyBatchRepository { |
| ApplyBatchRepository.create@102 | method | L102-112 |  | create(input: CreateBatchInput = {}): ApplyBatch { |
| ApplyBatchRepository.findById@114 | method | L114-119 |  | findById(batchId: string): ApplyBatch \| null { |
| ApplyBatchRepository.findRecent@122 | method | L122-127 | 最近的批次（倒序）。 | findRecent(limit = 20): ApplyBatch[] { |
| ApplyBatchRepository.findLatestByDraft@130 | method | L130-135 | 某草稿最近一次的批次（重复 apply 前用它挡）。 | findLatestByDraft(draftId: string): ApplyBatch \| null { |
| ApplyBatchRepository.addItem@137 | method | L137-150 |  | addItem(batchId: string, item: AddBatchItemInput): number { |
| ApplyBatchRepository.addItems@152 | method | L152-157 |  | addItems(batchId: string, items: AddBatchItemInput[]): void { |
| ApplyBatchRepository.findItems@160 | method | L160-165 | 明细按 item_id 倒序：回滚必须逆着做的顺序来。 | findItems(batchId: string): ApplyBatchItem[] { |
| ApplyBatchRepository.setStats@167 | method | L167-171 |  | setStats(batchId: string, stats: Record<string, number>): void { |
| ApplyBatchRepository.markRolledBack@173 | method | L173-175 |  | markRolledBack(batchId: string, when = nowIso()): void { |
