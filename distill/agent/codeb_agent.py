"""codeb 子 agent 体系的**正式入口**。

与 `spawn.py` 的区别（这是它能不能承接真实派发的关键）：

    spawn.py    → 只能读（read_file / grep_text）
                  只能回答「这范围有什么」，改不了代码。
    codeb_agent.py → 能改文件（edit_file / write_file / append_file）
                     + 能跑验证（run_cmd）
                     + 每个 agent 的写权限由 Task 里的白名单硬性约束
                     + 上下文由 kb.py 组装，100% 复用，不重写

用法（leader 侧，比如 kb.py 里新增的 cmd_agent）：

    python kb.py agent --scope "packages/core/src/services" --task "..." \
        --allow "comment-service.ts" --allow "comment-prompt.ts" \
        --deny "CommentPanel.tsx" --repo atomkgraph --json

流程：
    1. kb dispatch 验这个范围的写冲突（已有，直接复用）
    2. kb pack 装订上下文（已有，直接复用）
    3. 注入上下文 + 任务，交给 openai-agents 跑
    4. 返回结构化结果：改动、回答、token、耗时、错误

**这一层不产生任何业务逻辑**：组装全部来自 kb.py，执行全部来自 openai-agents，
它只做三件事：把规格翻译成 Agent、注入、收结果。
"""
from __future__ import annotations

import argparse
import asyncio
import io
import contextlib
import json
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

CODEB = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(CODEB))
import kb  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
from tools_fs import (  # noqa: E402
    ROOTS, read_file, read_file_range, list_dir, grep_text,
    edit_file, write_file, append_file, run_cmd, diff_summary,
    file_index, read_block, rollback_file, snap_list,
    grep_count, find_line,
)
from context_cache import ContextCache  # noqa: E402
from session_log import SessionLog, DualSink  # noqa: E402

from agents import (  # noqa: E402
    Agent, AgentHooks, Runner, function_tool, OpenAIChatCompletionsModel,
    set_tracing_disabled, RunConfig,
)
from openai import AsyncOpenAI  # noqa: E402

set_tracing_disabled(True)


class TraceHooks(AgentHooks):
    """记录每次工具调用的 hook。

    **为什么必须有它**：`Runner.run` 抛 `MaxTurnsExceeded` 时**拿不到 RunResult**，
    于是 `_collect` 里的 `r.new_items` 是空的，`steps` 全空。
    leader 只知道「失败了」，不知道 agent 死前改了什么——
    实测 w2 就是这样：改了 73 行但 steps=[]。

    hook 在工具调用**发生时**就记录到外部列表，不依赖 RunResult，
    所以异常也能拿到轨迹。

    注意：`on_tool_start` / `on_tool_end` 拿不到工具参数（框架不传），
    所以这里记的是「调了什么工具 + 结果摘要」；参数由 write_trace 补。
    """

    def __init__(self, sink: list[dict]):
        self.sink = sink

    async def on_tool_start(self, context, agent, tool) -> None:
        self.sink.append({"tool": tool.name, "stage": "start"})

    async def on_tool_end(self, context, agent, tool, result) -> None:
        text = str(result)
        self.sink.append({"tool": tool.name, "stage": "end",
                          "result": text[:200] + ("…" if len(text) > 200 else "")})


# ===================================================================== 凭据
def load_env(path: str | None = None) -> dict:
    """读 .env。默认找 codeb 上一级约定的位置，可传路径覆盖。"""
    p = Path(path) if path else ROOTS["infohub"] / "collector" / ".env"
    out: dict[str, str] = {}
    if not p.exists():
        return out
    for line in p.read_text(encoding="utf-8-sig", errors="replace").splitlines():
        s = line.strip()
        if not s or s.startswith("#") or "=" not in s:
            continue
        k, v = s.split("=", 1)
        if k.strip().startswith("ZHIHU_LLM_"):
            out.setdefault(k.strip(), v.strip().strip('"').strip("'"))
    return out


def _kb(argv: list[str]) -> tuple[int, str]:
    o, e = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(o), contextlib.redirect_stderr(e):
        rc = kb.main(argv)
    return rc, (o.getvalue() if rc == 0 else e.getvalue()).strip()


