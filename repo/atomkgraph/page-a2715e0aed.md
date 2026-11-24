---
title: Current plan and known failing tests
---

# 当前计划与已知失败测试：下一步做什么、哪些失败不用管

记录「现在做到哪、下一步该做什么、哪些失败是真 bug」。按优先级排列，每条写清「为什么还没做」或「为什么不用管」。

## 已完成（不用重做）

- **R62 删除前端**：两步预检弹窗，`apps/web/src/{App,api,i18n}.ts`。见 `knowledge/` 下删除页。
- **题目导入 `--from-plan` 三 bug**：见 `knowledge/from-plan`。
- **MCP 工具面 parity**：`apps/mcp` 12 个 action-dispatched 工具与 `packages/core` 侧 chat-service 对齐，`verify-agent-parity.mjs` 全绿。

## 下一步（按用户提的顺序，导出在删除之后）

### 手动导出前端（删除已完成，这是下一个）

**后端早已完整，前端一行都没有**——这是和 R62 删除完全一样的局面：

- `GET /api/export/{json,markdown,pdf}` 三种格式齐全（`export-service.ts` + `routes.ts:~2482`）。
- JSON = 全库备份；Markdown = 可读导出；PDF = 讲义，支持 `pageBreakDepth`/`tocDepth`/`landscape`/`dedupe`。
- 格式矩阵：`questions`（inline/appendix）、`answers`（inline/appendix/exclude）、`refs`、`frontmatter`、`anchors`、`maxDepth`、`rootId`。

**缺的全在前端**：`apps/web/src/api.ts` **没有任何 export 方法**；`apps/web/src` 全域搜「导出|下载|download|/api/export」命中的全是注释——**没有任何按钮或菜单**。`SettingsPanel` 也没有。i18n 没有导出字符串。普通用户目前**够不着**导出功能。

做法可照 R62 删除的模式：先定 `data-testid` 契约 → 实现方与验证方并行 → 变异测试证明脚本敏感。注意 R62 的教训：**先确认后端行为再动手**（删除那次是先用独立探针实测 `dry_run` 语义，才发现后端早已完整、只缺前端）。

## 已知失败测试（判据：是否与本仓库改动相关）

这些**都是既有噪音，不是真 bug**，动手前别被它们误导：

1. **`test-question-view.ts` 20 项失败**：脚本复制**真库**再断言全库总数 = 291，但 2026-11-05 题库录入新增 1 题（`q_1d59b1f66e5e4d0a`，`source='bank'`）使活题变 292 → **20 项全部恰好差 1**。判据很干净：所有失败都差 1，且 `292 − 新建 1 = 291`。**修法**：把硬编码数字改成「先查实际总数再逐项相对断言」，否则每录一道题就红一片。
2. **`test-elevation.ts` `[E3]`**：高层等高线 0 条，确定性失败。`packages/graph-engine` 无未提交改动。
3. **`test-md-roundtrip.ts` 520/545**：嵌套列表缩进丢失。`editor/markdown.ts` 自 R22 起未改动。
4. **`verify-partition-outline.mjs` 6/11**：探针滞后于「凸包→领土」渲染改动。
5. **`verify-perf.mjs` 9/10**：`[3c]` 档位切换计数敏感。
6. **`verify-graph-gesture.mjs`**：缺 `playwright` 依赖，无法运行。
7. **`test-server.ts`**：`assetsDir` 相对路径，HEAD 上同样失败。

## 代码层的已知债（非功能缺口）

1. **`paper-plan.ts` 死代码**：`makePaperOrder`/`PART_ORDER_STRIDE`（span-10000 方案）只被测试引用；生产用 `makeOrderAllocator`（连续整卷计数器）。而文件头注释描述的是 span 方案——**注释与实现不符**，容易误导。建议二选一：删死代码或改注释。
2. **`group-ingest.ts` 不传 `paper`**：多文件试卷组路径**不能创建试卷**（见 `knowledge/from-plan`）。

## 删除功能的三处未做（R62 遗留）

`migrate_relations_to` 未接 UI（`api.remove()` 已暴露但无入口）；软删无 undo 入口；未跑 `pnpm build`。详见 `knowledge/` 删除页的「未做」段。
