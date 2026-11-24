---
covers:
  - collector/llm/audience.py
title: Semantic block index: audience.py (layer 4)
updated: 2026-11-24
---

# 语义块索引：audience.py（第4层）

**源码文件**：`collector/llm/audience.py`  
**解析器**：`ast`  
**第5层完整正文**：`read_block(path="collector/llm/audience.py", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| plan_audience_input@112 | def | L112-145 | 把评论/弹幕确定性地预筛成一段给 LLM 的文本。 | def plan_audience_input( |
| _pick_comments@152 | def | L152-170 | 按赞数预筛评论。保持稳定：同赞按原顺序（Python sort 是稳定的）。 | def _pick_comments(items: list[dict], limit: int) -> list[dict]: |
| _pick_danmaku@173 | def | L173-215 | 按「频次 × 长度」预筛弹幕，去重并保留频次。 | def _pick_danmaku(items: list[dict], limit: int) -> list[dict]: |
| _fmt_ts@218 | def | L218-222 |  | def _fmt_ts(ms: int) -> str: |
| _direction_conflict@225 | def | L225-249 | claim 的立场与 quote 的方向是否相反。 | def _direction_conflict(claim: str, quote: str) -> bool: |
| _clamp_support@259 | def | L259-281 | 把模型自报的 support 压到材料里实际能支持的上限。 | def _clamp_support(reported: int, claim: str, material: str) -> int: |
| _source_of@296 | def | L296-310 | 按 quote 所在那一行的前缀判断它来自评论还是弹幕。 | def _source_of(quote: str, material: str) -> str: |
| _norm@313 | def | L313-314 |  | def _norm(t: str) -> str: |
| _verbatim@317 | def | L317-326 | quote 是否逐字出现在材料里（只归并空白，不忽略标点/字词）。 | def _verbatim(quote: str, material: str) -> bool: |
| summarize_audience@329 | def | L329-429 | 把评论/弹幕归纳成卡片可用的几段。没材料时返回 None（不烧一次 LLM）。 | def summarize_audience( |
| render_audience_md@432 | def | L432-461 | 把归纳结果渲染成卡片正文的一节。没有内容时返回空串（不写空标题）。 | def render_audience_md(aud: dict[str, Any], *, n_comments: int, n_danm… |