# ===================================================================== 任务规格
@dataclass
class Task:
    """一个子 agent 的完整定义。**这是 leader 需要写清楚的东西。**

    必需：scope（写范围）、task（要做什么）、repo（哪个仓库）。
    写权限：allowed 为白名单（空=不限制），denied 为禁止清单（叠加在全局之上）。
    """
    name: str
    scope: str
    task: str
    repo: str = "infohub"
    allowed: list[str] = field(default_factory=list)
    denied: list[str] = field(default_factory=list)
    # 上下文组装：budget / with_source 决定 kb pack 装多少
    budget: int = 8000
    # **默认必须 True**。`kb pack --no-source` 只装知识层，对没有知识页认领的代码范围
    # 会装出「0 块 0 tok」——agent 拿到一片空白，然后靠 read_file 自己把源码读回来。
    # 那等于绕过了 codeb 的组装，也白花了装订的 token。
    # 只有「问这个范围有什么坑」这类答案不在源码里的任务才该关掉。
    with_source: bool = True
    # **虚拟内存模型**：预填充上下文里，源码只放「函数级索引」，不放全文。
    # 用到哪个函数，agent 用 read_block(key) 按需调入——上下文即 cache，
    # 索引即页表，miss 才去磁盘（源文件）取一次。
    # 实测 Sidebar.tsx：全文 529 行，索引只 ~30 行、单块 11 行。
    # 只有确实需要通读整个文件的小任务才设 False。
    index_only: bool = True
    # 上下文淘汰：最近 N 条工具结果留在热区，更早的长结果换出到 sidecar。
    # 与 index_only 配合：索引是页表，read_block 是缺页调入，这里是换页。
    # None = 不淘汰（小任务不用折腾）。
    cache_keep_recent: int | None = 2
    # 执行：轮次上限。**None = 不限**。
    # 不要画人为上限：w2-sidebar 曾因 max_turns=14 被强杀——它已经改了 73 行、
    # 正在收敛，却被按停止键，结果 leader 得亲自补完。
    # 任务该靠「拆细」收敛，不是靠轮数掐断。真要防止失控，用 Scheduler 的依赖
    # 分阶段 + 每个子任务足够小，而不是给一个大任务套 max_turns。
    max_turns: int | None = None
    with_cmd: bool = True
    # 额外的静态上下文（契约、事实、方向警告等），直接拼进注入文本
    note: str = ""
    # ---- 调度：依赖与产物 ----
    # 这些任务必须先成功完成，它们的**结论**会被注入本任务的上下文。
    # 空 = 无依赖，可立刻跑。
    depends_on: list[str] = field(default_factory=list)
    # 是否把完整执行轨迹（读了什么、改了哪些、原始回答）落盘。
    # 默认 False：只把**结论**传给下游，过程丢掉——这就是「任务边界折叠」。
    # 下游真的需要细节时，leader 再单独派一个任务去读盘上的轨迹。
    persist: bool = False
    # ---- 路由装订（替代 scope 的 pack）----
    # 路由规格 JSON 路径。给了它就不走 `kb pack`，改走 `kb route --spec`：
    # 成员集与每成员保真度（full/index/outline）由 leader 显式声明。
    # 为什么需要：目录 pack 按「预算 ÷ 文件数」平分，实测 200k 预算下
    # apps/web 43 个文件仍降级 19 个大文件（含 20k tok 的 QuestionPanel）。
    route: str = ""
    # 路由超预算时是否允许自动降档。默认 False：降一档答案就基于大纲而不是原文，
    # 而它长得像装订成功——这类失败最难被发现。
    route_degrade: bool = False


