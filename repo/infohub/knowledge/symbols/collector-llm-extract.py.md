---
covers:
  - collector/llm/extract.py
title: Semantic block index: extract.py (layer 4)
updated: 2026-11-24
---

# 语义块索引：extract.py（第4层）

**源码文件**：`collector/llm/extract.py`  
**解析器**：`ast`  
**第5层完整正文**：`read_block(path="collector/llm/extract.py", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| LlmUnavailable@36 | class | L36-37 | 没有凭据 / 重试耗尽 / 输出始终不合法。调用方据此回退正则。 | class LlmUnavailable(RuntimeError): |
| ExtractResult@41 | class | L41-48 |  | class ExtractResult: |
| _cache_path@53 | def | L53-56 | ---------------------------------------------------------------- 缓存 | def _cache_path() -> Path: |
| _cache_open@59 | def | L59-72 |  | def _cache_open() -> sqlite3.Connection: |
| cache_key@75 | def | L75-77 |  | def cache_key(prompt_version: str, model: str, name: str, payload: str… |
| cache_get@80 | def | L80-88 |  | def cache_get(key: str) -> tuple[dict[str, Any], str] \| None: |
| cache_put@91 | def | L91-97 |  | def cache_put(key: str, name: str, prompt_version: str, model: str, mo… |
| cache_stats@100 | def | L100-104 |  | def cache_stats() -> dict[str, int]: |
| model_name@109 | def | L109-110 | ---------------------------------------------------------------- 客户端 | def model_name() -> str: |
| _client@113 | def | L113-122 |  | def _client(): |
| _throttle@125 | def | L125-131 |  | def _throttle() -> None: |
| _extra_body@134 | def | L134-150 | 推理型模型（如 Nemotron）会先吐 reasoning_content，把 max_tokens 吃光、content 为空。 | def _extra_body() -> dict[str, Any]: |
| _format_rejected@153 | def | L153-159 | 只有「provider 不认 response_format」才值得换下一种格式；超时/网络错误换格式没用。 | def _format_rejected(err: Exception) -> bool: |
| validate@175 | def | L175-205 | 只支持本项目用得到的子集：type / properties / required / items / enum / nullable。 | def validate(instance: Any, schema: dict[str, Any], path: str = "$") -… |
| _extract_json@208 | def | L208-220 |  | def _extract_json(text: str) -> dict[str, Any] \| None: |
| llm_json@225 | def | L225-305 | ---------------------------------------------------------------- 主入口 | def llm_json( |
| locate@313 | def | L313-316 |  | def locate(quote: str, source: str) -> bool: |
| check_fields@319 | def | L319-337 | 逐字复制检查：命中的字段值必须在原文出现，否则计数（不改值）。 | def check_fields(items: list[dict[str, Any]], source: str, verbatim: t… |
