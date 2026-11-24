---
covers:
  - packages/core/src/services/comment-service.ts
title: comment-service.ts semantic block index (layer 4)
updated: 2025-08-27
---

# 语义块索引：comment-service.ts（第4层）

**源码文件**：`packages/core/src/services/comment-service.ts`

**解析器**：`typescript` · **解析器**：`typescript` · **第5层完整正文**：`read_block(path="packages/core/src/services/comment-service.ts", key="CommentService@10")`

| 语义块 key | 类型 | 行号 | 作用 |
|:--|:--|:--|:--|
| createLlmCriticFn@39 | function | L39-52 | export function createLlmCriticFn(cfg?: LLMConfig): CriticFn { |
| createLlmReplier@90 | function | L90-109 | export function createLlmReplier(cfg?: LLMConfig): ReplyFn { |
| Material@112 | interface | L112-117 | interface Material { |
| CommentService@119 | class | L119-337 | export class CommentService { |
| CommentService.list@135 | method | L135-137 | list(targetType: CommentTargetType, targetId: string, status?: Comment… |
| CommentService.count@140 | method | L140-142 | count(targetType: CommentTargetType, targetId: string): { open: number… |
| CommentService.add@145 | method | L145-170 | add(input: { |
| CommentService.update@173 | method | L173-175 | update(id: string, patch: { content?: string; suggestion?: string; sta… |
| CommentService.remove@178 | method | L178-180 | remove(id: string): boolean { |
| CommentService.generate@186 | method | L186-219 | async generate( |
| CommentService.removeByTarget@222 | method | L222-224 | removeByTarget(targetType: CommentTargetType, targetId: string): numbe… |
| CommentService.generateReply@239 | method | L239-289 | async generateReply(commentId: string): Promise<Comment \| null> { |
| CommentService.listReplies@292 | method | L292-294 | listReplies(parentId: string): Comment[] { |
| CommentService.targetExists@297 | method | L297-301 | private targetExists(targetType: CommentTargetType, targetId: string):… |
| CommentService.loadMaterial@304 | method | L304-336 | private loadMaterial(targetType: CommentTargetType, targetId: string):… |
