---
covers:
  - collector/refs/oa.py
title: Semantic block index: oa.py (layer 4)
updated: 2026-11-24
---

# 语义块索引：oa.py（第4层）

**源码文件**：`collector/refs/oa.py`  
**解析器**：`ast`  
**第5层完整正文**：`read_block(path="collector/refs/oa.py", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| doi_of@20 | def | L20-26 |  | def doi_of(url: str) -> str: |
| _get@29 | def | L29-34 |  | def _get(url: str, api_key: str = "") -> dict: |
| locations@37 | def | L37-67 | DOI → {"pdf_url","oa_url","is_oa"}。查不到的 DOI 不出现在结果里（不猜）。 | def locations(dois: list[str], api_key: str = "", sleep: float = 1.0, |
| d_ok@70 | def | L70-71 |  | def d_ok(value: str) -> bool: |
| links_for@74 | def | L74-77 | 单篇（少量条目用）；批量请走 locations()。 | def links_for(url: str, api_key: str = "") -> dict: |