# ===================================================================== 工具
# 所有文件工具的 root 绑定到 Task.repo，白名单也从 Task 取。
# 用闭包而不是把白名单塞进每个工具签名——tools_fs 保持纯函数，权限策略在执行层。
def make_tools(t: Task, cache: "ContextCache | None" = None) -> list:
    """按任务的权限构造该 agent 的工具集。

    cache 不为 None 时，额外挂一个 `cache_get` 工具——
    墓碑里写了「用 cache_get 取回」，就必须真有这个工具，否则是空头承诺。
    """
    def _r(path: str, max_lines: int = 150) -> str:
        return read_file(path, max_lines, root=t.repo)

    def _rr(path: str, offset: int, limit: int = 150) -> str:
        return read_file_range(path, offset, limit, root=t.repo)

    def _ld(path: str = ".", pattern: str = "*") -> str:
        return list_dir(path, pattern, root=t.repo)

    def _g(pattern: str, path: str = ".", max_hits: int = 20) -> str:
        return grep_text(pattern, path, max_hits, root=t.repo)

    def _gc(pattern: str, path: str = ".") -> str:
        """直接返回命中条数——回答「有几个」用它。"""
        return grep_count(pattern, path, root=t.repo)

    def _fl(literal: str, path: str = ".") -> str:
        """直接返回 文件:行号——回答「第几行」用它。"""
        return find_line(literal, path, root=t.repo)

    def _fi(path: str) -> str:
        """给代码文件建函数级索引（只给目录，不给正文）。"""
        return file_index(path, root=t.repo)

    def _rb(path: str, key: str) -> str:
        """按 file_index 给的 key（函数名@行号）取一个函数的完整正文。"""
        return read_block(path, key, root=t.repo)

    def _e(path: str, old: str, new: str, replace_all: bool = False) -> str:
        return edit_file(path, old, new, root=t.repo,
                         allowed=t.allowed, denied=t.denied, replace_all=replace_all)

    def _w(path: str, content: str) -> str:
        return write_file(path, content, root=t.repo,
                          allowed=t.allowed, denied=t.denied)

    def _a(path: str, content: str) -> str:
        return append_file(path, content, root=t.repo,
                           allowed=t.allowed, denied=t.denied)

    def _rollback(path: str, snapshot_id: str = "") -> str:
        """把文件回滚到某次写前的原文；不给 snapshot_id 就取最近快照。"""
        return rollback_file(path, root=t.repo, snapshot_id=snapshot_id or None)

    def _snaps(path: str) -> str:
        return snap_list(path, root=t.repo)

    tools = [
        function_tool(_r, name_override="read_file",
                      description_override="读仓库里的文件，返回前 N 行及总行数。大文件用 read_file_range 分段读。"),
        function_tool(_rr, name_override="read_file_range",
                      description_override="从 offset（1 起）读一段，用于读大文件中段。"),
        function_tool(_ld, name_override="list_dir",
                      description_override="列目录（单层），带文件大小。"),
        function_tool(_g, name_override="grep_text",
                      description_override="在目录里搜字符串，返回 路径:行号:内容。找原文用它，不要凭记忆写 old。"),
        # 这两个是「归约型」工具：直接给答案，不让模型自己数。
        # 实测依据见 tools_fs.grep_count 的注释：给原料（grep 命中行）时
        # 计数题 1/3，给条数时 3/3。
        function_tool(_gc, name_override="grep_count",
                      description_override=("正则搜索并**直接返回命中条数**。"
                                             "问题问「有几个 / 多少条」时**必须用它**，"
                                             "不要自己数 grep_text 的输出——实测模型数不准。")),
        function_tool(_fl, name_override="find_line",
                      description_override=("找一个字面量出现的 **文件:行号**。"
                                             "问题问「在第几行 / 在哪」时**必须用它**，不要凭上下文里的行号猜。")),
        function_tool(_fi, name_override="file_index",
                      description_override=("给一个代码文件建**函数级索引**，每块一行 `函数名@行号:签名`。"
                                             "只给目录不给正文——先看索引定位，再用 read_block 取需要的函数。"
                                             "**读大文件优先用它，不要一上来 read_file 全文。**")),
        function_tool(_rb, name_override="read_block",
                      description_override=("按 file_index 给的 key（`函数名@行号`）取一个函数的完整正文。"
                                             "这是缺页调入：上下文里只放索引，用到哪块取哪块。")),
        function_tool(_e, name_override="edit_file",
                      description_override=("在文件里把 old 字面替换成 new。old 必须精确匹配含空白标点，"
                                             "找不到会报错不会静默不动。出现多次时需显式 replace_all。"
                                             "**只能改本次白名单里的文件。**")),
        function_tool(_w, name_override="write_file",
                      description_override="新建或整篇覆盖一个文件。**只能改白名单里的文件。**"),
        function_tool(_a, name_override="append_file",
                      description_override="往文件末尾追加。**只能改白名单里的文件。**"),
        function_tool(_rollback, name_override="rollback_file",
                      description_override=("把文件回滚到某次写前的原文。写工具返回里带 [快照 ID]，"
                                             "误改或验证失败时用该 ID 精确回滚；不传 ID 回滚到最近快照。")),
        function_tool(_snaps, name_override="snap_list",
                      description_override="列出某文件的所有快照 ID（最新在后），配合 rollback_file 使用。"),
    ]
    if t.with_cmd:
        def _cmd(cmd: str) -> str:
            """跑一条验证命令，返回退出码与输出。

            **cwd 固定在仓库根**，不是 scope 的第一段。原来用
            `t.scope.split("/")[0]`，对 `apps/web/src/api.ts` 会跑到 `apps/`，
            于是 `npx tsc -p apps/web/tsconfig.json` 这类命令全挂。
            验证命令几乎总是要从仓库根跑的。
            """
            return run_cmd(cmd, root=t.repo, cwd=".")

        tools.append(function_tool(_cmd, name_override="run_cmd",
                                   description_override="跑验证命令，返回退出码与输出。"))

    if cache is not None:
        def _cache_get(key: str) -> str:
            """按 key 取回被换出到 sidecar 的工具结果正文。

            上下文里看到 `[已换出：...]` 墓碑时，用这个工具把正文调回来
            （虚拟内存的缺页调入）。
            """
            body = cache.get(key)
            return body if body is not None else f"sidecar 里没有 key：{key}"

        tools.append(function_tool(_cache_get, name_override="cache_get",
                                   description_override=(
                                       "按 key 取回被换出的工具结果正文。"
                                       "看到 `[已换出：...]` 墓碑时用，key 就是墓碑里那个。"
                                       "不要凭记忆猜被换出的内容。")))
    return tools


# ===================================================================== 组装
@dataclass
class Context:
    task: Task
    dispatch: str = ""
    knowledge: str = ""
    tokens: int = 0


