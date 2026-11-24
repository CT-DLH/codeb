---
covers:
  - collector/llm/projects.py
title: Semantic block index: projects.py (layer 4)
updated: 2026-11-24
---

# 语义块索引：projects.py（第4层）

**源码文件**：`collector/llm/projects.py`  
**解析器**：`ast`  
**第5层完整正文**：`read_block(path="collector/llm/projects.py", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| _squash@96 | def | L96-97 |  | def _squash(text: str) -> str: |
| _fold@100 | def | L100-102 | 比对用：去空白、统一连字符与大小写。只用于「这个值在不在原文里」，不改写值本身。 | def _fold(text: str) -> str: |
| build_user_prompt@105 | def | L105-108 |  | def build_user_prompt(lines: list[str], offset: int = 0) -> str: |
| _pick@111 | def | L111-116 | 非 name 字段必须逐字出现在这一行，否则当作模型补出来的，丢掉。 | def _pick(value: Any, row: str) -> str \| None: |
| _pick_role@119 | def | L119-121 |  | def _pick_role(value: Any, row: str) -> str \| None: |
| _pick_amount@124 | def | L124-126 |  | def _pick_amount(value: Any, row: str) -> str \| None: |
| _pick_code@129 | def | L129-133 |  | def _pick_code(value: Any, row: str) -> str \| None: |
| normalize_projects@136 | def | L136-191 | 模型输出 → 可用项目条目。纯函数，离线可测。 | def normalize_projects( |
| extract_projects@194 | def | L194-259 | 一张卡的项目清单 → 项目条目。 | def extract_projects( |
