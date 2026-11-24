---
covers:
  - collector/tools/selftest_robots.py
title: Semantic block index: selftest_robots.py (layer 4)
updated: 2026-11-24
---

# 语义块索引：selftest_robots.py（第4层）

**源码文件**：`collector/tools/selftest_robots.py`  
**解析器**：`ast`  
**第5层完整正文**：`read_block(path="collector/tools/selftest_robots.py", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| check@34 | def | L34-41 |  | def check(cond: bool, msg: str) -> None: |
| deny_parser@44 | def | L44-47 |  | def deny_parser(): |
| allow_parser@50 | def | L50-53 |  | def allow_parser(): |
| inject@56 | def | L56-57 |  | def inject(root: str, parser, note: str) -> None: |
| main@60 | def | L60-188 |  | def main() -> int: |
| fake@78 | def | L78-79 |  | def fake(root, timeout, ua, _code=code): |
| refuse_open@106 | def | L106-108 |  | def refuse_open(req, **kw): |
| seen_open@128 | def | L128-130 |  | def seen_open(req, **kw): |
| FakeResult@144 | class | L144-151 |  | class FakeResult: |
| FakeHttp@153 | class | L153-155 |  | class FakeHttp: |
| FakeHttp.fetch@154 | def | L154-155 |  | def fetch(self, url, **kw): |
