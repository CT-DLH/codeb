---
covers:
  - collector/site_crawl/column.py
title: Semantic block index: column.py (layer 4)
updated: 2026-11-24
---

# 语义块索引：column.py（第4层）

**源码文件**：`collector/site_crawl/column.py`  
**解析器**：`ast`  
**第5层完整正文**：`read_block(path="collector/site_crawl/column.py", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| ColumnReport@35 | class | L35-46 |  | class ColumnReport: |
| ColumnReport.summary@43 | def | L43-46 |  | def summary(self) -> str: |
| _parse_items@58 | def | L58-86 | 栏目页的「条目」= 页面里的内容链接（排除附件与分页控件），按绝对 URL 去重。 | def _parse_items(html: str, url: str) -> list[dict]: |
| _attachment_links@89 | def | L89-107 |  | def _attachment_links(html: str, url: str, file_pattern: str = "") -> … |
| _CachedHttp@110 | class | L110-129 | 按 URL 缓存一次 fetch 的结果。 | class _CachedHttp: |
| _CachedHttp.__init__@118 | def | L118-120 |  | def __init__(self, inner: Any): |
| _CachedHttp.fetch@122 | def | L122-126 |  | def fetch(self, url: str, **kw): |
| _CachedHttp.__getattr__@128 | def | L128-129 |  | def __getattr__(self, name): |
| _result_html@132 | def | L132-138 | 从 http 的 FetchResult 取 HTML 文本；与 kit.paging 的口径一致。 | def _result_html(result: Any) -> str: |
| crawl_column@141 | def | L141-260 | 按 spec 跑一遍栏目采集，返回报告。http 可注入（离线自检传假实现）。 | def crawl_column(spec: dict, *, http: Any = None, max_pages: int = 10)… |
