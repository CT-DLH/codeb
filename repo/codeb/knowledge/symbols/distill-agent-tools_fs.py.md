---
covers:
  - distill/agent/tools_fs.py
title: Semantic block index: tools_fs.py (layer 4)
updated: 2026-11-24
---

# 语义块索引：tools_fs.py（第4层）

**源码文件**：`distill/agent/tools_fs.py`  
**解析器**：`ast`  
**第5层完整正文**：`read_block(path="distill/agent/tools_fs.py", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| resolve@44 | def | L44-62 | 把 agent 给的相对路径解析到某个仓库根下；跨根或越界返回 None。 | def resolve(path: str, root: str) -> Path \| None: |
| _denied@65 | def | L65-67 |  | def _denied(path: str) -> bool: |
| _read@70 | def | L70-72 | 内部实现：不做根解析，供 read_file / edit_file 共用。 | def _read(path: str, max_lines: int) -> str: |
| _sig_info@96 | def | L96-103 | 返回 (indent, name) 或 None。集中处理两个分支，避免调用方重复。 | def _sig_info(line: str): |
| file_index@106 | def | L106-132 | 给一个代码文件建语义块索引：每块一行 key:行号:签名。 | def file_index(path: str, root: str = "infohub") -> str: |
| read_block@135 | def | L135-177 | 按 file_index 给的 key 取一个语义块的完整正文（缺页中断）。 | def read_block(path: str, key: str, root: str = "infohub") -> str: |
| read_file@180 | def | L180-198 | 读一个文件，返回前 max_lines 行，并附总行数。 | def read_file(path: str, max_lines: int = 150, root: str = "infohub") … |
| read_file_range@201 | def | L201-211 | 从 offset（1 起）读一段，用于读大文件的中段。 | def read_file_range(path: str, offset: int, limit: int = 150, root: st… |
| list_dir@214 | def | L214-234 | 列目录（单层），带文件大小。 | def list_dir(path: str = ".", pattern: str = "*", root: str = "infohub… |
| grep_text@237 | def | L237-265 | 在目录下搜字符串（子串匹配），返回 路径:行号:内容。 | def grep_text(pattern: str, path: str = ".", max_hits: int = 20, root:… |
| _check_allowed@268 | def | L268-292 | 返回 None 表示可写；否则返回拒绝原因。 | def _check_allowed(path: str, root: str, allowed: list[str], denied: l… |
| _match_any@295 | def | L295-311 | 判断相对路径是否命中任一模式。 | def _match_any(rel: str, patterns: list[str]) -> bool: |
| _snapshot_dir@324 | def | L324-327 | 某个文件的快照目录（路径 hash，避免目录名里有斜杠）。 | def _snapshot_dir(path: str, root: str) -> Path: |
| _snapshot@330 | def | L330-343 | 写前存原文快照，返回 snapshot_id；文件不存在返回 None。 | def _snapshot(path: str, root: str) -> str \| None: |
| rollback_file@346 | def | L346-371 | 把文件恢复到某次写前的原文。不传 snapshot_id 就取最近一次快照。 | def rollback_file(path: str, root: str = "infohub", |
| snap_list@374 | def | L374-380 | 列出某文件的所有快照 id（最新在后）。 | def snap_list(path: str, root: str = "infohub") -> str: |
| edit_file@383 | def | L383-408 | 在文件里把 old 字面替换成 new。 | def edit_file(path: str, old: str, new: str, root: str = "infohub", |
| write_file@411 | def | L411-424 | 新建或整篇覆盖一个文件。 | def write_file(path: str, content: str, root: str = "infohub", |
| append_file@427 | def | L427-440 | 往文件末尾追加（自动空行分隔）。 | def append_file(path: str, content: str, root: str = "infohub", |
| run_cmd@443 | def | L443-470 | 在仓库里跑一条命令，返回退出码与输出。 | def run_cmd(cmd: str, root: str = "infohub", cwd: str = ".", |
| diff_summary@473 | def | L473-481 | 读一个文件的行数与首尾几行，用于报告「改了什么」。 | def diff_summary(path: str, root: str = "infohub") -> str: |
