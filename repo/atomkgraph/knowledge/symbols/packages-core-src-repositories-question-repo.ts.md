---
covers:
  - packages/core/src/repositories/question-repo.ts
title: Semantic block index: question-repo.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：question-repo.ts（第4层）

**源码文件**：`packages/core/src/repositories/question-repo.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="packages/core/src/repositories/question-repo.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| markdownFieldsOf@67 | function | L67-91 | 把一道题里所有 Markdown 字段摊平成体检入参（字段名要能让 AI 直接定位）。 | function markdownFieldsOf(q: Question): MarkdownField[] { |
| QuestionRow@93 | interface | L93-125 |  | interface QuestionRow { |
| rowToQuestion@132 | function | L132-165 | 归一化多解析数组。实现已迁到 question-normalize.ts（R29：小问内部也要复用同一套规则， | function rowToQuestion(r: QuestionRow, knowledgeIds?: string[]): Quest… |
| CreateQuestionInput@167 | interface | L167-211 |  | export interface CreateQuestionInput { |
| OptionUpsert@269 | interface | L269-272 | option_upsert：按下标替换一条选项；省略下标则追加到末尾。 | export interface OptionUpsert { |
| AnalysisUpsert@275 | interface | L275-279 | analysis_upsert：按下标替换一条解析；省略下标则追加。只覆盖传入字段。 | export interface AnalysisUpsert { |
| SubQuestionUpsert@282 | interface | L282-292 | sub_question_upsert：按下标替换一个小问；省略下标则追加。只覆盖传入字段。 | export interface SubQuestionUpsert { |
| assertSingleForm@328 | function | L328-335 | 同一数组的多种写法互斥；给多了直接报错（避免「谁生效」含糊）。 | function assertSingleForm(label: string, forms: boolean[], code: strin… |
| mergeSubQuestion@338 | function | L338-349 | upsert 命中时只覆盖传入字段，未传的沿用原值。 | function mergeSubQuestion(cur: SubQuestion, s: SubQuestionUpsert): Sub… |
| buildSubQuestion@352 | function | L352-363 | 追加一个小问：未传的可选字段不带键（与归一规则一致）。 | function buildSubQuestion(s: SubQuestionUpsert): SubQuestion { |
| resolveQuestionFieldOps@376 | function | L376-504 | R55：把题目侧的字段级虚拟字段（*_append / *_search_replace / *_upsert / *_remove） | function resolveQuestionFieldOps( |
| QuestionRevisionRow@508 | interface | L508-514 | ---- 题目版本历史（R22，对齐 knowledge_revision） ---- | interface QuestionRevisionRow { |
| rowToQuestionRevision@516 | function | L516-524 |  | function rowToQuestionRevision(r: QuestionRevisionRow): QuestionRevisi… |
| QuestionRevisionRepository@532 | class | L532-587 | 题目版本历史仓库：每次编辑前存一份完整快照。 | export class QuestionRevisionRepository { |
| QuestionRevisionRepository.create@536 | method | L536-551 | 存一份题目快照。 | create(question: Question, changeNote = ''): QuestionRevision { |
| QuestionRevisionRepository.findByQuestion@554 | method | L554-561 | 某题的全部历史版本，最近优先。 | findByQuestion(questionId: string): QuestionRevision[] { |
| QuestionRevisionRepository.findById@563 | method | L563-568 |  | findById(revisionId: string): QuestionRevision \| null { |
| QuestionRevisionRepository.parseSnapshot@571 | method | L571-573 | 快照解析回题目对象。 | static parseSnapshot(revision: QuestionRevision): Question { |
| QuestionRevisionRepository.countByQuestion@575 | method | L575-581 |  | countByQuestion(questionId: string): number { |
| QuestionRevisionRepository.removeByQuestion@584 | method | L584-586 | 题目被删除时清理其版本历史（软删的题目无处可回滚）。 | removeByQuestion(questionId: string): number { |
| toQuestionBrief@596 | function | L596-612 | R26：mode: 'summary' 用的轻量投影。 | function toQuestionBrief(q: Question): Question { |
| QuestionRepository@614 | class | L614-1158 |  | export class QuestionRepository { |
| QuestionRepository.create@621 | method | L621-689 |  | create(input: CreateQuestionInput): QuestionWithCheck { |
| QuestionRepository.findByFingerprint@697 | method | L697-702 | 按整题指纹查重（R12 Stage 0 / docs/15 §7.2）。 | findByFingerprint(fingerprint: string): Question \| null { |
| QuestionRepository.softDeleteByBatch@708 | method | L708-716 | 整批软删（docs/15 §7.3 回滚）。空 batch_id 直接返回 0—— | softDeleteByBatch(batchId: string): number { |
| QuestionRepository.syncKnowledgeLinks@720 | method | L720-736 | 同步题目-知识点关联表（整体替换指定 question 的关联；source 默认 manual）。 | syncKnowledgeLinks(questionId: string, knowledgeIds: string[], source … |
| QuestionRepository.addKnowledgeLink@739 | method | L739-751 | 追加一条题目-知识点关联（不删除已有；用于向量自动关联 / 模型挂载）。 | addKnowledgeLink(questionId: string, knowledgeId: string, source = 've… |
| QuestionRepository.clearKnowledgeLinks@757 | method | L757-762 | 删除某题的关联。source 省略 = 全删（手工编辑关联时的「整体替换」语义）； | clearKnowledgeLinks(questionId: string, source?: string): number { |
| QuestionRepository.findKnowledgeIds@771 | method | L771-776 | 读取题目关联的知识点 ID（走关联表，非 JSON 字段）。 | findKnowledgeIds(questionId: string): string[] { |
| QuestionRepository.liveKnowledgeIds@791 | method | L791-802 | R61：只返回活知识点的关联 id（过滤已软删的目标）。 | liveKnowledgeIds(questionId: string): string[] { |
| QuestionRepository.staleLinkCount@810 | method | L810-820 | R61：失效关联数（指向已软删知识点的边）。 | staleLinkCount(questionId: string): number { |
| QuestionRepository.deepestKnowledgeId@837 | method | L837-845 | 关联节点里最深的那个——答题记掌握度的落点。 | deepestKnowledgeId(questionId: string): string \| undefined { |
| QuestionRepository.hydrate@853 | method | L853-855 | 用关联表数据填充题目的 relate_knowledge_ids（关联表为事实源）。 | private hydrate(q: Question): Question { |
| QuestionRepository.findById@857 | method | L857-862 |  | findById(id: string): Question \| null { |
| QuestionRepository.findAll@864 | method | L864-869 |  | findAll(): Question[] { |
| QuestionRepository.findByKnowledge@872 | method | L872-882 | 按知识点反查关联题目（多对多的一侧）：走关联表 JOIN 索引，替代 LIKE 全表扫。 | findByKnowledge(knowledgeId: string): Question[] { |
| QuestionRepository.countByKnowledgeId@890 | method | L890-899 | 统计挂在某知识点上的存活题目数。 | countByKnowledgeId(knowledgeId: string): number { |
| QuestionRepository.distinctSources@908 | method | L908-915 | R61：库里实际存在的来源取值。 | distinctSources(): string[] { |
| QuestionRepository.list@927 | method | L927-975 | R26：带过滤的题目列表。GET /api/questions 与 akg_list_questions 共用。 | list(opts: { |
| QuestionRepository.update@977 | method | L977-1030 |  | update(id: string, patch: UpdateQuestionPatch): QuestionWithCheck \| n… |
| QuestionRepository.applyUpdate@1036 | method | L1036-1097 | 真正的写入（不产生版本）。抽出来是为了让 rollback 复用同一条写路径—— | private applyUpdate( |
| QuestionRepository.softDelete@1099 | method | L1099-1104 |  | softDelete(id: string): boolean { |
| QuestionRepository.listRevisions@1109 | method | L1109-1111 | 某题的历史版本（最近优先）。 | listRevisions(id: string): QuestionRevision[] { |
| QuestionRepository.rollback@1119 | method | L1119-1157 | 回滚到指定历史版本：先存当前状态为新版本（回滚本身也可回滚），再套用快照。 | rollback(id: string, revisionId: string): Question \| null { |
| AttemptRow@1162 | interface | L1162-1170 | ---- 作答历史（R20） ---- | interface AttemptRow { |
| rowToAttempt@1172 | function | L1172-1182 |  | function rowToAttempt(r: AttemptRow): QuestionAttempt { |
| CreateAttemptInput@1184 | interface | L1184-1190 |  | export interface CreateAttemptInput { |
| QuestionAttemptRepository@1198 | class | L1198-1248 | 作答历史仓库：同一道题可反复作答，每次落一条。 | export class QuestionAttemptRepository { |
| QuestionAttemptRepository.create@1201 | method | L1201-1221 |  | create(input: CreateAttemptInput): QuestionAttempt { |
| QuestionAttemptRepository.findByQuestion@1224 | method | L1224-1233 | 某题的作答历史（时间倒序，最新在前）。 | findByQuestion(questionId: string, limit = 20): QuestionAttempt[] { |
| QuestionAttemptRepository.countByQuestion@1236 | method | L1236-1242 | 某题作答次数。 | countByQuestion(questionId: string): number { |
| QuestionAttemptRepository.removeByQuestion@1245 | method | L1245-1247 | 题目被删除时清理其作答历史。 | removeByQuestion(questionId: string): number { |
