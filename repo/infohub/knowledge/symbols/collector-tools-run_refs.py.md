---
covers:
  - collector/tools/run_refs.py
title: Semantic block index: run_refs.py (layer 4)
updated: 2026-11-24
---

# 语义块索引：run_refs.py（第4层）

**源码文件**：`collector/tools/run_refs.py`  
**解析器**：`ast`  
**第5层完整正文**：`read_block(path="collector/tools/run_refs.py", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| _coverage@43 | def | L43-44 |  | def _coverage(entries) -> Counter: |
| _report@47 | def | L47-59 |  | def _report(entries, resolved: bool = False) -> dict: |
| _tool@62 | def | L62-69 | 进程内调用另一个采集器工具（同一套插件注册与状态机，不复制逻辑）。 | def _tool(script: str, argv: list[str]) -> int: |
| main@72 | def | L72-192 |  | def main(argv: list[str] \| None = None) -> int: |
