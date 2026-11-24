---
covers:
  - collector/tools/selftest_register.py
title: Semantic block index: selftest_register.py (layer 4)
updated: 2026-11-24
---

# 语义块索引：selftest_register.py（第4层）

**源码文件**：`collector/tools/selftest_register.py`  
**解析器**：`ast`  
**第5层完整正文**：`read_block(path="collector/tools/selftest_register.py", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| check@45 | def | L45-52 |  | def check(cond: bool, msg: str) -> None: |
| teacher@63 | def | L63-71 |  | def teacher(slug: str, papers: list[str] \| None = None) -> dict: |
| json_tail@74 | def | L74-82 | collect_site --json 把人话行和 JSON 一起打到 stdout；取顶层那段 JSON。 | def json_tail(text: str) -> dict: |
| main@85 | def | L85-356 |  | def main() -> int: |
| cand@318 | def | L318-319 |  | def cand(url: str, key: str) -> dict: |
