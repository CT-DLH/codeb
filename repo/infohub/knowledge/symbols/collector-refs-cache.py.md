---
covers:
  - collector/refs/cache.py
title: Semantic block index: cache.py (layer 4)
updated: 2026-11-24
---

# 语义块索引：cache.py（第4层）

**源码文件**：`collector/refs/cache.py`  
**解析器**：`ast`  
**第5层完整正文**：`read_block(path="collector/refs/cache.py", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| default_path@27 | def | L27-30 |  | def default_path() -> Path: |
| LookupCache@33 | class | L33-110 |  | class LookupCache: |
| LookupCache.__init__@34 | def | L34-39 |  | def __init__(self, path: Path \| str \| None = None, readonly: bool = … |
| LookupCache.conn@42 | def | L42-50 |  | def conn(self) -> Iterator[sqlite3.Connection]: |
| LookupCache._init@52 | def | L52-65 |  | def _init(self) -> None: |
| LookupCache.get@67 | def | L67-78 |  | def get(self, key: str) -> Resolved \| None: |
| LookupCache.put@80 | def | L80-104 | 写入/累加尝试次数。缓存里的 DOI 一旦拿到就不被后来的 miss 覆盖。 | def put(self, key: str, res: Resolved) -> None: |
| LookupCache.stats@106 | def | L106-110 |  | def stats(self) -> dict: |
