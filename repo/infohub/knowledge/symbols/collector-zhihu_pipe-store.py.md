---
covers:
  - collector/zhihu_pipe/store.py
title: Semantic block index: store.py (layer 4)
updated: 2026-11-24
---

# 语义块索引：store.py（第4层）

**源码文件**：`collector/zhihu_pipe/store.py`  
**解析器**：`ast`  
**第5层完整正文**：`read_block(path="collector/zhihu_pipe/store.py", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| platform_of@42 | def | L42-62 | 这行属于哪个源插件——取正文资格的判定基础，口径与历史身份键兼容。 | def platform_of(canonical_key: str, url: str, known: tuple[str, ...] \… |
| _is_zhihu@78 | def | L78-79 |  | def _is_zhihu(netloc: str) -> bool: |
| _is_zhihu_article_path@92 | def | L92-93 |  | def _is_zhihu_article_path(path: str) -> bool: |
| canonicalize_url@96 | def | L96-146 | 把同一篇文章的各种 URL 形态收敛成一个形态（内核的默认规范化）。 | def canonicalize_url(url: str) -> str: |
| content_key@149 | def | L149-150 |  | def content_key(kind: str, content_id: str) -> str: |
| sha256@153 | def | L153-154 |  | def sha256(text: str) -> str: |
| ArticleRow@158 | class | L158-187 |  | class ArticleRow: |
| ArticleRow.to_dict@186 | def | L186-187 |  | def to_dict(self) -> dict: |
| Store@190 | class | L190-733 |  | class Store: |
| Store.__init__@191 | def | L191-199 | canonicalizer 让 URL 规范化归插件所有（设计稿 §2 第③条）。 | def __init__(self, db_path: Path \| str, canonicalizer=None): |
| Store.conn@202 | def | L202-213 |  | def conn(self) -> Iterator[sqlite3.Connection]: |
| Store._init_schema@215 | def | L215-339 |  | def _init_schema(self) -> None: |
| Store.upsert@343 | def | L343-428 | 写入/更新一条记录。 | def upsert(self, row: ArticleRow) -> tuple[bool, bool]: |
| Store.mark_fetched@430 | def | L430-443 | 正文已抓取。fidelity 不给时按「有正文但完整度未声明」记 partial， | def mark_fetched(self, url: str, raw_path: str, content_hash: str, wor… |
| Store.mark_read@445 | def | L445-463 | 正文已读过，但当前主题不需要（或暂不总结）。 | def mark_read(self, url: str, raw_path: str, content_hash: str, word_c… |
| Store.mark_seen@465 | def | L465-480 | 只登记元数据：搜索到的条目落库即可建卡，正文留待获取流水线补。 | def mark_seen(self, row: ArticleRow) -> tuple[bool, bool]: |
| Store.set_status@482 | def | L482-486 | 只改状态，不动正文/时间戳（用于复用已有正文时排队总结）。 | def set_status(self, url: str, status: str) -> None: |
| Store.mark_summarized@488 | def | L488-501 | backend 落进 summary_backend 列——「这篇摘要是哪个后端产的」只有一个真值来源。 | def mark_summarized(self, url: str, summary_path: str, backend: str = … |
| Store.mark_skipped@503 | def | L503-509 |  | def mark_skipped(self, url: str, reason: str = "") -> None: |
| Store.mark_failed@511 | def | L511-517 |  | def mark_failed(self, url: str, error: str) -> None: |
| Store.mark_unfetchable@519 | def | L519-533 | 平台级取不到正文，判死并退出获取队列。 | def mark_unfetchable(self, url: str, reason: str) -> None: |
| Store.get@537 | def | L537-541 | ---------- 查询 ---------- | def get(self, url: str) -> dict \| None: |
| Store.pending@543 | def | L543-551 |  | def pending(self, limit: int = 0) -> list[dict]: |
| Store.queue@553 | def | L553-598 | 获取流水线的唯一候选查询：还没正文、而且确实还能取到正文的行。 | def queue(self, *, limit: int = 0, platform: str = "", retry: bool = F… |
| Store.all_rows@600 | def | L600-608 |  | def all_rows(self, status: str \| None = None) -> list[dict]: |
| Store.stats@610 | def | L610-613 |  | def stats(self) -> dict: |
| Store.log_run@615 | def | L615-619 |  | def log_run(self, **kw) -> None: |
| Store.normalize_query@624 | def | L624-632 | 台账查找用的归一化键：只影响「是不是同一个词」，不影响真正发出去的检索词。 | def normalize_query(query: str) -> str: |
| Store.ledger_get@634 | def | L634-641 | 查这个词在某平台上的进度。没有记录返回 None。 | def ledger_get(self, platform: str, query: str, topic: str = "") -> di… |
| Store.ledger_should_skip@643 | def | L643-662 | 该不该跳过这个词（不联网就省一次）。 | def ledger_should_skip(self, platform: str, query: str, topic: str = "… |
| Store.ledger_record@664 | def | L664-718 | 记一次检索的结果。语义按「这一轮累计」而不是「这次调用」来写。 | def ledger_record( |
| Store.ledger_rows@720 | def | L720-733 |  | def ledger_rows(self, topic: str = "", platform: str = "") -> list[dic… |
