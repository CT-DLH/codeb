---
covers:
  - collector/tools/lookup_cnki.py
title: Semantic block index: lookup_cnki.py (layer 4)
updated: 2026-11-24
---

# 语义块索引：lookup_cnki.py（第4层）

**源码文件**：`collector/tools/lookup_cnki.py`  
**解析器**：`ast`  
**第5层完整正文**：`read_block(path="collector/tools/lookup_cnki.py", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| read_frontmatter@45 | def | L45-48 | frontmatter.read_frontmatter 返回 (fm, body)，这里只要 fm（与 lookup_papers 同一写法）。 | def read_frontmatter(path: Path) -> dict \| None: |
| norm_title@51 | def | L51-57 | NFKC + 去空白 + 去书名号/引号 + 去尾标点 + 小写；只做归一化，不做同义改写。 | def norm_title(s: str) -> str: |
| strip_tail_marks@60 | def | L60-66 | 剥掉「（网络首发）」这类版次后缀；只剥已知的这几个，别做通用去括号。 | def strip_tail_marks(s: str) -> str: |
| title_matches@69 | def | L69-73 |  | def title_matches(card_title: str, result_title: str) -> bool: |
| authors_overlap@76 | def | L76-79 |  | def authors_overlap(card_authors: str, result_authors: str) -> bool: |
| detail_url@82 | def | L82-87 | 导出号（形如 SXZZ202301001）拼稳定链接；拿不到就退回结果页 URL。 | def detail_url(item) -> str: |
| main@90 | def | L90-223 |  | def main(argv: list[str] \| None = None) -> int: |
