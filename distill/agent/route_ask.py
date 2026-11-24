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
    "回答规则：\n"
    "1. **分析题**（为什么慢、影响面、要改哪些文件、怎么改）必须基于包内代码推理"
    "并给出结论。不要因为包里没有现成的「结论」就拒答——包给的是证据，"
    "结论是你的工作。\n"
    "2. **事实题**（有几个、第几行）必须先调用 grep_count / find_line 拿答案，"
    "不要自己数。这两个工具直接返回数字或行号。\n"
    "3. **把结果转述给用户时，原样引用工具给的数字**，不要在此基础上再加减。"
    "如果工具的 pattern 和问题的措辞可能对不上（例如问题说「函数」而 pattern 匹配了"
    "`const`），要在答案里写明你实际用的 pattern 是什么。\n"
    "4. 只有包里确实完全没有的信息，才说「包里没有」，并写明你找过什么。\n"
    "5. 引用代码给 `文件:行号`。结论先行，再给依据。\n"
    "\n"
    "为什么规矩这么细：实测同一个模型在 155k 原文里做计数题 0/3 全错；"
    "给了 grep_count 后升到 3/3。而在没有工具时，它会把文件头部印出的"
    "「共 526 行」直接当成答案报出来——所以「去查」这件事不能省。"
)

# 首轮是否强制调工具：**永远不要**。这不是模型挑选的问题，是端点不支持。
#
# 实测（nemotron-3.5 两家都在这个端点上）：
#   tool_choice="auto"     → finish=stop，正常
#   tool_choice="required" → finish=length，content 空、reasoning_content 空，
#                            且把 max_tokens（2000 和 4000 都试过）全部烧光，
#                            一次 tool_call 都不产生。
# 也就是说 required 在这里不是「强制调用」，是「吐出 2000 个不可见 token 然后停」。
#
# 所以「让模型去查」只能靠提示词，不能靠 tool_choice。下面的 COUNTY /
# needs_fact_lookup 保留下来做**提示词分流**：事实题走强化措辞，分析题走普通措辞。
COUNTY = re.compile(
    r"多少|几个|几条|几处|几次|第几行|哪一行|在哪|位置|行号|数量|个数|"
    r"哪个|哪一个|什么文件|"
    r"how many|which line|which one|what file|line number|count", re.I)


def needs_fact_lookup(question: str) -> bool:
    """问题里有没有「一个工具能直接答出的事实」。

    用途仅剩提示词分流：事实题在 user 消息末尾追加一句强制指令。
    **不要用它去设 tool_choice="required"**——那个组合在端点上产出空回答。
    """
    return bool(COUNTY.search(question))


# 事实题的强化指令。实测有效：加了它以后模型会调 grep_count 并原样转述结果。
FACT_SUFFIX = (
    "\n\n---\n\n"
    "【本题是事实题】答案是一个数字或行号。\n"
    "**必须先调用工具，再用它的返回值作答。** 具体做法：\n"
    "- 问「有几个/多少条」→ 调 `grep_count`。\n"
    "- 问「第几行/在哪」→ 调 `find_line`。\n"
    "\n"
    "**关键词必须从问题里原样抄，不要改写、不要加转义、不要自己造变体。**\n"
    "问题说 `指向 ./ 的 import`，你要找的就是 `from './` 这个子串——\n"
    "把问题里的原话直接当 pattern 传进去，不要把它改写成别的正则。\n"
    "\n"
    "**工具的返回值就是答案。** 如果它说「命中 28 条」，答案就是 28。\n"
    "不要因为「看起来太多/太少」就换一个 pattern 再试，也不要对结果做二次解释。\n"
    "如果你觉得 pattern 可能不对，先把**第一次**调用用的 pattern 和得到的数字\n"
    "写进答案里，让提问的人自己判断——这比悄悄换成另一个 pattern 有用得多。\n"
    "\n"
    "反面教材（真实发生过）：同一道「App.tsx 里指向 ./ 的 import 有多少条」，\n"
    "模型连调 6 次 grep_count，每次换一个自己发明的 pattern，最后报了个 2。\n"
    "正确做法是第一次就用 `from './`，得到 28，直接回答 28。"
)


