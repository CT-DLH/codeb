---
covers:
  - collector/frontmatter.py
title: Semantic block index: frontmatter.py (layer 4)
updated: 2026-11-24
---

# 语义块索引：frontmatter.py（第4层）

**源码文件**：`collector/frontmatter.py`  
**解析器**：`ast`  
**第5层完整正文**：`read_block(path="collector/frontmatter.py", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| split_frontmatter@22 | def | L22-35 | 返回 (yaml 文本, 正文)。没有成对的分隔行时前者为 None，正文原样返回。 | def split_frontmatter(text: str) -> tuple[str \| None, str]: |
| body_of@38 | def | L38-39 |  | def body_of(text: str) -> str: |
| read_frontmatter@42 | def | L42-52 | 读一个 markdown 文件的 (frontmatter, 正文)；解析失败时 frontmatter 为 None。 | def read_frontmatter(path: Path) -> tuple[dict \| None, str]: |
