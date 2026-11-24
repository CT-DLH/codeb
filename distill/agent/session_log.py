"""Append-only session log for codeb agents.

The context window is only a *materialized view*; this log is the source of
truth.  Every tool call, decision and task transition is appended as an
immutable event (JSONL).  Views can be materialized and replayed from the log
at any time, which is what makes long-running tasks resumable and auditable.

Design notes
------------
* Append-only: events are never modified in place.  A wrong event is corrected
  by appending a ``correction`` event that references the original seq.
* Crash-safe: each event is one JSON line, written and flushed atomically.
* Thread-safe: a lock guards append and seq allocation (Scheduler runs tasks
  concurrently).
* Self-numbering: seq continues from the last line if the file already exists,
  so a resumed session keeps a monotonic sequence.
"""
from __future__ import annotations

import json
import threading
import time
from pathlib import Path
from typing import Any, Iterator

DEFAULT_DIR = Path("_kbwork/agent-logs")


class DualSink:
    """A sink that both fills the legacy list and appends to the session log.

    TraceHooks currently appends dicts to a plain list (hook_trace).  Wrapping
    that list in DualSink adds event logging without touching the hook code.
    """

    def __init__(self, legacy: list, log: "SessionLog") -> None:
        self.legacy = legacy
        self.log = log

    def append(self, event: dict) -> None:
        self.legacy.append(event)
        self.log.append("tool_hook", **event)

    def __iter__(self):
        return iter(self.legacy)

    def __len__(self) -> int:
        return len(self.legacy)


class SessionLog:
    """Append-only JSONL event log for one agent session."""

    def __init__(self, session_id: str, path: str | Path | None = None,
                 root: str | Path | None = None) -> None:
        self.session_id = session_id
        if path is None:
            base = Path(root) if root else DEFAULT_DIR
            path = base / f"{session_id}.jsonl"
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        # 从已有日志恢复 seq，保证续跑时单调
        self._seq = self._last_seq() + 1
        if not self.path.exists():
            self.path.touch()

    def _last_seq(self) -> int:
        if not self.path.exists():
            return 0
        last = 0
        try:
            with self.path.open("r", encoding="utf-8") as f:
                for line in f:
                    if not line.strip():
                        continue
                    try:
                        ev = json.loads(line)
                        last = max(last, int(ev.get("seq", 0)))
                    except (ValueError, TypeError):
                        continue
        except OSError:
            return 0
        return last

    def append(self, event_type: str, **payload: Any) -> dict:
        """Append one immutable event and return it."""
        with self._lock:
            event = {
                "seq": self._seq,
                "ts": round(time.time(), 6),
                "session": self.session_id,
                "type": event_type,
            }
            event.update(payload)
            with self.path.open("a", encoding="utf-8") as f:
                f.write(json.dumps(event, ensure_ascii=False, sort_keys=True) + "\n")
                f.flush()
            self._seq += 1
            return event

    def events(self, event_type: str | None = None,
               since_seq: int = 0) -> Iterator[dict]:
        """Yield events in order, optionally filtered by type / seq."""
        if not self.path.exists():
            return
        with self.path.open("r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    ev = json.loads(line)
                except ValueError:
                    continue
                if int(ev.get("seq", 0)) <= since_seq:
                    continue
                if event_type and ev.get("type") != event_type:
                    continue
                yield ev

    def replay(self, event_type: str | None = None) -> list[dict]:
        """Full replay of the log (optionally one event type)."""
        return list(self.events(event_type))

    def materialize(self) -> dict[str, Any]:
        """Build the current view from the log: what tools ran, what changed,
        what failed.  This is the data models actually need, reconstructed
        from immutable events rather than kept in the context window.
        """
        view: dict[str, Any] = {
            "session": self.session_id,
            "tool_calls": [],
            "files_changed": [],
            "decisions": [],
            "errors": [],
            "event_count": 0,
        }
        for ev in self.events():
            view["event_count"] += 1
            t = ev.get("type")
            if t == "tool_call":
                view["tool_calls"].append({
                    "tool": ev.get("tool"),
                    "args": ev.get("args"),
                    "seq": ev.get("seq"),
                })
            elif t == "file_change":
                view["files_changed"].append({
                    "path": ev.get("path"),
                    "op": ev.get("op"),
                    "seq": ev.get("seq"),
                    "snapshot": ev.get("snapshot"),
                })
            elif t == "decision":
                view["decisions"].append({
                    "text": ev.get("text"),
                    "seq": ev.get("seq"),
                })
            elif t in ("task_error", "tool_error"):
                view["errors"].append({
                    "error": ev.get("error"),
                    "seq": ev.get("seq"),
                })
        return view

    def stats(self) -> dict[str, int]:
        """Count events by type — cheap observability hook."""
        counts: dict[str, int] = {}
        for ev in self.events():
            t = ev.get("type", "?")
            counts[t] = counts.get(t, 0) + 1
        return counts
