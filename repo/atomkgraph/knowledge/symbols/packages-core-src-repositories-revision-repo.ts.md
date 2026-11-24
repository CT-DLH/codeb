---
covers:
  - packages/core/src/repositories/revision-repo.ts
title: Semantic block index: revision-repo.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：revision-repo.ts（第4层）

**源码文件**：`packages/core/src/repositories/revision-repo.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="packages/core/src/repositories/revision-repo.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| RevisionRow@8 | interface | L8-14 |  | interface RevisionRow { |
| rowToRevision@16 | function | L16-24 |  | function rowToRevision(r: RevisionRow): KnowledgeRevision { |
| RevisionRepository@26 | class | L26-73 |  | export class RevisionRepository { |
| RevisionRepository.create@30 | method | L30-45 | 存一份知识点快照。 | create(knowledge: Knowledge, changeNote = ''): KnowledgeRevision { |
| RevisionRepository.findByKnowledge@48 | method | L48-53 | 某知识点的全部版本，最近优先。 | findByKnowledge(knowledgeId: string): KnowledgeRevision[] { |
| RevisionRepository.findById@55 | method | L55-60 |  | findById(revisionId: string): KnowledgeRevision \| null { |
| RevisionRepository.parseSnapshot@63 | method | L63-65 | 快照解析回知识点对象。 | static parseSnapshot(revision: KnowledgeRevision): Knowledge { |
| RevisionRepository.countByKnowledge@67 | method | L67-72 |  | countByKnowledge(knowledgeId: string): number { |
