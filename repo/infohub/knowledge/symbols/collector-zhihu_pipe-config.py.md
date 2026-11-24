---
covers:
  - collector/zhihu_pipe/config.py
title: Semantic block index: config.py (layer 4)
updated: 2026-11-24
---

# 语义块索引：config.py（第4层）

**源码文件**：`collector/zhihu_pipe/config.py`  
**解析器**：`ast`  
**第5层完整正文**：`read_block(path="collector/zhihu_pipe/config.py", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| load_dotenv@16 | def | L16-35 |  | def load_dotenv() -> None: |
| get_env@38 | def | L38-40 |  | def get_env(key: str, default: str = "") -> str: |
| github_token@43 | def | L43-45 | GitHub PAT。不填也能跑，但配额从 5000/h 降到 60/h、搜索从 30/min 降到 10/min。 | def github_token() -> str: |
| bili_cookie@48 | def | L48-54 | B 站浏览器 Cookie（整串，形如 SESSDATA=xxx; bili_jct=yyy; ...）。 | def bili_cookie() -> str: |
| xhs_cookie@57 | def | L57-65 | 小红书浏览器 Cookie（整串，必须含 web_session）。 | def xhs_cookie() -> str: |
| web_pages@68 | def | L68-81 | web 源翻几页，默认 1。 | def web_pages() -> int: |
| web_timeout@84 | def | L84-89 | web 源单次请求超时（秒），默认 20。被墙/慢站可调小。 | def web_timeout() -> float: |
