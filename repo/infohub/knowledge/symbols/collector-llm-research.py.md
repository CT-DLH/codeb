---
covers:
  - collector/llm/research.py
title: Semantic block index: research.py (layer 4)
updated: 2026-11-24
---

# 语义块索引：research.py（第4层）

**源码文件**：`collector/llm/research.py`  
**解析器**：`ast`  
**第5层完整正文**：`read_block(path="collector/llm/research.py", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| _fmt_learnings@107 | def | L107-117 | 把已有收获压成提示词里的清单。太多就取最近的（越新越接近当前前沿）。 | def _fmt_learnings(learnings: list[dict], limit: int = 40) -> str: |
| plan_queries@120 | def | L120-171 | 决定下一轮检索词。返回 [{query, goal}]。 | def plan_queries( |
| bridge_terms@209 | def | L209-226 | 要一组跨语言的核心词（中文 + 英文），用于跑题闸判「是否切题」。 | def bridge_terms(topic: str) -> list[str]: |
| _pick_terms@229 | def | L229-252 | 从模型给的 terms 里挑出真正能起桥接作用的词。 | def _pick_terms(raw: list, topic: str) -> list[str]: |
| _generic_head@278 | def | L278-285 | 这个词是不是「泛化词打头」——Bing 会把它塌缩成该泛化词的词条页。 | def _generic_head(tok: str) -> bool: |
| _split_long_token@288 | def | L288-306 | 把「不带空格的长中文串」切成有意义的几段，让词序轮转能起作用。 | def _split_long_token(query: str) -> str: |
| _fix_generic_heads@309 | def | L309-337 | 把「泛化词打头」的查询重排成「具体词打头」。 | def _fix_generic_heads(queries: list[dict]) -> list[dict]: |
| mine_evidence@393 | def | L393-464 | 从一篇正文里挖证据。返回 (证据列表, 校验统计)。 | def mine_evidence( |
| _prose_chars@474 | def | L474-483 | 这条 quote 里实质文字有多少字（剥掉 markdown 链接、裸 URL、标点空白）。 | def _prose_chars(q: str) -> int: |
| _is_heading_only@486 | def | L486-493 | 这条 quote 是不是「只有一行标题」——是就不能当证据（理由见调用处）。 | def _is_heading_only(q: str) -> bool: |
| classify_source@518 | def | L518-543 | 按域名定 primary / secondary / unknown，模型判断只当兜底。 | def classify_source(url: str, model_kind: str = "") -> str: |
| _norm_strict@551 | def | L551-553 | 严格归一：只压空白。quote 能这样对上就是逐字原样。 | def _norm_strict(s: str) -> str: |
| _norm_loose@556 | def | L556-579 | 宽松归一：抹掉 markdown 记号与全部空白后再比。 | def _norm_loose(s: str) -> str: |
| _verbatim@582 | def | L582-592 | 逐字校验：归一后必须能在正文里找到。 | def _verbatim(quote: str, source: str, *, loose: bool = False) -> bool… |
| build_outline@646 | def | L646-671 | 把证据聚成章节大纲 + 缺口清单。 | def build_outline(topic: str, evidence: list[dict], *, focus: str = ""… |
