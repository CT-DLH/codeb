---
covers:
  - distill/agent/semantic_blocks.py
title: Semantic block parser - component table (layer 3)
updated: 2026-11-22
---

# 模块：语义块解析器（semantic_blocks.py）——部件细页表（第3层）

**项目**：codeb
**源码文件**：`distill/agent/semantic_blocks.py`（解析器=ast，6 个语义块）
**第4层语义块索引**：[semantic_blocks.py](../symbols/semantic_blocks.py.md)
**写范围**：`distill/agent/semantic_blocks.py`
**验证命令**：`& "_kbwork\agvenv\Scripts\python.exe" -X utf8 "_kbwork/test_semantic_blocks.py"`

## 职责
用语法树把源码自动拆成语义块（函数/类/方法），替代正则猜边界。Python 用 stdlib `ast`（精确 `end_lineno`）、TS/JS 用 node+`typescript`（精确 `getEnd()`）、其它语言正则回退。提供统一入口 `parse_blocks`，产出 `file_index` 用的索引和 `read_block` 用的块表。

## 适用场景
- 改解析器：新增语言支持、修撞名、修边界、加新块类型。
- `file_index` / `read_block` 行为异常时，先查本模块。
- 想确认某函数精确行号范围（不靠缩进猜）。

## 功能部件

| 部件 key | 类型 | 行号 | 作用 |
|:--|:--|:--|:--|
| `_ts_blocks@81` | def | L81-110 | TS/TSX/JS/JSX 解析（node + typescript） |
| `_py_blocks@114` | def | L114-146 | Python 解析（stdlib ast，精确 end_lineno） |
| `walk@124` | def | L124-143 | ast 节点遍历，构造作用域前缀 |
| `_fallback_blocks@158` | def | L158-166 | 其它语言正则回退 |
| `parse_blocks@170` | def | L170-183 | 统一入口，分发 parser，返回 (blocks, parser) |
| `format_index@186` | def | L186-201 | 渲染索引（页表输出） |

## 测试文件
- `_kbwork/test_semantic_blocks.py`（12/0，覆盖 ast、TS 解析器、作用域前缀、精确方法边界）

## 下沉指引
```
选中部件 → 打开第4层 semantic_blocks.py.md → read_block(path="distill/agent/semantic_blocks.py", key="parse_blocks@170")
```
