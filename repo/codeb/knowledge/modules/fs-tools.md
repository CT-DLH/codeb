---
covers:
  - distill/agent/tools_fs.py
title: Filesystem tools - component table (layer 3)
updated: 2026-11-22
---

# 模块：文件系统工具层（tools_fs.py）——部件细页表（第3层）

**项目**：codeb
**源码文件**：`distill/agent/tools_fs.py`（解析器=ast，17 个语义块）
**第4层语义块索引**：[tools_fs.py](../symbols/tools_fs.py.md)
**写范围**：`distill/agent/tools_fs.py`（权限层 enforce allow/deny）
**验证命令**：`& "_kbwork\agvenv\Scripts\python.exe" -X utf8 "_kbwork/test_tools_fs.py"`

## 职责
给子 agent 提供文件系统工具，是虚拟内存的“缺页中断”执行器。`file_index` 委托 `semantic_blocks.parse_blocks` 拿语义块页表，`read_block` 用精确 `start-end` 调入块正文；`edit_file`/`write_file`/`append_file` 在工具层做白名单/黑名单校验。

## 适用场景
- 改工具行为：增/改工具、改权限模型（`ROOTS`/`DENY_PATTERNS`）、修 `read_block` 边界匹配。
- 调 `file_index`/`read_block` 行为：如报“定位不到”、越界，先查本模块。
- 确认某路径是否在白名单内（`resolve`/`_check_allowed`）。

## 功能部件

| 部件 key | 类型 | 行号 | 作用 |
|:--|:--|:--|:--|
| `resolve@44` | def | L44-62 | 路径解析与归一化 |
| `_denied@65` | def | L65-67 | 黑名单判定 |
| `_read@70` | def | L70-72 | 底层行读取 |
| `file_index@106` | def | L106-132 | 语义块索引（委托 parse_blocks+format_index） |
| `read_block@135` | def | L135-177 | 按需调入精确 start-end 块 |
| `read_file@180` | def | L180-198 | 读文件（默认 150 行） |
| `read_file_range@201` | def | L201-211 | 按行区间读 |
| `list_dir@214` | def | L214-234 | 列目录 |
| `grep_text@237` | def | L237-265 | 内容搜索 |
| `_check_allowed@268` | def | L268-292 | 写操作白名单校验 |
| `_match_any@295` | def | L295-311 | 路径模式匹配 |
| `edit_file@314` | def | L314-338 | 精确替换（old 逐字符匹配） |
| `write_file@341` | def | L341-352 | 整篇覆盖 |
| `append_file@355` | def | L355-367 | 追加 |
| `run_cmd@370` | def | L370-397 | 跑验证命令 |
| `diff_summary@400` | def | L400-408 | 改动摘要 |

## 测试文件
- `_kbwork/test_tools_fs.py`（25/0）
- `_kbwork/test_block_index.py`（13/0，file_index/read_block）

## 下沉指引
```
选中部件 → 打开第4层 tools_fs.py.md → read_block(path="distill/agent/tools_fs.py", key="read_block@135")
```
