"""把结论固化成可复用的最小实现：codeb 组装 + openai-agents 执行。

这不是探针，是候选正式代码。约 120 行。
它证明一件事：openai-agents 在 codeb 里只当「执行壳」，
组装 100% 由 kb.py 完成——没有一行业务逻辑重复。
"""
import sys, asyncio, io, contextlib, json
from pathlib import Path
from dataclasses import dataclass, field

CODEB = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(CODEB))
import kb

from agents import (Agent, Runner, function_tool, OpenAIChatCompletionsModel,
                    set_tracing_disabled, RunConfig)
from openai import AsyncOpenAI
set_tracing_disabled(True)


# ---------------------------------------------------------------- 凭据
def load_env() -> dict:
    out = {}
    p = Path("D:/work/project/infohub/collector/.env")
    if not p.exists():
        return out
    for line in p.read_text(encoding="utf-8-sig", errors="replace").splitlines():
        s = line.strip()
        if s and not s.startswith("#") and "=" in s:
            k, v = s.split("=", 1)
            if k.strip().startswith("ZHIHU_LLM_"):
                out.setdefault(k.strip(), v.strip().strip('"').strip("'"))
    return out


# ---------------------------------------------------------------- codeb 调用
def _kb(argv: list[str]) -> tuple[int, str]:
    o, e = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(o), contextlib.redirect_stderr(e):
        rc = kb.main(argv)
    return rc, (o.getvalue() if rc == 0 else e.getvalue()).strip()


# ---------------------------------------------------------------- 文件工具
# 子 agent 只拿「干活」的工具，不拿「找上下文」的工具——
# 上下文由 codeb 组装好后直接注入（实测调用数 0，比让它自己调 kb_pack 快一倍）。
@function_tool
def read_file(path: str, max_lines: int = 150) -> str:
    """读仓库里的一个文件（相对仓库根），返回前 max_lines 行。"""
    roots = {"infohub": Path("D:/work/project/infohub"),
             "atomkgraph": Path("D:/work/project/knowledge_map/atomkgraph"),
             "codeb": CODEB}
    for name, base in roots.items():
        f = base / path
        if f.exists():
            lines = f.read_text(encoding="utf-8", errors="replace").splitlines()
            return (f"{path}（{len(lines)} 行，显示前 {min(max_lines, len(lines))} 行）\n"
                    + "\n".join(lines[:max_lines]))
    return f"不存在：{path}（已试 {', '.join(roots)}）"


