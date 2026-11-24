---
covers:
  - collector/zhihu_pipe/sources/__init__.py
title: Semantic block index: __init__.py (layer 4)
updated: 2026-11-24
---

# 语义块索引：__init__.py（第4层）

**源码文件**：`collector/zhihu_pipe/sources/__init__.py`  
**解析器**：`ast`  
**第5层完整正文**：`read_block(path="collector/zhihu_pipe/sources/__init__.py", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| _register_site_sources@47 | def | L47-63 |  | def _register_site_sources() -> None: |
| available@71 | def | L71-72 |  | def available() -> list[str]: |
| site_source_names@75 | def | L75-77 | 已注册的站点源名（供 capabilities.py 把平台源与站点源分栏）。 | def site_source_names() -> tuple[str, ...]: |
| is_site_source@80 | def | L80-81 |  | def is_site_source(name: str) -> bool: |
| get_source@84 | def | L84-95 |  | def get_source(name: str) -> Source: |
| enabled_sources@98 | def | L98-101 |  | def enabled_sources(names: Iterable[str] \| None = None) -> list[Sourc… |
| capability_report@104 | def | L104-138 | 逐个插件问它自己「能干什么」，产出血缘唯一的能力清单。 | def capability_report() -> dict[str, dict]: |
| body_capable_platforms@141 | def | L141-160 | (可以取正文的平台集合, 逐插件说明)。 | def body_capable_platforms() -> tuple[set[str], dict[str, str]]: |
