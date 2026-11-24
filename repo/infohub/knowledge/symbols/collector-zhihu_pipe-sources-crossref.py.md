---
covers:
  - collector/zhihu_pipe/sources/crossref.py
title: Semantic block index: crossref.py (layer 4)
updated: 2026-11-24
---

# 语义块索引：crossref.py（第4层）

**源码文件**：`collector/zhihu_pipe/sources/crossref.py`  
**解析器**：`ast`  
**第5层完整正文**：`read_block(path="collector/zhihu_pipe/sources/crossref.py", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| _year@26 | def | L26-31 |  | def _year(msg: dict) -> int: |
| _authors@34 | def | L34-40 |  | def _authors(msg: dict) -> list[str]: |
| CrossrefSource@43 | class | L43-147 |  | class CrossrefSource(AcademicSource): |
| CrossrefSource._params@73 | def | L73-78 | ---------------------------------------------------------------- 传输 | def _params(self, extra: dict) -> dict: |
| CrossrefSource._search@82 | def | L82-93 | ---------------------------------------------------------------- 协议 | def _search(self, query: str, limit: int, cursor: str \| None) -> Sear… |
| CrossrefSource._parse@95 | def | L95-121 |  | def _parse(self, w: dict) -> Item \| None: |
| CrossrefSource._fetch_item@123 | def | L123-129 |  | def _fetch_item(self, content_id: str) -> Item: |
| CrossrefSource._ident_from_url@131 | def | L131-133 |  | def _ident_from_url(self, url: str) -> str: |
| CrossrefSource.canonicalize@135 | def | L135-138 | DOI 不区分大小写，统一成小写 doi.org 链接——这是跨源合并的主键。 | def canonicalize(self, url: str) -> str: |
| CrossrefSource.health@140 | def | L140-147 |  | def health(self) -> Health: |
