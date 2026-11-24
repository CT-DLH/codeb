---
covers:
  - collector/tools/enrich_queue.py
title: Semantic block index: enrich_queue.py (layer 4)
updated: 2026-11-24
---

# 语义块索引：enrich_queue.py（第4层）

**源码文件**：`collector/tools/enrich_queue.py`  
**解析器**：`ast`  
**第5层完整正文**：`read_block(path="collector/tools/enrich_queue.py", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| fetchable_platforms@42 | def | L42-51 | (可取正文的集合, 确认没有 body 能力的集合)。 | def fetchable_platforms(report: dict) -> tuple[set[str], set[str]]: |
| explain@54 | def | L54-81 | 返回 (人类可读原因, 可判死的 reason code 或空串)。 | def explain(row: dict \| None, report: dict, no_body: set[str], retry:… |
| entry@84 | def | L84-101 | 队列行 → enrich_batch 吃的计划条目。字段全取自库，不在 TS 侧再解析一次日期。 | def entry(row: dict, card_id: str) -> dict: |
| main@104 | def | L104-222 |  | def main(argv: list[str] \| None = None) -> int: |