def assemble(t: Task) -> Context:
    """复用 kb dispatch + kb pack / kb route，不重写组装逻辑。

    给了 `route` 就走路由装订：成员集 + 每成员保真度由 leader 的规格决定，
    而不是「预算 ÷ 文件数」。目录装订在 200k 预算下仍会把 19 个大文件降级（实测），
    所以「想看这些文件的原文」只能靠路由表达。
    """
    ctx = Context(task=t)
    rc, d = _kb(["dispatch", t.scope])
    if rc != 0:
        raise RuntimeError(f"dispatch 失败：{d}")
    ctx.dispatch = d
    if t.route:
        # 路由规格里已经写死了 budget/成员，不再叠加 pack 的参数
        argv = ["route", "--spec", t.route]
        if getattr(t, "route_degrade", False):
            argv.append("--degrade")
        rc, k = _kb(argv)
        if rc != 0:
            raise RuntimeError(f"route 失败：{k}")
        ctx.knowledge = k
        ctx.tokens = kb.est_tokens(d) + kb.est_tokens(k)
        return ctx
    argv = ["pack", t.scope, "--budget", str(t.budget)]
    if not t.with_source:
        argv.append("--no-source")
    elif t.index_only:
        # 虚拟内存：让 kb pack 从源头就只装函数级索引，
        # 省下的预算全留给知识层（约束/契约/踩坑）——那才是「改之前必须知道的」。
        # 之前在 agent 层做字符串替换，预算是 pack 内部算的，知识层已被挤光才换，
        # 白省了源码却救不回知识。必须在源头做。
        argv.append("--index")
    rc, k = _kb(argv)
    if rc != 0:
        raise RuntimeError(f"pack 失败：{k}")
    ctx.knowledge = k
    ctx.tokens = kb.est_tokens(d) + kb.est_tokens(k)
    return ctx


def _shared_instructions() -> str:
    """**所有子 agent 共用的系统指令。**

    这里绝不能插 scope / 任务名 / 白名单这类每个 agent 都不同的内容：
    指令是消息序列的最前面，一旦在开头就分叉，后面再长也一律不命中 cache。
    「你只负责 X」这种差异化约束放到 user 消息靠后的位置（见 render）。
    """
    return (
        "你是 codeb 派出的子 agent，负责一个明确的写范围。\n"
        "**只碰白名单里的文件**；白名单之外一律不要动，也不要绕过（不要用别的工具间接改）。\n"
        "上下文已给全：源码以函数级索引给出，需要某个函数用 read_block(key) 调入，"
        "不要一上来 read_file 全文。需要定位用 file_index / grep_text。\n"
        "看到 `[已换出：...]` 墓碑时，用 cache_get(key) 取回被换出的正文。\n"
        "改代码用 edit_file。改完必须跑验证命令确认没破坏既有测试。\n"
        "用中文回答，先给结论，再给改动清单。"
    )


def render(ctx: Context, t: Task, deps: dict[str, str] | None = None) -> list[dict]:
    """把上下文变成注入消息。

    **顺序就是 cache 布局**，从稳定到易变：

        1. 共用的世界常识（COMMON_WORLD）              ← 所有任务逐字节一致
        2. 写范围检查（kb dispatch）                    ← 同范围一致，比知识层短
        3. 知识层（kb pack）                            ← 同范围一致（**最大块，也最易变**）
        4. 上游结论（depends_on）                       ← 只依赖同一批任务时一致
        5. 本次写范围与白名单                           ← 每个任务不同
        6. 任务本身（最短，放最后）                     ← 每个任务不同

    为什么知识层要排在 dispatch 之后而不是之前：知识与范围强相关，
    换范围就整段不同，**它是最容易分叉的大块**。放得越靠前，后面能共享的就越少。
    实测（同仓库不同范围）：COMMON_WORLD 之后先接 dispatch，公共前缀从 296 涨到 454 字符，
    提高 53%。

    真正的 cache 收益在**同一范围**的任务上：那时 1/2/3 全一致，
    公共前缀达到 859/861 字符（99.8%），只有最后的差异约束不同。
    """
    parts: list[str] = [COMMON_WORLD]

    # 2. 写范围检查（短，且同范围完全一致）
    if ctx.dispatch:
        parts.append(f"=== 写范围检查 ===\n{ctx.dispatch}")

    # 3. 知识层（大块，同范围一致、异范围整段不同）
    if ctx.knowledge:
        parts.append(f"=== 知识层（本范围装订） ===\n{ctx.knowledge}")

    # 4. 上游结论：只放**结论**，不放过程
    if deps:
        blocks = [f"--- 来自「{name}」的结论 ---\n{text}" for name, text in deps.items()]
        parts.append(
            "=== 上游结论（已完成的任务，你可以直接依赖） ===\n"
            + "\n\n".join(blocks)
        )

    # 5. 本任务的差异约束（放这里而不是 instructions，就是为了保住前缀）
    tail = [f"你负责的写范围是 `{t.scope}`（仓库 `{t.repo}`）。"]
    if t.allowed:
        tail.append(f"可改文件白名单：{', '.join(f'`{a}`' for a in t.allowed)}。")
    if t.denied:
        tail.append(f"禁止改动：{', '.join(f'`{d}`' for d in t.denied)}。")
    if t.note:
        tail.append(f"\n=== 补充说明（leader 要求） ===\n{t.note}")
    parts.append("\n".join(tail))

    return [
        {"role": "system", "content": _shared_instructions()},
        {"role": "user", "content": "\n\n".join(parts)},
        {"role": "user", "content": t.task},
    ]


