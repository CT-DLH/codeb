---
covers:
  - collector/tools/run_site.py
title: Semantic block index: run_site.py (layer 4)
updated: 2026-11-24
---

# 语义块索引：run_site.py（第4层）

**源码文件**：`collector/tools/run_site.py`  
**解析器**：`ast`  
**第5层完整正文**：`read_block(path="collector/tools/run_site.py", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| build_site_register@49 | def | L49-82 | --register 回调：把一条教师记录登记进 pipeline.db（裁决 7）。 | def build_site_register(spec: dict, pipeline_store: "PipelineStore"): |
| _register@60 | def | L60-80 |  | def _register(record: dict, sha1: str) -> bool: |
| _cards_dir_candidates@85 | def | L85-110 | --from-cards 的候选目录，按优先级排（写死顺序，解析与报错共用一份）。 | def _cards_dir_candidates(source: str) -> list[Path]: |
| _resolve_cards_dir@113 | def | L113-116 | 把 --from-cards 的取值解析成卡片目录（不存在时返回首个候选，由调用方报错）。 | def _resolve_cards_dir(source: str) -> Path: |
| load_card_targets@119 | def | L119-164 | 从 cards/<domain> 读 ext.homepage，生成带「预期姓名」的批量目标。 | def load_card_targets(source: str, only: list[str]) -> tuple[list[dict… |
| main@167 | def | L167-254 |  | def main(argv: list[str] \| None = None) -> int: |
