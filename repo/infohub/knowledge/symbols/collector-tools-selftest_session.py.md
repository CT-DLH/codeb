---
covers:
  - collector/tools/selftest_session.py
title: Semantic block index: selftest_session.py (layer 4)
updated: 2026-11-24
---

# 语义块索引：selftest_session.py（第4层）

**源码文件**：`collector/tools/selftest_session.py`  
**解析器**：`ast`  
**第5层完整正文**：`read_block(path="collector/tools/selftest_session.py", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| check@29 | def | L29-34 |  | def check(name: str, got, want) -> None: |
| make_args@37 | def | L37-43 |  | def make_args(**kw) -> argparse.Namespace: |
| make_session@46 | def | L46-48 |  | def make_session(store: Store, pool, **overrides) -> rs.Session: |
| seed_store@51 | def | L51-62 |  | def seed_store(tmp: Path) -> Store: |
| main@65 | def | L65-169 |  | def main() -> int: |
| fake_run@101 | def | L101-117 |  | def fake_run(argv): |
| failing_run@143 | def | L143-145 |  | def failing_run(argv): |
