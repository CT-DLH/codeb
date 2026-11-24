---
covers:
  - collector/zhihu_pipe/busy.py
title: Semantic block index: busy.py (layer 4)
updated: 2026-11-24
---

# 语义块索引：busy.py（第4层）

**源码文件**：`collector/zhihu_pipe/busy.py`  
**解析器**：`ast`  
**第5层完整正文**：`read_block(path="collector/zhihu_pipe/busy.py", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| busy_file@24 | def | L24-25 |  | def busy_file() -> Path: |
| touch@28 | def | L28-37 | 登记「现在有人在用 LLM」。写临时文件再 rename，避免半个 JSON 被读到。 | def touch(kind: str, note: str = "") -> None: |
| current@40 | def | L40-52 | 当前持有者；没有文件或心跳过期都算空闲。 | def current() -> dict \| None: |
| busy@55 | def | L55-62 | 除 exclude_kind（自己）之外还有人在用 LLM 就返回那条记录。 | def busy(exclude_kind: str = "") -> dict \| None: |
| release@65 | def | L65-72 | 收尾时删掉标志；只删自己写的那个，别把刚接手的任务的心跳抹了。 | def release() -> None: |
| held@75 | def | L75-81 | 上下文形式：进入与每条心跳都靠调用方 touch，退出时释放。 | def held(kind: str, note: str = "") -> Iterator[None]: |
