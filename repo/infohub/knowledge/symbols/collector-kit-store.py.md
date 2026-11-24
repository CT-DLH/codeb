---
covers:
  - collector/kit/store.py
title: Semantic block index: store.py (layer 4)
updated: 2026-11-24
---

# 语义块索引：store.py（第4层）

**源码文件**：`collector/kit/store.py`  
**解析器**：`ast`  
**第5层完整正文**：`read_block(path="collector/kit/store.py", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| connect@25 | def | L25-37 | 打开（必要时创建）一个 sqlite 库，固定姿势一次做齐。 | def connect(path: str \| Path, *, timeout: float = 5.0) -> sqlite3.Con… |
| user_version@40 | def | L40-42 |  | def user_version(conn: sqlite3.Connection) -> int: |
| migrate@45 | def | L45-77 | 按版本号升序执行尚未跑过的 SQL，返回本次实际执行的版本号列表。 | def migrate(conn: sqlite3.Connection, migrations: Iterable[tuple[int, … |
| ensure_columns@80 | def | L80-100 | 给已有表补列（只加不删、不改类型），返回真正补上的列名。 | def ensure_columns(conn: sqlite3.Connection, table: str, |
