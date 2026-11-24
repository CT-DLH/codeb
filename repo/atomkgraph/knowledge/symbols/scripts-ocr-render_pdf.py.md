---
covers:
  - scripts/ocr/render_pdf.py
title: Semantic block index: render_pdf.py (layer 4)
updated: 2026-11-24
---

# 语义块索引：render_pdf.py（第4层）

**源码文件**：`scripts/ocr/render_pdf.py`  
**解析器**：`ast`  
**第5层完整正文**：`read_block(path="scripts/ocr/render_pdf.py", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| log@33 | def | L33-34 |  | def log(msg: str) -> None: |
| parse_pages@37 | def | L37-52 | '1-10,15' → [1..10, 15]（1-based，越界丢弃）。None → 全部。 | def parse_pages(spec: str \| None, total: int) -> list[int]: |
| main@55 | def | L55-110 |  | def main() -> int: |
