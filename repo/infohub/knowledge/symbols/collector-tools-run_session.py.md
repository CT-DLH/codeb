---
covers:
  - collector/tools/run_session.py
title: Semantic block index: run_session.py (layer 4)
updated: 2026-11-24
---

# 语义块索引：run_session.py（第4层）

**源码文件**：`collector/tools/run_session.py`  
**解析器**：`ast`  
**第5层完整正文**：`read_block(path="collector/tools/run_session.py", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| _topic_fname@70 | def | L70-71 |  | def _topic_fname(topic: str) -> str: |
| _deadline@76 | def | L76-93 | --until HH:MM（已过今天该时刻就顺延到明天）或 --budget 90m/1.5h/45。 | def _deadline(until: str, budget: str) -> float: |
| _snapshot@96 | def | L96-103 | 库的真实状态。用它做前后差值，而不是去解析子进程打印的统计行。 | def _snapshot(store: Store) -> dict: |
| topic_pool@108 | def | L108-131 | 主题从哪来：内置注册表 + 历史跑过的主题 + 库里真实命中过的词。 | def topic_pool(store: Store, override: list[str]) -> list[str]: |
| Session@136 | class | L136-271 | ---------------------------------------------------------------- 四种补活动作 | class Session: |
| Session.__init__@137 | def | L137-152 |  | def __init__(self, args, store: Store, pool: list[str]): |
| Session._collectible_sources@154 | def | L154-169 | 只把声明了 SEARCH 能力的源放进随机采集池。 | def _collectible_sources(self) -> list[str]: |
| Session.pick_topic@173 | def | L173-176 | 每个动作返回「做了多少件事」，0 表示这条路暂时没货（用于自动降权） | def pick_topic(self) -> str: |
| Session.pick_unseen@178 | def | L178-187 | 本地动作挑没做过的主题：同一主题重筛第二遍不会产出新工作， | def pick_unseen(self) -> str \| None: |
| Session.act_digest@189 | def | L189-199 |  | def act_digest(self) -> int: |
| Session.act_rescreen@201 | def | L201-209 |  | def act_rescreen(self) -> int: |
| Session.act_collect@211 | def | L211-249 |  | def act_collect(self) -> int: |
| Session.act_report@251 | def | L251-258 |  | def act_report(self) -> int: |
| Session.pause@262 | def | L262-271 | ---------------------------------------------------------------- 节律 | def pause(self, long: bool = False) -> None: |
| subprocess_run_source@274 | def | L274-283 | 在子进程里跑 run_source（只登记），返回退出码（1 = 本源暂时不可用）。 | def subprocess_run_source(argv: list[str]) -> int: |
| subprocess_run_enrich@286 | def | L286-295 | 在子进程里跑 enrich_batch（获取腿：抓正文 + 摘要）。M3 起它是唯一抓正文实现。 | def subprocess_run_enrich(argv: list[str]) -> int: |
| _build_parser@300 | def | L300-323 | ---------------------------------------------------------------- 入口 | def _build_parser() -> argparse.ArgumentParser: |
| main@326 | def | L326-401 |  | def main(argv: list[str] \| None = None) -> int: |
