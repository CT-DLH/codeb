---
covers:
  - packages/shared/src/types.ts
title: Semantic block index: types.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：types.ts（第4层）

**源码文件**：`packages/shared/src/types.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="packages/shared/src/types.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| Knowledge@51 | interface | L51-115 | 原子知识点实体（5.1） | export interface Knowledge { |
| KnowledgeNav@131 | interface | L131-141 | 导航用的知识点骨架：Knowledge 去掉一切大字段，只留树渲染需要的东西。 | export interface KnowledgeNav { |
| KnowledgeNavNode@144 | interface | L144-147 | 导航树的节点形状，与 core 的 KnowledgeTreeNode 同构，供前后端共用。 | export interface KnowledgeNavNode { |
| Mastery@150 | interface | L150-153 | 掌握度（派生值，不存储） | export interface Mastery { |
| Relation@158 | interface | L158-167 |  | export interface Relation { |
| QuestionAnalysis@178 | interface | L178-183 | 一题多解中的一条解析（R19）。 | export interface QuestionAnalysis { |
| SubQuestion@199 | interface | L199-227 | 一题多问中的一个小问（R29）。 | export interface SubQuestion { |
| Question@229 | interface | L229-323 |  | export interface Question { |
| Paper@341 | interface | L341-376 | 卷（R61）。整卷视角的容器，不在知识点树里（避免污染掌握度聚合）。 | export interface Paper { |
| PaperPart@384 | interface | L384-396 | 卷内大题（R61），如「一、单项选择题」。 | export interface PaperPart { |
| PaperWithStats@402 | interface | L402-411 | 卷 + 其大题 + 题数统计（列表/详情视图用）。 | export interface PaperWithStats extends Paper { |
| QuestionAttempt@420 | interface | L420-432 | 一次作答记录（R20）。 | export interface QuestionAttempt { |
| QuestionRevision@441 | interface | L441-449 | 题目版本历史实体（R22，对齐 KnowledgeRevision）。 | export interface QuestionRevision { |
| Tag@452 | interface | L452-457 | 标签实体（5.3） | export interface Tag { |
| LearningRecord@462 | interface | L462-469 |  | export interface LearningRecord { |
| SplitResult@472 | interface | L472-478 | 拆解结果（Phase 0 验证用） | export interface SplitResult { |
| KnowledgeRevision@482 | interface | L482-490 | 知识点版本历史实体（5.7）：每次编辑前的快照，可追溯/可回滚。 | export interface KnowledgeRevision { |
| Draft@496 | interface | L496-510 | 缓存区草稿（R1）：暂存未处理的原始材料，由固定 AI 统一拆解入库。 | export interface Draft { |
| DraftProcessResult@513 | interface | L513-519 | 草稿处理（AI 拆解入库）结果摘要。 | export interface DraftProcessResult { |
| DraftNode@562 | interface | L562-581 |  | export interface DraftNode { |
| DraftNodeEvidence@589 | interface | L589-602 | 定位证据：LLM 当时看到了什么才做出这个判断。 | export interface DraftNodeEvidence { |
| ApplyBatch@605 | interface | L605-614 | 一次 apply = 一个批次，整批可逆。 | export interface ApplyBatch { |
| ApplyBatchItem@617 | interface | L617-625 | 批次明细：回滚的唯一依据（不依赖 revision 链）。 | export interface ApplyBatchItem { |
| Comment@648 | interface | L648-670 | 评论（R4）：模拟学生提出的问题/挑刺 + AI 给出的讲解优化建议。 | export interface Comment { |
| CommentGenerationResult@673 | interface | L673-679 | 「让 AI 挑刺」的结果：本轮生成的多条学生评论。 | export interface CommentGenerationResult { |
