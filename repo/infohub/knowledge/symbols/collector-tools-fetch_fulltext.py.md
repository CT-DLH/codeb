---
covers:
  - collector/tools/fetch_fulltext.py
title: Semantic block index: fetch_fulltext.py (layer 4)
updated: 2026-11-24
---

# 语义块索引：fetch_fulltext.py（第4层）

**源码文件**：`collector/tools/fetch_fulltext.py`  
**解析器**：`ast`  
**第5层完整正文**：`read_block(path="collector/tools/fetch_fulltext.py", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| candidates@42 | def | L42-52 |  | def candidates(store: Store, sources: list[str]) -> list[dict]: |
| body_of@55 | def | L55-57 |  | def body_of(path: Path) -> str: |
| links_of@60 | def | L60-73 | 库里的 assets 优先；没有就用 OA 位置。顺序：PDF 在前，落地页在后。 | def links_of(row: dict, oa: dict) -> list[str]: |
| _apply_one@76 | def | L76-108 | 下载 → 抽文 → 追加进正文 → 重算摘要。任何一步失败就抛，由调用方按条隔离。 | def _apply_one(store: Store, data_dir: Path, row: dict, links: list[st… |
| main@111 | def | L111-195 |  | def main(argv: list[str] \| None = None) -> int: |
