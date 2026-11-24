---
covers:
  - collector/refs/queue.py
title: Semantic block index: queue.py (layer 4)
updated: 2026-11-24
---

# 语义块索引：queue.py（第4层）

**源码文件**：`collector/refs/queue.py`  
**解析器**：`ast`  
**第5层完整正文**：`read_block(path="collector/refs/queue.py", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| Entry@27 | class | L27-41 |  | class Entry: |
| Entry.add_source@33 | def | L33-36 |  | def add_source(self, from_ref: str, raw: str) -> None: |
| Entry.to_dict@38 | def | L38-41 |  | def to_dict(self) -> dict: |
| default_db@44 | def | L44-47 |  | def default_db() -> Path: |
| card_ids_by_homepage@50 | def | L50-60 | 主页 slug → card_id。队列要能指回具体那张卡，不然关联层接不上。 | def card_ids_by_homepage(domain: str = "mentor", cards_dir: Path \| st… |
| from_crawl_db@63 | def | L63-90 | [(来源标记, 引用串)]，来源标记 = mentor/<card_id>（卡找不到时用 slug 兜底）。 | def from_crawl_db(db_path: Path \| str \| None = None, slugs: list[str… |
| from_cards@93 | def | L93-112 | 从已落卡正文里取引用串——证明这条链路不限于采集库，卡片本身就是入口。 | def from_cards(domain: str, section: str = "科研论文", cards_dir: Path \| … |
| from_llm_jsonl@115 | def | L115-149 | LLM 抽好的题录（llm_compare --out 的产物）→ Entry。 | def from_llm_jsonl(path: Path \| str) -> list[Entry]: |
| build_entries@152 | def | L152-167 |  | def build_entries(pairs: list[tuple[str, str]], lex: dict \| None = No… |
| write_outputs@170 | def | L170-199 |  | def write_outputs(entries: list[Entry], out_dir: Path \| str) -> dict[… |
