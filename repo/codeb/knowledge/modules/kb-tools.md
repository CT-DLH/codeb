---
covers:
  - kb.py
title: KB tools - component table (layer 3)
updated: 2026-11-22
---

# 模块：KB 工具链（kb.py）——部件细页表（第3层）

**项目**：codeb
**源码文件**：`kb.py`（约 2384 行，解析器=ast，68 个语义块）
**第4层语义块索引**：[kb.py](../symbols/kb.py.md)
**写范围**：`kb.py`（不得碰 `packages/**`、`apps/**`）
**验证命令**：`powershell -NoProfile -ExecutionPolicy Bypass -File _kbwork/run_regression.ps1`

## 职责
实现 codeb 的只读命令行内核：把 `repo/` 下的 Markdown 知识页与源码文件按预算装订成 agent 可读的上下文包（`kb pack`），提供目录树、检索、反查、计划、派发、代理命令。stdlib-only，不依赖外部包。

## 适用场景
- 在 `kb.py` 加/改命令（`tree/read/search/where/graph/plan/pack/dispatch/agent/init/upsert`）。
- 改 `kb pack` 的预算分配、索引层、知识层装配（尤其 `--index` 从源头只装语义块索引）。
- 确认某知识页覆盖哪些源码（`kb where`）、两写范围是否冲突（`kb dispatch`）。

## 功能部件（核心）

| 部件 key | 类型 | 行号 | 作用 |
|:--|:--|:--|:--|
| `_source_index_block@1145` | def | L1145-1185 | 源码语义块索引（subprocess 调 semantic_blocks.py） |
| `render_source@1188` | def | L1188-1216 | 单文件源码装订（全文/大纲/索引） |
| `file_outline@1124` | def | L1124-1135 | 单文件大纲提取（第4层兜底） |
| `cmd_pack@1297` | def | L1297-1467 | `kb pack` 命令入口（--index/--budget/--no-source） |
| `cmd_agent@1470` | def | L1470-1538 | `kb agent` 命令入口（single/plan 模式） |
| `cmd_dispatch@1670` | def | L1670-1826 | `kb dispatch` 写范围检查 |
| `cmd_where@1829` | def | L1829-1853 | `kb where` 源码→知识页反查 |
| `cmd_tree@380` | def | L380-499 | `kb tree` 目录树 |
| `cmd_read@502` | def | L502-540 | `kb read` 读页（可指定 section） |
| `cmd_search@561` | def | L561-590 | `kb search` 全库搜词 |
| `cmd_plan@818` | def | L818-898 | `kb plan` 计划读取 |
| `cmd_upsert@2043` | def | L2043-2054 | `kb upsert` 写知识库入口 |
| `build_parser@2236` | def | L2236-2350 | argparse 命令定义 |
| `main@2361` | def | L2361-2383 | 入口 |

## 测试文件
- `_kbwork/test_block_index.py`（13/0，块索引）
- `_kbwork/test_index_mode_e2e.py`（5/0，真实 LLM，--index 端到端）

## 下沉指引
```
选中部件 → 打开第4层 kb.py.md → 确认精确行号 → read_block(path="kb.py", key="cmd_pack@1297")
```
