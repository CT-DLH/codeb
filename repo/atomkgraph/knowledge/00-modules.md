---
covers:
  - packages/**
  - apps/**
title: atomkgraph module navigation (layer 2)
updated: 2026-11-22
---

# atomkgraph 项目模块导航（第2层页表）

> 进入 atomkgraph 项目后先读本页：列出该项目内部的模块。
> 每个模块指向第3层部件细页表（部分模块的部件级拆分待后续补充）。

## 模块列表

| 模块 | 源码范围 | 知识页 | 第3层部件细页表 | 状态 |
|:--|:--|:--|:--|:--|
| 评论与回复 | `packages/shared/src/types.ts`、`packages/core/src/db/connection.ts`、`packages/core/src/repositories/comment-repo.ts`、`packages/core/src/services/comment-service.ts`、`apps/server/src/routes.ts`、`apps/web/src/components/CommentPanel.tsx` | [comment-panel-and-reply-gap](comment-panel-and-reply-gap.md)、[comment-reply-feature](comment-reply-feature.md) | [comment-reply](modules/comment-reply.md) | 有效 |
| 侧边栏拖拽排序 | `apps/web/src/components/Sidebar.tsx`、`apps/web/src/api.ts` | [sidebar-tree-drag-sort-backend-already-ready-frontend-wiring](knowledge/sidebar-tree-drag-sort-backend-already-ready-frontend-wiring.md) | [sidebar-drag-sort](modules/sidebar-drag-sort.md) | 有效 |
| 核心图与复习 | `packages/core/**`、`apps/server/src/routes.ts` | [knowledge-relation-first-then-enrich](knowledge-relation-first-then-enrich.md)、[review-sm2-and-progress](review-sm2-and-progress.md) | （待建） | 有效 |
| Web 前端 | `apps/web/src/**` | [web-build-and-dev-commands](web-build-and-dev-commands.md) | （待建） | 有效 |

## 第4层语义块索引

`symbols/` 下共 **388** 个符号索引页、**3230** 个语义块，全部由
`distill/agent/semantic_blocks.py` 解析生成（TS/TSX 用 TypeScript compiler API），
key 与行号精确到源码真实位置。

**用途列**：块表新增「用途」列，内容取自源码的 JSDoc / 紧邻 `//` 注释首句，
覆盖率 **40%**；取不到的留空，**不拿签名冒充**（签名单独成列）。

按目录的块分布：

| 范围 | 块数 |
|:--|--:|
| `packages/core/**` | 1533 |
| `apps/web/**` | 335 |
| `packages/graph-engine/**` | 132 |
| `packages/shared/**` | 131 |
| `apps/mcp/**` | 61 |
| `apps/server/**` | 44 |
| `scripts/ocr/**` | 37 |
| `apps/cli/**` | 13 |

`node_modules`、`dist/`、`.turbo/` 等依赖与构建产物由 [`repo/.kbignore`](../../.kbignore) 排除，
已在索引中核验无混入。

## 查找流程

```
本页 → 选中模块 → 打开对应第3层部件细页表（或直接读上方知识页）
    → 选中部件 → 打开第4层语义块索引（看「用途」列判断是不是要找的）
    → 选中语义块 → read_block 调入第5层完整正文
```

**查用途**：`python -X utf8 kb.py blocks --name <关键词> --purpose`

**写范围**：默认 `packages/**`、`apps/**`。改前端前先跑 `npx tsc -p apps/web/tsconfig.json --noEmit`，改后端前先跑 `npx tsc -p apps/server/tsconfig.json --noEmit`。
**验证命令**：`npx tsc -p <project>/tsconfig.json --noEmit`、`pnpm --filter @atomkgraph/web build`。
