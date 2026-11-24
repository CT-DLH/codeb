---
covers:
  - collector/zhihu_pipe/runs.py
title: Semantic block index: runs.py (layer 4)
updated: 2026-11-24
---

# 语义块索引：runs.py（第4层）

**源码文件**：`collector/zhihu_pipe/runs.py`  
**解析器**：`ast`  
**第5层完整正文**：`read_block(path="collector/zhihu_pipe/runs.py", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| run_file@27 | def | L27-33 | run_id 会当文件名用（它来自命令行参数），消毒后必须仍落在 active/ 里。 | def run_file(run_id: str) -> Path: |
| pid_alive@36 | def | L36-67 |  | def pid_alive(pid: object) -> bool: |
| register@70 | def | L70-91 | 登记一条正在跑的任务。 | def register(run_id: str, kind: str, *, source: str = "", profile: str… |
| unregister@94 | def | L94-98 |  | def unregister(run_id: str) -> None: |
| read_active@101 | def | L101-121 | 读登记表并按 pid 探活；死的默认顺手清掉（残留不该永久挡住流水线）。 | def read_active(prune: bool = True) -> list[dict]: |
