---
covers:
  - collector/zhihu_pipe/fetch.py
title: Semantic block index: fetch.py (layer 4)
updated: 2026-11-24
---

# 语义块索引：fetch.py（第4层）

**源码文件**：`collector/zhihu_pipe/fetch.py`  
**解析器**：`ast`  
**第5层完整正文**：`read_block(path="collector/zhihu_pipe/fetch.py", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| _strip@25 | def | L25-27 | search_v3 会在命中词外包 <em>…</em> 高亮标签，落库前去掉。 | def _strip(text: str) -> str: |
| set_min_interval@59 | def | L59-63 | 设置两次请求之间的最小间隔（秒）；0 = 不限速。 | def set_min_interval(seconds: float) -> None: |
| _throttle@66 | def | L66-68 | 在发起请求前确保距上次请求至少 _MIN_INTERVAL 秒（委托 Throttle.wait）。 | def _throttle() -> None: |
| _status_of@71 | def | L71-77 | 从异常里取出 HTTP 状态码（curl_cffi 与一般 requests 都兼容）。 | def _status_of(e: Exception) -> int: |
| _get@80 | def | L80-99 |  | def _get(url: str, *, skip_app_headers: bool = True, retries: int = 3)… |
| _stream@102 | def | L102-147 | 翻页拉取列表接口，直到没有下一页或达到 max_items。 | def _stream(url: str, max_items: int, page_size: int = 20) -> list[dic… |
| list_author_articles@152 | def | L152-176 | ---------------------------------------------------------------- 列表 | def list_author_articles(url_token: str, max_items: int = 50) -> list[… |
| list_author_answers@179 | def | L179-202 |  | def list_author_answers(url_token: str, max_items: int = 50) -> list[d… |
| fetch_article_doc@207 | def | L207-221 | 取单篇文章的完整内容（HTML → Markdown）。 | def fetch_article_doc(content_id: str) -> dict[str, Any]: |
| fetch_answer_doc@224 | def | L224-240 | 取单个回答的完整内容（HTML → Markdown）。 | def fetch_answer_doc(content_id: str) -> dict[str, Any]: |
| fetch_doc@243 | def | L243-244 |  | def fetch_doc(kind: str, content_id: str) -> dict[str, Any]: |
| search_topic@249 | def | L249-317 | 按关键词搜索（search_v3），返回问答与文章混合结果，自动翻页。 | def search_topic(keyword: str, max_items: int = 30) -> list[dict[str, … |
| list_hot@320 | def | L320-344 | 免登录可用的热榜。作为流水线无登录时的数据源，用来跑通采集/查重/筛选。 | def list_hot() -> list[dict[str, Any]]: |
| whoami@347 | def | L347-352 |  | def whoami() -> str: |
