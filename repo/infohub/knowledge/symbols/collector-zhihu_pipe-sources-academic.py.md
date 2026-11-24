---
covers:
  - collector/zhihu_pipe/sources/academic.py
title: Semantic block index: academic.py (layer 4)
updated: 2026-11-24
---

# 语义块索引：academic.py（第4层）

**源码文件**：`collector/zhihu_pipe/sources/academic.py`  
**解析器**：`ast`  
**第5层完整正文**：`read_block(path="collector/zhihu_pipe/sources/academic.py", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| _ts_from_iso@54 | def | L54-73 | 2025-10-30T17:52:02Z / 2025-10-30 / 2025 → epoch（拿不到就 0）。 | def _ts_from_iso(iso: str) -> int: |
| _text@76 | def | L76-78 | ElementTree 里的可读文本（ArticleTitle 里会嵌 <i>/<sup>）。 | def _text(el) -> str: |
| _reconstruct_abstract@81 | def | L81-93 | OpenAlex 的摘要存成「词 → 出现位置」，按位置拼回原文。 | def _reconstruct_abstract(inverted: dict \| None) -> str: |
| AcademicSource@96 | class | L96-230 | 学术源的公共骨架。子类只需要填 name 和四个端点实现。 | class AcademicSource: |
| AcademicSource.__init__@105 | def | L105-111 |  | def __init__(self) -> None: |
| AcademicSource.set_min_interval@113 | def | L113-115 |  | def set_min_interval(self, seconds: float) -> None: |
| AcademicSource._throttle@119 | def | L119-120 | ---------------------------------------------------------------- 传输 | def _throttle(self) -> None: |
| AcademicSource._headers@122 | def | L122-123 |  | def _headers(self) -> dict[str, str]: |
| AcademicSource._get@125 | def | L125-154 |  | def _get(self, url: str, *, retries: int = 1) -> str: |
| AcademicSource._get_json@156 | def | L156-157 |  | def _get_json(self, url: str) -> Any: |
| AcademicSource.search@161 | def | L161-165 | ---------------------------------------------------------------- 协议 | def search(self, query: str, *, limit: int = 30, cursor: str \| None =… |
| AcademicSource.list_author@167 | def | L167-170 | 只有 OpenAlex / S2 有稳定的作者→论文接口；其余返回空列表（不硬猜）。 | def list_author(self, author_id: str, *, kinds: Iterable[str] \| None … |
| AcademicSource.fetch@172 | def | L172-174 |  | def fetch(self, ref: ContentRef) -> Document: |
| AcademicSource._document@176 | def | L176-207 |  | def _document(self, ref: ContentRef, item: Item) -> Document: |
| AcademicSource.parse_url@209 | def | L209-213 |  | def parse_url(self, url: str) -> Item \| None: |
| AcademicSource._search@217 | def | L217-218 | ---------------------------------------------------------------- 子类实现 | def _search(self, query: str, limit: int, cursor: str \| None) -> Sear… |
| AcademicSource._fetch_item@220 | def | L220-221 |  | def _fetch_item(self, content_id: str) -> Item: |
| AcademicSource._ident_from_url@223 | def | L223-224 |  | def _ident_from_url(self, url: str) -> str: |
| AcademicSource.canonicalize@226 | def | L226-227 |  | def canonicalize(self, url: str) -> str: |
| AcademicSource.health@229 | def | L229-230 |  | def health(self) -> Health: |
| ArxivSource@235 | class | L235-378 | ====================================================================== arXiv | class ArxivSource(AcademicSource): |
| ArxivSource._build_query@293 | def | L293-307 | 把调用方的检索词翻成 arXiv 语法。 | def _build_query(self, query: str) -> str: |
| ArxivSource._search@309 | def | L309-320 |  | def _search(self, query: str, limit: int, cursor: str \| None) -> Sear… |
| ArxivSource._parse_entry@322 | def | L322-349 |  | def _parse_entry(self, e) -> Item \| None: |
| ArxivSource._fetch_item@351 | def | L351-358 |  | def _fetch_item(self, content_id: str) -> Item: |
| ArxivSource._ident_from_url@360 | def | L360-362 |  | def _ident_from_url(self, url: str) -> str: |
| ArxivSource.canonicalize@364 | def | L364-370 | 版本号不进身份：2510.26768v1 与 v2 是同一篇（更新只改正文，不另建条目）。 | def canonicalize(self, url: str) -> str: |
| ArxivSource.health@372 | def | L372-378 |  | def health(self) -> Health: |
| S2Source@383 | class | L383-475 | ========================================================== Semantic Scholar | class S2Source(AcademicSource): |
| S2Source._headers@400 | def | L400-405 |  | def _headers(self) -> dict[str, str]: |
| S2Source._search@407 | def | L407-417 |  | def _search(self, query: str, limit: int, cursor: str \| None) -> Sear… |
| S2Source._parse@419 | def | L419-441 |  | def _parse(self, p: dict) -> Item \| None: |
| S2Source._fetch_item@443 | def | L443-448 |  | def _fetch_item(self, content_id: str) -> Item: |
| S2Source.list_author@450 | def | L450-454 |  | def list_author(self, author_id: str, *, kinds: Iterable[str] \| None … |
| S2Source._ident_from_url@456 | def | L456-458 |  | def _ident_from_url(self, url: str) -> str: |
| S2Source.canonicalize@460 | def | L460-464 |  | def canonicalize(self, url: str) -> str: |
| S2Source.health@466 | def | L466-475 |  | def health(self) -> Health: |
| OpenAlexSource@480 | class | L480-592 | ==================================================================== OpenAlex | class OpenAlexSource(AcademicSource): |
| OpenAlexSource._search_url@500 | def | L500-510 |  | def _search_url(self, path: str, params: dict) -> str: |
| OpenAlexSource._search@512 | def | L512-520 |  | def _search(self, query: str, limit: int, cursor: str \| None) -> Sear… |
| OpenAlexSource._parse@522 | def | L522-549 |  | def _parse(self, w: dict) -> Item \| None: |
| OpenAlexSource._fetch_item@551 | def | L551-557 |  | def _fetch_item(self, content_id: str) -> Item: |
| OpenAlexSource.list_author@559 | def | L559-565 |  | def list_author(self, author_id: str, *, kinds: Iterable[str] \| None … |
| OpenAlexSource._ident_from_url@567 | def | L567-572 |  | def _ident_from_url(self, url: str) -> str: |
| OpenAlexSource.canonicalize@574 | def | L574-583 | DOI 是学术界的身份：doi.org 链接统一成小写 DOI，OpenAlex 的 W 号原样保留。 | def canonicalize(self, url: str) -> str: |
| OpenAlexSource.health@585 | def | L585-592 |  | def health(self) -> Health: |
| PubmedSource@597 | class | L597-720 | ===================================================================== PubMed | class PubmedSource(AcademicSource): |
| PubmedSource._params@616 | def | L616-624 |  | def _params(self, extra: dict) -> dict: |
| PubmedSource._search@626 | def | L626-634 |  | def _search(self, query: str, limit: int, cursor: str \| None) -> Sear… |
| PubmedSource._esearch@636 | def | L636-648 |  | def _esearch(self, query: str, retmax: int, retstart: int = 0) -> list… |
| PubmedSource._efetch@650 | def | L650-654 |  | def _efetch(self, ids: list[str]) -> list[Item]: |
| PubmedSource._parse_article@656 | def | L656-698 |  | def _parse_article(self, art) -> Item \| None: |
| PubmedSource._fetch_item@700 | def | L700-704 |  | def _fetch_item(self, content_id: str) -> Item: |
| PubmedSource._ident_from_url@706 | def | L706-708 |  | def _ident_from_url(self, url: str) -> str: |
| PubmedSource.canonicalize@710 | def | L710-712 |  | def canonicalize(self, url: str) -> str: |
| PubmedSource.health@714 | def | L714-720 |  | def health(self) -> Health: |
| _pubmed_date@727 | def | L727-737 | PubMed 的月份可能是 Dec 也可能是 12，年份缺失时返回 0（不猜）。 | def _pubmed_date(year: str, month: str, day: str) -> int: |
