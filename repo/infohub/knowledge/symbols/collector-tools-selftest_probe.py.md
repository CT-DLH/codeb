---
covers:
  - collector/tools/selftest_probe.py
title: Semantic block index: selftest_probe.py (layer 4)
updated: 2026-11-24
---

# 语义块索引：selftest_probe.py（第4层）

**源码文件**：`collector/tools/selftest_probe.py`  
**解析器**：`ast`  
**第5层完整正文**：`read_block(path="collector/tools/selftest_probe.py", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| check@31 | def | L31-38 |  | def check(cond: bool, msg: str) -> None: |
| FakeResult@41 | class | L41-51 |  | class FakeResult: |
| FakeResult.__init__@42 | def | L42-51 |  | def __init__(self, ok=True, text="", reason="", status=200, robots_not… |
| FakeHttp@54 | class | L54-67 |  | class FakeHttp: |
| FakeHttp.__init__@55 | def | L55-58 |  | def __init__(self, pages=None, *, fail=None): |
| FakeHttp.fetch@60 | def | L60-67 |  | def fetch(self, url, **kw): |
| page@70 | def | L70-75 |  | def page(ids, *, next_href="", attachments=()): |
| main@89 | def | L89-214 |  | def main() -> int: |
