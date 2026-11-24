---
covers:
  - collector/refs/grammar.py
title: Semantic block index: grammar.py (layer 4)
updated: 2026-11-24
---

# 语义块索引：grammar.py（第4层）

**源码文件**：`collector/refs/grammar.py`  
**解析器**：`ast`  
**第5层完整正文**：`read_block(path="collector/refs/grammar.py", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| Citation@41 | class | L41-62 |  | class Citation: |
| Citation.to_dict@54 | def | L54-55 |  | def to_dict(self) -> dict: |
| Citation.merge_key@58 | def | L58-62 | 跨老师合并的键：DOI 优先，其次「规范标题+年份」。 | def merge_key(self) -> str: |
| load_lexicon@66 | def | L66-68 |  | def load_lexicon(path: str \| None = None) -> dict: |
| to_halfwidth@71 | def | L71-72 |  | def to_halfwidth(text: str) -> str: |
| norm_title@75 | def | L75-77 | 标题比较用的归一化：半角、小写、去掉空白与标点，只留语义骨架。 | def norm_title(text: str) -> str: |
| _strip_noise@80 | def | L80-84 |  | def _strip_noise(text: str, lex: dict) -> str: |
| _gate@87 | def | L87-94 |  | def _gate(text: str, lex: dict) -> bool: |
| _name_like@97 | def | L97-117 |  | def _name_like(seg: str, lex: dict) -> bool: |
| _split_authors_colon@120 | def | L120-137 | DBLP 风格的「作者串: 题目」——第一个「冒号+空格」前是作者。 | def _split_authors_colon(text: str) -> tuple[str, str]: |
| _year_of@140 | def | L140-145 |  | def _year_of(tail: str) -> int: |
| _split_title_venue@148 | def | L148-165 | 题目/出处的分界：第一个「. 」之后是出处（含年份或期刊提示词）的那一处。 | def _split_title_venue(rest: str, lex: dict) -> tuple[str, str]: |
| _authors_from_commas@168 | def | L168-188 | 无冒号风格（「A, B, C, 题名, 期刊, 年」）：前面连续的「像名字」的段算作者。 | def _authors_from_commas(text: str, lex: dict) -> tuple[list[str], str… |
| _title_min_ok@191 | def | L191-195 |  | def _title_min_ok(title: str, lex: dict) -> bool: |
| _split_names@198 | def | L198-199 |  | def _split_names(authors: str) -> list[str]: |
| _rule_tagged@204 | def | L204-235 | [TII@22] Zhang W, ... et al. 题名[J]. 期刊, 2022, 19(1): 123-134 | def _rule_tagged(text: str, lex: dict) -> Citation \| None: |
| _rule_quoted@238 | def | L238-253 | 题名被引号包起来：A, B, “Clustered Adaptive Graph … ,” IEEE Trans., 2026. | def _rule_quoted(text: str, lex: dict) -> Citation \| None: |
| _rule_cnki_dotted@256 | def | L256-272 | 中文题录：王国峰,刘川意,潘鹤中等.云计算模式内部威胁综述.计算机学报,2017,40(2):296-316 | def _rule_cnki_dotted(text: str, lex: dict) -> Citation \| None: |
| _rule_dblp@275 | def | L275-288 | DBLP 式：作者: 题名. 期刊 卷(期): 页 (年) | def _rule_dblp(text: str, lex: dict) -> Citation \| None: |
| _rule_comma_tail@291 | def | L291-305 | 逗号串式：Zhixiao Wu, Yao Lu*, …, 题名, IEEE T-IFS , 2026. | def _rule_comma_tail(text: str, lex: dict) -> Citation \| None: |
| _rule_bare@308 | def | L308-320 | 兜底：整行当标题，只带年份/链接。低置信，照样可查，但结果要人工抽查。 | def _rule_bare(text: str, lex: dict) -> Citation: |
| _is_name_list@334 | def | L334-343 | 整行是逗号分隔的人名：Caishen Zhou, Yihong Tang, and Min Zhang | def _is_name_list(text: str, lex: dict) -> bool: |
| line_role@346 | def | L346-381 | 这一行在「一条引用」里扮演什么角色。 | def line_role(text: str, lex: dict \| None = None) -> str: |
| starts_record@384 | def | L384-388 | 行首带标号/项目符号（[38]、68.、■、）——列表里「下一篇」的通用信号。 | def starts_record(text: str, lex: dict \| None = None) -> bool: |
| merge_wrapped@391 | def | L391-424 | 把排版拆成多行的同一条引用拼回「一条一行」。 | def merge_wrapped(lines: list[str], lex: dict \| None = None) -> list[… |
| _looks_fragment@427 | def | L427-448 | 「标题」其实是作者碎片：Xiangping Wu、and Wentai Zhang。 | def _looks_fragment(cit: Citation, lex: dict) -> bool: |
| parse@451 | def | L451-481 | 一条引用串 → Citation。 | def parse(text: str, lex: dict \| None = None) -> Citation: |
