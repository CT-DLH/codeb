---
covers:
  - distill/agent/semantic_blocks.py
title: Semantic block index: semantic_blocks.py (layer 4)
updated: 2026-11-24
---

# 语义块索引：semantic_blocks.py（第4层）

**源码文件**：`distill/agent/semantic_blocks.py`  
**解析器**：`ast`  
**第5层完整正文**：`read_block(path="distill/agent/semantic_blocks.py", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| _ts_blocks@109 | def | L109-139 | 用 atomkgraph 的 typescript 包解析 TS/TSX/JS/JSX。 | def _ts_blocks(path: Path) -> list[dict] \| None: |
| _clean_purpose@146 | def | L146-150 | 压成一行、去掉 markdown 重音与多余空白，截到 _PURPOSE_MAX。 | def _clean_purpose(text: str) -> str: |
| _py_blocks@153 | def | L153-225 | 用标准库 ast 解析 Python：精确边界 + 作用域 + 方法列表 + 用途。 | def _py_blocks(path: Path) -> list[dict] \| None: |
| purpose_of@171 | def | L171-200 |  | def purpose_of(node) -> tuple[str, str]: |
| walk@202 | def | L202-222 |  | def walk(node, scope: str) -> None: |
| _fallback_blocks@237 | def | L237-245 |  | def _fallback_blocks(path: Path, lines: list[str]) -> list[dict]: |
| parse_blocks@249 | def | L249-262 | 返回 (块列表, 解析器名)。块已按作用域命名、带精确边界。 | def parse_blocks(path: Path) -> tuple[list[dict], str]: |
| format_index@265 | def | L265-280 | 渲染成 agent 可读的索引。 | def format_index(path: str, blocks: list[dict], parser: str, total: in… |
