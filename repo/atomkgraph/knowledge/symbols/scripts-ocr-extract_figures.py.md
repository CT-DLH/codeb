---
covers:
  - scripts/ocr/extract_figures.py
title: Semantic block index: extract_figures.py (layer 4)
updated: 2026-11-24
---

# 语义块索引：extract_figures.py（第4层）

**源码文件**：`scripts/ocr/extract_figures.py`  
**解析器**：`ast`  
**第5层完整正文**：`read_block(path="scripts/ocr/extract_figures.py", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| log@38 | def | L38-39 |  | def log(msg: str) -> None: |
| parse_pages@42 | def | L42-56 |  | def parse_pages(spec: str \| None, total: int) -> list[int]: |
| DSU@59 | class | L59-72 |  | class DSU: |
| DSU.__init__@60 | def | L60-61 |  | def __init__(self, n: int) -> None: |
| DSU.find@63 | def | L63-67 |  | def find(self, x: int) -> int: |
| DSU.union@69 | def | L69-72 |  | def union(self, a: int, b: int) -> None: |
| close@75 | def | L75-79 | 两个矩形（含 gap 外扩）是否相交。 | def close(a, b, gap: float) -> bool: |
| union_box@82 | def | L82-83 |  | def union_box(a, b): |
| clamp_box@86 | def | L86-87 |  | def clamp_box(b, rect): |
| raster_region_boxes@90 | def | L90-152 | 整页位图页：涂白文字层 → 非白连通域 → 合并相邻子框 → 候选图区（pt 坐标）。 | def raster_region_boxes(page, page_area, dpi, min_area, max_area, gap_… |
| main@155 | def | L155-428 |  | def main() -> int: |
