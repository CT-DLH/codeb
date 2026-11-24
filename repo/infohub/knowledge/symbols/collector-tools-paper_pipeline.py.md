---
covers:
  - collector/tools/paper_pipeline.py
title: Semantic block index: paper_pipeline.py (layer 4)
updated: 2026-11-24
---

# 语义块索引：paper_pipeline.py（第4层）

**源码文件**：`collector/tools/paper_pipeline.py`  
**解析器**：`ast`  
**第5层完整正文**：`read_block(path="collector/tools/paper_pipeline.py", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| run@41 | def | L41-59 | 跑一条命令，只留最后几行输出——3600 篇的日志全打出来没人看。 | def run(cmd: list[str], cwd: Path, label: str, tail: int = 6) -> tuple… |
| mcp_import@62 | def | L62-72 | 走 MCP 落卡：判重、合并、来源登记都归导入内核，这里只负责触发。 | def mcp_import(config: str, dry: bool = False) -> tuple[int, str]: |
| main@75 | def | L75-147 |  | def main() -> int: |
