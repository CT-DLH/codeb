---
covers:
  - collector/site_crawl/specs.py
title: Semantic block index: specs.py (layer 4)
updated: 2026-11-24
---

# 语义块索引：specs.py（第4层）

**源码文件**：`collector/site_crawl/specs.py`  
**解析器**：`ast`  
**第5层完整正文**：`read_block(path="collector/site_crawl/specs.py", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| SpecError@71 | class | L71-72 | 配置不合法。消息里带配置路径，便于直接定位。 | class SpecError(ValueError): |
| _check_keys@75 | def | L75-80 |  | def _check_keys(obj: Any, allowed: set[str], where: str) -> None: |
| _require@83 | def | L83-86 |  | def _require(obj: dict, keys: list[str], where: str) -> None: |
| _validate_common@89 | def | L89-105 |  | def _validate_common(data: dict) -> None: |
| _validate_output@108 | def | L108-118 |  | def _validate_output(out: Any) -> None: |
| _validate_teacher_home@121 | def | L121-133 |  | def _validate_teacher_home(data: dict) -> None: |
| _validate_list_common@136 | def | L136-168 | 列表型（column_list / announcement_list）共用形状：seeds / paging / attach 都是可选声明，但写了就要合法。 | def _validate_list_common(data: dict) -> None: |
| _validate_column_list@171 | def | L171-173 | 栏目型：与公告列表同族，output 可选。 | def _validate_column_list(data: dict) -> None: |
| _validate_announcement_list@176 | def | L176-179 | 公告列表型：与栏目型同族、复用同一份 L2，但输出是结构化列表，output 必填。 | def _validate_announcement_list(data: dict) -> None: |
| load_spec@190 | def | L190-203 |  | def load_spec(path: str \| Path) -> dict: |
| spec_summary@206 | def | L206-230 |  | def spec_summary(spec: dict) -> str: |
