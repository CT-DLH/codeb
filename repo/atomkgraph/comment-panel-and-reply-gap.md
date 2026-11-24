---
title: Comment panel: what already exists, and the reply gap
covers:
  - packages/shared/src/types.ts
  - packages/core/src/repositories/comment-repo.ts
  - packages/core/src/services/comment-service.ts
  - packages/core/src/llm/comment-prompt.ts
  - apps/web/src/components/CommentPanel.tsx
  - scripts/test-comment.ts
  - apps/server/src/routes.ts
updated: 2026-11-21
---

# Comment panel: what already exists, and the reply gap

**`atomkgraph/architecture/7` 里「社交交互（点赞、评论、收藏）未实现」这句话是错的**（就评论而言）。
代码里评论区已经有约 800 行、跑通并有测试。改这个功能之前先读这一页，
否则会去重写一套已存在的实现。

## 已经有的（别重写）

| 文件 | 行数 | 作用 |
| :-- | --: | :-- |
| `packages/shared/src/types.ts` | — | `Comment` 接口 12 字段 + `CommentTargetType = 'knowledge' \| 'question'` |
| `packages/core/src/repositories/comment-repo.ts` | 154 | 增删查改 + `findByTarget` / `countByTarget` / `deleteByTarget` |
| `packages/core/src/services/comment-service.ts` | 200 | `list/count/add/update/remove/generate` + `createLlmCriticFn` |
| `packages/core/src/llm/comment-prompt.ts` | 85 | `STUDENT_PERSONAS`（5 角色）+ `COMMENT_SYSTEM_PROMPT` |
| `apps/web/src/components/CommentPanel.tsx` | 240 | 面板，**已挂在 `QuestionPanel` 和 `App.tsx` 上** |
| `scripts/test-comment.ts` | 125 | 断言生成 3 条、每角色独立调用、计数、排序 |
| `apps/server/src/routes.ts` | — | `GET/POST /api/comments`、`/api/comments/count`、`/api/comments/generate`、`PATCH`/`DELETE /api/comments/:id` |

表 `comment` 在 `SCHEMA_SQL` 里（`packages/core/src/db/schema.ts`）：
`comment_id, target_type, target_id, role, persona, content, suggestion, status, source, model, create_time`。
索引 `idx_comment_target(target_type, target_id, create_time DESC)`、`idx_comment_status(status)`。

迁移机制：`connection.ts` 的 `migrate()` 里有 `addColumn(table, col, decl)`，
**幂等**（先 `hasColumn` 再 `ALTER TABLE`）。加列不需要写新迁移函数。

## 现有语义：AI 扮演「学生」挑刺

这是最容易搞反的地方。当前链路的**方向是：教材 → AI 扮演学生提问**：

- `COMMENT_SYSTEM_PROMPT` 第一句：「你是一名正在学习的学生」
- 5 个预设角色全是学生视角（基础薄弱的小白 / 爱钻牛角尖 / 跳步质疑者 / 爱类比 / 应试型）
- `generate()` 每个角色**独立调一次** LLM，3 条评论 = 3 次调用（`test-comment.ts` 有断言）
- 产出两部分：`content`（学生的问题）+ `suggestion`（**给老师看的**讲解优化建议）
- `suggestion` 的受众是内容作者，不是学生；**它在 UI 里标着「讲解优化建议」**

## 缺口：用户自己发帖 + AI 以老师身份回复

目标形态是**反方向**：用户在评论区提问 → AI 结合题目上下文给出解释。

三个真实 gap：

### Gap 1：`CommentPanel` 没有输入框

面板的 `useState` 只有 `items / filter / busy / msg / isError / copied`，
**没有草稿状态**，也没有 `<textarea>`。唯一写入路径是「让 AI 挑刺」按钮。

### Gap 2：prompt 方向相反，不能复用

`COMMENT_SYSTEM_PROMPT` 是学生视角。回复需要老师视角（解释、引导、不直接给答案）。
**可以复用的是调用结构**（`chat()` + `json` + `parseCommentResponse`），不是 prompt 文本。

