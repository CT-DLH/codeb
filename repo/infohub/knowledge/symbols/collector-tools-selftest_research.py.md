---
covers:
  - collector/tools/selftest_research.py
title: Semantic block index: selftest_research.py (layer 4)
updated: 2026-11-24
---

# 语义块索引：selftest_research.py（第4层）

**源码文件**：`collector/tools/selftest_research.py`  
**解析器**：`ast`  
**第5层完整正文**：`read_block(path="collector/tools/selftest_research.py", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| check@23 | def | L23-30 |  | def check(name: str, got, want) -> None: |
| section@33 | def | L33-34 |  | def section(title: str) -> None: |
| test_relevance@38 | def | L38-91 | ---------------------------------------------------------------- 1. 跑题闸 | def test_relevance() -> None: |
| ot@42 | def | L42-43 | 带桥接词的调用形式（off_topic 的第三参） | def ot(text, tt, bt=frozenset()): |
| test_collision_page@95 | def | L95-154 | ---------------------------------------------------------------- 1b. 撞名页 | def test_collision_page() -> None: |
| test_classify_source@158 | def | L158-196 | ---------------------------------------------------------------- 2. 一手/二手 | def test_classify_source() -> None: |
| test_evidence_gates@200 | def | L200-221 | ---------------------------------------------------------------- 3. 证据过滤 | def test_evidence_gates() -> None: |
| test_verbatim@224 | def | L224-252 |  | def test_verbatim() -> None: |
| test_query_rewrite@256 | def | L256-281 | ---------------------------------------------------------------- 4. 查询重排 | def test_query_rewrite() -> None: |
| one@266 | def | L266-267 |  | def one(q: str) -> dict: |
| test_english_topic@285 | def | L285-319 | ---------------------------------------------------------------- 4b. 英文主题 | def test_english_topic() -> None: |
| test_round_budget@323 | def | L323-330 | ---------------------------------------------------------------- 5. 轮次语义 | def test_round_budget() -> None: |
| main@333 | def | L333-350 |  | def main() -> int: |
