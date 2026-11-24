---
covers:
  - collector/tools/run_research.py
title: Semantic block index: run_research.py (layer 4)
updated: 2026-11-24
---

# 语义块索引：run_research.py（第4层）

**源码文件**：`collector/tools/run_research.py`  
**解析器**：`ast`  
**第5层完整正文**：`read_block(path="collector/tools/run_research.py", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| load_state@81 | def | L81-87 | -------------------------------------------------------------------------- 状态 ---------------------- | def load_state(path: Path) -> dict: |
| save_state@90 | def | L90-92 |  | def save_state(path: Path, state: dict) -> None: |
| new_state@95 | def | L95-109 |  | def new_state(name: str, topic: str, args) -> dict: |
| run_cmd@116 | def | L116-126 | 跑子进程。cwd 默认是 collector/（采集器都在这里）， | def run_cmd(cmd: list[str], label: str, tail: int = 3, |
| _Ledger@129 | class | L129-165 | 检索词台账的只读视图（写回由 run_source.py --ledger 负责）。 | class _Ledger: |
| _Ledger.__init__@137 | def | L137-145 |  | def __init__(self, db_path: Path): |
| _Ledger.should_skip@147 | def | L147-153 |  | def should_skip(self, platform: str, query: str, topic: str) -> tuple[… |
| _Ledger.cursor_of@155 | def | L155-165 | 上次停下时的游标。空串表示从头搜或已到底。 | def cursor_of(self, platform: str, query: str, topic: str) -> str: |
| register@168 | def | L168-245 | 逐条检索词登记到库，返回本次命中的 (源名, url)（去重、保序）。 | def register(queries: list[dict], args, tag: str, |
| absorb@197 | def | L197-204 |  | def absorb(src: str, stats: dict) -> int: |
| export_cards@248 | def | L248-279 | 补完正文后把这几篇内容投影成采集卡（调研链路此前完全漏掉了这一步）。 | def export_cards(urls: list[str], tag: str) -> None: |
| enrich@282 | def | L282-304 | 补正文。只补这批 URL，不碰库里其他待办。 | def enrich(hits: list[tuple[str, str]], args, tag: str) -> None: |
| fetch_docs@311 | def | L311-343 | 从库里取这批 URL 的正文（已抓过的才有 raw_path）。 | def fetch_docs(urls: list[str], visited: set[str]) -> list[dict]: |
| mine@350 | def | L350-405 | 逐篇挖证据；逐字校验不过的丢掉。返回 (新证据, 统计)。 | def mine(docs: list[dict], state: dict, args, focus: str) -> tuple[lis… |
| core_terms@439 | def | L439-462 | 从主题里取「实体名/核心词」，用于喂养判定集（_topic_terms(extra_terms=)）。 | def core_terms(topic: str) -> set[str]: |
| _topic_terms@465 | def | L465-517 | 从主题里取「够具体」的词，用来判断一篇正文是不是跑题了。 | def _topic_terms(topic: str, extra_terms: "set[str] \| None" = None) -… |
| relevance@528 | def | L528-565 | 正文里主题词的浓度：每千字命中多少次「长度 ≥MIN_TERM_LEN 的主题词」。 | def relevance(text: str, terms: set[str]) -> float: |
| _count_term@577 | def | L577-601 | 数一个主题词在正文里出现几次。 | def _count_term(text: str, term: str) -> int: |
| off_topic@619 | def | L619-677 | 这篇正文算不算跑题。 | def off_topic(text: str, topic_terms: set[str], bridge_terms: set[str]… |
| dedup@680 | def | L680-689 | 按 quote 归一化文本去重（同一段话被多篇转载只留一条）。保序。 | def dedup(evidence: list[dict]) -> list[dict]: |
| _sections_of@692 | def | L692-717 | 章节划分：报告与综述卡共用同一份，不能两处各写一遍（会漂）。 | def _sections_of(outline: dict \| None, evidence: list[dict]) -> tuple… |
| _derived_from@724 | def | L724-733 | 这组证据的指纹：判断「这批材料有没有变」用。 | def _derived_from(state: dict) -> str: |
| _short_topic@736 | def | L736-746 | 主题的短名，用于卡片标题的后半段（章节名在前，主题在后做区分）。 | def _short_topic(topic: str, limit: int = 24) -> str: |
| write_report@753 | def | L753-827 | 出人读的报告。章节由证据长出来；缺口如实写。 | def write_report(state: dict, outline: dict \| None = None) -> Path: |
| _platform_of@830 | def | L830-842 | 按 URL 主机判这篇内容来自哪个平台（报告里要让读者看见搜了哪几家）。 | def _platform_of(url: str) -> str: |
| _report_title@845 | def | L845-857 | 报告标题：人读的名字，也是 reports/ 里的文件名主干。 | def _report_title(state: dict) -> str: |
| _write@860 | def | L860-891 | 写报告文件：reports/<标题>.md，带 YAML frontmatter。 | def _write(state: dict, lines: list[str], *, sections: list[dict] \| N… |
| yaml_dump@894 | def | L894-915 | 极简 YAML 输出：只处理本报告用到的类型（str / int / list[str]）。 | def yaml_dump(meta: dict) -> str: |
| _needs_bridge@922 | def | L922-932 | 主题是不是需要跨语言桥接词。 | def _needs_bridge(topic: str) -> bool: |
| run_round@935 | def | L935-1046 | 跑一轮：搜 → 抓 → 挖 → 记账。返回「是否值得再跑一轮」。 | def run_round(state: dict, args, state_path: Path) -> bool: |
| main@1049 | def | L1049-1135 |  | def main(argv: list[str] \| None = None) -> int: |
