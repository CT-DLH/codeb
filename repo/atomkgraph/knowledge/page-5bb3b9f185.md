---
covers:
  - apps/web/src/App.tsx
  - apps/web/src/api.ts
  - apps/web/src/i18n.ts
  - apps/server/src/routes.ts
  - packages/core/src/services/knowledge-service.ts
title: Deleting a knowledge point: two-step confirm and its pitfalls
updated: 2026-11-22
---

# 知识点手动删除：两步预检弹窗的设计与踩坑

前端删除入口（R62）走**两步**：点「删除」→ `dry_run` 预检（不落刀）→ 弹窗列真实影响面 → 用户确认才真删。

后端 `DELETE /api/knowledge/:id`（`apps/server/src/routes.ts:636`）+ `knowledge.remove()`（`packages/core/src/services/knowledge-service.ts:1899`）**早已完整**——R62 只补前端。改的三个文件：`apps/web/src/App.tsx`、`api.ts`、`i18n.ts`；`styles.css` 与后端文件均未动。

## 为什么不做成「裸按钮 + window.confirm」

删除的核心副作用是**「子节点上提到祖父」**——用户点之前无法预判，而它不可逆。后端恰好提供 `dry_run`，正好回答「点下去会发生什么」。所以弹窗展示「将上提 N 个子节点、失效 M 条关系」+ 逐个列出子节点标题（标题比 id 有意义）。`window.confirm` 承载不了这信息量，也无法被自动化断言。

**六-testid 契约**（实现方与验证方靠它对齐，改名即验证失败）：
`knowledge-delete` / `delete-dialog` / `delete-impact` / `delete-children` / `delete-confirm` / `delete-cancel`。选择器**只用 testid 不依赖文案**（文案要 i18n）。

## 两个互为因果的真 bug（R62 最有价值的部分）

**(a) `feedback` 是死的**：它原本只渲染在 `selected` 非空分支，而删除成功恰好 `setSelected(null)` → 切到 `!selected` 分支 → **「已删除 X，N 个子节点已上提」这句唯一的结果反馈永远看不到**。这是实现方写验证脚本前自测抓到的。

**(b) 修好 (a) 后，UI 断言 `[10]` 变红——这是真信号，不是回归**：`[10]` 用 `document.body.innerText.includes(midTitle)` 判「详情区还在显示 mid」，而反馈文案 `已删除「<mid 标题>」…` **本身含 mid 标题**。**它之前能绿，纯粹是因为 (a) 让反馈没渲染出来。**

更麻烦的是它**间歇性**：`setFeedback()` 与 `await reload()` 之间有窗口，抢在反馈渲染前判就绿、之后判就红——同一份代码一次绿一次红。间歇性假阳性比稳定假红更危险（容易被当 flaky 放过）。

修法是**双判据**：
1. 文本判据**限定 `main.detail`**（不用 `body`：侧栏树、聊天面板也可能含该标题），并**克隆后移除 `.feedback`**，把反馈排除在判据之外；
2. **纯结构判据**（更硬）：`knowledge-delete` 按钮只存在于「有选中节点」那一支，它消失就说明详情区确实切走了——**完全不依赖任何文案**。

> **方法论：产品代码不要为了测试好写而改。** `App.tsx` 让「未选中」分支也渲染 feedback 是必须保留的正确设计（否则用户看不到结果），该改的是断言。实现方一度想删掉那处渲染，被拦住了。

## 两处真实竞态

1. **失焦保存打向已删节点**：用户改了正文 → 直接点删除，编辑器失焦触发 `PATCH`，而节点已被软删 → 后端 404 → 前端弹「保存失败」。**删除成功了却报错。** 处理：`deletingIdRef` 存**具体 id**（不是 boolean）——待删节点的保存直接不发；飞行中被删则静默丢弃。**不靠错误码猜**（真删之外的 404 照旧上报）。存 id 而非 boolean 的原因：删完 `setSelected(null)` 后 ref 仍留旧 id，但 `selected?.knowledge_id` 已是别的值，不会误伤后续节点的保存。
2. **过期预检响应又弹窗**：预检飞行中用户按 Esc，响应回来后弹窗自己又弹出来。处理：`deleteSeqRef` 序号令牌，过期响应作废。

`Esc` 监听挂 **`window`** 而不是弹窗上——焦点可能还在正文编辑器里。

## 两个刻意的设计

- `delete-impact` 在 0 子 / 0 关系时**仍输出数字**（「将上提 0 个子节点、失效 0 条关系。」），而不是切成纯文字——契约要求该元素含数字，切文字会让数字断言假红。
- `delete-dialog` **只在 dry_run 返回后才挂载**（`del.phase !== 'precheck'`）——满足「弹窗出现即代表预检已返回」，否则预检期间那个空壳弹窗会让断言假绿。

## 验证脚本

`scripts/verify-r62-delete-ui.mjs`（36 断言，真机 Chrome）+ `scripts/test-r62-delete-api.mjs`（42 断言，真库副本 + `app.inject`）。后者**必须** `node node_modules/tsx/dist/cli.mjs` 跑（import `.ts` 源）。

## 未做（如实记录）

