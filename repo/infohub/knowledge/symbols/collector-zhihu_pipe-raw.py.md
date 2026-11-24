---
covers:
  - collector/zhihu_pipe/raw.py
title: Semantic block index: raw.py (layer 4)
updated: 2026-11-24
---

# 语义块索引：raw.py（第4层）

**源码文件**：`collector/zhihu_pipe/raw.py`  
**解析器**：`ast`  
**第5层完整正文**：`read_block(path="collector/zhihu_pipe/raw.py", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| safe_name@25 | def | L25-32 | content_id 可能含 /（GitHub 的 owner/repo），做文件名前必须消毒。 | def safe_name(value: object) -> str: |
| save_raw@35 | def | L35-60 |  | def save_raw(data_dir: Path, source: str, item, body: str, score: floa… |
