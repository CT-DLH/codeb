---
covers:
  - distill/agent/context_cache.py
title: Semantic block index: context_cache.py (layer 4)
updated: 2026-11-24
---

# 语义块索引：context_cache.py（第4层）

**源码文件**：`distill/agent/context_cache.py`  
**解析器**：`ast`  
**第5层完整正文**：`read_block(path="distill/agent/context_cache.py", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| ContextCache@20 | class | L20-81 | 把老工具结果的正文换出上下文（保留墓碑 + sidecar 可取回）。 | class ContextCache: |
| ContextCache.__init__@29 | def | L29-34 |  | def __init__(self, keep_recent: int = 2, max_chars: int = 200): |
| ContextCache._key@36 | def | L36-38 |  | def _key(self, msg: dict) -> str: |
| ContextCache.filter@40 | def | L40-73 | CallModelInputFilter：就地改写 ModelInputData.input。 | def filter(self, data) -> "ModelInputData": |
| ContextCache.get@75 | def | L75-76 |  | def get(self, key: str) -> str \| None: |
| ContextCache.stats@78 | def | L78-81 |  | def stats(self) -> dict: |
