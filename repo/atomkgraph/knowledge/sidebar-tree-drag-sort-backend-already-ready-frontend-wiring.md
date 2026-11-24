---
covers:
  - apps/web/src/components/Sidebar.tsx
  - apps/web/src/api.ts
  - apps/server/src/routes.ts
  - packages/core/src/repositories/knowledge-repo.ts
  - packages/core/src/services/knowledge-service.ts
  - scripts/e2e-drag-sort.ts
  - scripts/verify-drag-logic.ts
updated: 2026-11-22
---

# Sidebar tree drag-sort: backend already ready, frontend wiring and the getData trap

侧栏目录树的拖拽手动排序。**侦察结论：后端早就完全就绪，缺口全在前端。**
改这个功能前先读这一页，能省掉一遍 grep。

## Sidebar.tsx 侦察结果（行号是当时的，改完要复核）

| 能力 | 位置 | 状态 |
| :-- | :-- | :-- |
| `POST /api/knowledge/:id/move` | `apps/server/src/routes.ts:549` | 已支持 `before_id` / `after_id` / `parent_id` |
| `setSortOrder()` | `packages/core/src/repositories/knowledge-repo.ts:336` | 只改 sort_order，不动 edit_count/content_hash |
| `SORT_ORDER_STEP = 10` | `packages/core/src/services/knowledge-service.ts:113` | 稀疏约定 10/20/30 |
| 排序锚点逻辑 | `knowledge-service.ts:1564` | `before_id`/`after_id` 会覆盖显式 sort_order |
| 树接口 | `/api/knowledge/tree` | 返回 `{knowledge, children}` 数组 |

**坑**：`/api/knowledge?tree=1` 返回的是**扁平全量列表**，不是树。
写 e2e 时用错这个接口会报 `Cannot read properties of undefined`。

## Sidebar.tsx 拖拽语义契约（leader 必须在派发前定稿）

1. **同级拖拽 = 纯排序**：请求体**只带 `before_id` 或 `after_id`，不带 `parent_id`**。带 `parent_id` 后端会当移动节点。
2. **跨级拖拽 = reparent，是另一个语义，不做**。`handleDrop` 里必须比对源与目标的 `parent_id`，不等就忽略。
3. **`dragover` 阶段 `dataTransfer.getData()` 返回空串**（浏览器安全限制，只有 `drop` 能读到）。
   判断同级和画插入位置线必须用**模块级变量** `dragSource: { id, parentId } | null`，
   `dragStart` 写入，`dragEnd` / 卸载时清空。用 `getData` 判断会导致提示线永远不显示。
4. **`onReload` 要从 Sidebar 递归传到每个 `TreeNodeView`**，否则 tsc 报
   `Cannot find name 'api' / 'onReload'`。这是上次子 agent 漏掉的数据通路。

## 拆任务方式（4 个，同一文件靠 depends_on 串行）

```
w0-types        api.ts 加 moveKnowledge              → tsc 0
w1-tree-props   import api + onReload 递归传参        → tsc 0
w2-drag-state   dragSource + 2 state + 卸载清理        → tsc 0
w3-drag-handlers 5 个 handleDrag* + 绑 DOM + 视觉反馈  → tsc 0
```

按**决策性质**拆，不按文件大小拆。每个任务以 `tsc --noEmit` 退出码 0 为完成标准。
计划文件在 `_kbwork/plan-sidebar-split.json`（已验证拓扑，未实际派发）。

**注意**：后三个任务写同一个文件，不能靠 `kb dispatch` 互斥，靠 `depends_on` 串行。

## 实现状态与验证

功能已实现（w1 子 agent 做了 API 层，UI 层由 leader 补完），验证全绿：

- `npx tsc -p apps/web/tsconfig.json --noEmit` → 0
- `pnpm --filter @atomkgraph/web build` → 0（9.00s）
- `scripts/e2e-drag-sort.ts` → **7 通过 / 0**：move(after_id) 得 `BBB,CCC,AAA`；move(before_id) 得 `AAA,BBB,CCC`；sort_order `10,20,30`
- `scripts/verify-drag-logic.ts` → **17 通过 / 0**：同级判断 + before/after 判定 + 参数名
- 组件渲染 → 8 通过 / 0：`draggable="true"` 出现 3 次

**未验证**：浏览器里真实鼠标拖拽（无 playwright/puppeteer）。DOM 属性、判断逻辑、后端链路各自验证过，
但拼起来的完整交互只能手动点。
