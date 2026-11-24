---
covers:
  - kb.py
  - distill/agent/semantic_blocks.py
  - distill/agent/tools_fs.py
  - distill/agent/codeb_agent.py
  - distill/agent/context_cache.py
  - mcp/server.ts
title: codeb five-layer page-table navigation
updated: 2026-11-22
---

# codeb 五级页表导航

codeb 项目的页表体系按多级页表组织，**越往下页表文件越多、粒度越细**，最终落到单个源码语义块。执行操作不属页表，单独在 `tasks/`。

## 五级结构

| 层级 | 名称 | 粒度 | codeb 落地 | 文件数 |
|:--|:--|:--|:--|:--|
| 第1层 | 项目索引 | 项目 | [`repo/00-projects.md`](../../00-projects.md) | 1 |
| 第2层 | 模块导航 | 模块 | [`codeb/knowledge/00-modules.md`](00-modules.md) | 1 |
| 第3层 | 部件细页表 | 模块内部件 | [`codeb/knowledge/modules/*.md`](modules/) | 6 |
| 第4层 | 语义块索引 | 源码文件内语义块 | [`codeb/knowledge/symbols/*.md`](symbols/) | 6 |
| 第5层 | 完整源码页帧 | 单个语义块正文 | 不落盘，`read_block(path, key)` 运行时调入 | 0 |

## 跨层跳转链

```
第1层 00-projects.md
   └─> 第2层 codeb/knowledge/00-modules.md（6 个模块）
         ├─> 第3层 modules/kb-tools.md          → 第4层 symbols/kb.py.md
         ├─> 第3层 modules/semantic-parser.md   → 第4层 symbols/semantic_blocks.py.md
         ├─> 第3层 modules/fs-tools.md          → 第4层 symbols/tools_fs.py.md
         ├─> 第3层 modules/agent-exec.md        → 第4层 symbols/codeb_agent.py.md
         ├─> 第3层 modules/context-cache.md     → 第4层 symbols/context_cache.py.md
         └─> 第3层 modules/mcp-server.md        → 第4层 symbols/mcp-server.ts.md
```

## 标准查找流程

```
需求 → 第1层选项目 → 第2层选模块 → 第3层选部件 → 第4层确认精确行号
     → read_block 调入第5层完整正文 → 按 tasks/ 任务清单执行改码与验证
```

## 执行层（非页表）

- 任务清单模板：[`tasks/_template.md`](tasks/_template.md)
- 示例任务：[`tasks/fix-render-deps.task.md`](tasks/fix-render-deps.task.md)

**原则**：页表只负责“定位与映射”；`edit_file`/`write_file`/`run_cmd` 等执行操作归任务清单，由 leader 派发。

## 维护规则

- 第3/4层的语义块 key 与行号来自 `semantic_blocks.py` 的语法树解析（ast / typescript / regex-fallback）。
- 源码改动后，若行号或签名变化，**必须同步更新第3层与第4层**，否则 `read_block` 找不到对应行号。
- 新增模块时，在第2层 `00-modules.md` 追加一行，并新建对应第3层页表。
