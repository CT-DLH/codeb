---
covers:
  - packages/core/src/repositories/learning-repo.ts
title: Semantic block index: learning-repo.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：learning-repo.ts（第4层）

**源码文件**：`packages/core/src/repositories/learning-repo.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="packages/core/src/repositories/learning-repo.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| RecordRow@8 | interface | L8-15 |  | interface RecordRow { |
| rowToRecord@17 | function | L17-26 |  | function rowToRecord(r: RecordRow): LearningRecord { |
| CreateRecordInput@28 | interface | L28-33 |  | export interface CreateRecordInput { |
| LearningRecordRepository@35 | class | L35-89 |  | export class LearningRecordRepository { |
| LearningRecordRepository.create@38 | method | L38-54 |  | create(input: CreateRecordInput): LearningRecord { |
| LearningRecordRepository.findById@56 | method | L56-61 |  | findById(id: string): LearningRecord \| null { |
| LearningRecordRepository.findByTarget@64 | method | L64-69 | 某知识点的全部学习记录（时间倒序），用于掌握度计算与学习轨迹。 | findByTarget(targetId: string): LearningRecord[] { |
| LearningRecordRepository.findByType@71 | method | L71-76 |  | findByType(type: RecordType, limit = 100): LearningRecord[] { |
| LearningRecordRepository.totalDuration@79 | method | L79-84 | 总学习时长（秒），供仪表盘使用。 | totalDuration(): number { |
| LearningRecordRepository.count@86 | method | L86-88 |  | count(): number { |
| QueueRow@93 | interface | L93-100 | ---- 复习队列 ---- | interface QueueRow { |
| ReviewQueueItem@102 | interface | L102-109 |  | export interface ReviewQueueItem { |
| rowToQueue@111 | function | L111-120 |  | function rowToQueue(r: QueueRow): ReviewQueueItem { |
| ReviewQueueRepository@122 | class | L122-176 |  | export class ReviewQueueRepository { |
| ReviewQueueRepository.enqueue@126 | method | L126-151 | 入队；同一知识点已有 pending 项时更新其到期时间，避免重复堆积。 | enqueue(knowledgeId: string, dueAt: string, priority = 0): ReviewQueue… |
| ReviewQueueRepository.findDue@154 | method | L154-161 | 取到期项（按优先级降序、到期时间升序），供复习提醒生成队列。 | findDue(now: string = nowIso(), limit = 50): ReviewQueueItem[] { |
| ReviewQueueRepository.markStatus@163 | method | L163-168 |  | markStatus(queueId: string, status: ReviewQueueItem['status']): boolea… |
| ReviewQueueRepository.findAll@170 | method | L170-175 |  | findAll(): ReviewQueueItem[] { |
| ReviewHistoryItem@180 | interface | L180-189 | ---- 复习历史轨迹（Phase 4） ---- | export interface ReviewHistoryItem { |
| CreateReviewHistoryInput@191 | interface | L191-198 |  | export interface CreateReviewHistoryInput { |
| RevHistRow@200 | interface | L200-209 |  | interface RevHistRow { |
| rowToRevHist@211 | function | L211-213 |  | function rowToRevHist(r: RevHistRow): ReviewHistoryItem { |
| ReviewHistoryRepository@215 | class | L215-246 |  | export class ReviewHistoryRepository { |
| ReviewHistoryRepository.create@218 | method | L218-237 |  | create(input: CreateReviewHistoryInput): ReviewHistoryItem { |
| ReviewHistoryRepository.findByKnowledge@240 | method | L240-245 | 某知识点的复习轨迹（时间倒序），用于掌握度曲线。 | findByKnowledge(knowledgeId: string, limit = 100): ReviewHistoryItem[]… |
