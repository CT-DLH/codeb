---
covers:
  - sizes.py
title: Semantic block index: sizes.py (layer 4)
updated: 2026-11-24
---

# 语义块索引：sizes.py（第4层）

**源码文件**：`sizes.py`  
**解析器**：`ast`  
**第5层完整正文**：`read_block(path="sizes.py", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| count_lines@34 | def | L34-45 | 按 LF 计行，与编辑器显示一致；读 utf-8-sig 去掉可能的 BOM。 | def count_lines(p: Path) -> int: |
| walk_files@48 | def | L48-55 |  | def walk_files(base: Path, exts: set[str] \| None = None): |
| human@73 | def | L73-74 |  | def human(n: int) -> str: |
| cmd_path@77 | def | L77-97 |  | def cmd_path(target: str) -> dict: |
| cmd_modules@100 | def | L100-113 |  | def cmd_modules() -> list[dict]: |
| cmd_overview@116 | def | L116-128 |  | def cmd_overview() -> list[dict]: |
| main@131 | def | L131-166 |  | def main() -> int: |
