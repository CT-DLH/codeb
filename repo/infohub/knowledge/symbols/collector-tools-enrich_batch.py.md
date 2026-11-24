---
covers:
  - collector/tools/enrich_batch.py
title: Semantic block index: enrich_batch.py (layer 4)
updated: 2026-11-24
---

# 语义块索引：enrich_batch.py（第4层）

**源码文件**：`collector/tools/enrich_batch.py`  
**解析器**：`ast`  
**第5层完整正文**：`read_block(path="collector/tools/enrich_batch.py", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| _ref_of@53 | def | L53-59 |  | def _ref_of(entry: dict) -> ContentRef: |
| _item_of@62 | def | L62-76 | 把卡片上的元数据还原成 Item，只为落盘时 front matter 不丢字段。 | def _item_of(entry: dict) -> Item: |
| _audience_section@79 | def | L79-120 | 抓观众反馈 → LLM 归纳 → 渲染成 ## 观众反馈 一节。 | def _audience_section(src, ref: ContentRef, item: Item, result: dict) … |
| _entries_from_store@123 | def | L123-150 | 按 URL 从库里取已登记的行，还原成与卡片计划同形状的条目。 | def _entries_from_store(store: Store, source_name: str, urls: list[str… |
| main@153 | def | L153-412 |  | def main(argv: list[str] \| None = None) -> int: |
