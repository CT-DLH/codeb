---
covers:
  - collector/tools/llm_projects.py
title: Semantic block index: llm_projects.py (layer 4)
updated: 2026-11-24
---

# 语义块索引：llm_projects.py（第4层）

**源码文件**：`collector/tools/llm_projects.py`  
**解析器**：`ast`  
**第5层完整正文**：`read_block(path="collector/tools/llm_projects.py", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| section_lines@34 | def | L34-48 | 取 ## 小节 下的非空行，去掉 markdown 前缀（### / - / *），保留原文供溯源。 | def section_lines(card_path: Path, section: str) -> list[str]: |
| main@51 | def | L51-143 |  | def main() -> int: |
