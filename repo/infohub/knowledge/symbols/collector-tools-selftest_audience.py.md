---
covers:
  - collector/tools/selftest_audience.py
title: Semantic block index: selftest_audience.py (layer 4)
updated: 2026-11-24
---

# 语义块索引：selftest_audience.py（第4层）

**源码文件**：`collector/tools/selftest_audience.py`  
**解析器**：`ast`  
**第5层完整正文**：`read_block(path="collector/tools/selftest_audience.py", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| check@22 | def | L22-29 |  | def check(name: str, got, want) -> None: |
| section@32 | def | L32-33 |  | def section(title: str) -> None: |
| test_dm_protobuf@37 | def | L37-72 | ------------------------------------------------------------ 1. 弹幕 protobuf | def test_dm_protobuf() -> None: |
| varint@42 | def | L42-49 |  | def varint(v: int) -> bytes: |
| elem@51 | def | L51-57 |  | def elem(content: str, progress: int, weight: int = 0) -> bytes: |
| test_prefilter@76 | def | L76-116 | ------------------------------------------------------------ 2. 预筛 | def test_prefilter() -> None: |
| test_gates@120 | def | L120-162 | ------------------------------------------------------------ 3. 三道闸 | def test_gates() -> None: |
| test_no_dump@166 | def | L166-182 | ------------------------------------------------------------ 4. 不做破坏性记录 | def test_no_dump() -> None: |
| main@185 | def | L185-199 |  | def main() -> int: |