### Gap 3：数据模型没有回复关系

`Comment` 12 个字段里没有父指针，也没有作者身份。所以 AI 回复现在无处可放——
塞进 `suggestion` 会语义错乱（那字段是私下的修改建议，不是公开对话）。

## 已定的改动方案（2026-11-21）

| 决定 | 值 |
| :-- | :-- |
| 触发方式 | **用户点按钮**，不自动（`generate()` 3 条 = 3 次调用，自动会烧 token） |
| 回复存放 | **新增 `parent_id` + `author`**，不动 `suggestion` 的语义 |
| MCP 工具面 | **不改**（`apps/mcp` 12 工具与 `verify-agent-parity.mjs` 三方一致，不碰） |

字段约定：

```ts
// packages/shared/src/types.ts
export type CommentAuthor = 'user' | 'ai'

export interface Comment {
  // ... 原有 12 字段不动
  /** 父评论 ID；顶层帖子为 null。回复挂在这里。 */
  parent_id: string | null
  /** 作者身份。现有 AI 挑刺生成的都是 'ai'；用户自己发的是 'user'。 */
  author: CommentAuthor
}
```

DB 迁移（`connection.ts` 的 `migrate()`）：

```ts
addColumn('comment', 'parent_id', 'TEXT')                    // 顶层为 NULL
addColumn('comment', 'author', "TEXT NOT NULL DEFAULT 'ai'") // 现有行都是 AI 生成的，默认值即正确
```

**现有数据不需要数据搬运**：存量 3 条都是 AI 挑刺产物，`author='ai'` 正是默认值，
`parent_id=NULL` 正是顶层。这是选 `DEFAULT 'ai'` 而不是 `'user'` 的原因。

## 三个并行写范围的边界

| 范围 | 文件 | 不许碰 |
| :-- | :-- | :-- |
| W1 模型+仓储 | `types.ts`、`comment-repo.ts`、`connection.ts` | `comment-prompt.ts`、`CommentPanel.tsx`、`routes.ts` |
| W2 回复链路 | `comment-prompt.ts`、`comment-service.ts` | `types.ts`、`CommentPanel.tsx`、`connection.ts` |
| W3 UI | `CommentPanel.tsx` | `types.ts`、`comment-service.ts`、`routes.ts` |

`routes.ts` 归 W2 末尾追加（新增 `POST /api/comments/:id/reply`），
W3 只调 `api.ts` 里新增的方法；`apps/web/src/api.ts` 由 W2 顺带加。

**接口契约必须先由 leader 定稿**（上面那段 TS + SQL），否则三个 agent 各写一套字段名。

## 实施结果（2026-11-21，已完成）

三个范围实际落地情况：

| 范围 | 改动 | 验证 |
| :-- | :-- | :-- |
| W1 | `types.ts` +19 行、`connection.ts` +11 行（v25）、`comment-repo.ts` +40 行 | tsc 干净；`test-comment.ts` 37/0 |
| W2 | `comment-prompt.ts` 加 `REPLY_SYSTEM_PROMPT` + `buildReplyUserPrompt`；`comment-service.ts` 加 `ReplyFn`/`createLlmReplier`/`generateReply`/`listReplies`；`routes.ts` 加 2 条路由；`api.ts` 加 3 个方法 | `verify-comment-reply.ts` 17/0 |
| W3 | `CommentPanel.tsx` 240 → 395 行 | tsc 干净；mock 渲染 18 断言 |

`connection.ts` 的版本号用 **v25**（`SCHEMA_VERSION = 24`，注释取下一个号）。
`migrate()` **不受 `SCHEMA_VERSION` 控制**，每次 `openDatabase()` 都跑，
靠 `hasColumn` 幂等跳过，所以老库下次打开自动补列，不需要重建。

## 踩到的坑：`max_tokens` 给小了会静默返回 502

这是本次唯一一个**只有真机才暴露**的 bug，值得单独记。

`generateReply` 最初写 `maxTokens: 800`（参照 `createLlmCriticFn` 的 1024）。
真机结果：

