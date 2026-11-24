---
covers:
  - packages/core/src/services/draft-service.ts
title: Semantic block index: draft-service.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：draft-service.ts（第4层）

**源码文件**：`packages/core/src/services/draft-service.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="packages/core/src/services/draft-service.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| DraftProcessOptions@19 | interface | L19-26 |  | export interface DraftProcessOptions { |
| DraftPublishInput@29 | interface | L29-38 | 发布草稿为知识点的入参（R13）。 | export interface DraftPublishInput { |
| DraftPublishResult@41 | interface | L41-44 | 发布结果：新建的知识点 + 归档后的草稿。 | export interface DraftPublishResult { |
| deriveDraftLabel@47 | function | L47-55 | 从内容首行推导草稿展示标题（前端列表用；不写入 title 字段）。 | export function deriveDraftLabel(draft: Draft): string { |
| DraftService@57 | class | L57-185 |  | export class DraftService { |
| DraftService.create@73 | method | L73-77 | ---- 草稿 CRUD ---- | create(input: CreateDraftInput): Draft { |
| DraftService.list@79 | method | L79-81 |  | list(status?: DraftStatus): Array<Draft & { label: string }> { |
| DraftService.get@83 | method | L83-86 |  | get(id: string): (Draft & { label: string }) \| null { |
| DraftService.update@88 | method | L88-93 |  | update(id: string, patch: UpdateDraftInput): Draft \| null { |
| DraftService.setStatus@96 | method | L96-98 | 归档 / 转回活动。 | setStatus(id: string, status: DraftStatus): Draft \| null { |
| DraftService.archive@100 | method | L100-102 |  | archive(id: string): Draft \| null { |
| DraftService.unarchive@104 | method | L104-106 |  | unarchive(id: string): Draft \| null { |
| DraftService.remove@108 | method | L108-110 |  | remove(id: string): boolean { |
| DraftService.countActive@112 | method | L112-114 |  | countActive(): number { |
| DraftService.process@123 | method | L123-155 | 处理草稿：把材料交给固定拆解管线 → 原子知识点树入库。 | async process(id: string, opts: DraftProcessOptions = {}): Promise<{ |
| DraftService.publish@165 | method | L165-184 | 发布草稿：把整篇草稿作为单个知识点入库。 | publish(id: string, input: DraftPublishInput = {}): DraftPublishResult… |
