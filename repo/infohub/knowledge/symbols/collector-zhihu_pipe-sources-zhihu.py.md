---
covers:
  - collector/zhihu_pipe/sources/zhihu.py
title: Semantic block index: zhihu.py (layer 4)
updated: 2026-11-24
---

# 语义块索引：zhihu.py（第4层）

**源码文件**：`collector/zhihu_pipe/sources/zhihu.py`  
**解析器**：`ast`  
**第5层完整正文**：`read_block(path="collector/zhihu_pipe/sources/zhihu.py", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| ZhihuSource@21 | class | L21-116 |  | class ZhihuSource: |
| ZhihuSource.__init__@48 | def | L48-50 |  | def __init__(self) -> None: |
| ZhihuSource._to_item@53 | def | L53-70 |  | def _to_item(it: dict) -> Item: |
| ZhihuSource.search@72 | def | L72-79 |  | def search(self, query: str, *, limit: int = 30, cursor: str \| None =… |
| ZhihuSource.list_author@81 | def | L81-91 |  | def list_author(self, author_id: str, *, kinds: Iterable[str] \| None … |
| ZhihuSource.fetch@93 | def | L93-103 |  | def fetch(self, ref: ContentRef) -> Document: |
| ZhihuSource.canonicalize@105 | def | L105-107 |  | def canonicalize(self, url: str) -> str: |
| ZhihuSource.health@109 | def | L109-116 |  | def health(self) -> Health: |
