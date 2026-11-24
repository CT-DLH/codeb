---
covers:
  - collector/tools/crawl_course.py
title: Semantic block index: crawl_course.py (layer 4)
updated: 2026-11-24
---

# 语义块索引：crawl_course.py（第4层）

**源码文件**：`collector/tools/crawl_course.py`  
**解析器**：`ast`  
**第5层完整正文**：`read_block(path="collector/tools/crawl_course.py", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| log@65 | def | L65-66 |  | def log(msg: str) -> None: |
| run@69 | def | L69-73 |  | def run(cmd: list[str], cwd: Path, timeout: int = 3600) -> tuple[int, … |
| tail@76 | def | L76-78 |  | def tail(text: str, n: int = 4) -> str: |
| login_state@81 | def | L81-88 | 探登录态：cnki 看 last_login 标记，小红书看 cookie。 | def login_state(source: str) -> bool: |
| pending_urls@91 | def | L91-103 | 取该平台「已登记但没正文」的 URL。 | def pending_urls(platform: str) -> list[str]: |
| main@106 | def | L106-284 |  | def main() -> int: |