1. **`migrate_relations_to` 未接 UI**：`api.remove()` 已暴露该选项、类型完整，但详情页没有「把关系迁到某节点」入口。删除时关系仍失效（走后端死边语义），弹窗只做文字提示。**未实现、未验证。**
2. **软删无 undo 入口**，只靠弹窗文案告知「可在数据库层恢复」。
3. **真删请求飞行中点遮罩/取消不生效**（避免用户以为取消了但其实删了）；但 **Esc 在 deleting 阶段仍会关弹窗**——已知小不一致（判断依据：「等待中能关掉」优于「锁死 UI」）。
4. `delete-children` 只列**直接**子节点（与后端 `reparented_children` 口径一致；孙辈随父整体上提）。
5. **en 文案只经机器断言**（非空 + 含英文），无母语者校对。
6. **未跑 `pnpm build`**，只验 dev server + typecheck + 真机。

## 删除语义（后端，Lead 实测确认）

子节点上提到祖父；**软删**（行保留 + `deleted_at`，`findById` 过滤 `deleted_at IS NULL`）；顶层节点删除 → 子节点变顶层（`parent_id` → null）；`dry_run` 字节级非变更。返回 `{ok, knowledge_id, reparented_children, affected_relations, migrated_relations, hint, blocked_by_questions, error}`；节点不存在 → 404 `{error:'知识点不存在或已删除'}`；**挂载存活题目 → 409**（见下节「挂载题目不可删除」）。

## 挂载题目不可删除（挂题守卫，R63）

**规则**：节点只要还关联着**存活**题目，就不允许删除；必须先把题目移到别的知识点（挂载归零）才能删。这是对既有删除语义的**硬约束**，所有删除路径（HTTP、批量/MCP、draft-locate）统一生效。

**挂载口径**：只数 `question_knowledge` 关联的、`question.deleted_at IS NULL` 的题。**软删的题不算挂载**（它已不在用户视野里，不该挡住节点删除）。实现为 `QuestionRepository.countByKnowledgeId()`（`packages/core/src/repositories/question-repo.ts`，紧邻 `findByKnowledge`，同样走 JOIN 索引而非全表扫）。

**守卫位置与「前置检查」这个关键坑**：守卫落在 `KnowledgeService.remove()`（`packages/core/src/services/knowledge-service.ts`），因为所有调用方都过它。**在 `remove()` 内部拦截**，而不是在路由里查一次再调——否则每条删除路径都要各自记得查一次，漏一处就漏防。

**`remove()` 的行为**（三分支，顺序很重要）：

1. 节点不存在 → 立即 `{ok:false}`，无守卫问题。
2. `dry_run` → **不拦截**，仍返回 `ok:true`，但回填 `blocked_by_questions` 与 `error`，让预检能看到「现在不可删」。预检的承诺是「数据库一个字节不动」，拦了就违背了它。
3. 真实删除 → 先算挂题数，**>0 就返回 `ok:false` + `blocked_by_questions` + 中文提示，且不做任何写入**（子节点不上提、节点不软删）。**必须先查挂题、再 `reparentChildren` / `softDelete`**——顺序反了就会先改了库再报错，留下半截状态。

**路由层的前置守卫（`apps/server/src/routes.ts`）**：`DELETE /api/knowledge/:id` 里，守卫检查**前置于 `migrate_relations_to`**。这是本改动最关键的一处——否则关系会**先被迁移走**、删除才被拒绝，留下「关系没了、节点还在」的半截状态。做法：进入 handler 先 `remove(id, {dryRun:true})` 拿挂题数，`linked>0 && !dryRun` 直接 **409** + `blocked_by_questions` + `hint`，根本不走到迁移。挂题拒绝返回 **409** 而不是误导的 404「知识点不存在」——404 会让用户以为 id 写错了，实际是「题没挪走」。dry-run 响应额外带 `deletable`（`linked===0`）与针对性提示。

**批量/MCP 路径（`apps/server/src/batch.ts`）**：`case 'delete'` 的 `!r.ok` 分支原本一律抛「知识点不存在」，挂题被拦时会误报。改为先看 `blocked_by_questions>0`，抛真实原因。MCP 的 `akg_delete_knowledge` 即走此路径，故**已自动覆盖**；其工具描述（`packages/shared/src/agent/catalog.ts`）同步补充了「挂载题目的节点不可删除」的说明，让 AI 调用方知道先挪题。

**前端（`apps/web/src`，三处协同）**：
- `api.ts` 的 `req()` 原本只抛后端 `error` 文案，**丢掉结构化信息**。改为把响应体（`error`/`code`/`blocked_by_questions`/`hint`）挂在异常的 `detail` 上、并记 `httpStatus`——后端给的结构化错误不再被抹平。
- `RemoveKnowledgeResult` 类型补 `blocked_by_questions` / `hint`。
- `App.tsx` 删除弹窗：由 `delImpact.blocked_by_questions` 派生 `delBlocked`，挂题时**显示红色警告**（i18n 新增 `delete.blocked`/`delete.blockedHint`/`delete.confirmDisabled`，含 `{n}` 占位）并**禁用确认按钮**（`disabled={delBusy || delBlocked}`，按钮文案切「不可删除」）。**禁用是双保险**：即使用户绕过按钮，真删请求被拒时 `del.error` 也会渲染后端的 409 文案。新增 testid `delete-blocked` 供验证脚本断言。

**验证**：`scripts/test-delete-with-questions.ts`（14 断言，真实库 + 事务回滚，不污染数据）——挂题节点真实删除被拒且**节点仍在库中未被软删、无副作用**；挂题节点 dry-run 可预检且回填计数；空节点删除成功；不存在节点 `ok:false`。改动文件经 `tsc -b` 零报错。

**边界**：本守卫只针对**直接挂题**。节点的**子节点**是否挂题不影响删除（子节点随父整体上提，其题目关系不动）。</think><arg_key>expect</arg_key><arg_value>1
