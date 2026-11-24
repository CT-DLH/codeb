---
covers:
  - collector/zhihu_pipe/summarize.py
title: Semantic block index: summarize.py (layer 4)
updated: 2026-11-24
---

# 语义块索引：summarize.py（第4层）

**源码文件**：`collector/zhihu_pipe/summarize.py`  
**解析器**：`ast`  
**第5层完整正文**：`read_block(path="collector/zhihu_pipe/summarize.py", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| _safe_filename@33 | def | L33-45 | content_id 可能含路径分隔符（GitHub 的 owner/repo），必须消毒后才能当文件名。 | def _safe_filename(name: str) -> str: |
| _load_dotenv@48 | def | L48-76 | 从项目根目录（或 CWD）的 .env 读取配置，注入环境变量。 | def _load_dotenv() -> None: |
| set_llm_min_interval@91 | def | L91-93 |  | def set_llm_min_interval(seconds: float) -> None: |
| _llm_throttle@96 | def | L96-102 |  | def _llm_throttle() -> None: |
| SummaryResult@106 | class | L106-113 |  | class SummaryResult: |
| _clean@124 | def | L124-162 |  | def _clean(md: str, title: str = "", collapse: bool = True) -> str: |
| _units@165 | def | L165-183 | 按块切正文再分句。 | def _units(markdown: str, title: str = "") -> list[str]: |
| _sentences@186 | def | L186-189 |  | def _sentences(text: str) -> list[str]: |
| extract_summary@192 | def | L192-235 |  | def extract_summary(title: str, markdown: str, word_count: int = 0, ur… |
| llm_input@241 | def | L241-258 | 喂给模型的正文：优先「## 摘要」小节；没有就滤掉页眉再截。 | def llm_input(markdown: str, limit: int = 6000) -> str: |
| _fidelity_hint@261 | def | L261-273 | 只有题录时明确禁止推测。 | def _fidelity_hint(fidelity: str) -> str: |
| _prompt@276 | def | L276-302 | 按材料类型选提示。 | def _prompt(kind: str, title: str, markdown: str, fidelity: str) -> st… |
| _llm_summarize@305 | def | L305-353 |  | def _llm_summarize(title: str, markdown: str, fidelity: str = "", kind… |
| _parse_llm@356 | def | L356-374 |  | def _parse_llm(text: str) -> tuple[str, list[str]]: |
| _clip@377 | def | L377-384 | 要点要有可读长度：整段摘要/整个参考文献块都不该原样进卡片。 | def _clip(text: str, limit: int = 200) -> str: |
| Summarizer@390 | class | L390-433 |  | class Summarizer: |
| Summarizer.__init__@391 | def | L391-397 |  | def __init__(self, backend: str = "extract"): |
| Summarizer.summarize@399 | def | L399-413 |  | def summarize(self, title: str, markdown: str, **kw) -> SummaryResult: |
| Summarizer.render@415 | def | L415-433 |  | def render(self, r: SummaryResult) -> str: |
| main_cli@436 | def | L436-515 | 总结待办队列。stats_out 传入空字典时填入本轮计数（含后端分布）。 | def main_cli(data_dir: Path, backend: str, limit: int, force: bool = F… |
| _emit@451 | def | L451-455 |  | def _emit(done: int, mix: dict[str, int]) -> None: |
| resummarize_topic@518 | def | L518-591 | 把「命中某主题、但摘要不是目标后端」的条目重新总结一遍。 | def resummarize_topic(data_dir: Path, topic: str, keywords: list[str] … |
| build_report@594 | def | L594-704 | 汇总所有已总结内容，生成一份可按需筛选的清单（链接 + 一句话结论 + 要点）。 | def build_report(data_dir: Path, out_path: str, top: int = 0, |
| _fidelity_label@707 | def | L707-713 | 正文完整度的人话标签（设计稿 §2：fidelity 是核心字段，不是装饰）。 | def _fidelity_label(fidelity: str) -> str: |
| _source_label@716 | def | L716-737 | 把内部 source 标记翻译成人话，避免清单里出现 author-expand:xxx 这种噪声。 | def _source_label(source: str) -> str: |
| _parse_summary_md@740 | def | L740-755 |  | def _parse_summary_md(text: str) -> tuple[str, list[str]]: |
