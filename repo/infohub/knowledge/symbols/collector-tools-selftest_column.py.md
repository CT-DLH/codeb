---
covers:
  - collector/tools/selftest_column.py
title: Semantic block index: selftest_column.py (layer 4)
updated: 2026-11-24
---

# 语义块索引：selftest_column.py（第4层）

**源码文件**：`collector/tools/selftest_column.py`  
**解析器**：`ast`  
**第5层完整正文**：`read_block(path="collector/tools/selftest_column.py", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| check@35 | def | L35-42 |  | def check(cond: bool, msg: str) -> None: |
| FakeResult@45 | class | L45-56 |  | class FakeResult: |
| FakeResult.__init__@46 | def | L46-56 |  | def __init__(self, ok=True, text="", content=b"", content_type="text/h… |
| FakeHttp@59 | class | L59-77 | 按 URL 返回预设页面或附件字节，并记下每一次 fetch。 | class FakeHttp: |
| FakeHttp.__init__@62 | def | L62-65 |  | def __init__(self, pages: dict[str, str], blobs: dict[str, bytes]): |
| FakeHttp.fetch@67 | def | L67-77 |  | def fetch(self, url: str, **kw): |
| make_docx@80 | def | L80-88 |  | def make_docx(text: str) -> bytes: |
| page@94 | def | L94-99 |  | def page(ids: range, *, next_href="", attachments=()): |
| main@113 | def | L113-218 |  | def main() -> int: |
| write@117 | def | L117-120 |  | def write(obj: dict, name="s.yaml"): |
