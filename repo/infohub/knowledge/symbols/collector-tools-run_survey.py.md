---
covers:
  - collector/tools/run_survey.py
title: Semantic block index: run_survey.py (layer 4)
updated: 2026-11-24
---

# 语义块索引：run_survey.py（第4层）

**源码文件**：`collector/tools/run_survey.py`  
**解析器**：`ast`  
**第5层完整正文**：`read_block(path="collector/tools/run_survey.py", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| load_list@57 | def | L57-72 | 解析名单文件。序号/名称必填，检索词缺省用名称，备注可空。 | def load_list(path: Path) -> list[dict]: |
| load_state@75 | def | L75-81 |  | def load_state(path: Path) -> dict: |
| save_state@84 | def | L84-86 |  | def save_state(path: Path, state: dict) -> None: |
| run@89 | def | L89-102 | 跑一条命令，只留尾部输出——64 条实体的日志全打出来没人看。 | def run(cmd: list[str], label: str, tail: int = 4) -> tuple[int, str]: |
| query_variants@119 | def | L119-166 | 候选检索词，按「信息量从多到少」排；去重且保序。 | def query_variants(row: dict) -> list[str]: |
| _read_urls@169 | def | L169-177 | 读一份 run_source --json-out 的结果，取它的 URL 清单（缺失/坏文件当空）。 | def _read_urls(json_out: Path) -> list[str]: |
| _merge_urls@180 | def | L180-194 | 把一份结果里的 URL 并进该实体的累积清单，返回合并后的整份清单。 | def _merge_urls(state: dict, key: str, json_out: Path) -> list[str]: |
| stage_register@197 | def | L197-256 | 每个实体按候选检索词依次试 Bing → 登记元数据进库。 | def stage_register(rows: list[dict], state: dict, args) -> None: |
| stage_enrich@259 | def | L259-285 | 把 web 源已登记的 URL 一次性交给 enrich_batch 补正文。 | def stage_enrich(state: dict, args) -> None: |
| stage_zhihu@288 | def | L288-320 | 同一批实体名丢给知乎源。已有采集器，不新写实现——这就是「复用」。 | def stage_zhihu(rows: list[dict], state: dict, args) -> None: |
| write_report@323 | def | L323-349 | 人读的报告：每个实体一行，落没落、拿到几条、缺什么。 | def write_report(rows: list[dict], state: dict, args) -> None: |
| main@352 | def | L352-400 |  | def main(argv: list[str] \| None = None) -> int: |
