---
covers:
  - packages/shared/src/types.ts
  - packages/core/src/repositories/comment-repo.ts
  - packages/core/src/services/comment-service.ts
  - packages/core/src/llm/comment-prompt.ts
  - apps/server/src/routes.ts
  - apps/web/src/components/CommentPanel.tsx
title: Comment & Reply Module — Component Table (Layer 3)
updated: 2025-08-27
---

# 模块：评论与回复模块——部件细页表（第3层）

**项目**：atomkgraph
**源码文件**：`types.ts`, `comment-repo.ts`, `comment-service.ts`, `comment-prompt.ts`, `routes.ts`, `CommentPanel.tsx`
**第4层语义块索引**：
- [`types.ts`](../symbols/types.ts.md)
- [`comment-repo.ts`](../symbols/comment-repo.ts.md)
- [`comment-service.ts`](../symbols/comment-service.ts.md)
- [`comment-prompt.ts`](../symbols/comment-prompt.ts.md)
- [`routes.ts`](../symbols/routes.ts.md)
- [`CommentPanel.tsx`](../symbols/CommentPanel.tsx.md)
**写范围**：`types.ts`, `comment-repo.ts`, `comment-service.ts`, `comment-prompt.ts`, `routes.ts`, `CommentPanel.tsx`（不得碰 `packages/` 与 `apps/` 源码直调）
**验证命令**：`npx tsc -p apps/web/tsconfig.json --noEmit` 或 `npx tsc -p apps/server/tsconfig.json --noEmit`

## 职责
实现评论与回复的核心功能：类型定义（`types.ts`）、评论持久化与查询（`comment-repo.ts`）、评论服务与生成（`comment-service.ts`）、LLM prompt 构建（`comment-prompt.ts`）、路由注册与请求分发（`routes.ts`）、前端评论面板（`CommentPanel.tsx`）。涵盖接口、仓库方法、服务方法、prompt 建模、路由入口及 UI 组件六个层面。

## 适用场景
- 修改评论类型定义或接口（`types.ts`）—— 确保 `Comment`/`CommentRow` 变更同步更新所有依赖。
- 调整评论的增删改查逻辑（`comment-repo.ts`）—— 仓库层变更需同步检查 `comment-service.ts` 的方法签名。
- 变更 LLM prompt 构建或回复解析（`comment-prompt.ts`）—— prompt 结构变更会影响前端 `CommentPanel` 显示。
- 添加/修改评论相关 API（`routes.ts`）—— 新增路由需在 `routes.ts` 注册并同步前端 `CommentPanel` 交互。
- 重构前端评论面板（`CommentPanel.tsx`）—— UI 变更需对应后端接口形变，保持请求/响应一致。

## 功能部件

| 部件 key | 类型 | 行号 | 作用 |
|:--|:--|:--|:--|
| Comment@648 | interface | 648 | 定义评论实体接口，包含作者、内容、状态、元数据等字段 |
| CommentRow@8 | interface | 8 | 仓库层使用的轻量级行接口，用于批量持久化 |
| CommentRepository@59 | class | 59 | 评论仓库类，封装所有持久化操作 |
| CommentRepository.create@62 | method | 62 | 新建一条评论 |
| CommentRepository.findByTarget@104 | method | 104 | 根据目标类型与 ID 查找评论列表 |
| CommentService@119 | class | 119 | 评论服务类，包含业务逻辑与 LLM 调度 |
| CommentService.generate@186 | method | 186 | 异步生成评论（LLM 调用） |
| CommentService.generateReply@239 | method | 239 | 异步生成指定评论的回复 |
| buildCommentUserPrompt@44 | function | 44 | 根据上下文构建评论用的 LLM prompt |
| registerRoutes@152 | function | 152 | 主路由注册函数，绑定评论相关路径 |
| CommentPanel@43 | function | 43 | 前端评论面板组件，提供发送、回复、删除操作 |
| CommentPanel.onSend@110 | method | 110 | 发送用户评论 |

## 测试文件
- 项目自有的单元测试：`packages/core/src/repositories/__tests__/comment-repo.test.ts`、`packages/core/src/services/__tests__/comment-service.test.ts` 等

## 下沉指引
```
选中部件 → 打开第4层 symbols 文件 → read_block(path="types.ts", key="Comment@648")
read_block(path="comment-repo.ts", key="CommentRepository.create@62")
read_block(path="comment-service.ts", key="CommentService.generate@186")
read_block(path="comment-prompt.ts", key="buildCommentUserPrompt@44")
read_block(path="routes.ts", key="registerRoutes@152")
read_block(path="CommentPanel.tsx", key="CommentPanel.onSend@110")
```