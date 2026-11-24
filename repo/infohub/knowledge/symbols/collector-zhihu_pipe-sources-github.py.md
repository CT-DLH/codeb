---
covers:
  - collector/zhihu_pipe/sources/github.py
title: Semantic block index: github.py (layer 4)
updated: 2026-11-24
---

# 语义块索引：github.py（第4层）

**源码文件**：`collector/zhihu_pipe/sources/github.py`  
**解析器**：`ast`  
**第5层完整正文**：`read_block(path="collector/zhihu_pipe/sources/github.py", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| RateLimited@50 | class | L50-51 | 配额耗尽。调用方应把它当作「本源的临时不可用」，而不是内容错误。 | class RateLimited(QuotaExceeded): |
| _ts@54 | def | L54-60 |  | def _ts(iso: str \| None) -> int: |
| GitHubSource@63 | class | L63-328 |  | class GitHubSource: |
| GitHubSource.__init__@90 | def | L90-99 |  | def __init__(self) -> None: |
| GitHubSource.set_min_interval@101 | def | L101-108 | 统一覆盖两档间隔（CLI 的 --delay）。 | def set_min_interval(self, seconds: float) -> None: |
| GitHubSource._throttle@112 | def | L112-113 | ---------------------------------------------------------------- 底层请求 | def _throttle(self, bucket: str) -> None: |
| GitHubSource._call@115 | def | L115-153 |  | def _call(self, path: str, params: dict \| None = None, *, |
| GitHubSource._repo_item@157 | def | L157-185 | ---------------------------------------------------------------- 翻译层 | def _repo_item(self, r: dict) -> Item: |
| GitHubSource._issue_item@187 | def | L187-204 |  | def _issue_item(self, r: dict) -> Item: |
| GitHubSource.search@208 | def | L208-234 | 检索仓库（默认）或 issue/PR。 | def search(self, query: str, *, limit: int = 30, cursor: str \| None =… |
| GitHubSource.list_author@236 | def | L236-245 | 按 owner 铺开：拿这个人的其他仓库（按最近推送排序）。 | def list_author(self, author_id: str, *, kinds: Iterable[str] \| None … |
| GitHubSource.fetch@247 | def | L247-250 |  | def fetch(self, ref: ContentRef) -> Document: |
| GitHubSource._fetch_repo@252 | def | L252-288 |  | def _fetch_repo(self, ref: ContentRef) -> Document: |
| GitHubSource._fetch_issue@290 | def | L290-306 |  | def _fetch_issue(self, ref: ContentRef) -> Document: |
| GitHubSource.canonicalize@308 | def | L308-313 |  | def canonicalize(self, url: str) -> str: |
| GitHubSource.health@315 | def | L315-328 |  | def health(self) -> Health: |
