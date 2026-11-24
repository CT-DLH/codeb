---
covers:
  - scripts/ocr/extract_office.py
title: Semantic block index: extract_office.py (layer 4)
updated: 2026-11-24
---

# 语义块索引：extract_office.py（第4层）

**源码文件**：`scripts/ocr/extract_office.py`  
**解析器**：`ast`  
**第5层完整正文**：`read_block(path="scripts/ocr/extract_office.py", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| log@33 | def | L33-34 |  | def log(msg: str) -> None: |
| clean@37 | def | L37-39 |  | def clean(text: str) -> str: |
| table_to_md@42 | def | L42-52 |  | def table_to_md(table) -> str: |
| convert_docx@55 | def | L55-97 |  | def convert_docx(path: str) -> tuple[str, int, int, list[str]]: |
| convert_pptx@100 | def | L100-141 |  | def convert_pptx(path: str) -> tuple[str, int, int, list[str]]: |
| main@144 | def | L144-213 |  | def main() -> int: |
