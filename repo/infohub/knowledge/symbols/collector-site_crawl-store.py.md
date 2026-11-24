---
covers:
  - collector/site_crawl/store.py
title: Semantic block index: store.py (layer 4)
updated: 2026-11-24
---

# 语义块索引：store.py（第4层）

**源码文件**：`collector/site_crawl/store.py`  
**解析器**：`ast`  
**第5层完整正文**：`read_block(path="collector/site_crawl/store.py", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| _canonical@90 | def | L90-96 |  | def _canonical(value: Any) -> str: |
| teacher_sha1@99 | def | L99-109 |  | def teacher_sha1(row: dict) -> str: |
| _encode@112 | def | L112-116 |  | def _encode(rec: dict) -> dict: |
| content_fingerprint@119 | def | L119-126 | 给一份采集记录算内容指纹（与 cache_put 存进 sha1 列的口径完全一致）。 | def content_fingerprint(rec: dict) -> str: |
| _decode@129 | def | L129-140 |  | def _decode(row: sqlite3.Row \| dict) -> dict: |
| now_stamp@143 | def | L143-144 |  | def now_stamp() -> str: |
| Store@147 | class | L147-262 |  | class Store: |
| Store.__init__@148 | def | L148-156 |  | def __init__(self, path: str \| Path): |
| Store.close@158 | def | L158-159 |  | def close(self) -> None: |
| Store.start_run@166 | def | L166-172 | [废弃] 保留壳但不写库：runs 表是只读历史归档，不再产生新行。 | def start_run(self, scope: str, family: str = "") -> int: |
| Store.finish_run@174 | def | L174-179 | [废弃] 保留壳但不写库：runs 表是只读历史归档，不再回写计数。 | def finish_run(self, run_id: int, counts: dict, note: str = "") -> Non… |
| Store.cache_cold@183 | def | L183-189 | 内容缓存是否「冷」：库刚建或 teachers 为空。 | def cache_cold(self) -> bool: |
| Store.cache_get@191 | def | L191-194 | 返回该 slug 缓存的内容指纹 sha1；没有记录返回 None。 | def cache_get(self, slug: str) -> str \| None: |
| Store.cache_put@196 | def | L196-236 | 以 slug 为键、sha1 为内容指纹写缓存，只比较内容哈希。 | def cache_put(self, slug: str, sha1: str, rec: dict \| None = None) ->… |
| Store.upsert_teacher@238 | def | L238-251 | [废弃兼容壳] 旧生命周期接口；新代码一律用 cache_put()。 | def upsert_teacher(self, rec: dict) -> str: |
| Store.get_teacher@253 | def | L253-255 |  | def get_teacher(self, slug: str) -> dict \| None: |
| Store.teachers@257 | def | L257-259 |  | def teachers(self) -> list[dict]: |
| Store.count_teachers@261 | def | L261-262 |  | def count_teachers(self) -> int: |
| default_db_path@265 | def | L265-268 | crawl.db 与 pipeline.db 同目录，但独立文件：两套状态机互不影响。 | def default_db_path() -> Path: |
| content_cache_cold@271 | def | L271-287 | 只读判断 crawl.db 内容缓存是否冷：库不存在 / teachers 为空 / 表不存在 → True。 | def content_cache_cold(path: str \| Path) -> bool: |
