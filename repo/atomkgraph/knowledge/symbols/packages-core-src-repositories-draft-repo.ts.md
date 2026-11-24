---
covers:
  - packages/core/src/repositories/draft-repo.ts
title: Semantic block index: draft-repo.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：draft-repo.ts（第4层）

**源码文件**：`packages/core/src/repositories/draft-repo.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="packages/core/src/repositories/draft-repo.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| DraftRow@9 | interface | L9-19 |  | interface DraftRow { |
| parseResult@22 | function | L22-30 | 解析结果 JSON（容错：脏数据返回 null）。 | function parseResult(raw: string): DraftProcessResult \| null { |
| rowToDraft@32 | function | L32-44 |  | function rowToDraft(r: DraftRow): Draft { |
| CreateDraftInput@46 | interface | L46-50 |  | export interface CreateDraftInput { |
| DraftRepository@54 | class | L54-158 |  | export class DraftRepository { |
| DraftRepository.create@57 | method | L57-87 |  | create(input: CreateDraftInput): Draft { |
| DraftRepository.findById@89 | method | L89-92 |  | findById(id: string): Draft \| null { |
| DraftRepository.findAll@95 | method | L95-104 | 按状态列出（活动在前、最近更新优先）。status 省略时返回全部。 | findAll(status?: DraftStatus): Draft[] { |
| DraftRepository.countActive@107 | method | L107-110 | 活动草稿数量（前端角标用）。 | countActive(): number { |
| DraftRepository.update@112 | method | L112-130 |  | update(id: string, patch: UpdateDraftInput): Draft \| null { |
| DraftRepository.markProcessed@133 | method | L133-144 | 记录一次处理结果（不改动 content，仅记时间与结果摘要）。 | markProcessed(id: string, result: Omit<DraftProcessResult, 'processed_… |
| DraftRepository.setStatus@147 | method | L147-152 | 归档 / 转回活动。 | setStatus(id: string, status: DraftStatus): Draft \| null { |
| DraftRepository.delete@155 | method | L155-157 | 硬删除草稿（材料已入库或不再需要，无需软删）。 | delete(id: string): boolean { |
