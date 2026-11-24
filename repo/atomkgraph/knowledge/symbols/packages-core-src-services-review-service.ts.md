---
covers:
  - packages/core/src/services/review-service.ts
title: Semantic block index: review-service.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：review-service.ts（第4层）

**源码文件**：`packages/core/src/services/review-service.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="packages/core/src/services/review-service.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| MasteryThresholds@19 | interface | L19-22 | 掌握度阈值（薄弱线 / 已掌握线），计划书要求可由设置覆盖，此处给默认值。 | export interface MasteryThresholds { |
| AnswerFeedback@26 | interface | L26-32 |  | export interface AnswerFeedback { |
| ReviewService@34 | class | L34-237 |  | export class ReviewService { |
| ReviewService.collectAnswers@56 | method | L56-71 | 收集某知识点的全部答题结果（含直接挂知识点 + 挂在关联题目上的）。 | private collectAnswers(knowledgeId: string, knowledgeDifficulty: numbe… |
| ReviewService.deriveMastery@74 | method | L74-85 | 由 SM-2 参数派生掌握度（0-100）与状态，不落库（纯 SM-2 分，作为综合分的退化基准）。 | deriveMastery(state: SM2State): Mastery { |
| ReviewService.deriveMasteryForKnowledge@91 | method | L91-114 | 综合掌握度（计划书模块4）：难度加权正确率 + SM-2 + 学习投入 + 阅读（R5）修正。 | deriveMasteryForKnowledge(knowledgeId: string, state: SM2State, diffic… |
| ReviewService.recordAnswer@120 | method | L120-167 | 记录一次答题：写入学习记录 → 更新 SM-2 → 重算掌握度 → 排下一次复习。 | recordAnswer( |
| ReviewService.dueReviews@170 | method | L170-172 | 取当前到期复习队列。 | dueReviews(limit = 50): ReviewQueueItem[] { |
| ReviewService.completeReview@175 | method | L175-177 | 标记复习完成。 | completeReview(queueId: string): boolean { |
| ReviewService.aggregateProgress@184 | method | L184-223 | 自底向上进度聚合（计划书模块5）： | aggregateProgress(thresholds: MasteryThresholds = this.thresholds): Ma… |
| ReviewService.aggregateProgress.compute@195 | arrow | L195-218 |  | const compute = (k: (typeof all)[number]): number => { |
| ReviewService.weakPoints@226 | method | L226-236 | 薄弱点识别：聚合掌握度低于薄弱线的知识点。 | weakPoints(): Array<{ knowledge_id: string; title: string; score: numb… |
