---
covers:
  - scripts/ocr/ocr_pdf.py
title: Semantic block index: ocr_pdf.py (layer 4)
updated: 2026-11-24
---

# 语义块索引：ocr_pdf.py（第4层）

**源码文件**：`scripts/ocr/ocr_pdf.py`  
**解析器**：`ast`  
**第5层完整正文**：`read_block(path="scripts/ocr/ocr_pdf.py", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| log@42 | def | L42-43 |  | def log(msg: str) -> None: |
| parse_pages@46 | def | L46-63 | '1-10,15' → [1..10, 15]（1-based，越界丢弃）。None → 全部。 | def parse_pages(spec: str \| None, total: int) -> list[int]: |
| page_images@66 | def | L66-80 | 取页内嵌位图（PIL Image 列表）。取不到就返回空，不抛。 | def page_images(page: Any) -> list[Any]: |
| to_rgb@83 | def | L83-94 | 统一成 RGB。JP2 解出来可能是 CMYK / 灰度 / 1-bit。 | def to_rgb(im: Any) -> Any: |
| scale_image@97 | def | L97-109 | 长边不足 MIN_LONG_SIDE 时放大，返回 (图, 实际倍数)。 | def scale_image(im: Any, want: float) -> tuple[Any, float]: |
| group_lines@112 | def | L112-144 | 把检测框按阅读顺序排成行。 | def group_lines(items: Iterable[tuple[list[list[float]], str, float]])… |
| ocr_one_page@147 | def | L147-205 |  | def ocr_one_page(engine: Any, page: Any, page_no: int, scale: float, m… |
| page_cache_path@208 | def | L208-211 |  | def page_cache_path(cache_dir: str, page_no: int) -> str: |
| read_page_cache@214 | def | L214-223 | 页级缓存：整本 318 页要跑半小时，中途中断必须能续，不能从第 1 页重来。 | def read_page_cache(cache_dir: str, page_no: int) -> dict \| None: |
| write_page_cache@226 | def | L226-236 |  | def write_page_cache(cache_dir: str, page_no: int, result: dict) -> No… |
| main@239 | def | L239-343 |  | def main() -> int: |
