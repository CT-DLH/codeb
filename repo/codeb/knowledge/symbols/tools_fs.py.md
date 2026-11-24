---
covers:
  - distill/agent/tools_fs.py
title: tools_fs.py semantic block index (layer 4)
updated: 2026-11-22
---

# 语义块索引：tools_fs.py（第4层）

**源码文件**：`distill/agent/tools_fs.py`（解析器=ast，17 个语义块）
**第5层完整正文**：`read_block(path="distill/agent/tools_fs.py", key="<name>@<line>")`

| 语义块 key | 类型 | 行号 | 作用 |
|:--|:--|:--|:--|
| `resolve@44` | def | L44-62 | 路径解析与归一化 |
| `_denied@65` | def | L65-67 | 黑名单判定 |
| `_read@70` | def | L70-72 | 底层行读取 |
| `_sig_info@96` | def | L96-103 | 签名信息 |
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
