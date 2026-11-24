---
covers:
  - collector/tools/selftest_plugin.py
title: Semantic block index: selftest_plugin.py (layer 4)
updated: 2026-11-24
---

# 语义块索引：selftest_plugin.py（第4层）

**源码文件**：`collector/tools/selftest_plugin.py`  
**解析器**：`ast`  
**第5层完整正文**：`read_block(path="collector/tools/selftest_plugin.py", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| FakeSource@37 | class | L37-106 | 一个「像 B 站」的假源：URL 的 query 有意义、正文有残片、没有 README 那套规矩。 | class FakeSource: |
| FakeSource.__init__@44 | def | L44-47 |  | def __init__(self) -> None: |
| FakeSource.parse_url@49 | def | L49-54 | 导入器钩子：从链接反查 Item（FakeSource 用它冒充「无搜索能力的源」）。 | def parse_url(self, url: str): |
| FakeSource.search@56 | def | L56-75 |  | def search(self, query: str, *, limit: int = 30, cursor: str \| None =… |
| FakeSource.list_author@77 | def | L77-78 |  | def list_author(self, author_id: str, *, kinds=None, limit: int = 50) … |
| FakeSource.fetch@80 | def | L80-96 |  | def fetch(self, ref: ContentRef) -> Document: |
| FakeSource.canonicalize@98 | def | L98-103 | 插件自己的口径：p 是内容身份的一部分，必须留下；其余参数丢掉。 | def canonicalize(self, url: str) -> str: |
| FakeSource.health@105 | def | L105-106 |  | def health(self) -> Health: |
| _fail@109 | def | L109-111 |  | def _fail(msg: str) -> None: |
| main@114 | def | L114-267 |  | def main() -> int: |
| EnSource@249 | class | L249-250 |  | class EnSource(FakeSource): |
| ZhSource@252 | class | L252-253 |  | class ZhSource(FakeSource): |
