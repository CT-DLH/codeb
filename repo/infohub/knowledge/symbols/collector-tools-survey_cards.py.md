---
covers:
  - collector/tools/survey_cards.py
title: Semantic block index: survey_cards.py (layer 4)
updated: 2026-11-24
---

# 语义块索引：survey_cards.py（第4层）

**源码文件**：`collector/tools/survey_cards.py`  
**解析器**：`ast`  
**第5层完整正文**：`read_block(path="collector/tools/survey_cards.py", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| load_list@86 | def | L86-103 | 与 run_survey.load_list 同一口径，多记一个行号用于溯源。 | def load_list(path: Path) -> list[dict]: |
| register_urls@106 | def | L106-136 | 序号 → 该实体历史上检索到过的 URL 清单。 | def register_urls(name: str) -> dict[str, list[str]]: |
| db_rows@139 | def | L139-157 | 库里所有平台的已登记内容（含知乎等），归属靠 URL 清单匹配。 | def db_rows() -> list[tuple[str, str, str, float, str]]: |
| _norm@160 | def | L160-163 | 比对用：只留中日韩文字与数字，去掉「第九届」「2026」「_百度百科」这类外壳。 | def _norm(text: str) -> str: |
| assign@166 | def | L166-231 | 归属：优先按检索清单，其次按标题里的项目名兜底。 | def assign(url_map: dict[str, list[str]], rows: list[tuple], |
| body_of@234 | def | L234-265 | 竞赛卡正文：原文规则 + 候选网址 + 关联采集概况。全部来自已有产物。 | def body_of(row: dict, items: list[dict]) -> str: |
| load_curated_notes@268 | def | L268-274 | 兼容包装：实现已移到 survey_refs.load_curated_notes（能力模块，可单独复用）。 | def load_curated_notes() -> dict[str, str]: |
| main@277 | def | L277-432 |  | def main(argv: list[str] \| None = None) -> int: |
