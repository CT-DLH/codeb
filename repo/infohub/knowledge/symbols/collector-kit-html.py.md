---
covers:
  - collector/kit/html.py
title: Semantic block index: html.py (layer 4)
updated: 2026-11-24
---

# 语义块索引：html.py（第4层）

**源码文件**：`collector/kit/html.py`  
**解析器**：`ast`  
**第5层完整正文**：`read_block(path="collector/kit/html.py", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| parse_html@75 | def | L75-90 | HTML 字符串 → lxml 根节点；空输入或坏文档返回 None（不抛异常）。 | def parse_html(html: str): |
| select@93 | def | L93-102 | CSS 选择器取后代节点。选择器写错直接抛错，不静默返回 []。 | def select(node, selector: str) -> list: |
| select_one@105 | def | L105-107 |  | def select_one(node, selector: str): |
| node_text@110 | def | L110-114 | 节点全部文本（含后代），空白归一。等价于 bs4 的 get_text(" ")。 | def node_text(node) -> str: |
| attr@117 | def | L117-121 |  | def attr(node, name: str, default: str = "") -> str: |
| to_html@124 | def | L124-128 | 节点 → HTML 字符串（不含 tail）。给需要二次解析的调用方用。 | def to_html(node) -> str: |
| drop@131 | def | L131-140 | 移除节点但保留它的 tail 文本（drop_tree 会把 tail 并回上一个兄弟）。 | def drop(node) -> None: |
| _drop_tags@143 | def | L143-146 |  | def _drop_tags(node, tags) -> None: |
| clean_text@152 | def | L152-155 |  | def clean_text(value: str) -> str: |
| _walk@158 | def | L158-174 |  | def _walk(node, out: list[str]) -> None: |
| _block_lines@177 | def | L177-189 | 按块级元素换行、行内元素直接拼接。 | def _block_lines(node) -> list[str]: |
| html_to_text@192 | def | L192-199 |  | def html_to_text(html: str) -> str: |
| extract_content_ex@202 | def | L202-224 | 按选择器链取正文容器，返回 (正文, 原因)。 | def extract_content_ex(html: str, selectors: tuple[str, ...] \| list[s… |
| extract_content@227 | def | L227-229 | 按选择器链取正文容器，取不到则退回整页文本。 | def extract_content(html: str, selectors: tuple[str, ...] \| list[str]… |
| looks_like_file@232 | def | L232-233 |  | def looks_like_file(href: str, pattern: str = r"\.(pdf\|docx?\|xlsx?\|… |
| extract_links@236 | def | L236-250 |  | def extract_links(html: str, base: str, file_pattern: str = "") -> lis… |
| to_iso@256 | def | L256-260 |  | def to_iso(year, month, day) -> str: |
| join_digits@263 | def | L263-269 | 把被标签拆开的数字粘回去：20 26 年 9 月 → 2026 年 9 月。 | def join_digits(raw: str) -> str: |
| normalize_date@272 | def | L272-289 | 把一处文本里的首个日期归一为 ISO。 | def normalize_date(raw: str, default_year: int = 0) -> str: |
| parse_publish@292 | def | L292-303 | 站点给的发布日期字段五花八门，统一为 ISO。 | def parse_publish(value: str) -> str: |
| clean_title@306 | def | L306-308 | 列表卡片常把日期与标题放同一节点，去掉尾部日期（发布日期另有字段）。 | def clean_title(title: str) -> str: |
| detail_date@311 | def | L311-323 | 详情页标注的发布日期，找不到时退回正文首段扫描。 | def detail_date(html: str, content_selectors: tuple[str, ...] \| list[… |
| card_of@329 | def | L329-339 | 条目链接对应的卡片：优先 li/tr，其次只包住这一条的 div，否则用链接自身。 | def card_of(anchor): |
| dedupe@342 | def | L342-350 |  | def dedupe(items, key=None) -> list: |
| now_stamp@353 | def | L353-354 |  | def now_stamp() -> str: |
| _clean@380 | def | L380-383 | --------------------------------------------------------------------------- 文本 | def _clean(s: str) -> str: |
| _abs@386 | def | L386-399 |  | def _abs(href: str, base: str) -> str: |
| _flat@402 | def | L402-427 | 把一个节点摊平成一行文本：链接保留成 [文字](绝对地址)，图片只留 alt。 | def _flat(el, base: str = "") -> str: |
| _emit@435 | def | L435-479 | 块级结构 → 行文本。混合内容（直接文本 + 块级子节点）两边都不丢。 | def _emit(el, base: str, out: list[str], depth: int = 0) -> None: |
| _link_density@482 | def | L482-489 |  | def _link_density(el) -> float: |
| _content_len@492 | def | L492-499 | 只算段落类节点的字数：导航/列表页的短链堆再多也不算「正文很厚」。 | def _content_len(el) -> int: |
| _tidy@502 | def | L502-517 |  | def _tidy(text: str, max_chars: int) -> str: |
| Extraction@521 | class | L521-528 |  | class Extraction: |
| _pick@531 | def | L531-568 | 挑正文容器：按它实际能产出多少正文排序，而不是按它有多少字。 | def _pick(doc, base: str): |
| _prune@571 | def | L571-586 |  | def _prune(doc, aggressive: bool) -> None: |
| density_extract@589 | def | L589-644 | HTML → 正文。抽不出就 text="" + reason，绝不拿导航文字凑数。 | def density_extract(html: str, url: str = "", *, max_chars: int = MAX_… |
