---
covers:
  - packages/core/src/services/quiz-service.ts
title: Semantic block index: quiz-service.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：quiz-service.ts（第4层）

**源码文件**：`packages/core/src/services/quiz-service.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="packages/core/src/services/quiz-service.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| QuizAttemptResult@14 | interface | L14-36 | 一次作答的批改 + 掌握度反馈。 | export interface QuizAttemptResult extends GradeResult { |
| QuizService@38 | class | L38-202 |  | export class QuizService { |
| QuizService.questionsForKnowledge@52 | method | L52-54 | 按知识点出题（多对多一侧）。 | questionsForKnowledge(knowledgeId: string): Question[] { |
| QuizService.drawQuestions@71 | method | L71-99 | 随机抽题：给定知识点集合，抽取若干题。 | drawQuestions( |
| QuizService.submitAnswer@108 | method | L108-169 | 作答并批改： | submitAnswer(questionId: string, got: string, opts: { duration?: numbe… |
| QuizService.attemptsFor@172 | method | L172-174 | R20：某题的作答历史（时间倒序）。 | attemptsFor(questionId: string, limit = 20): QuestionAttempt[] { |
| QuizService.wrongSet@180 | method | L180-201 | 错题集：从学习记录里筛出「答错」的题目（grade<3 且 target 是题目）。 | wrongSet(): Array<{ question: Question; lastWrongAt: string; wrongCoun… |
