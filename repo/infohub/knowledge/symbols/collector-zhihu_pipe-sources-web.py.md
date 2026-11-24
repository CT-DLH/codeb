---
covers:
  - collector/zhihu_pipe/sources/web.py
title: Semantic block index: web.py (layer 4)
updated: 2026-11-24
---

# 语义块索引：web.py（第4层）

**源码文件**：`collector/zhihu_pipe/sources/web.py`  
**解析器**：`ast`  
**第5层完整正文**：`read_block(path="collector/zhihu_pipe/sources/web.py", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| _is_lexicon_entry@144 | def | L144-157 | 这条结果是不是一个「词条页」（而不是真实内容页）。 | def _is_lexicon_entry(title: str) -> bool: |
| _unwrap@175 | def | L175-196 | 拆 Bing 的跳转壳：bing.com/ck/a?...&u=a1<base64url>。 | def _unwrap(href: str) -> str: |
| _owner@199 | def | L199-209 | 这个域名归哪个已接入源管？返回空串表示「确实是 web 源该接的外部站」。 | def _owner(netloc: str) -> str: |
| _tokens@212 | def | L212-214 | 按空白/中英文标点切词，丢掉单字（单字命中没有判断力）。 | def _tokens(query: str) -> list[str]: |
| _head_only@217 | def | L217-227 | 降级重试用的查询词：多词查询丢掉后面的词，只留首词；单词查询返回空串（不重试）。 | def _head_only(query: str) -> str: |
| WebSource@230 | class | L230-645 | 通用网页搜索 + 正文抓取。正文走 zhihu_pipe/html_text.py，三条闸见模块 docstring。 | class WebSource: |
| WebSource.__init__@260 | def | L260-271 |  | def __init__(self) -> None: |
| WebSource.set_min_interval@275 | def | L275-279 | ------------------------------------------------------------------ 传输 | def set_min_interval(self, seconds: float) -> None: |
| WebSource._throttle@281 | def | L281-282 |  | def _throttle(self) -> None: |
| WebSource._get@284 | def | L284-299 |  | def _get(self, url: str, referer: str = "") -> str: |
| WebSource.search@303 | def | L303-323 | kind 是内核概念，本插件没有多种内容类型，忽略。 | def search(self, query: str, *, limit: int, cursor: str \| None = None… |
| WebSource._search_http@325 | def | L325-359 |  | def _search_http(self, query: str, limit: int) -> SearchPage: |
| WebSource._allow_browser_fallback@361 | def | L361-371 | 能不能用浏览器通道救场。只探一次，失败就记住别反复起浏览器。 | def _allow_browser_fallback(self) -> bool: |
| WebSource._search_http_once@373 | def | L373-377 |  | def _search_http_once(self, query: str, limit: int) -> SearchPage: |
| WebSource._search_browser@379 | def | L379-406 |  | def _search_browser(self, query: str, limit: int, page_no: int) -> Sea… |
| WebSource._parse_page@410 | def | L410-426 | ------------------------------------------------------------------ 解析 | def _parse_page(self, body: str, limit: int) -> tuple[list[Item], int,… |
| WebSource._build@428 | def | L428-463 |  | def _build(self, rows: list[dict], limit: int) -> tuple[list[Item], in… |
| WebSource._report@465 | def | L465-536 | 把「为什么结果少了/不对」说清楚。静默扣减比返回垃圾更难查。 | def _report(self, query: str, items: list[Item], dropped: int, total: … |
| WebSource.canonicalize@540 | def | L540-552 | 去追踪参数 + fragment + 尾斜杠，scheme 统一成 https。必须幂等。 | def canonicalize(self, url: str) -> str: |
| WebSource._cid@554 | def | L554-559 | 身份 = 去掉 scheme 的规范 URL。可读、可查重、换参数仍是同一条。 | def _cid(self, url: str) -> str: |
| WebSource.parse_url@561 | def | L561-590 | 按链接导入：顺手取一次 <title> / meta description。 | def parse_url(self, url: str) -> Item \| None: |
| WebSource.fetch@592 | def | L592-618 | 抓正文：robots → 下载 → 解码 → 密度打分抽正文。 | def fetch(self, ref: ContentRef) -> Document: |
| WebSource._notice@621 | def | L621-630 | 抓不到正文时的正文：原因写在卡上，不留空让人猜。 | def _notice(url: str, why: str) -> str: |
| WebSource.health@632 | def | L632-645 |  | def health(self) -> Health: |