# 所有子 agent 逐字节相同的开头。**这是 cache 的地基**：
# 它越靠前、越稳定，后续每条消息能命中的公共前缀就越长。
COMMON_WORLD = (
    "=== 关于 codeb ===\n"
    "codeb 是一个多仓库知识库。每个范围的知识页（约束、踩过的坑、接口契约）"
    "已由 kb.py 装订进上下文，源码也一并装进来了。\n"
    "工具说明：read_file / read_file_range / list_dir / grep_text 用来取细节；"
    "edit_file 做精确替换（old 必须逐字符匹配）；write_file 整篇覆盖；"
    "append_file 追加；run_cmd 跑验证命令。\n"
    "**不要猜 API 或文件内容，用工具查。**改完必须验证。\n"
)


# ===================================================================== 执行
async def run_task(t: Task, env: dict, deps: dict[str, str] | None = None) -> dict:
    ctx = assemble(t)
    # client 必须显式关闭：httpx 的连接池在事件循环关闭后仍会触发异步清理，
    # 于是打出 `RuntimeError: Event loop is closed`。这行噪音会盖住真正的错误，
    # 所以用 try/finally 关掉，而不是指望 gc。
    client = AsyncOpenAI(base_url=env["ZHIHU_LLM_BASE_URL"],
                         api_key=env["ZHIHU_LLM_API_KEY"])
    # hook 轨迹独立于 RunResult：即使 MaxTurnsExceeded 也有内容
    hook_trace: list[dict] = []
    # append-only session log：事实源。上下文窗口只是从它 materialize 的视图。
    # 每个任务一行 JSONL，崩溃后续跑 seq 自动延续。
    slog = SessionLog(t.name, root=CODEB / "_kbwork" / "agent-logs")
    slog.append("task_start", scope=t.scope, repo=t.repo,
                task=t.task[:300], budget=t.budget)
    # hook 事件同时喂给 legacy list 与 session log（测试仍读 hook_trace）
    hook_sink = DualSink(hook_trace, slog)
    # 上下文缓存（换页层）：老工具结果换出上下文，正文留 sidecar。
    cache = None
    if t.cache_keep_recent is not None:
        cache = ContextCache(keep_recent=t.cache_keep_recent)
    agent = Agent(
        name=t.name,
        # 共用指令，不含任何 per-task 内容（否则 cache 从第一个字节就不命中）
        instructions=_shared_instructions(),
        model=OpenAIChatCompletionsModel(model=env["ZHIHU_LLM_MODEL"],
                                         openai_client=client),
        tools=make_tools(t, cache),
        hooks=TraceHooks(hook_sink),
    )
    cfg = RunConfig(call_model_input_filter=cache.filter) if cache else RunConfig()
    t0 = time.perf_counter()
    try:
        r = await Runner.run(agent, render(ctx, t, deps), run_config=cfg,
                             max_turns=t.max_turns)
        dt = time.perf_counter() - t0
        slog.append("task_end", ok=True, seconds=round(dt, 1),
                    answer=str(r.final_output)[:300])
        result = _collect(t, ctx, r, dt, ok=True, error=None, hook_trace=hook_trace,
                          cache_stats=cache.stats() if cache else None)
        result["session_log"] = str(slog.path)
        return result
    except Exception as e:
        dt = time.perf_counter() - t0
        # 关键：异常时**不抛裸异常**，而是返回「部分结果」。
        # 烧满轮次 / 429 / 超时都可能在这里发生，此时模型可能已经改了一部分文件——
        # 丢掉这些信息，leader 就不知道它改了什么，只能整块重跑（浪费已花的 token 和时间）。
        # RunResult 拿不到（r=None），但 hook_trace 有工具调用记录，作为 fallback。
        err = f"{type(e).__name__}: {e}"
        slog.append("task_error", ok=False, error=err[:300], seconds=round(dt, 1))
        result = _collect(t, ctx, None, dt, ok=False, error=err,
                          hook_trace=hook_trace,
                          cache_stats=cache.stats() if cache else None)
        result["session_log"] = str(slog.path)
        return result
    finally:
        try:
            await client.close()
        except Exception:
            pass


