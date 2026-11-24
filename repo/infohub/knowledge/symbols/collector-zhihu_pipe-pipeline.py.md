---
covers:
  - collector/zhihu_pipe/pipeline.py
title: Semantic block index: pipeline.py (layer 4)
updated: 2026-11-24
---

# 语义块索引：pipeline.py（第4层）

**源码文件**：`collector/zhihu_pipe/pipeline.py`  
**解析器**：`ast`  
**第5层完整正文**：`read_block(path="collector/zhihu_pipe/pipeline.py", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| RunOptions@37 | class | L37-54 |  | class RunOptions: |
| Hit@58 | class | L58-81 |  | class Hit: |
| Hit.row@64 | def | L64-81 |  | def row(self) -> ArticleRow: |
| Pipeline@84 | class | L84-414 |  | class Pipeline: |
| Pipeline.__init__@85 | def | L85-91 |  | def __init__(self, data_dir: Path, store: Store \| None = None): |
| Pipeline.collect@95 | def | L95-149 | ------------------------------------------------------------ 步骤 1 采集 | def collect(self, opts: RunOptions) -> list[dict]: |
| Pipeline.screen@153 | def | L153-200 | --------------------------------------------- 步骤 2 查重 + 步骤 3 筛选 | def screen(self, pool: list[dict], opts: RunOptions) -> tuple[list[Hit… |
| Pipeline.deep_screen@204 | def | L204-232 | 粗筛未通过时抓正文再筛一次。 | def deep_screen(self, hits: list[Hit], topic: Topic \| None) -> list[H… |
| Pipeline._save_raw@236 | def | L236-256 | ------------------------------------------------------------ 落盘助手 | def _save_raw(self, it: dict, doc: dict, score: float, matched: list[s… |
| Pipeline.fetch_bodies@260 | def | L260-325 | 抓正文。已有正文的条目不再联网，直接复用（不浪费原则）。 | def fetch_bodies(self, hits: list[Hit], limit: int = 0) -> tuple[list[… |
| Pipeline.rescreen_topic@329 | def | L329-358 | 用新主题在本地重扫已入库内容，零联网。 | def rescreen_topic(self, topic_name: str, keywords: list[str] \| None … |
| Pipeline.run@362 | def | L362-414 | ------------------------------------------------------------ 主入口 | def run(self, opts: RunOptions, fetch_bodies: bool = True) -> dict: |
