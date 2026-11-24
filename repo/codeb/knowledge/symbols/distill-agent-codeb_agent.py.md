---
covers:
  - distill/agent/codeb_agent.py
title: Semantic block index: codeb_agent.py (layer 4)
updated: 2026-11-24
---

# 语义块索引：codeb_agent.py（第4层）

**源码文件**：`distill/agent/codeb_agent.py`  
**解析器**：`ast`  
**第5层完整正文**：`read_block(path="distill/agent/codeb_agent.py", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| TraceHooks@61 | class | L61-85 | 记录每次工具调用的 hook。 | class TraceHooks(AgentHooks): |
| TraceHooks.__init__@76 | def | L76-77 |  | def __init__(self, sink: list[dict]): |
| TraceHooks.on_tool_start@79 | async def | L79-80 |  | async def on_tool_start(self, context, agent, tool) -> None: |
| TraceHooks.on_tool_end@82 | async def | L82-85 |  | async def on_tool_end(self, context, agent, tool, result) -> None: |
| load_env@89 | def | L89-102 | 读 .env。默认找 codeb 上一级约定的位置，可传路径覆盖。 | def load_env(path: str \| None = None) -> dict: |
| _kb@105 | def | L105-109 |  | def _kb(argv: list[str]) -> tuple[int, str]: |
| Task@114 | class | L114-159 | 一个子 agent 的完整定义。这是 leader 需要写清楚的东西。 | class Task: |
| make_tools@165 | def | L165-269 | 按任务的权限构造该 agent 的工具集。 | def make_tools(t: Task, cache: "ContextCache \| None" = None) -> list: |
| _r@171 | def | L171-172 |  | def _r(path: str, max_lines: int = 150) -> str: |
| _rr@174 | def | L174-175 |  | def _rr(path: str, offset: int, limit: int = 150) -> str: |
| _ld@177 | def | L177-178 |  | def _ld(path: str = ".", pattern: str = "*") -> str: |
| _g@180 | def | L180-181 |  | def _g(pattern: str, path: str = ".", max_hits: int = 20) -> str: |
| _fi@183 | def | L183-185 | 给代码文件建函数级索引（只给目录，不给正文）。 | def _fi(path: str) -> str: |
| _rb@187 | def | L187-189 | 按 file_index 给的 key（函数名@行号）取一个函数的完整正文。 | def _rb(path: str, key: str) -> str: |
| _e@191 | def | L191-193 |  | def _e(path: str, old: str, new: str, replace_all: bool = False) -> st… |
| _w@195 | def | L195-197 |  | def _w(path: str, content: str) -> str: |
| _a@199 | def | L199-201 |  | def _a(path: str, content: str) -> str: |
| _rollback@203 | def | L203-205 | 把文件回滚到某次写前的原文；不给 snapshot_id 就取最近快照。 | def _rollback(path: str, snapshot_id: str = "") -> str: |
| _snaps@207 | def | L207-208 |  | def _snaps(path: str) -> str: |
| _cmd@241 | def | L241-249 | 跑一条验证命令，返回退出码与输出。 | def _cmd(cmd: str) -> str: |
| _cache_get@255 | def | L255-262 | 按 key 取回被换出到 sidecar 的工具结果正文。 | def _cache_get(key: str) -> str: |
| Context@274 | class | L274-278 | ===================================================================== 组装 | class Context: |
| assemble@281 | def | L281-302 | 复用 kb dispatch + kb pack，不重写组装逻辑。 | def assemble(t: Task) -> Context: |
| _shared_instructions@305 | def | L305-320 | 所有子 agent 共用的系统指令。 | def _shared_instructions() -> str: |
| render@323 | def | L323-375 | 把上下文变成注入消息。 | def render(ctx: Context, t: Task, deps: dict[str, str] \| None = None)… |
| run_task@392 | async def | L392-450 | ===================================================================== 执行 | async def run_task(t: Task, env: dict, deps: dict[str, str] \| None = … |
| _collect@453 | def | L453-491 | 从 RunResult（或 None）里整理结果。 | def _collect(t: Task, ctx: Context, r, dt: float, ok: bool, error: str… |
| Trace@501 | class | L501-514 | 一个任务的落盘轨迹。persist=False 时只在内存里，不写盘。 | class Trace: |
| Trace.to_dict@511 | def | L511-514 |  | def to_dict(self) -> dict: |
| Scheduler@517 | class | L517-615 | 按依赖 + 并发上限调度任务。 | class Scheduler: |
| Scheduler.__init__@531 | def | L531-540 |  | def __init__(self, tasks: list[Task], env: dict, concurrency: int = DE… |
| Scheduler._validate@542 | def | L542-550 |  | def _validate(self) -> None: |
| Scheduler._topo@552 | def | L552-568 | 拓扑序。同时用于环检测——排不完说明有环。 | def _topo(self) -> list[str]: |
| Scheduler._run_one@570 | async def | L570-592 |  | async def _run_one(self, name: str) -> None: |
| Scheduler._persist@594 | def | L594-600 |  | def _persist(self, t: Task, r: dict) -> None: |
| Scheduler.run@602 | async def | L602-615 | 按依赖分层跑。同层内受并发上限约束，跨层必须等前一层。 | async def run(self) -> list[dict]: |
| run_many@618 | async def | L618-636 | 并行跑多个子 agent：先验互斥，再按依赖 + 并发上限调度。 | async def run_many(tasks: list[Task], env: dict \| None = None, |
| run_sync@639 | def | L639-646 | 同步入口：kb.py 的 cmd_* 可以直接调。 | def run_sync(tasks: list[Task], **kw) -> list[dict]: |
| build_parser@650 | def | L650-683 | ===================================================================== CLI | def build_parser() -> argparse.ArgumentParser: |
| plan_from_json@686 | def | L686-715 | 从 JSON 读任务列表。 | def plan_from_json(path: str, persist_all: bool = False) -> list[Task]… |
| _print_result@718 | def | L718-732 |  | def _print_result(r: dict, as_json: bool) -> None: |
| main@735 | def | L735-787 |  | def main(argv: list[str] \| None = None) -> int: |
