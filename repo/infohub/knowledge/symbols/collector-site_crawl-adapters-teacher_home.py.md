---
covers:
  - collector/site_crawl/adapters/teacher_home.py
title: Semantic block index: teacher_home.py (layer 4)
updated: 2026-11-24
---

# 语义块索引：teacher_home.py（第4层）

**源码文件**：`collector/site_crawl/adapters/teacher_home.py`  
**解析器**：`ast`  
**第5层完整正文**：`read_block(path="collector/site_crawl/adapters/teacher_home.py", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| slug_of@32 | def | L32-49 | 把 URL 或裸 slug 还原成主页标识；外域返回空字符串。 | def slug_of(value: str, host: str = "homepage.hit.edu.cn") -> str: |
| split_title@52 | def | L52-60 | 栏目名可能写成「研究方向 Research Direction」，中文在前、英文在后。 | def split_title(title: str) -> tuple[str, str]: |
| first_sentence@63 | def | L63-70 |  | def first_sentence(text: str, limit: int = 180) -> str: |
| canonical_section@73 | def | L73-101 | 把「发表论文 / 论文及著作 / Publications」收敛成一个稳定的小节名。 | def canonical_section(title: str, aliases: dict[str, list[str]]) -> st… |
| title_matches@104 | def | L104-106 |  | def title_matches(title: str, names: list[str]) -> bool: |
| merge_sections@109 | def | L109-139 | 同一归并名只留一份：中文优先、更长优先；论文/项目保留第一份做正文兜底。 | def merge_sections(sections: list[dict]) -> list[dict]: |
| subhead_segments@142 | def | L142-170 | 把「科研情况」这类大栏目按正文里的小标题拆段。 | def subhead_segments(text: str, aliases: dict[str, list[str]]) -> tupl… |
| _node_text@173 | def | L173-180 |  | def _node_text(node, prefer_attr: str = "") -> str: |
| TeacherHomeAdapter@183 | class | L183-533 |  | class TeacherHomeAdapter: |
| TeacherHomeAdapter.__init__@186 | def | L186-193 |  | def __init__(self, spec: dict, http: Http): |
| TeacherHomeAdapter.collect@197 | def | L197-210 | ------------------------------------------------------------ 入口 | def collect(self, target: str) -> dict: |
| TeacherHomeAdapter._profile@214 | def | L214-269 | ------------------------------------------------------------ 首屏资料 | def _profile(self, slug: str, url: str) -> dict: |
| TeacherHomeAdapter._sections@273 | def | L273-375 | ------------------------------------------------------------ 全部栏目 | def _sections(self, tid: str, referer: str) -> tuple[list[dict], list[… |
| TeacherHomeAdapter._extract_papers@377 | def | L377-389 |  | def _extract_papers(self, node, item_sel: str) -> list[str]: |
| TeacherHomeAdapter._papers_from_lines@392 | def | L392-396 |  | def _papers_from_lines(lines: list[str]) -> list[str]: |
| TeacherHomeAdapter._extract_projects@398 | def | L398-421 |  | def _extract_projects(self, node) -> list[dict]: |
| TeacherHomeAdapter._projects_from_lines@423 | def | L423-447 |  | def _projects_from_lines(self, lines: list[str]) -> list[dict]: |
| TeacherHomeAdapter._enrich@451 | def | L451-477 | 主页系统自带的姓名检索：补英文名、单位英文名、浏览量；失败不影响主流程。 | def _enrich(self, record: dict) -> None: |
| TeacherHomeAdapter._record@479 | def | L479-528 |  | def _record(self, slug, url, profile, sections, papers, projects) -> d… |
| TeacherHomeAdapter._finish@530 | def | L530-533 | 把「栏目存在但没抓到内容」补进 flags；放在 enrich 之后，避免误报。 | def _finish(self, record: dict, sections: list[dict], papers: list[str… |
| _find_section@536 | def | L536-540 |  | def _find_section(sections: list[dict], names: list[str]) -> dict \| N… |
| _dedupe@543 | def | L543-551 |  | def _dedupe(items: list, key=None) -> list: |
