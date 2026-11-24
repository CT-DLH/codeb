---
covers:
  - collector/zhihu_pipe/source.py
title: Semantic block index: source.py (layer 4)
updated: 2026-11-24
---

# 语义块索引：source.py（第4层）

**源码文件**：`collector/zhihu_pipe/source.py`  
**解析器**：`ast`  
**第5层完整正文**：`read_block(path="collector/zhihu_pipe/source.py", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| QuotaExceeded@26 | class | L26-30 | 本源配额/限流耗尽，属于「临时不可用」，不应判为内容抓取失败。 | class QuotaExceeded(RuntimeError): |
| NoSearch@33 | class | L33-38 | 这个源根本没有可用的搜索接口（小红书搜索要 x-s 签名，只有浏览器能产生）。 | class NoSearch(RuntimeError): |
| Capability@41 | class | L41-46 |  | class Capability(str, Enum): |
| Fidelity@49 | class | L49-52 |  | class Fidelity(str, Enum): |
| ContentRef@56 | class | L56-67 |  | class ContentRef: |
| ContentRef.uid@66 | def | L66-67 |  | def uid(self) -> str: |
| Item@71 | class | L71-87 | 内核认识的内容元数据。插件把平台字段翻译成这个结构。 | class Item: |
| Item.uid@86 | def | L86-87 |  | def uid(self) -> str: |
| Document@91 | class | L91-112 | 正文 + 完整度。空正文不是异常，而是 METADATA_ONLY。 | class Document: |
| SearchPage@116 | class | L116-120 | 一页搜索结果。next_cursor 为 None 表示没有下一页。 | class SearchPage: |
| ThrottleSpec@124 | class | L124-129 | 该源的速率约定，由内核的令牌桶读取。 | class ThrottleSpec: |
| Health@133 | class | L133-136 |  | class Health: |
| QueryGuide@140 | class | L140-161 | 「这个平台的检索词该怎么写」——由插件自己声明，不在文档里各写一份。 | class QueryGuide: |
| Source@165 | class | L165-217 | 插件必须实现的接口。 | class Source(Protocol): |
| Source.search@194 | def | L194-202 | kind 是内核级概念（就是 ContentRef.kind）：内核可以要求「只要视频」 | def search(self, query: str, *, limit: int, cursor: str \| None = None… |
| Source.list_author@204 | def | L204-205 |  | def list_author(self, author_id: str, *, kinds: Iterable[str] \| None … |
| Source.fetch@207 | def | L207-209 | 需要访问参数（token/referrer）的源读 ref.url，内核会把规范化的 URL 带上。 | def fetch(self, ref: ContentRef) -> Document: |
| Source.canonicalize@211 | def | L211-215 | 必须幂等：内核会把已经规范化的 URL 再喂进来一次（store.get 等）。 | def canonicalize(self, url: str) -> str: |
| Source.health@217 | def | L217-217 |  | def health(self) -> Health: ... |
| Audience@221 | class | L221-234 | 一个内容的观众反馈原始材料（未经归纳）。 | class Audience: |
| get_source@242 | def | L242-244 | 向后兼容：老代码 from zhihu_pipe.source import get_source 仍然可用。 实现按需加载，避免「装了 GitHub 插件就必须装知乎依赖」这种耦合。 ------- | def get_source(name: str) -> Source: |
| enabled_sources@247 | def | L247-249 |  | def enabled_sources(names: Iterable[str] \| None = None) -> list[Sourc… |
| __getattr__@252 | def | L252-272 |  | def __getattr__(name: str): |