@function_tool
def grep_text(pattern: str, path: str = ".") -> str:
    """在目录里搜字符串，返回 路径:行号:内容（最多 20 条）。"""
    for base in (Path("D:/work/project/infohub"), CODEB):
        d = base / path
        if not d.exists():
            continue
        out = []
        for f in d.rglob("*"):
            if f.suffix not in (".py", ".ts", ".yaml", ".yml", ".md"):
                continue
            try:
                for i, line in enumerate(
                        f.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
                    if pattern in line:
                        out.append(f"{f.relative_to(base).as_posix()}:{i}: {line.strip()[:100]}")
                        if len(out) >= 20:
                            return "\n".join(out)
            except Exception:
                pass
        return "\n".join(out) or "没有命中"
    return f"目录不存在：{path}"


# ---------------------------------------------------------------- 组装
@dataclass
class Context:
    """codeb 组装出来的一份上下文。这就是「子 agent 看到的世界」。"""
    scope: str
    dispatch: str = ""
    knowledge: str = ""
    budget: int = 8000
    tokens: int = 0
    report: dict = field(default_factory=dict)


def assemble(scope: str, budget: int = 8000, with_source: bool = False) -> Context:
    """复用 kb dispatch + kb pack，不重写任何组装逻辑。"""
    ctx = Context(scope=scope, budget=budget)
    rc, d = _kb(["dispatch", scope])
    if rc != 0:
        raise RuntimeError(f"dispatch 失败：{d}")
    ctx.dispatch = d
    argv = ["pack", scope, "--budget", str(budget)]
    if not with_source:
        argv.append("--no-source")
    rc, k = _kb(argv)
    if rc != 0:
        raise RuntimeError(f"pack 失败：{k}")
    ctx.knowledge = k
    ctx.tokens = kb.est_tokens(d) + kb.est_tokens(k)
    return ctx


def render(ctx: Context, task: str) -> list[dict]:
    """把上下文变成注入用的消息。

    两段式：先给世界（装订结果），再给任务。
    合成一条会让模型把「任务」当成上下文的一部分，答得发散。
    """
    return [
        {"role": "user", "content":
         f"你负责的写范围是 `{ctx.scope}`。下面是 codeb 为它装订好的上下文，"
         f"已包含文件清单、约束和派生文件信息。**只依据它和文件工具回答，不要猜。**\n\n"
         f"=== 写范围检查 ===\n{ctx.dispatch}\n\n"
         f"=== 知识层 ===\n{ctx.knowledge}"},
        {"role": "user", "content": task},
    ]


# ---------------------------------------------------------------- 执行
def _client(env):
    return AsyncOpenAI(base_url=env["ZHIHU_LLM_BASE_URL"], api_key=env["ZHIHU_LLM_API_KEY"])


async def spawn_one(ctx: Context, task: str, env: dict, max_turns: int = 4) -> dict:
    agent = Agent(
        name=f"worker-{ctx.scope.strip('/').replace('/', '-')}",
        instructions=(f"你只负责写范围 `{ctx.scope}`，不要碰别的目录。\n"
                      f"上下文已给全；需要源码细节时用 read_file / grep_text。\n"
                      f"用中文回答，简短，先给结论。"),
        model=OpenAIChatCompletionsModel(model=env["ZHIHU_LLM_MODEL"],
                                         openai_client=_client(env)),
        tools=[read_file, grep_text],
    )
    r = await Runner.run(agent, render(ctx, task), run_config=RunConfig(),
                         max_turns=max_turns)
    return {
        "scope": ctx.scope,
        "answer": str(r.final_output),
        "tool_calls": len([i for i in r.new_items if type(i).__name__ == "ToolCallItem"]),
        "context_tokens": ctx.tokens,
    }


async def spawn_many(scopes: list[str], task: str, *,
                     budget: int = 8000, with_source: bool = False,
                     max_turns: int = 4) -> list[dict]:
    """并行跑 N 个子 agent。**先 dispatch 验互斥，冲突就拒绝派发。**"""
    env = load_env()
    # 一次性验互斥：不让 N 个 agent 互相覆盖
    rc, d = _kb(["dispatch"] + scopes + ["--json"])
    if rc != 0:
        raise RuntimeError(f"dispatch 失败：{d}")
    info = json.loads(d)
    if info["conflicts"]:
        raise RuntimeError(
            f"写范围冲突，拒绝并行派发：{json.dumps(info['conflicts'], ensure_ascii=False)[:300]}")
    if info.get("serial_bottlenecks"):
        # 不拦，但要带进上下文提醒
        note = ("\n\n=== 全局串行点（不要自己重生成）===\n"
                + "\n".join(f"- {k}" for k in info["serial_bottlenecks"]))
    else:
        note = ""

    ctxs = []
    for s in scopes:
        c = assemble(s, budget=budget, with_source=with_source)
        c.dispatch += note
        ctxs.append(c)
    return await asyncio.gather(*[spawn_one(c, task, env, max_turns) for c in ctxs],
                                return_exceptions=True)


def run_sync(scopes: list[str], task: str, **kw) -> list[dict]:
    """同步入口：codeb 的 cmd_* 可以直接调这个。"""
    return asyncio.run(spawn_many(scopes, task, **kw))


if __name__ == "__main__":
    import time
    scopes = sys.argv[1].split(",") if len(sys.argv) > 1 else ["collector/kit/", "collector/refs/"]
    task = sys.argv[2] if len(sys.argv) > 2 else "这范围里有哪些文件？改之前最重要的两条约束？"
    t0 = time.perf_counter()
    out = run_sync(scopes, task)
    dt = time.perf_counter() - t0
    print(f"并行 {len(scopes)} 个子 agent，总耗时 {dt:.1f}s\n")
    for r in out:
        if isinstance(r, Exception):
            print(f"✗ 失败：{type(r).__name__}: {str(r)[:150]}")
            continue
        print(f"=== {r['scope']} ===")
        print(f"上下文 {r['context_tokens']} tok · 工具调用 {r['tool_calls']} 次")
        print(r["answer"][:700])
        print()
