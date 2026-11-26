"""路由提问：一次装订，逐条提问，**每问都是全新调用、无历史**。

为什么每问不带历史（这是使用者明确要求的语义，也是实测结论支撑的）：

1. 装订占 99% 的 token。实测 155k 的包，后续每问只增加 86 tok（三问合计）。
   历史对话相对包体是噪声，留着它反而让「这一问的答案」和「上一问的答案」
   在上下文里抢位置。
2. 每问独立 ⟹ 前缀完全相同 ⟹ 前缀缓存每次都能命中。带历史的话前缀每轮都变，
   缓存全废。
3. 每问独立 ⟹ 答案可并行、可重跑、可单独判定。带历史时第 3 问答错，
   你无法判断是问题难还是第 2 问把它带偏了。

代价是「追问」不存在：想问「那你刚才说的第三点展开」必须重新组织成一个
自足的问题。这是刻意的——自足的问题才能被单独复现和评判。
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
CODEB = HERE.parent.parent

# 默认模型。选它的理由在 load_env 的 docstring 里，是实测出来的：
# 换成 30b 会让事实题从 2/2 掉到 0/2，并且它仍然给出精确的错数字。
DEFAULT_MODEL = "nvidia/nemotron-3.5-super-vl-120b-a12b"


def load_env() -> dict:
    """从 infohub 的 .env 读 NVIDIA 端点（与探针脚本同一来源）。"""
    p = Path("D:/work/project/infohub/collector/.env")
    out: dict[str, str] = {}
    if p.is_file():
        for line in p.read_text(encoding="utf-8-sig", errors="replace").splitlines():
            s = line.strip()
            if s and not s.startswith("#") and "=" in s:
                k, v = s.split("=", 1)
                if k.strip().startswith(("ZHIHU_LLM_", "NVIDIA_")):
                    out.setdefault(k.strip(), v.strip().strip('"').strip("'"))
    for k in ("ZHIHU_LLM_BASE_URL", "ZHIHU_LLM_API_KEY", "ZHIHU_LLM_MODEL"):
        if os.environ.get(k):
            out[k] = os.environ[k]
    # 模型默认固定成 super-vl-120b，**不跟随 .env 的 ZHIHU_LLM_MODEL**。
    # 实测结论直接推翻了 .env 的默认值，同一份包、同一套提示词、同一批题：
    #   super-vl-120b：两道事实题 2/2（28 / 106），都正确调了 grep_count/find_line
    #   lightning-30b：两道都错（11 / 163），而且一次工具都没调
    # 「读到工具返回值后原样转述」是路由问答的底线能力，30b 做不到，
    # 而且它错得很自信（给出精确的错数字，不表示不确定）。
    out.setdefault("ZHIHU_LLM_MODEL", DEFAULT_MODEL)
    if os.environ.get("KB_ROUTE_MODEL"):
        out["ZHIHU_LLM_MODEL"] = os.environ["KB_ROUTE_MODEL"]
    return out


SYSTEM = (
    "你在读一份 leader 装订好的上下文包，里面有源码原文（标 `full`）、"
    "函数级索引（标 `index`，正文用 read_block 取）和签名（标 `outline`）。\n"
    "\n"
    "你有三个工具：read_block 取正文、grep_count 数命中、find_line 定位行号。"
    "**是否需要用、用哪个、用几次，完全由你自己判断**——不要凭问题里出现了"
    "「几个」「哪个」这类词就机械地决定去数数。开放式问题（哪个命令做什么、"
    "为什么慢）答案在源码里，读原文/推理；只有真正需要精确计数或行号时才用"
    "grep_count / find_line。\n"
    "\n"
    "回答规则：\n"
    "1. 结论先行，给依据，引用代码给 `文件:行号`。\n"
    "2. 引用工具给的数字时原样照搬，不要自己加减。\n"
    "3. 包里确实没有的信息才说「没有」，并写明你找过什么。"
)


def build_tools(route: dict, roots: dict[str, Path],
                cache: dict | None = None):
    """只暴露包内成员所在的仓库，且只给「读/查」三类工具。

    给写工具是危险的：这一层的任务是回答问题，不是改代码。
    给它 edit_file 等于允许它在回答过程中把被观察的对象改掉。

    cache 不为 None 时，工具结果按 (name, sorted_kwargs) 缓存，
    并行提问时不同问题触发相同调用可直接复用。
    """
    sys.path.insert(0, str(HERE))
    import tools_fs  # noqa: E402
    import threading

    repo = route.get("repo") or ""
    root = repo if repo in tools_fs.ROOTS else "codeb"

    lock = threading.Lock()

    def _cached(name: str, fn, **kw):
        """带缓存的工具调用包装。cache 为 None 时直通。"""
        if cache is None:
            return fn(**kw)
        key = (name, json.dumps(kw, sort_keys=True, ensure_ascii=False))
        with lock:
            if key in cache:
                return cache[key]
        result = fn(**kw)
        with lock:
            cache[key] = result
        return result

    specs = [
        {
            "type": "function",
            "function": {
                "name": "grep_count",
                "description": ("正则搜索并**直接返回命中条数**。"
                                "问题问「有几个 / 多少条」时必须用它，不要自己数。"),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "pattern": {"type": "string", "description": "Python 正则"},
                        "path": {"type": "string", "description": "仓库内相对路径或目录，默认 ."},
                    },
                    "required": ["pattern"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "find_line",
                "description": ("找一个字面量出现的 **文件:行号**。"
                                "问题问「在第几行 / 在哪」时必须用它。"),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "literal": {"type": "string"},
                        "path": {"type": "string"},
                    },
                    "required": ["literal"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "read_block",
                "description": ("按 key 取出一段正文（key 形如 `函数名@行号`，"
                                "来自包内 index 成员的索引）。"),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string"},
                        "key": {"type": "string"},
                    },
                    "required": ["path", "key"],
                },
            },
        },
    ]

    impl = {
        "grep_count": lambda **kw: _cached("grep_count", tools_fs.grep_count, root=root, **kw),
        "find_line": lambda **kw: _cached("find_line", tools_fs.find_line, root=root, **kw),
        "read_block": lambda **kw: _cached("read_block", tools_fs.read_block, root=root, **kw),
    }
    return specs, impl


def ask_one(client, model: str, pack: str, question: str, tools, impl,
            max_tokens: int = 4000) -> dict:
    """**全新调用**：messages 每次都从 pack + 这一条问题重建，不带任何历史。

    不设工具调用轮次上限：要不要继续查由模型自己决定，外层不替它判断
    「查够了没」。实测过固定 4 轮把分析题截断、固定 8 轮又把开放式问题
    逼成空转——任何硬上限都是在拿某一种题的错误换另一种题的错误。
    """
    msgs = [
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": f"{pack}\n\n---\n\n## 问题\n\n{question}"},
    ]
    used: list[str] = []
    last_usage = {"prompt": 0, "completion": 0}

    # 只防「模型反复调用工具但永远不收尾」这一种真正的死循环：
    # 连续若干次相同调用且没有任何新信息时，提示它直接作答。
    recent: list[tuple[str, str]] = []
    while True:
        r = client.chat.completions.create(
            model=model, messages=msgs, tools=tools, tool_choice="auto",
            temperature=0, max_tokens=max_tokens,
            extra_body={"chat_template_kwargs": {"enable_thinking": False}},
        )
        last_usage = {"prompt": r.usage.prompt_tokens,
                      "completion": r.usage.completion_tokens}
        m = r.choices[0].message
        if not getattr(m, "tool_calls", None):
            ans = (m.content or "").strip()
            if not ans:
                ans = (f"（空回答；finish_reason={r.choices[0].finish_reason}，"
                       f"可能被 max_tokens 截断）")
            return {"answer": ans, "tools": used, "usage": last_usage,
                    "finish": r.choices[0].finish_reason}

        msgs.append(m.model_dump(exclude_none=True))
        for tc in m.tool_calls:
            name = tc.function.name
            try:
                kw = json.loads(tc.function.arguments or "{}")
            except json.JSONDecodeError:
                kw = {}
            kw.setdefault("path", ".")
            out = impl[name](**kw) if name in impl else f"未知工具 {name}"
            used.append(name)
            msgs.append({"role": "tool", "tool_call_id": tc.id, "content": out})
            # 检测完全相同的调用反复出现（说明它卡住了）
            sig = (name, json.dumps(kw, sort_keys=True, ensure_ascii=False))
            if sig in recent:
                msgs.append({"role": "user", "content":
                    "你已经用相同参数调用过这个工具多次且得到了相同结果。"
                    "请停止重复调用，直接用已有信息给出结论；"
                    "如果确实没有答案，就明确说没有。"})
                recent.clear()
            else:
                recent.append(sig)
                if len(recent) > 6:
                    recent.pop(0)


def run(spec: str, questions: list[str] | None, budget: int, as_json: bool) -> int:
    import subprocess

    # 先装订一次。argv 与 MCP 完全一致，保证「CLI 看到的包 == 提问用的包」。
    argv = [sys.executable, "-X", "utf8", str(CODEB / "kb.py"), "route",
            "--spec", spec, "--json"]
    if budget:
        argv += ["--budget", str(budget)]
    # stdin=DEVNULL：kb route 自己不读 stdin，但它的 git_files 会起 git 子进程；
    # 一旦继承到调用方那根永不关闭的管道，git 会挂在那里等输入。
    r = subprocess.run(argv, cwd=CODEB, stdin=subprocess.DEVNULL,
                       capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    if r.returncode != 0:
        print(r.stderr or r.stdout, file=sys.stderr)
        return r.returncode
    route = json.loads(r.stdout)

    # 用**文本形态**喂模型：JSON 里每个块还带 prio/tokens 字段，
    # 那些是给人看的元信息，白占 token。
    parts = [f"# 路由包：{route.get('entry') or route.get('repo')}", ""]
    parts.append(f"仓库 `{route.get('repo')}` · {len(route.get('members', []))} 成员")
    parts.append("")
    parts.append("| tok | 保真度 | 成员 |")
    parts.append("| --: | :-- | :-- |")
    for m in route.get("members", []):
        parts.append(f"| {m['tokens']} | `{m['role']}` | `{m['path']}` |")
    parts.append("")
    for b in route.get("blocks", []):
        parts.append(f"## {b['label']}   〔{b['tokens']} tok〕")
        parts.append("")
        parts.append(b["text"])
        parts.append("")
    pack = "\n".join(parts)

    env = load_env()
    if not env.get("ZHIHU_LLM_API_KEY"):
        print("缺 ZHIHU_LLM_API_KEY（检查 infohub/collector/.env）", file=sys.stderr)
        return 2
    from openai import OpenAI
    client = OpenAI(base_url=env.get("ZHIHU_LLM_BASE_URL",
                                    "https://integrate.api.nvidia.com/v1"),
                    api_key=env["ZHIHU_LLM_API_KEY"],
                    timeout=180.0, max_retries=2)
    model = env.get("ZHIHU_LLM_MODEL", "nvidia/nemotron-3.5-super-vl-120b-a12b")

    qs = questions or route.get("questions") or []
    if not qs:
        print("规格里没有 questions，也没从命令行给；无事可做。", file=sys.stderr)
        return 2

    # 跨问共享的工具结果缓存：不同问题触发相同工具调用时直接复用
    tool_cache: dict = {}
    tools, impl = build_tools(route, {}, cache=tool_cache)

    # 并行提问：每问独立 ⟹ 可并发。用 ThreadPoolExecutor 而非 asyncio，
    # 因为 OpenAI client 是同步的，线程池足够且不引入 async 复杂度。
    from concurrent.futures import ThreadPoolExecutor, as_completed

    def _ask_one_indexed(i: int, q: str):
        t0 = time.time()
        res = ask_one(client, model, pack, q, tools, impl)
        res.update({"index": i, "question": q, "seconds": round(time.time() - t0, 1)})
        return res

    results = []
    t_all = time.time()
    with ThreadPoolExecutor(max_workers=min(len(qs), 4)) as pool:
        futures = {pool.submit(_ask_one_indexed, i, q): (i, q)
                   for i, q in enumerate(qs, 1)}
        for future in as_completed(futures):
            res = future.result()
            results.append(res)
            if not as_json:
                print(f"\n{'=' * 70}\n[{res['index']}/{len(qs)}] {res['question']}\n{'=' * 70}")
                print(res["answer"])
                print(f"\n  ({res['seconds']}s · 工具 {res['tools'] or '未用'})")

    results.sort(key=lambda r: r["index"])

    summary = {
        "pack_tokens": sum(b["tokens"] for b in route.get("blocks", [])),
        "model": model,
        "questions": len(qs),
        "seconds": round(time.time() - t_all, 1),
        "each_is_fresh_conversation": True,
        "results": results,
    }
    if as_json:
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    else:
        print(f"\n{'=' * 70}")
        print(f"包 {summary['pack_tokens']} tok · {summary['questions']} 问 · "
              f"{summary['seconds']}s · 每问都是全新会话（共享同一份包前缀）")
        for r2 in results:
            u = r2.get("usage") or {}
            print(f"  [{r2['index']}] prompt {u.get('prompt', 0)} tok · "
                  f"{r2['seconds']}s · 工具 {r2['tools'] or '未用'}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="路由提问：一次装订、逐条独立提问")
    ap.add_argument("--spec", required=True, help="路由规格 JSON")
    ap.add_argument("--q", action="append", default=[], help="覆盖问题（可重复）")
    ap.add_argument("--budget", type=int, default=0)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    return run(a.spec, a.q, a.budget, a.json)


if __name__ == "__main__":
    raise SystemExit(main())
