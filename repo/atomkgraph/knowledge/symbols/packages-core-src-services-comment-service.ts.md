---
covers:
  - packages/core/src/services/comment-service.ts
title: Semantic block index: comment-service.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：comment-service.ts（第4层）

**源码文件**：`packages/core/src/services/comment-service.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="packages/core/src/services/comment-service.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| createLlmCriticFn@39 | function | L39-52 | 基于 LLM 的默认挑刺器。每个角色独立一次调用（无历史上下文）。 | export function createLlmCriticFn(cfg?: LLMConfig): CriticFn { |
| createLlmReplier@90 | function | L90-109 | 基于 LLM 的默认回复器。 | export function createLlmReplier(cfg?: LLMConfig): ReplyFn { |
| Material@112 | interface | L112-117 | 取材料信息（标题/正文/类型/上下文），供挑刺器使用。 | interface Material { |
| CommentService@119 | class | L119-337 |  | export class CommentService { |
| CommentService.list@135 | method | L135-137 | 列出某目标的评论（最近优先）；status 可选过滤。 | list(targetType: CommentTargetType, targetId: string, status?: Comment… |
| CommentService.count@140 | method | L140-142 | 目标评论计数（待处理 / 总数）。 | count(targetType: CommentTargetType, targetId: string): { open: number… |
| CommentService.add@145 | method | L145-170 | 手动新增一条评论（人工补充，source='manual'）。 | add(input: { |
| CommentService.update@173 | method | L173-175 | 更新评论（改状态/正文/建议）——「采纳」即把 status 置为 adopted。 | update(id: string, patch: { content?: string; suggestion?: string; sta… |
| CommentService.remove@178 | method | L178-180 | 删除评论。 | remove(id: string): boolean { |
| CommentService.generate@186 | method | L186-219 | 「让 AI 挑刺」：为某目标生成若干条模拟学生评论并入库。 | async generate( |
| CommentService.removeByTarget@222 | method | L222-224 | 清理某目标的全部评论（目标被删除时调用）。 | removeByTarget(targetType: CommentTargetType, targetId: string): numbe… |
| CommentService.generateReply@239 | method | L239-289 | AI 以老师身份回复某条用户评论（手动触发，不自动）。 | async generateReply(commentId: string): Promise<Comment \| null> { |
| CommentService.listReplies@292 | method | L292-294 | 取某条帖子下的回复（按时间正序）。 | listReplies(parentId: string): Comment[] { |
| CommentService.targetExists@297 | method | L297-301 | 目标是否仍存在（未删除）。 | private targetExists(targetType: CommentTargetType, targetId: string):… |
| CommentService.loadMaterial@304 | method | L304-336 | 载入挑刺所需材料；目标不存在返回 null。 | private loadMaterial(targetType: CommentTargetType, targetId: string):… |
