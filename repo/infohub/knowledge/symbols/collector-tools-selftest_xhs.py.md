---
covers:
  - collector/tools/selftest_xhs.py
title: Semantic block index: selftest_xhs.py (layer 4)
updated: 2026-11-24
---

# 语义块索引：selftest_xhs.py（第4层）

**源码文件**：`collector/tools/selftest_xhs.py`  
**解析器**：`ast`  
**第5层完整正文**：`read_block(path="collector/tools/selftest_xhs.py", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| check@54 | def | L54-59 |  | def check(name: str, got, want) -> None: |
| image_note@62 | def | L62-73 |  | def image_note() -> dict: |
| page@76 | def | L76-80 | 造一个含 JS 痕迹（undefined）与尾随脚本的页面，逼近真实 HTML。 | def page(state: dict) -> str: |
| dom_smoke@83 | def | L83-102 | 在真浏览器里跑搜索页 JS：验选择器与字段翻译，不访问小红书。 | def dom_smoke(src: XhsSource) -> None: |
| main@105 | def | L105-260 |  | def main() -> int: |
| wall@162 | def | L162-163 |  | def wall(url): |
