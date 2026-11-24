---
covers:
  - collector/zhihu_pipe/sources/cnki.py
title: Semantic block index: cnki.py (layer 4)
updated: 2026-11-24
---

# 语义块索引：cnki.py（第4层）

**源码文件**：`collector/zhihu_pipe/sources/cnki.py`  
**解析器**：`ast`  
**第5层完整正文**：`read_block(path="collector/zhihu_pipe/sources/cnki.py", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| NoSearchAvailable@141 | class | L141-142 |  | class NoSearchAvailable(NoSearch): |
| _clean@145 | def | L145-146 |  | def _clean(s: Any) -> str: |
| _count@149 | def | L149-151 |  | def _count(v: Any) -> int: |
| _date_ts@154 | def | L154-172 | 2023-05-15 / 2023年05期 / 2023 → unix 时间戳；解析不了返回 0。 | def _date_ts(s: str) -> int: |
| _page_mark@175 | def | L175-178 | 1/300 → (1, 300)。取不到就是 (0, 0)。 | def _page_mark(s: str) -> tuple[int, int]: |
| _looks_like_filename@181 | def | L181-187 | CNKI 的 filename 是短 ID（如 SXZZ202301001）；v 令牌通常 60+ 字符。 | def _looks_like_filename(s: str) -> bool: |
| _content_id@190 | def | L190-198 |  | def _content_id(href: str, export_id: str = "") -> str: |
| _url_for@201 | def | L201-205 | 没有 ref.url 时的兜底：filename 走 detail.aspx，其余按 v 参数处理。 | def _url_for(content_id: str) -> str: |
| CnkiSource@208 | class | L208-485 |  | class CnkiSource(BrowserSource): |
| CnkiSource.__init__@238 | def | L238-242 |  | def __init__(self) -> None: |
| CnkiSource.capabilities@245 | def | L245-254 |  | def capabilities(self) -> frozenset[Capability]: |
| CnkiSource._page@258 | def | L258-261 | ---------------------------------------------------------------- 搜索 | def _page(self): |
| CnkiSource._submit@263 | def | L263-274 |  | def _submit(self, page, query: str) -> None: |
| CnkiSource._next@276 | def | L276-287 |  | def _next(self, page) -> bool: |
| CnkiSource.search@289 | def | L289-312 |  | def search(self, query: str, *, limit: int = 20, cursor: str \| None =… |
| CnkiSource._row_item@314 | def | L314-336 |  | def _row_item(self, row: dict) -> Item: |
| CnkiSource._load_detail@340 | def | L340-355 | ---------------------------------------------------------------- 详情 | def _load_detail(self, url: str) -> dict: |
| CnkiSource.parse_url@357 | def | L357-368 |  | def parse_url(self, url: str) -> Item \| None: |
| CnkiSource._detail_item@370 | def | L370-387 |  | def _detail_item(self, url: str, cid: str, data: dict) -> Item: |
| CnkiSource.fetch@389 | def | L389-393 |  | def fetch(self, ref: ContentRef) -> Document: |
| CnkiSource._document@395 | def | L395-430 |  | def _document(self, ref: ContentRef, data: dict) -> Document: |
| CnkiSource.canonicalize@434 | def | L434-462 | ---------------------------------------------------------------- 身份 | def canonicalize(self, url: str) -> str: |
| CnkiSource.health@464 | def | L464-480 |  | def health(self) -> Health: |
| CnkiSource.list_author@482 | def | L482-485 | 知网没有「按作者铺开」的公开入口；作者检索属于高级检索，暂不实现。 | def list_author(self, author_id: str, *, kinds: Iterable[str] \| None … |
