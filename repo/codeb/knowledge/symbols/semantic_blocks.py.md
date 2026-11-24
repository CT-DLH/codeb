---
covers:
  - distill/agent/semantic_blocks.py
title: semantic_blocks.py semantic block index (layer 4)
updated: 2026-11-22
---

# 语义块索引：semantic_blocks.py（第4层）

**源码文件**：`distill/agent/semantic_blocks.py`（解析器=ast，6 个语义块）
**第5层完整正文**：`read_block(path="distill/agent/semantic_blocks.py", key="<name>@<line>")`

| 语义块 key | 类型 | 行号 | 作用 |
|:--|:--|:--|:--|
| `_ts_blocks@81` | def | L81-110 | TS/TSX/JS/JSX 解析（node + typescript） |
| `_py_blocks@114` | def | L114-146 | Python 解析（stdlib ast，精确 end_lineno） |
| `walk@124` | def | L124-143 | ast 节点遍历，构造作用域前缀 |
| `_fallback_blocks@158` | def | L158-166 | 其它语言正则回退 |
| `parse_blocks@170` | def | L170-183 | 统一入口，返回 (blocks, parser) |
| `format_index@186` | def | L186-201 | 渲染索引（页表输出） |

**说明**：本文件自身的 Python 解析用 stdlib `ast`，是虚拟内存“页表”的生成器。
