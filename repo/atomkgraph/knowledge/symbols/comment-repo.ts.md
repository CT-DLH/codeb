---
covers:
  - packages/core/src/repositories/comment-repo.ts
title: comment-repo.ts semantic block index (layer 4)
updated: 2025-08-27
---

# 语义块索引：comment-repo.ts（第4层）

**源码文件**：`packages/core/src/repositories/comment-repo.ts`

**解析器**：`typescript` · **解析器**：`typescript` · **第5层完整正文**：`read_block(path="packages/core/src/repositories/comment-repo.ts", key="CommentRow@8")`

| 语义块 key | 类型 | 行号 | 作用 |
|:--|:--|:--|:--|
| CommentRow@8 | interface | L8-22 | interface CommentRow { |
| rowToComment@24 | function | L24-40 | function rowToComment(r: CommentRow): Comment { |
| CreateCommentInput@42 | interface | L42-55 | export interface CreateCommentInput { |
| CommentRepository@59 | class | L59-179 | export class CommentRepository { |
| CommentRepository.create@62 | method | L62-89 | create(input: CreateCommentInput): Comment { |
| CommentRepository.findById@91 | method | L91-96 | findById(id: string): Comment \| null { |
| CommentRepository.findByTarget@104 | method | L104-119 | findByTarget(targetType: CommentTargetType, targetId: string, status?:… |
| CommentRepository.findReplies@122 | method | L122-129 | findReplies(parentId: string): Comment[] { |
| CommentRepository.findAll@132 | method | L132-137 | findAll(): Comment[] { |
| CommentRepository.countByTarget@140 | method | L140-150 | countByTarget(targetType: CommentTargetType, targetId: string): { open… |
| CommentRepository.update@152 | method | L152-167 | update(id: string, patch: UpdateCommentInput): Comment \| null { |
| CommentRepository.delete@169 | method | L169-171 | delete(id: string): boolean { |
| CommentRepository.deleteByTarget@174 | method | L174-178 | deleteByTarget(targetType: CommentTargetType, targetId: string): numbe… |