def _collect(t: Task, ctx: Context, r, dt: float, ok: bool, error: str | None,
             hook_trace: list[dict] | None = None,
             cache_stats: dict | None = None) -> dict:
    """从 RunResult（或 None）里整理结果。

    异常时 r 为 None，此时用 `hook_trace` 兜底——
    那是 hook 在工具调用发生时记下的，不依赖 RunResult。
    """
    calls: list[str] = []
    steps: list[dict] = []
    answer = ""
    if r is not None:
        for i in r.new_items:
            if type(i).__name__ == "ToolCallItem":
                ri = getattr(i, "raw_item", None)
                name = getattr(ri, "name", "?")
                args = getattr(ri, "arguments", "")
                if isinstance(args, str) and len(args) > 200:
                    args = args[:200] + "…"
                calls.append(name)
                steps.append({"tool": name, "args": args})
        answer = str(r.final_output)
    # fallback：RunResult 不可用（异常）时，从 hook 轨迹还原工具调用序列
    if not steps and hook_trace:
        ends = [h for h in hook_trace if h.get("stage") == "end"]
        calls = [h["tool"] for h in ends]
        steps = [{"tool": h["tool"], "result": h.get("result", "")} for h in ends]
    return {
        "name": t.name,
        "scope": t.scope,
        "ok": ok,
        "error": error,
        "seconds": round(dt, 1),
        "context_tokens": ctx.tokens,
        "tool_calls": calls,
        "steps": steps,
        "answer": answer,
        "cache": cache_stats,
    }


# ===================================================================== 调度
# 并发上限，类比「CPU 核数」。超过就排队，不是全丢给 asyncio.gather。
# 实测依据：同一 key 并发 2 个就出现过 429 导致烧满 8 轮，所以默认 2 而不是 8。
DEFAULT_CONCURRENCY = 2


@dataclass
class Trace:
    """一个任务的落盘轨迹。persist=False 时只在内存里，不写盘。"""
    name: str
    scope: str
    ok: bool
    conclusion: str
    steps: list[dict]
    error: str | None
    seconds: float

    def to_dict(self) -> dict:
        return {"name": self.name, "scope": self.scope, "ok": self.ok,
                "conclusion": self.conclusion, "steps": self.steps,
                "error": self.error, "seconds": self.seconds}


class Scheduler:
    """按依赖 + 并发上限调度任务。

    设计要点（都是这次讨论定下来的）：

    1. **并发上限 = 队列，不是全放**。`asyncio.gather` 一次性全发，
       同 key 并发立刻撞 429；用信号量压到 N，超出的排队等。
    2. **依赖失败就不跑下游**。上游结论是下游的输入，上游失败时下游拿到的
       是噪音，宁可标记 skipped 也不要让它基于错误前提改文件。
    3. **任务边界折叠**：下游只拿上游的**结论**（conclusion），不拿它的过程。
       这是最彻底的折叠——不需要裁剪历史，因为历史根本没进下游的上下文。
    4. **persist 决定轨迹是否写盘**。默认只传结论；需要追查时 leader 显式开。
    """

    def __init__(self, tasks: list[Task], env: dict, concurrency: int = DEFAULT_CONCURRENCY,
                 trace_dir: Path | None = None):
        self.tasks = {t.name: t for t in tasks}
        self.order = [t.name for t in tasks]
        self.env = env
        self.sem = asyncio.Semaphore(max(1, concurrency))
        self.trace_dir = trace_dir or (CODEB / "_kbwork" / "agent-traces")
        self.results: dict[str, dict] = {}
        self.conclusions: dict[str, str] = {}
        self._validate()

    def _validate(self) -> None:
        for t in self.tasks.values():
            for d in t.depends_on:
                if d not in self.tasks:
                    raise RuntimeError(f"任务 {t.name} 依赖 {d}，但后者不在本次派发里")
                if d == t.name:
                    raise RuntimeError(f"任务 {t.name} 依赖自己")
        # 环检测（拓扑排序能处理完就是无环）
        self._topo()

    def _topo(self) -> list[str]:
        """拓扑序。同时用于环检测——排不完说明有环。"""
        done: list[str] = []
        seen = set()
        while len(done) < len(self.order):
            progressed = False
            for name in self.order:
                if name in seen:
                    continue
                if all(d in seen for d in self.tasks[name].depends_on):
                    done.append(name)
                    seen.add(name)
                    progressed = True
            if not progressed:
                cycle = [n for n in self.order if n not in seen]
                raise RuntimeError(f"依赖成环，无法调度：{cycle}")
        return done

    async def _run_one(self, name: str) -> None:
        t = self.tasks[name]
        # 上游全部成功才跑；任一失败/跳过则本任务跳过
        bad = [d for d in t.depends_on
               if not self.results.get(d, {}).get("ok")]
        if bad:
            self.results[name] = {
                "name": name, "scope": t.scope, "ok": False,
                "error": f"上游未成功，跳过：{bad}", "skipped": True,
                "seconds": 0, "context_tokens": 0, "tool_calls": [], "steps": [],
                "answer": "", "conclusion": "",
            }
            self.conclusions[name] = ""
            return

        deps = {d: self.conclusions.get(d, "") for d in t.depends_on if self.conclusions.get(d)}
        async with self.sem:                       # ← 并发上限在这里生效
            r = await run_task(t, self.env, deps)
        self.results[name] = r
        # 结论 = 回答的第一段（去掉可能的冗长细节），这是传给下游的全部内容
        self.conclusions[name] = r.get("answer", "") if r.get("ok") else ""
        if t.persist:
            self._persist(t, r)

    def _persist(self, t: Task, r: dict) -> None:
        self.trace_dir.mkdir(parents=True, exist_ok=True)
        p = self.trace_dir / f"{t.name}.json"
        tr = Trace(t.name, t.scope, r.get("ok", False), r.get("answer", ""),
                   r.get("steps", []), r.get("error"), r.get("seconds", 0))
        p.write_text(json.dumps(tr.to_dict(), ensure_ascii=False, indent=2),
                     encoding="utf-8")

    async def run(self) -> list[dict]:
        """按依赖分层跑。同层内受并发上限约束，跨层必须等前一层。"""
        done: set[str] = set()
        remaining = list(self.order)
        while remaining:
            # 当前所有依赖已满足的任务构成一层
            ready = [n for n in remaining
                     if all(d in done for d in self.tasks[n].depends_on)]
            if not ready:
                raise RuntimeError(f"调度卡住，剩余：{remaining}")
            await asyncio.gather(*[self._run_one(n) for n in ready])
            done.update(ready)
            remaining = [n for n in remaining if n not in done]
        return [self.results[n] for n in self.order]


