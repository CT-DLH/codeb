---
covers:
  - collector/kit/paging.py
title: Semantic block index: paging.py (layer 4)
updated: 2026-11-24
---

# 语义块索引：paging.py（第4层）

**源码文件**：`collector/kit/paging.py`  
**解析器**：`ast`  
**第5层完整正文**：`read_block(path="collector/kit/paging.py", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| is_paging_label@93 | def | L93-96 | 锚文本是不是分页控件（去空白 + 小写后判定；含纯数字 / 空文本）。 | def is_paging_label(text: str) -> bool: |
| item_key@102 | def | L102-127 | 条目 → 可比较的键。dict 依次取 url/href/link/id/title；对象取 url/id/title。 | def item_key(item: Any) -> str: |
| _key_str@130 | def | L130-134 |  | def _key_str(value: str) -> str: |
| _result_text@140 | def | L140-158 | 从 http 层的返回值里取 HTML 文本。 | def _result_text(result: Any) -> str: |
| _fetch_text@161 | def | L161-183 | 取一页，返回 (html, 失败原因)。成功时原因为空串。 | def _fetch_text(http: Any, url: str) -> tuple[str, str]: |
| _safe_parse@186 | def | L186-196 | 调调用方的解析器；抛错按「0 条」处理（原因由调用方那条路径给出）。 | def _safe_parse(parse: Callable[[str, str], Sequence[Any]], html: str,… |
| _urls_from_anchors@202 | def | L202-230 | 页面里显式声明/写明的「下一页」链接，优先级最高。 | def _urls_from_anchors(html: str, base: str) -> list[str]: |
| _with_page_query@233 | def | L233-238 | 把 page=N 拼到 query 上（先去掉已有的 page，避免 page=1&page=2）。 | def _with_page_query(url: str, n: int) -> str: |
| _sibling@241 | def | L241-245 | 同目录下的兄弟文件：/a/b/list.htm + list2.htm → /a/b/list2.htm。 | def _sibling(url: str, name: str) -> str: |
| _candidates@248 | def | L248-273 | 候选 URL，按优先级排。越可能真是下一页的越靠前。 | def _candidates(html: str, url: str) -> list[str]: |
| _is_new_page@279 | def | L279-298 | 候选页相对当前页有多少新增条目。 | def _is_new_page(base_keys: set[str], candidate_items: Sequence[Any]) … |
| _find_next@301 | def | L301-339 | 已有当前页的 html/条目时的探测主体（iter_pages 复用，避免重复取当前页）。 | def _find_next( |
| find_next_page@342 | def | L342-372 | 找下一页。返回 (next_url, "") 或 ("", reason)，reason ∈ REASONS。 | def find_next_page( |
| iter_pages@375 | def | L375-414 | 逐页 yield (page_url, items)，遇到 soft_404 就停。 | def iter_pages( |
