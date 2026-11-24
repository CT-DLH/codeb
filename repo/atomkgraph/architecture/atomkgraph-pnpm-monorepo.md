---
covers:
  - package.json
  - apps/server/src/routes.ts
  - packages/core/src/services/
  - packages/graph-engine/
  - apps/web/src/api.ts
  - apps/web/src/i18n.ts
  - apps/mcp/
  - pnpm-workspace.yaml
updated: 2026-11-18
title: AtomKGraph: pnpm monorepo and its two frontends
---

# AtomKGraph: pnpm monorepo 与两个前端形态

五包 pnpm monorepo。四包有 tsconfig（用 `npx tsc -p apps/{web,server,mcp,cli}/tsconfig.json --noEmit`），`packages/core` **没有** tsconfig——`packages/core/src` 直接 import `.ts` 源，跑测试要 `node node_modules/tsx/dist/cli.mjs`。Node v24.14.1，Windows + pwsh。

## 包职责

- `packages/shared`：纯类型与常量，被其余包依赖。
- `packages/core`：领域逻辑全在这里——services（`knowledge-service`、`relation-service`、`question-service`、`export-service`…）、repositories（SQLite）、`ingest/`（题目/知识点导入：`unified.ts`、`apply.ts`、`paper-plan.ts`）。**不碰 HTTP，不碰 DOM。**
- `packages/graph-engine`：图数据结构（领土/地形/等高线三种视图）。
- `apps/server`：Fastify HTTP API + 托管前端构建产物。`src/routes.ts` 是全部路由（单文件，~2500 行）。**生产后端 3939 托管的是 `apps/web/dist` 里已构建的 bundle。**
- `apps/web`：React + Tailwind（Vite）。`src/api.ts` 是类型化 API client，`src/i18n.ts` 中英字典，`src/App.tsx` 主壳 + 详情视图。
- `apps/mcp`：12 个 MCP 工具，与 `packages/core` 侧 `chat-service` 的 `AGENT_TOOLS` 共享一个工具目录（`app.inject`），`verify-agent-parity.mjs` 三方比对保持一致。

## 端口与两个前端形态

| 端口 | 是什么 |
|---|---|
| 3939 | 生产后端，托管 `apps/web/dist` 的 **已构建** bundle。改前端源码**不会**出现在这里。 |
| 5199 | vite dev server，**改前端源码立即生效**。`/api` 代理到 3939。UI 验证脚本都用这个。 |

vite dev 必须加 `--host 127.0.0.1`——vite 默认只绑 IPv6 `::1`，而既有脚本都用 `127.0.0.1`，不显式指定会连不上。

## 两个容易踩的坑

1. **中文乱码是显示层的**：pwsh console 里中文 mojibake，但磁盘上文件是正确的 UTF-8。写文件时带 `-Encoding UTF8` 读，别因为 console 乱码就以为文件坏了。
2. **PowerShell inline `-e` 引号嵌套必然出事**：嵌套引号触发 `ParserError`。永远先写 `.ts`/`.mjs` 文件再 `node` 跑，不要 `pwsh -Command '...-e "..."...'` 内联。

## 测试组织

- `scripts/test-*.ts`（46 个，`packages/core` 层，用 tsx 跑）+ `scripts/verify-*.mjs`（HTTP/真机层）。
- 变异脚本 `mutate-rXX.mjs`：验证每个新功能都要证明「该红的红、不该红的不红」。
- `apps/mcp/verify-protocol.mjs`（协议握手）+ `verify-agent-parity.mjs`（工具面 parity）。