async def run_many(tasks: list[Task], env: dict | None = None,
                   concurrency: int = DEFAULT_CONCURRENCY) -> list[dict]:
    """并行跑多个子 agent：先验互斥，再按依赖 + 并发上限调度。"""
    env = env or load_env()
    scopes = [t.scope for t in tasks]
    rc, d = _kb(["dispatch"] + scopes + ["--json"])
    if rc != 0:
        raise RuntimeError(f"dispatch 失败：{d}")
    info = json.loads(d)
    if info["conflicts"]:
        raise RuntimeError(
            f"写范围冲突，拒绝并行派发：{json.dumps(info['conflicts'], ensure_ascii=False)[:400]}")
    note = ""
    if info.get("serial_bottlenecks"):
        note = ("\n\n=== 全局串行点（不要自己重生成，等 leader 统一处理）===\n"
                + "\n".join(f"- {k}" for k in info["serial_bottlenecks"]))
    # 把串行点提醒追加进每个任务的 note
    enriched = [Task(**{**t.__dict__, "note": (t.note + note).strip()}) for t in tasks]
    return await Scheduler(enriched, env, concurrency).run()


def run_sync(tasks: list[Task], **kw) -> list[dict]:
    """同步入口：kb.py 的 cmd_* 可以直接调。

    `Event loop is closed` 那类噪音的正确修法在 `run_task` 的 finally 里
    （显式 `await client.close()`），不是在这里加 sleep——httpx 连接池的
    清理协程必须在循环关闭**之前**跑完，事后补是补不上的。
    """
    return asyncio.run(run_many(tasks, **kw))


# ===================================================================== CLI
def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="codeb_agent",
                                description="在 codeb 里组装并运行子 agent")
    sub = p.add_subparsers(dest="cmd", required=True)

    r = sub.add_parser("run", help="跑一个子 agent（单任务）")
    r.add_argument("--scope", required=True, help="写范围（相对仓库根）")
    r.add_argument("--task", required=True, help="要做什么")
    r.add_argument("--repo", default="infohub", help="仓库名（codeb/infohub/atomkgraph）")
    r.add_argument("--name", default="", help="子 agent 名，默认由 scope 推导")
    r.add_argument("--allow", action="append", default=[], help="可改文件白名单，可多次")
    r.add_argument("--deny", action="append", default=[], help="禁止文件，可多次")
    r.add_argument("--budget", type=int, default=8000, help="装订预算（tok）")
    # **默认必须与 Task.with_source 一致（True）**。
    # 之前写成 store_true 默认 False，CLI 构造 Task 时显式传 False，
    # 把 dataclass 的默认值彻底废掉了 —— 于是 kb agent 永远只装知识层，
    # 对没有知识页认领的范围装出 0 块 0 tok，agent 拿到空白上下文。
    r.add_argument("--no-source", action="store_true",
                   help="只装知识层不装源码（问「有哪些坑」时用）")
    r.add_argument("--max-turns", type=int, default=None,
                   help="轮次上限；默认不限。不要轻易设——任务该拆细，不是靠轮数掐断")
    r.add_argument("--no-cmd", action="store_true", help="不给 run_cmd 工具")
    r.add_argument("--note", default="", help="追加的静态上下文（契约/警告等）")
    r.add_argument("--route", default="",
                   help="路由规格 JSON 路径：改走 kb route --spec（成员集 + 每成员保真度）")
    r.add_argument("--route-degrade", action="store_true",
                   help="路由超预算时允许自动降档（默认拒绝）")
    r.add_argument("--persist", action="store_true", help="把完整执行轨迹落盘")
    r.add_argument("--json", action="store_true", help="输出 JSON")

    # 多任务：从 JSON 文件读任务列表，走 Scheduler（依赖 + 并发上限）
    m = sub.add_parser("run-plan", help="按计划文件跑多个子 agent（依赖 + 并发上限）")
    m.add_argument("plan", help="计划文件（JSON：任务数组）")
    m.add_argument("--concurrency", type=int, default=DEFAULT_CONCURRENCY,
                   help=f"并发上限，默认 {DEFAULT_CONCURRENCY}（同 key 并发过高会撞 429）")
    m.add_argument("--json", action="store_true", help="输出 JSON")
    m.add_argument("--persist-all", action="store_true", help="所有任务轨迹都落盘")
    return p