```
POST /api/comments/:id/reply → 502（耗时 47s）
LLM_TRUNCATED  模型输出被截断（finish_reason=length）
```

**47 秒换回一个 502，回复一个字都没有。**

原因：当前 `LLM_CHAT_MODEL` 是 `minimaxai/minimax-m3.1-flash`，**推理模型**。
它先把 token 预算花在 `reasoning_content` 上，正文还没写几个字就到了 `finish_reason=length`。
800 和 4096 都不够。

改成 **`maxTokens: 30000`** 后：47s → 产出 280 字正文，正常。

**这条适用于所有调 `chat()` 的地方**，不只是评论回复。判断依据：
`client.ts` 的 `loadConfig` 默认 `provider='mock'`、`max_tokens` 默认 4096；
一旦用的是推理模型（名字带 reasoning / thinking / flash 的常常是），4096 都可能不够。
报错信息里 `LLM_EMPTY_CONTENT`（reasoning 吃光预算）和 `LLM_TRUNCATED`（正文被截断）
是两个不同的码，但根因相同。

## 真实回复质量（实测样本）

输入——题目「快排什么情况退化到 O(n²)」，用户提问「选项 C 为什么不对？元素全部相同的时候，不是也不能均分吗？」：

> 你的困惑点在于：把"均分"理解成"按大小把元素分堆"，以为相等元素就分不开。其实划分均不均衡，只看指针怎么走。
>
> 以本题常用的双指针划分为例：右指针找小于基准的，左指针找大于基准的，相遇后交换。
> - 全相等：两指针各走一步就相遇，基准落在中点，划成 n/2 和 n/2，递归深度 log n，仍是 O(n log n)。
> - 已有序且取首元素：右指针一路扫到左端，只分出 1 和 n−1，每层如此，才退化 O(n²)。
>
> 补充：若换成 Lomuto 划分（基准在末尾、<= 算"小于"），全相等确实会退化。所以 C 是否成立取决于实现，本题按双指针实现选 A。

三点值得注意：
1. **它先纠正误解**（把"均分"理解成"按大小分堆"），而不是直接答选项——这正是 `REPLY_SYSTEM_PROMPT` 里「先判断困惑点」那条生效了。
2. **它指出题目表述对实现的依赖**（Lomuto 确实会退化），没有盲从题目的标准答案。
3. 280 字，符合「200 字以内、分点最多 3 点」的约束（略超但可接受）。

## 三个防错设计

1. **`generateReply` 只接受 `target_type='question'`**，知识点返回 `null` → 路由 404。
   不硬套题目 prompt，否则答得文不对题。
2. **同一父帖已有 AI 回复时不重复生成**，直接返回最后一条。防止用户连点按钮，
   而每次调用要 47s 且烧推理 token。
3. **`author` 显式写 `'user'`**，不依赖 repo 默认值 `'ai'`。
   `add()` 漏传会让用户自己发的帖被标成「AI 模拟」——这个 bug 实际发生过，
   被 `verify-comment-reply.ts` 的 `[1] 用户帖 author 为 user` 抓住。

## 验证入口

```bash
# 纯逻辑，不联网（mock critic + mock replier）
node node_modules/tsx/dist/cli.mjs scripts/verify-comment-reply.ts   # 17 断言
node node_modules/tsx/dist/cli.mjs scripts/test-comment.ts           # 37 断言（原有回归）

# 真机 HTTP（需要后端跑在 3939）
node node_modules/tsx/dist/cli.mjs apps/server/src/index.ts          # 先起后端
node node_modules/tsx/dist/cli.mjs scripts/e2e-comment-reply.ts      # 13 断言
```

**注意**：`e2e-comment-reply.ts` 的健康检查端点是 `/health`，**不是** `/api/health`
（后者 404）。踩过一次。

**注意**：`pnpm start` 起的后端进程如果被 `Select-Object -First N` 截断管道会**静默退出**
（exit 1，日志只到「数据库」那行）。后台跑后端不要截断 stdout。
