---
covers:
  - collector/tools/run_source.py
title: Semantic block index: run_source.py (layer 4)
updated: 2026-11-24
---

# 语义块索引：run_source.py（第4层）

**源码文件**：`collector/tools/run_source.py`  
**解析器**：`ast`  
**第5层完整正文**：`read_block(path="collector/tools/run_source.py", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| _heat@52 | def | L52-63 | 取「热度」：由插件声明哪个指标代表多少人看过/赞过，内核不猜平台字段名。 | def _heat(src, item) -> int: |
| _search_all@66 | def | L66-117 | 跟随 cursor 翻页，直到够数或没有下一页。 | def _search_all(src, query: str, max_items: int, kind: str = "", |
| _topic_query@120 | def | L120-134 | 主题 → 检索词要按源的语种挑「方言」（设计稿 §4）。 | def _topic_query(src, topic, explicit: str) -> str: |
| _expand_urls@140 | def | L140-155 | --urls 的参数可以是链接、也可以是存链接的文件；微信里粘贴的分享文案同样能抠出链接。 | def _expand_urls(src, given: list[str]) -> list[str]: |
| _import_urls@158 | def | L158-181 | 导入器入口：协议上没有搜索接口的源（小红书、知网）从链接进内核（设计稿 §7）。 | def _import_urls(src, given: list[str], max_items: int) -> list: |
| main@184 | def | L184-407 |  | def main(argv: list[str] \| None = None) -> int: |
| write_json@218 | def | L218-239 |  | def write_json() -> None: |
