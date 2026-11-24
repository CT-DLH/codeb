---
covers:
  - distill/agent/session_log.py
title: Semantic block index: session_log.py (layer 4)
updated: 2026-11-24
---

# 语义块索引：session_log.py（第4层）

**源码文件**：`distill/agent/session_log.py`  
**解析器**：`ast`  
**第5层完整正文**：`read_block(path="distill/agent/session_log.py", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| DualSink@29 | class | L29-48 | A sink that both fills the legacy list and appends to the session log. | class DualSink: |
| DualSink.__init__@36 | def | L36-38 |  | def __init__(self, legacy: list, log: "SessionLog") -> None: |
| DualSink.append@40 | def | L40-42 |  | def append(self, event: dict) -> None: |
| DualSink.__iter__@44 | def | L44-45 |  | def __iter__(self): |
| DualSink.__len__@47 | def | L47-48 |  | def __len__(self) -> int: |
| SessionLog@51 | class | L51-172 | Append-only JSONL event log for one agent session. | class SessionLog: |
| SessionLog.__init__@54 | def | L54-66 |  | def __init__(self, session_id: str, path: str \| Path \| None = None, |
| SessionLog._last_seq@68 | def | L68-84 |  | def _last_seq(self) -> int: |
| SessionLog.append@86 | def | L86-100 | Append one immutable event and return it. | def append(self, event_type: str, **payload: Any) -> dict: |
| SessionLog.events@102 | def | L102-119 | Yield events in order, optionally filtered by type / seq. | def events(self, event_type: str \| None = None, |
| SessionLog.replay@121 | def | L121-123 | Full replay of the log (optionally one event type). | def replay(self, event_type: str \| None = None) -> list[dict]: |
| SessionLog.materialize@125 | def | L125-164 | Build the current view from the log: what tools ran, what changed, | def materialize(self) -> dict[str, Any]: |
| SessionLog.stats@166 | def | L166-172 | Count events by type — cheap observability hook. | def stats(self) -> dict[str, int]: |
