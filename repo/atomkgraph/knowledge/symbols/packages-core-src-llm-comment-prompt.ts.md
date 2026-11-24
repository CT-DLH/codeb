---
covers:
  - packages/core/src/llm/comment-prompt.ts
title: Semantic block index: comment-prompt.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：comment-prompt.ts（第4层）

**源码文件**：`packages/core/src/llm/comment-prompt.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="packages/core/src/llm/comment-prompt.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| StudentPersona@9 | interface | L9-12 | 预设学生角色：覆盖典型困惑类型（基础薄弱 / 跳步质疑 / 边界较真 / 类比迁移）。 | export interface StudentPersona { |
| buildCommentUserPrompt@44 | function | L44-67 | 组装某学生角色单次挑刺的用户 prompt。 | export function buildCommentUserPrompt(ctx: { |
| parseCommentResponse@70 | function | L70-85 | 解析 LLM 返回的评论 JSON（容错：脏数据退化为纯文本评论）。 | export function parseCommentResponse(raw: string): { content: string; … |
| buildReplyUserPrompt@122 | function | L122-172 | 组装「用户提问 → 老师回复」的用户 prompt。 | export function buildReplyUserPrompt(ctx: { |