def plan_from_json(path: str, persist_all: bool = False) -> list[Task]:
    """从 JSON 读任务列表。

    格式（数组，字段与 Task 同名，只有 name/scope/task 必填）：

        [
          {"name": "w1", "scope": "a.py", "task": "改 X", "repo": "codeb",
           "allowed": ["a.py"]},
          {"name": "w2", "scope": "b.py", "task": "改 Y", "repo": "codeb",
           "allowed": ["b.py"], "depends_on": ["w1"]}
        ]
    """
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    if isinstance(raw, dict):
        raw = raw.get("tasks", [])
    if not isinstance(raw, list):
        raise RuntimeError("计划文件必须是任务数组，或 {\"tasks\": [...]}")
    out: list[Task] = []
    for i, item in enumerate(raw):
        if not isinstance(item, dict):
            raise RuntimeError(f"第 {i} 项不是对象")
        for k in ("scope", "task"):
            if not item.get(k):
                raise RuntimeError(f"第 {i} 项缺必填字段 {k}")
        kw = {k: v for k, v in item.items() if k in Task.__dataclass_fields__}
        kw.setdefault("name", f"worker-{i}")
        if persist_all:
            kw["persist"] = True
        out.append(Task(**kw))
    return out


def _print_result(r: dict, as_json: bool) -> None:
    if as_json:
        print(json.dumps(r, ensure_ascii=False, indent=2))
        return
    status = "✓" if r.get("ok") else ("⤼ 跳过" if r.get("skipped") else "✗ 失败")
    print(f"=== {status} {r['name']}  {r['scope']} ===")
    if r.get("error"):
        print(f"  错误：{r['error']}")
    print(f"  耗时 {r.get('seconds', 0)}s · 上下文 {r.get('context_tokens', 0)} tok · "
          f"工具调用 {len(r.get('tool_calls') or [])} 次")
    if r.get("tool_calls"):
        print(f"  调用：{r['tool_calls']}")
    if r.get("answer"):
        print()
        print(r["answer"])


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.cmd == "run":
        t = Task(
            name=args.name or f"worker-{args.scope.strip('/').replace('/', '-')}",
            scope=args.scope,
            task=args.task,
            repo=args.repo,
            allowed=args.allow,
            denied=args.deny,
            budget=args.budget,
            with_source=not args.no_source,     # ← 与 Task 默认一致，不再被 CLI 覆盖成 False
            max_turns=args.max_turns,
            with_cmd=not args.no_cmd,
            note=args.note,
            persist=args.persist,
            route=args.route,
            route_degrade=args.route_degrade,
        )
        try:
            out = run_sync([t])
        except Exception as e:
            print(json.dumps({"ok": False, "error": str(e)}, ensure_ascii=False, indent=2))
            return 2
        r = out[0]
        _print_result(r, args.json)
        return 0 if r.get("ok") else 1

    if args.cmd == "run-plan":
        try:
            tasks = plan_from_json(args.plan, args.persist_all)
        except Exception as e:
            print(json.dumps({"ok": False, "error": f"读取计划失败：{e}"},
                            ensure_ascii=False, indent=2))
            return 2
        try:
            out = run_sync(tasks, concurrency=args.concurrency)
        except Exception as e:
            print(json.dumps({"ok": False, "error": str(e)}, ensure_ascii=False, indent=2))
            return 2
        if args.json:
            print(json.dumps({"ok": all(r.get("ok") for r in out), "results": out},
                            ensure_ascii=False, indent=2))
        else:
            for r in out:
                _print_result(r, False)
                print()
            ok_n = sum(1 for r in out if r.get("ok"))
            skip_n = sum(1 for r in out if r.get("skipped"))
            print(f"合计 {len(out)} 个任务：成功 {ok_n} · 跳过 {skip_n} · "
                  f"失败 {len(out) - ok_n - skip_n}")
        return 0 if all(r.get("ok") for r in out) else 1

    return 1


if __name__ == "__main__":
    sys.exit(main())
