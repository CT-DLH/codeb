---
covers:
  - packages/core/src/repositories/relation-repo.ts
title: Semantic block index: relation-repo.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：relation-repo.ts（第4层）

**源码文件**：`packages/core/src/repositories/relation-repo.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="packages/core/src/repositories/relation-repo.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| RelationRow@8 | interface | L8-17 |  | interface RelationRow { |
| rowToRelation@19 | function | L19-30 |  | function rowToRelation(r: RelationRow): Relation { |
| CreateRelationInput@35 | interface | L35-41 |  | export interface CreateRelationInput { |
| RelationWithTitles@44 | interface | L44-47 | 关系 + 两端标题（详情页「关联关系」面板用）。 | export interface RelationWithTitles extends Relation { |
| CreateRelationStatus@50 | interface | L50-59 | createWithStatus() 的结果：关系本身 + 是否是「已存在直接复用」。 | export interface CreateRelationStatus { |
| UpdateRelationInput@72 | interface | L72-79 | 关系编辑的入参（PATCH 语义：只给要改的字段）。 | export interface UpdateRelationInput { |
| RelationRepository@86 | class | L86-376 |  | export class RelationRepository { |
| RelationRepository.createWithStatus@95 | method | L95-121 | 创建关系，并说明本次是新建还是命中已有。 | createWithStatus(input: CreateRelationInput): CreateRelationStatus { |
| RelationRepository.create@124 | method | L124-126 | 创建关系；同向同类型已存在时直接返回既有记录（幂等，防 AI 重复生成）。 | create(input: CreateRelationInput): Relation { |
| RelationRepository.createMany@142 | method | L142-176 | 批量创建关系（单事务）。 | createMany( |
| RelationRepository.update@190 | method | L190-271 | 修改一条已存在的关系：换类型、调权重、改端点、标审核状态。 | update( |
| RelationRepository.update.assign@202 | arrow | L202-207 | 逐个字段「只在值真的不同时才记一笔」——省略的字段保持原值（PATCH 语义）， 传了但与现状相同的字段不算变更。 | const assign = (field: keyof Relation, value: unknown): void => { |
| RelationRepository.migrate@280 | method | L280-316 | 关系迁移：把某知识点上的全部出边/入边改指向另一个知识点。 | migrate(fromId: string, toId: string): { moved: number; dropped: numbe… |
| RelationRepository.findById@318 | method | L318-323 |  | findById(id: string): Relation \| null { |
| RelationRepository.findByKnowledge@326 | method | L326-331 | 查询与某知识点相连的全部关系（出边 + 入边），用于图谱渲染。 | findByKnowledge(knowledgeId: string): Relation[] { |
| RelationRepository.findByKnowledgeWithTitles@341 | method | L341-359 | 同 findByKnowledge()，但每条关系带上两端知识点的标题。 | findByKnowledgeWithTitles(knowledgeId: string): RelationWithTitles[] { |
| RelationRepository.findByType@361 | method | L361-366 |  | findByType(relationType: RelationType): Relation[] { |
| RelationRepository.findAll@368 | method | L368-371 |  | findAll(): Relation[] { |
| RelationRepository.delete@373 | method | L373-375 |  | delete(id: string): boolean { |
