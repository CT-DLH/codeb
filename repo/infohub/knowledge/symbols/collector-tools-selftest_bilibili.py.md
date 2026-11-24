---
covers:
  - collector/tools/selftest_bilibili.py
title: Semantic block index: selftest_bilibili.py (layer 4)
updated: 2026-11-24
---

# 语义块索引：selftest_bilibili.py（第4层）

**源码文件**：`collector/tools/selftest_bilibili.py`  
**解析器**：`ast`  
**第5层完整正文**：`read_block(path="collector/tools/selftest_bilibili.py", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| check@26 | def | L26-31 |  | def check(name: str, got, want) -> None: |
| make_view@34 | def | L34-41 |  | def make_view(bvid: str, pages: list[dict], desc: str = "一套竞赛练习题") -> … |
| main@44 | def | L44-186 |  | def main() -> int: |
| fake_call_signed@75 | def | L75-81 |  | def fake_call_signed(path, params=None, *, bucket="core", sign=False): |
| fake_raw@83 | def | L83-86 |  | def fake_raw(url, *, bucket="core", retries=1): |
| no_subtitles@112 | def | L112-115 |  | def no_subtitles(path, params=None, *, bucket="core", sign=False): |
| notfound@134 | def | L134-135 |  | def notfound(url, *, bucket="core", retries=1): |
