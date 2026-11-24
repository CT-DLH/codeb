---
covers:
  - collector/refs/resolver.py
title: Semantic block index: resolver.py (layer 4)
updated: 2026-11-24
---

# 语义块索引：resolver.py（第4层）

**源码文件**：`collector/refs/resolver.py`  
**解析器**：`ast`  
**第5层完整正文**：`read_block(path="collector/refs/resolver.py", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| landing_url@30 | def | L30-37 |  | def landing_url(doi: str, fallback: str = "") -> str: |
| Resolved@41 | class | L41-58 |  | class Resolved: |
| Resolved.to_dict@57 | def | L57-58 |  | def to_dict(self) -> dict: |
| to_year@61 | def | L61-68 | epoch → 年份。1970 年以前的出版年是负数，Windows 的 localtime 会直接抛 OSError。 | def to_year(ts: int) -> int: |
| similarity@71 | def | L71-87 | 两条标题的相似度与口径。 | def similarity(a: str, b: str) -> tuple[float, str]: |
| Chain@90 | class | L90-268 | 按 lexicon 的 provider 顺序尝试；每个 provider 复用同一个插件实例（共享节流）。 | class Chain: |
| Chain.__init__@98 | def | L98-125 |  | def __init__(self, providers: list[str] \| None = None, lex: dict \| N… |
| Chain._item_to_resolved@129 | def | L129-150 | ------------------------------------------------------------------ 内部 | def _item_to_resolved(self, src, item, score: float, matched_by: str, … |
| Chain._by_doi@152 | def | L152-173 |  | def _by_doi(self, src, cit: Citation) -> Resolved \| None: |
| Chain._by_title@175 | def | L175-217 |  | def _by_title(self, src, cit: Citation) -> Resolved \| None: |
| Chain._cjk_ratio@222 | def | L222-225 | ------------------------------------------------------------------ 对外 | def _cjk_ratio(text: str) -> float: |
| Chain.resolve@227 | def | L227-268 |  | def resolve(self, cit: Citation) -> Resolved: |
