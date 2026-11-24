---
covers:
  - collector/site_crawl/runner.py
title: Semantic block index: runner.py (layer 4)
updated: 2026-11-24
---

# 语义块索引：runner.py（第4层）

**源码文件**：`collector/site_crawl/runner.py`  
**解析器**：`ast`  
**第5层完整正文**：`read_block(path="collector/site_crawl/runner.py", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| _http_from_spec@33 | def | L33-46 |  | def _http_from_spec(spec: dict) -> Http: |
| _name_key@49 | def | L49-51 |  | def _name_key(value: str) -> str: |
| _same_person@54 | def | L54-62 | 卡片标题与主页姓名必须对得上；只容忍「陈斌」 vs「陈斌2020」这种编号后缀。 | def _same_person(expected: str, actual: str) -> bool: |
| _split_target@65 | def | L65-69 |  | def _split_target(target) -> tuple[str, str, str]: |
| _brief@72 | def | L72-91 | 报告用的摘要：敏感值只留「采到了没有」。 | def _brief(record: dict, status: str, show_pii: bool = False, *, card_… |
| _print_brief@94 | def | L94-108 |  | def _print_brief(brief: dict, target: str) -> None: |
| run@111 | def | L111-228 | 跑一轮站点同步。 | def run( |
