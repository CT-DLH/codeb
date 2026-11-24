---
covers:
  - collector/tools/selftest_site.py
title: Semantic block index: selftest_site.py (layer 4)
updated: 2026-11-24
---

# 语义块索引：selftest_site.py（第4层）

**源码文件**：`collector/tools/selftest_site.py`  
**解析器**：`ast`  
**第5层完整正文**：`read_block(path="collector/tools/selftest_site.py", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| check@43 | def | L43-50 |  | def check(cond: bool, msg: str) -> None: |
| FakeResult@53 | class | L53-63 |  | class FakeResult: |
| FakeResult.__init__@54 | def | L54-63 |  | def __init__(self, text: str): |
| FakeHttp@66 | class | L66-75 | 只回一页固定 HTML，并记下每一次 fetch（证明构造期零请求）。 | class FakeHttp: |
| FakeHttp.__init__@69 | def | L69-71 |  | def __init__(self, html: str): |
| FakeHttp.fetch@73 | def | L73-75 |  | def fetch(self, url: str, **kw): |
| main@107 | def | L107-258 |  | def main() -> int: |
| BombHttp@113 | class | L113-120 | 构造即炸：若 __init__ 里建 Http / 发请求就会被抓住。 | class BombHttp: |
| BombHttp.__init__@116 | def | L116-117 |  | def __init__(self, *a, **k): |
| BombHttp.fetch@119 | def | L119-120 |  | def fetch(self, *a, **k): |
| BadHttp@190 | class | L190-198 |  | class BadHttp: |
| BadHttp.__init__@191 | def | L191-192 |  | def __init__(self, *a, **k): |
| BadHttp.fetch@194 | def | L194-198 |  | def fetch(self, url, **kw): |
