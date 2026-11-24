---
covers:
  - collector/tools/collect_site.py
title: Semantic block index: collect_site.py (layer 4)
updated: 2026-11-24
---

# 语义块索引：collect_site.py（第4层）

**源码文件**：`collector/tools/collect_site.py`  
**解析器**：`ast`  
**第5层完整正文**：`read_block(path="collector/tools/collect_site.py", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| item_fingerprint@48 | def | L48-59 | 一条栏目内容的内容指纹：url + 标题 + 正文，稳定且可复现。 | def item_fingerprint(item: dict) -> str: |
| build_register@62 | def | L62-101 | --register 回调工厂：把一条栏目内容登记进 pipeline.db（裁决 7）。 | def build_register(spec: dict, pipeline_store: "PipelineStore"): |
| _register@77 | def | L77-99 |  | def _register(item: dict) -> bool: |
| _default_teacher_targets@104 | def | L104-120 | 教师主页型没给目标时的默认值：spec 的 output.domain 里所有带主页的卡。 | def _default_teacher_targets(spec: dict) -> list[str]: |
| _run_teacher_home@123 | def | L123-200 | 教师主页型：转给 runner.run（L2 = adapters/teacher_home.py）。 | def _run_teacher_home(spec: dict, args: argparse.Namespace) -> int: |
| _emit@203 | def | L203-271 | 列表型的报告输出（红线 5：三个数分开列，绝不合并成一个「成功 N 条」）。 | def _emit( |
| main@274 | def | L274-341 |  | def main(argv: list[str] \| None = None) -> int: |
