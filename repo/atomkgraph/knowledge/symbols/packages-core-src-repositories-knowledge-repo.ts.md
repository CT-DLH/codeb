---
covers:
  - packages/core/src/repositories/knowledge-repo.ts
title: Semantic block index: knowledge-repo.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：knowledge-repo.ts（第4层）

**源码文件**：`packages/core/src/repositories/knowledge-repo.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="packages/core/src/repositories/knowledge-repo.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| KnowledgeRow@16 | interface | L16-48 | 数据库行（snake_case，布尔为 0/1，数组为 JSON 文本）。 | interface KnowledgeRow { |
| parseVizColumn@57 | function | L57-65 | R53：解析 viz 列（对象数组）。 | function parseVizColumn(raw: unknown): KnowledgeVisual[] { |
| rowToKnowledge@67 | function | L67-101 |  | function rowToKnowledge(r: KnowledgeRow): Knowledge { |
| CreateKnowledgeInput@104 | interface | L104-135 | 创建知识点时的入参（仅需必填项，其余走默认）。 | export interface CreateKnowledgeInput { |
| KnowledgeRepository@147 | class | L147-406 |  | export class KnowledgeRepository { |
| KnowledgeRepository.create@151 | method | L151-208 | 新建知识点，返回完整实体。位置未指定时由调用方（layout）分配，此处默认 0。 | create(input: CreateKnowledgeInput): Knowledge { |
| KnowledgeRepository.findById@211 | method | L211-216 | 按 id 取未删除的知识点。 | findById(id: string): Knowledge \| null { |
| KnowledgeRepository.findChildren@219 | method | L219-230 | 列出直接子节点（未删除）。 | findChildren(parentId: string \| null): Knowledge[] { |
| KnowledgeRepository.findSameTitleSiblings@241 | method | L241-260 | R26：同父 + 同名的未删节点（建节点查重用）。 | findSameTitleSiblings( |
| KnowledgeRepository.findAll@263 | method | L263-268 | 列出全部未删除知识点（图谱与树视图用）。 | findAll(): Knowledge[] { |
| KnowledgeRepository.findOrphans@276 | method | L276-283 | 列出未归档的孤立知识点（R10「未归档岛」）：is_orphan = 1。 | findOrphans(): Knowledge[] { |
| KnowledgeRepository.update@286 | method | L286-328 | 更新字段；未提供的字段保持原值，edit_count 自动 +1。 | update(id: string, patch: UpdateKnowledgeInput): Knowledge \| null { |
| KnowledgeRepository.setSortOrder@336 | method | L336-341 | 只改 sort_order（轻量写）。 | setSortOrder(id: string, sortOrder: number): boolean { |
| KnowledgeRepository.markRead@347 | method | L347-355 | 标记一次阅读（R5）：read_count+1、刷新 last_read_at、累加停留秒数。 | markRead(id: string, at: string, durationSec = 0): boolean { |
| KnowledgeRepository.addReadDuration@358 | method | L358-367 | 只累加停留时长（不增加阅读次数，用于同一阅读会话内的续时报数）。 | addReadDuration(id: string, durationSec: number): boolean { |
| KnowledgeRepository.updateSM2@370 | method | L370-384 | 更新 SM-2 遗忘曲线参数（掌握度的事实源，由 ReviewService 调用）。 | updateSM2(id: string, state: { ease_factor: number; interval_days: num… |
| KnowledgeRepository.reparentChildren@390 | method | L390-397 | 把某父节点下的直接子节点改挂到新父节点（用于删除时子节点上提）。 | reparentChildren(fromParentId: string, toParentId: string \| null): nu… |
| KnowledgeRepository.softDelete@400 | method | L400-405 | 软删除：写 deleted_at，保留可追溯与防重复生成。 | softDelete(id: string): boolean { |
