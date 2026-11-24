---
covers:
  - collector/tools/selftest_academic.py
title: Semantic block index: selftest_academic.py (layer 4)
updated: 2026-11-24
---

# 语义块索引：selftest_academic.py（第4层）

**源码文件**：`collector/tools/selftest_academic.py`  
**解析器**：`ast`  
**第5层完整正文**：`read_block(path="collector/tools/selftest_academic.py", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| check@33 | def | L33-38 |  | def check(name: str, got, want) -> None: |
| FakeArxiv@139 | class | L139-145 |  | class FakeArxiv(ArxivSource): |
| FakeArxiv.__init__@140 | def | L140-142 |  | def __init__(self, xml: str): |
| FakeArxiv._get@144 | def | L144-145 |  | def _get(self, url, *, retries=1): |
| FakeOpenAlex@148 | class | L148-162 |  | class FakeOpenAlex(OpenAlexSource): |
| FakeOpenAlex.__init__@149 | def | L149-151 |  | def __init__(self, data): |
| FakeOpenAlex._get_json@153 | def | L153-162 |  | def _get_json(self, url): |
| FakePubmed@165 | class | L165-174 |  | class FakePubmed(PubmedSource): |
| FakePubmed.__init__@166 | def | L166-168 |  | def __init__(self, ids, xml): |
| FakePubmed._get_json@170 | def | L170-171 |  | def _get_json(self, url): |
| FakePubmed._get@173 | def | L173-174 |  | def _get(self, url, *, retries=1): |
| FakeS2@177 | class | L177-185 |  | class FakeS2(S2Source): |
| FakeS2.__init__@178 | def | L178-180 |  | def __init__(self, data=None, fail=0): |
| FakeS2._get@182 | def | L182-185 |  | def _get(self, url, *, retries=1): |
| main@188 | def | L188-297 |  | def main() -> int: |
