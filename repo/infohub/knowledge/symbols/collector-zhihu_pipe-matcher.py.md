---
covers:
  - collector/zhihu_pipe/matcher.py
title: Semantic block index: matcher.py (layer 4)
updated: 2026-11-24
---

# 语义块索引：matcher.py（第4层）

**源码文件**：`collector/zhihu_pipe/matcher.py`  
**解析器**：`ast`  
**第5层完整正文**：`read_block(path="collector/zhihu_pipe/matcher.py", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| _norm@17 | def | L17-18 |  | def _norm(s: str) -> str: |
| _contains@21 | def | L21-40 | 关键词命中判断。 | def _contains(text_low: str, word: str) -> bool: |
| Topic@44 | class | L44-79 |  | class Topic: |
| Topic._hits@59 | def | L59-61 |  | def _hits(self, text: str, words: list[str]) -> list[str]: |
| Topic.score@63 | def | L63-79 |  | def score(self, title: str, excerpt: str = "", body: str = "") -> tupl… |
| resolve_topic@115 | def | L115-129 |  | def resolve_topic(name: str \| None, keywords: list[str] \| None) -> T… |
| strip_html@132 | def | L132-133 |  | def strip_html(s: str) -> str: |
