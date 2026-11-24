---
covers:
  - collector/zhihu_pipe/sources/site.py
title: Semantic block index: site.py (layer 4)
updated: 2026-11-24
---

# 语义块索引：site.py（第4层）

**源码文件**：`collector/zhihu_pipe/sources/site.py`  
**解析器**：`ast`  
**第5层完整正文**：`read_block(path="collector/zhihu_pipe/sources/site.py", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| SiteSource@56 | class | L56-267 | 一份站点 spec → 一个 Source 实例。构造期绝不联网。 | class SiteSource: |
| SiteSource.__init__@59 | def | L59-83 |  | def __init__(self, spec_path: str \| Path, *, http: Any = None) -> Non… |
| SiteSource._build_http@87 | def | L87-104 | 真正需要联网时才构建 Http（限速/UA/cookie 全部来自 spec）。 | def _build_http(self) -> Any: |
| SiteSource._client@106 | def | L106-107 |  | def _client(self) -> Any: |
| SiteSource._fidelity@110 | def | L110-115 | fidelity 只描述 body_md 完整度，与 extra 正交（裁决 4）。 | def _fidelity(body_md: str) -> Fidelity: |
| SiteSource._content_id@118 | def | L118-120 | 站点内容的稳定 id：URL 规范化后的短哈希，不编造语义。 | def _content_id(url: str) -> str: |
| SiteSource.search@124 | def | L124-132 | 没有 SEARCH 能力：返回空页，但明确说明为什么是空的（不是静默空列表）。 | def search(self, query: str, *, limit: int, cursor: str \| None = None… |
| SiteSource.list_author@134 | def | L134-139 | 站点源没有作者维度。沿用现有各源「不硬猜就返回空」的口径，但点名原因。 | def list_author(self, author_id: str, *, kinds: Iterable[str] \| None … |
| SiteSource.fetch@141 | def | L141-150 | 取一条站点内容：正文进 body_md，结构化字段进 extra，fidelity 按实际抽取设置。 | def fetch(self, ref: ContentRef) -> Document: |
| SiteSource._fetch_column@152 | def | L152-185 |  | def _fetch_column(self, ref: ContentRef, target: str) -> Document: |
| SiteSource._fetch_teacher_home@187 | def | L187-225 |  | def _fetch_teacher_home(self, ref: ContentRef, target: str) -> Documen… |
| SiteSource.canonicalize@227 | def | L227-251 | 幂等且带源前缀 site_<family>_<kind>:<规范化 URL>。 | def canonicalize(self, url: str) -> str: |
| SiteSource.health@253 | def | L253-267 | 探测放这里（构造期零请求）。打一次 base，点名成功/失败的具体原因。 | def health(self) -> Health: |
