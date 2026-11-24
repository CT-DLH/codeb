---
covers:
  - collector/tools/tag_cards.py
title: Semantic block index: tag_cards.py (layer 4)
updated: 2026-11-24
---

# 语义块索引：tag_cards.py（第4层）

**源码文件**：`collector/tools/tag_cards.py`  
**解析器**：`ast`  
**第5层完整正文**：`read_block(path="collector/tools/tag_cards.py", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| read_frontmatter@125 | def | L125-133 |  | def read_frontmatter(path: Path) -> dict \| None: |
| brief_context@136 | def | L136-160 | 给模型的材料描述：短到能批量塞进一个请求，又足够判断方向。 | def brief_context(fm: dict) -> str: |
| call_llm@163 | def | L163-180 | 一次请求给一批材料分类。返回每条的标签列表（与输入等长，失败则空列表）。 | def call_llm(batch: list[str]) -> list[list[str]]: |
| parse_items@183 | def | L183-245 | 三层兜底：JSON → 抠 JSON 片段 → 放弃这一批（宁可空着也不乱写）。 | def parse_items(content: str, expected: int) -> list[list[str]]: |
| main@248 | def | L248-342 |  | def main() -> int: |
