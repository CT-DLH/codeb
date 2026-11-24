---
covers:
  - collector/refs/llm_parse.py
title: Semantic block index: llm_parse.py (layer 4)
updated: 2026-11-24
---

# 语义块索引：llm_parse.py（第4层）

**源码文件**：`collector/refs/llm_parse.py`  
**解析器**：`ast`  
**第5层完整正文**：`read_block(path="collector/refs/llm_parse.py", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| build_user_prompt@70 | def | L70-76 |  | def build_user_prompt(lines: list[str], offset: int = 0) -> str: |
| _squash@82 | def | L82-83 |  | def _squash(text: str) -> str: |
| _strip_author_prefix@86 | def | L86-99 | 模型偶尔把作者一起抄进标题（实测 2/128：'Y. Xu, A new kernel …'）。 | def _strip_author_prefix(title: str, authors: list[str]) -> str: |
| normalize_papers@102 | def | L102-142 | 模型输出 → 可用题录。纯函数，离线可测。 | def normalize_papers( |
| dedupe_papers@145 | def | L145-154 |  | def dedupe_papers(papers: list[dict[str, Any]]) -> list[dict[str, Any]… |
| llm_parse_citations@157 | def | L157-217 | 一张卡（一组行）→ 题录列表。 | def llm_parse_citations( |
| grammar_papers@222 | def | L222-240 | ---------------------------------------------------------------- 对照 | def grammar_papers(lines: list[str]) -> list[dict[str, Any]]: |
| diff_papers@243 | def | L243-249 |  | def diff_papers(llm: list[dict[str, Any]], gram: list[dict[str, Any]])… |
