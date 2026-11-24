---
covers:
  - collector/tools/crawl_long.py
title: Semantic block index: crawl_long.py (layer 4)
updated: 2026-11-24
---

# 语义块索引：crawl_long.py（第4层）

**源码文件**：`collector/tools/crawl_long.py`  
**解析器**：`ast`  
**第5层完整正文**：`read_block(path="collector/tools/crawl_long.py", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| _read_round_json@317 | def | L317-327 | 本轮统计来自 run_source 的 --json-out，不再用正则解析它的中文 stdout。 | def _read_round_json(path: Path) -> dict: |
| build_argv@330 | def | L330-345 |  | def build_argv(profile: str, spec: dict, query: str, args, round_json:… |
| run_one@348 | def | L348-361 |  | def run_one(argv: list, timeout: int) -> tuple: |
| main@364 | def | L364-516 |  | def main() -> int: |
| _match@387 | def | L387-388 |  | def _match(s: dict) -> bool: |
| log@406 | def | L406-410 |  | def log(msg: str) -> None: |
| next_query@435 | def | L435-439 |  | def next_query(spec: dict) -> str: |
| save_progress@441 | def | L441-444 |  | def save_progress() -> None: |
