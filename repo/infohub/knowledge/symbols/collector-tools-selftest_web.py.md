---
covers:
  - collector/tools/selftest_web.py
title: Semantic block index: selftest_web.py (layer 4)
updated: 2026-11-24
---

# 语义块索引：selftest_web.py（第4层）

**源码文件**：`collector/tools/selftest_web.py`  
**解析器**：`ast`  
**第5层完整正文**：`read_block(path="collector/tools/selftest_web.py", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| check@44 | def | L44-49 |  | def check(name: str, got, want) -> None: |
| check_raises@52 | def | L52-62 |  | def check_raises(name: str, fn, exc) -> None: |
| check_ok@65 | def | L65-72 |  | def check_ok(name: str, fn) -> None: |
| test_unwrap@106 | def | L106-120 | ------------------------------------------------------------------ 1. 跳转壳 | def test_unwrap() -> None: |
| test_canonicalize@124 | def | L124-148 | ------------------------------------------------------------------ 2. 身份 | def test_canonicalize() -> None: |
| test_owner@151 | def | L151-166 |  | def test_owner() -> None: |
| test_tokens@169 | def | L169-174 |  | def test_tokens() -> None: |
| _items@178 | def | L178-180 | ------------------------------------------------------------------ 5. 降级判据 | def _items(*titles: str) -> list[Item]: |
| test_degraded@183 | def | L183-213 |  | def test_degraded() -> None: |
| test_parse@217 | def | L217-236 | ------------------------------------------------------------------ 6. 解析 | def test_parse() -> None: |
| test_fetch@240 | def | L240-289 | fetch 的三条路：抽到正文 / robots 拒绝 / 抽不出来。 | def test_fetch() -> None: |
| test_protocol@292 | def | L292-325 |  | def test_protocol() -> None: |
| test_build_guards@328 | def | L328-342 |  | def test_build_guards() -> None: |
| test_assign@345 | def | L345-403 | 归属：清单是凭据，标题只是兜底——两条都踩过坑，必须钉住。 | def test_assign() -> None: |
| main@406 | def | L406-423 |  | def main() -> int: |
