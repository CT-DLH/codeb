---
covers:
  - collector/tools/site_probe.py
title: Semantic block index: site_probe.py (layer 4)
updated: 2026-11-24
---

# 语义块索引：site_probe.py（第4层）

**源码文件**：`collector/tools/site_probe.py`  
**解析器**：`ast`  
**第5层完整正文**：`read_block(path="collector/tools/site_probe.py", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| scoped_hits@50 | def | L50-70 | 选择器命中数，带作用域。 | def scoped_hits(html: str, selector: str, scope_selector: str = "") ->… |
| _flatten_selectors@73 | def | L73-84 | 把 spec 的 selectors 展平成 (路径, 选择器)，逐个带作用域报告。 | def _flatten_selectors(spec: dict \| None) -> list[tuple[str, str]]: |
| _result_html@90 | def | L90-95 |  | def _result_html(result) -> str: |
| _candidate_detail@98 | def | L98-131 | 每个翻页候选各自的新增条目数：0 就是软 404，直接排除。 | def _candidate_detail(client, html: str, url: str, base_keys: set[str]… |
| run_probe@134 | def | L134-197 | 抓一次主页 + 逐个翻页候选，返回诊断报告 dict。http 可注入（离线自检）。 | def run_probe(url: str, *, http=None, spec: dict \| None = None, |
| _emit@203 | def | L203-225 |  | def _emit(report: dict, as_json: bool) -> None: |
| main@228 | def | L228-271 |  | def main(argv: list[str] \| None = None) -> int: |
