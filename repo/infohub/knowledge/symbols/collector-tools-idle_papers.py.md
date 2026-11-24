---
covers:
  - collector/tools/idle_papers.py
title: Semantic block index: idle_papers.py (layer 4)
updated: 2026-11-24
---

# 语义块索引：idle_papers.py（第4层）

**源码文件**：`collector/tools/idle_papers.py`  
**解析器**：`ast`  
**第5层完整正文**：`read_block(path="collector/tools/idle_papers.py", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| is_paper@42 | def | L42-45 |  | def is_paper(row: dict) -> bool: |
| summary_backend@48 | def | L48-55 | 这篇摘要是哪个后端产的——只读库里的 summary_backend 列。 | def summary_backend(row: dict) -> str: |
| done_rows@58 | def | L58-66 | 已经用 llm 总结过的论文行——只给 --redo-sample 用（验证提示词改动，不动待办口径）。 | def done_rows(store: Store, data_dir: Path) -> list[dict]: |
| pending_rows@69 | def | L69-81 |  | def pending_rows(store: Store, data_dir: Path, redo_extract: bool = Fa… |
| summarize_one@84 | def | L84-106 |  | def summarize_one(store: Store, data_dir: Path, s: Summarizer, row: di… |
| main@109 | def | L109-200 |  | def main() -> int: |
