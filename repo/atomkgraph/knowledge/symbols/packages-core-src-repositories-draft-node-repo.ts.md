---
covers:
  - packages/core/src/repositories/draft-node-repo.ts
title: Semantic block index: draft-node-repo.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：draft-node-repo.ts（第4层）

**源码文件**：`packages/core/src/repositories/draft-node-repo.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="packages/core/src/repositories/draft-node-repo.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| DraftNodeRow@15 | interface | L15-30 |  | interface DraftNodeRow { |
| parseEvidence@32 | function | L32-40 |  | function parseEvidence(raw: string): DraftNodeEvidence { |
| asAction@42 | function | L42-44 |  | function asAction(v: string): DraftNodeAction { |
| asPolicy@46 | function | L46-48 |  | function asPolicy(v: string): DraftContentPolicy { |
| asStatus@50 | function | L50-52 |  | function asStatus(v: string): DraftNodeStatus { |
| rowToNode@54 | function | L54-71 |  | function rowToNode(r: DraftNodeRow): DraftNode { |
| CreateDraftNodeInput@74 | interface | L74-78 | 新建候选：只给标题/正文，定位结果留空。 | export interface CreateDraftNodeInput { |
| DraftNodeRepository@87 | class | L87-213 |  | export class DraftNodeRepository { |
| DraftNodeRepository.createMany@91 | method | L91-120 | 批量写入（同一草稿内按 seq 顺序；seq 缺省时接在现有最大值之后）。 | createMany(draftId: string, items: CreateDraftNodeInput[]): DraftNode[… |
| DraftNodeRepository.findById@122 | method | L122-127 |  | findById(nodeId: string): DraftNode \| null { |
| DraftNodeRepository.findByDraft@129 | method | L129-138 |  | findByDraft(draftId: string, status?: DraftNodeStatus): DraftNode[] { |
| DraftNodeRepository.maxSeq@141 | method | L141-146 | 某草稿最近一次的落库批次（判断「这条草稿是不是已经用过」）。 | maxSeq(draftId: string): number { |
| DraftNodeRepository.update@148 | method | L148-175 |  | update(nodeId: string, patch: UpdateDraftNodeInput): DraftNode \| null… |
| DraftNodeRepository.deletePending@183 | method | L183-187 | 只删还没定位的候选（重跑抽取用）。 | deletePending(draftId: string): number { |
| DraftNodeRepository.deleteByDraft@190 | method | L190-192 | 连落库记录一起删（草稿作废时用；applied 的节点本身不会被删）。 | deleteByDraft(draftId: string): number { |
| DraftNodeRepository.resetLocated@199 | method | L199-203 | 把已定位的重置回待定位（改了召回/prompt 之后重跑用）。 | resetLocated(draftId: string): number { |
| DraftNodeRepository.countByDraft@205 | method | L205-212 |  | countByDraft(draftId: string): Record<DraftNodeStatus, number> { |