def build_tools(route: dict, roots: dict[str, Path]):
    """只暴露包内成员所在的仓库，且只给「读/查」三类工具。

    给写工具是危险的：这一层的任务是回答问题，不是改代码。
    给它 edit_file 等于允许它在回答过程中把被观察的对象改掉。
    """
    sys.path.insert(0, str(HERE))
    import tools_fs  # noqa: E402

    repo = route.get("repo") or ""
    root = repo if repo in tools_fs.ROOTS else "codeb"

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
        "grep_count": lambda **kw: tools_fs.grep_count(root=root, **kw),
        "find_line": lambda **kw: tools_fs.find_line(root=root, **kw),
        "read_block": lambda **kw: tools_fs.read_block(root=root, **kw),
    }
    return specs, impl


def ask_one(client, model: str, pack: str, question: str, tools, impl,
            max_rounds: int = 8, max_tokens: int = 2000) -> dict:
    """**全新调用**：messages 每次都从 pack + 这一条问题重建，不带任何历史。

    max_rounds 给到 8：实测分析题会用掉 3-5 轮（read_block 取索引正文），
    4 轮不够，会把「还在查证」误报成「答不出」。
    """
    msgs = [
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": f"{pack}\n\n---\n\n## 问题\n\n{question}"
                                    + (FACT_SUFFIX if needs_fact_lookup(question) else "")},
    ]
    used: list[str] = []
    # tool_choice 恒为 auto：required 在这个端点上产出 finish=length 的空回答。
    # 详见 COUNTY 上方那段实测记录。
    choice = "auto"
    last_usage = {"prompt": 0, "completion": 0}
    for _ in range(max_rounds + 1):
        r = client.chat.completions.create(
            model=model, messages=msgs, tools=tools, tool_choice=choice,
            temperature=0, max_tokens=max_tokens,
            extra_body={"chat_template_kwargs": {"enable_thinking": False}},
        )
        last_usage = {"prompt": r.usage.prompt_tokens,
                      "completion": r.usage.completion_tokens}
        m = r.choices[0].message
        if not getattr(m, "tool_calls", None):
            ans = (m.content or "").strip()
            if not ans:
                # 空答案必须标出来。实测 finish_reason=length 时 content 是空串，
                # 如果当成「答完了」会静默变成一次「无结论」。
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
    return {"answer": (f"（达到工具调用上限 {max_rounds} 轮仍未给出答案；"
                       f"共调用 {len(used)} 次：{used}）"),
            "tools": used, "usage": last_usage, "finish": "tool-loop"}


def run(spec: str, questions: list[str] | None, budget: int, as_json: bool) -> int:
    import subprocess

    # 先装订一次。argv 与 MCP 完全一致，保证「CLI 看到的包 == 提问用的包」。
    argv = [sys.executable, "-X", "utf8", str(CODEB / "kb.py"), "route",
            "--spec", spec, "--json"]
    if budget:
        argv += ["--budget", str(budget)]
    r = subprocess.run(argv, cwd=CODEB, capture_output=True, text=True,
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

    tools, impl = build_tools(route, {})
    results = []
    t_all = time.time()
    for i, q in enumerate(qs, 1):
        t0 = time.time()
        res = ask_one(client, model, pack, q, tools, impl)
        res.update({"index": i, "question": q, "seconds": round(time.time() - t0, 1)})
        results.append(res)
        if not as_json:
            print(f"\n{'=' * 70}\n[{i}/{len(qs)}] {q}\n{'=' * 70}")
            print(res["answer"])
            print(f"\n  ({res['seconds']}s · 工具 {res['tools'] or '未用'})")

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
