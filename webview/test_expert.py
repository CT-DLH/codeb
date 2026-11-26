"""测试专家：维护项目全部测试文件的**独立 agent**。

**它不是路由。** 路由是「读完一个包回答一个问题」，零工具、事实型；
测试专家要**跑东西、改东西、判断归因**，必须有工具和工具循环。

与 leader 的关系（与 route_agent 同构，但职责不同）：

    leader（会话 agent）
      └── ask_test_expert(question)          ← 把「测试这件事」整个派下去
            └── 测试专家（独立 session，自己的上下文）
                  ├── 预注入：测试清单 + 源码目录树（都来自 sqlite）
                  ├── run_suite      跑一个套件，拿真实通过数
                  ├── read_file      读源码或测试
                  └── edit_test      改测试文件（**只限测试文件**）

三条边界，每条都是设计决定：

1. **只报不修源码。** 专家的写权限白名单硬性限制在测试文件（`_tmp/test_*`、
   `mcp/smoke.ts`、`tests/`）。发现源码 bug 时它写报告，不动源码——
   「谁发现谁修」会让测试专家变成万能 agent，它的专业性就没有了。
   改源码由 leader 另派。

2. **改测试文件是它的本职，不算越权。** 测试期望过时（比如工具从 6 个砍到
   3 个）时，测试专家必须能改那个断言，否则它只能一直报「失败」，
   而失败的原因其实是测试自己过时了。**但要区分**：期望过时 → 改测试；
   代码真坏 → 只报。这个判断是它存在的核心理由。

3. **它不猜。** 清单里没有的套件就报「缺口」；跑不动就说跑不动
   （缺 Chrome / 缺 LLM 凭据 / 超时），不编一个「应该没问题」。

上下文成本：SYSTEM 约 1.1k + 测试清单约 1.7k + 源码目录树约 0.5k ≈ 3.3k。
同一会话内连问时前缀逐字节相同，走服务端 KV cache。
"""
from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
CODEB = HERE.parent
sys.path.insert(0, str(CODEB))
sys.path.insert(0, str(CODEB / "distill"))
sys.path.insert(0, str(CODEB / "distill" / "agent"))

import testtree  # noqa: E402

# 单次派发的预算与轮次上限。
# 上限存在的理由：leader 可能连派 3 次，每次装 20k 上下文 + 跑 8 轮工具。
MAX_TURNS = 8
MAX_ANSWER_TOKENS = 3000
RUN_TIMEOUT_CAP = 600

SYSTEM = (
    "你是 codeb 项目的**测试专家**。你对项目里全部的测试文件负责：\n"
    "知道每个测试证明什么、该在什么时候跑、失败了意味着什么。\n"
    "\n"
    "你的上下文里**已经预装了两份清单**：\n"
    "  1. 测试清单：每个套件的 id、类型、依赖、断言点数、证明什么、"
    "改了哪些路径该跑它。\n"
    "  2. 源码目录树：项目有哪些源码文件、各自多大。\n"
    "先看清单回答，不要靠猜。清单里没有的套件就是没有。\n"
    "\n"
    "## 你唯一的职责：给出**可归因**的测试结论\n"
    "\n"
    "跑完一个套件后，必须把结果归到下面三类之一，**不许含糊**：\n"
    "\n"
    "A. **代码坏了** —— 测试的期望是对的，代码违反了它。\n"
    "   报告：哪个断言、期望什么、实际什么、最可能改坏了哪一行/哪个函数。\n"
    "   **只报不修。** 源码不归你改。\n"
    "\n"
    "B. **测试期望过时** —— 代码是故意的，测试还在断言旧行为。\n"
    "   报告：为什么判断它过时（引用代码现状），然后用 edit_test 改掉那个断言。\n"
    "   这是你**唯一**该动文件的情形。改完重跑一次确认。\n"
    "\n"
    "C. **跑不动** —— 缺 Chrome / 缺 LLM 凭据 / 依赖别的仓库 / 超时。\n"
    "   报告：缺什么、要谁补。**不要把它说成失败，也不要说成通过。**\n"
    "\n"
    "三类里都没有「不确定所以先跑一遍看看」。要么跑出结论，要么明说缺什么。\n"
    "\n"
    "## 关于数字\n"
    "\n"
    "清单里的 `n_checks` 是**静态数出来的断言点数**，不是通过数。\n"
    "报「通过 N 条」只能来自 run_suite 的真实输出，不能来自清单。\n"
    "输出里只有 ALL PASS / FAILED 而没给具体数时，就报「全部通过」或\n"
    "「N 项失败」，不要自己算一个通过数。\n"
    "\n"
    "## 工具\n"
    "\n"
    "- run_suite(suite_id)：跑一个套件。**只用它跑，不要自己拼命令**——\n"
    "  它知道每个套件的超时、需要的解释器、要记录到哪张表。\n"
    "  它返回：退出码、耗时、判定、通过/失败数（能解析时）、输出尾部。\n"
    "- read_file(path)：读源码或测试原文。判断「期望过时还是代码坏了」\n"
    "  必须真读，不能凭清单的描述推断。\n"
    "- edit_test(suite_id, old, new)：改一个**测试文件**。\n"
    "  old 必须精确匹配（含空白标点）。只限测试文件，改源码会被拒绝。\n"
    "  改之前先 read_file 确认原文，不要凭记忆写 old。\n"
    "\n"
    "## 报告格式（leader 直接转给用户，所以必须自解释）\n"
    "\n"
    "结论先行。失败项逐条给：套件 id、断言名、归因类别（A/B/C）、依据。\n"
    "改过测试文件的，明确写「改了哪个断言、从什么改成什么、为什么」。\n"
    "最后一行给「建议下一步」（谁该修什么）。\n"
    "中文，简洁。不要复述整份测试清单。"
)


class ExpertError(Exception):
    """派发失败。消息直接给 leader 看。"""


# ---------------------------------------------------------------- 权限边界

def is_test_file(rel: str) -> bool:
    """判断一个路径是不是测试文件。**这是写权限的唯一判据。**

    走名单而不是黑名单：源码有几百个文件，黑名单漏一个就是越权；
    测试文件就那么几十个，白名单穷举得起。
    """
    p = rel.replace("\\", "/")
    name = p.rsplit("/", 1)[-1]
    if p.startswith("tests/"):
        return True
    if p == "mcp/smoke.ts":
        return True
    if p.startswith("_tmp/"):
        return (name.startswith("test_") or name.startswith("cdp_")
                or name.startswith("run_") and name.endswith(".py"))
    if "/" not in p and name.startswith("test_"):
        return True
    return False


# ---------------------------------------------------------------- 清单注入

def build_context(repo: str = "codeb") -> tuple[str, dict]:
    """装订测试专家的预注入上下文。返回 (文本, 各段 tok)。

    两段都来自 sqlite：
      - 测试清单：testtree.render_tree（test_suites + test_notes）
      - 源码目录树：chat_engine 的 _render_src_tree（kb.src_files 口径）

    与 leader 的区别：leader 只拿到一份几百 tok 的路由目录，
    测试专家拿全表。理由：它要回答「改了 X 该跑什么」，
    那需要 run_after 的完整反向索引，只给目录它答不了。
    """
    import kb

    parts: list[tuple[str, str]] = []
    tokens: dict[str, int] = {}

    try:
        tree_txt = testtree.render_tree(CODEB, repo)
        parts.append(("测试清单", tree_txt))
        tokens["测试清单"] = kb.est_tokens(tree_txt)
    except Exception as e:  # noqa: BLE001
        msg = f"（测试清单读不出来：{type(e).__name__}: {e}）"
        parts.append(("测试清单（读取失败）", msg))
        tokens["测试清单"] = kb.est_tokens(msg)

    # 源码目录树：复用 chat_engine 的渲染，口径与 leader 完全一致
    try:
        import chat_engine
        asm = chat_engine.ContextAssembler(CODEB)
        src_txt = asm._render_src_tree(repo, 3)
        if src_txt:
            parts.append((f"源码目录树：{repo}", src_txt))
            tokens["源码目录树"] = kb.est_tokens(src_txt)
    except Exception as e:  # noqa: BLE001
        msg = f"（源码目录树渲染失败：{type(e).__name__}: {e}）"
        parts.append(("源码目录树（失败）", msg))
        tokens["源码目录树"] = kb.est_tokens(msg)

    out = []
    for label, body in parts:
        out.append(f"\n---\n\n## {label}   〔{tokens.get(label.split('（')[0], 0)} tok〕\n")
        out.append(body)
    return "\n".join(out), tokens


# ---------------------------------------------------------------- 工具

def _db():
    return testtree.open_db(CODEB)


def tool_run_suite(suite_id: str, repo: str = "codeb") -> str:
    """跑一个套件，返回给模型看的文本。

    为什么必须有这个工具而不是让模型拼命令：每个套件的解释器、超时、
    记录方式都不同（python -X utf8 / node / 要 venv）。让模型拼，
    它会给 node 套 python 的参数，然后得出「跑不了」的错误结论。
    """
    conn = _db()
    row = conn.execute(
        "SELECT path, cmd, timeout_s, requires, status FROM test_suites"
        " WHERE repo=? AND suite_id=?", (repo, suite_id)).fetchone()
    if row is None:
        ids = [r[0] for r in conn.execute(
            "SELECT suite_id FROM test_suites WHERE repo=? AND status!='scratch'"
            " ORDER BY suite_id", (repo,))]
        return (f"没有叫 `{suite_id}` 的套件。清单里有：{', '.join(ids)}\n"
                f"如果这是清单的缺口，就如实报缺口，不要换一个套件顶替。")
    path, cmd, tmo, req, status = row
    tmo = min(int(tmo or 120), RUN_TIMEOUT_CAP)
    reqs = json.loads(req or "[]")

    t0 = time.time()
    try:
        r = subprocess.run(cmd, shell=True, cwd=str(CODEB),
                           capture_output=True, stdin=subprocess.DEVNULL,
                           text=True, encoding="utf-8", errors="replace",
                           timeout=tmo)
        out = ((r.stdout or "") + ("\n[stderr]\n" + (r.stderr or "")
                                   if (r.stderr or "").strip() else "")).strip()
        rc = r.returncode
    except subprocess.TimeoutExpired:
        el = time.time() - t0
        conn.execute("INSERT INTO test_runs VALUES (?,?,?,?,?,?,?,?,?)",
                     (repo, suite_id, time.strftime("%Y-%m-%dT%H:%M:%S%z"),
                      None, None, round(el, 1), None, None,
                      f"超时 {tmo}s"))
        conn.commit()
        return (f"套件 `{suite_id}` 超时（>{tmo}s）。\n"
                f"需要：{', '.join(reqs) or '—'}。\n"
                f"**归因类别 C（跑不动）**：不是失败，也不是通过。"
                f"要么它本来就慢（看 timeout_s），要么环境卡住了。")
    el = time.time() - t0

    ok = 1 if rc == 0 else 0
    passed, failed = _parse_counts(out)
    conn.execute("INSERT INTO test_runs VALUES (?,?,?,?,?,?,?,?,?)",
                 (repo, suite_id, time.strftime("%Y-%m-%dT%H:%M:%S%z"),
                  ok, rc, round(el, 1), passed, failed,
                  out[-3000:] if out else ""))
    conn.commit()

    head = (f"套件 `{suite_id}`（{path}）\n"
            f"退出码 {rc} · {el:.1f}s · 判定 "
            f"{'通过' if rc == 0 else '失败'}")
    if passed is not None and failed is not None:
        head += f" · 解析出 {passed} 通过 / {failed} 失败"
    elif "ALL PASS" in out:
        head += " · 输出含 ALL PASS"
    body = out[-4000:] if len(out) > 4000 else out
    if len(out) > 4000:
        head += f"\n（输出共 {len(out)} 字符，只给尾部 4000）"
    return head + "\n---\n" + body


def _parse_counts(out: str) -> tuple[int | None, int | None]:
    """从输出里解析「通过/失败」数。

    **解析不出就返回 None，不要猜。** 报一个推测出来的通过数，
    比报「输出里没给数字」危险得多——这是本项目反复踩的坑。
    """
    import re
    m = re.search(r"(\d+)\s*通过\s*/\s*(\d+)\s*失败", out)
    if m:
        return int(m.group(1)), int(m.group(2))
    m = re.search(r"(\d+)\s*FAILED", out)
    if m:
        return None, int(m.group(1))
    m = re.search(r"✓\s*(\d+)/(\d+)", out)
    if m:
        a, b = int(m.group(1)), int(m.group(2))
        return a, b - a
    return None, None


def tool_read_file(path: str, max_lines: int = 200, repo: str = "codeb") -> str:
    """读文件。不设写权限限制——读源码是判断归因的必要条件。"""
    import tools_fs
    cap = max(1, min(int(max_lines or 200), 400))
    return tools_fs.read_file(path, cap, root=repo)


def tool_edit_test(suite_id: str, old: str, new: str, repo: str = "codeb") -> str:
    """改一个**测试文件**。源码一律拒绝。

    这是「只报不修」的落地点：测试期望过时是测试的问题，归专家；
    源码坏了是代码的问题，归 leader。权限在工具层硬挡，
    不靠模型自觉——自觉在长上下文里会失效。
    """
    conn = _db()
    row = conn.execute("SELECT path FROM test_suites WHERE repo=? AND suite_id=?",
                       (repo, suite_id)).fetchone()
    if row is None:
        return f"没有叫 `{suite_id}` 的套件，不能改。"
    path = row[0]
    if not is_test_file(path):
        return (f"拒绝改动：{path} 不是测试文件。\n"
                f"**你只维护测试。源码问题写进报告，由 leader 另派。**")

    import tools_fs
    p = tools_fs.resolve(path, repo)
    if p is None:
        return f"路径解析失败：{path}"
    try:
        text = p.read_text(encoding="utf-8")
    except OSError as e:
        return f"读取失败：{e}"
    n = text.count(old)
    if n == 0:
        return (f"替换失败：在 {path} 里找不到这段原文（必须精确匹配，含空白标点）。\n"
                f"先 read_file 确认原文，不要凭记忆写 old。")
    if n > 1:
        return (f"替换中止：这段原文在 {path} 里出现 {n} 次，无法唯一定位。\n"
                f"带上前后几行让它唯一。")
    p.write_text(text.replace(old, new, 1), encoding="utf-8")
    # 改了测试文件，content_hash 必须刷新，否则清单会一直报「说明过期」
    src = p.read_text(encoding="utf-8")
    conn.execute("UPDATE test_suites SET content_hash=?, last_seen=?"
                 " WHERE repo=? AND suite_id=?",
                 (testtree.h16(src), time.strftime("%Y-%m-%dT%H:%M:%S%z"),
                  repo, suite_id))
    conn.commit()
    return f"✓ 已改 {path}（1 处）。**改完必须重跑一次确认它现在通过。**"


TOOLS_SPEC = [
    {"type": "function", "function": {
        "name": "run_suite",
        "description": ("跑一个测试套件，返回退出码、耗时、判定、通过/失败数、"
                        "输出尾部。**只用它跑，不要自己拼命令**——每个套件的"
                        "解释器和超时都不同。失败时先看输出再判断归因。"),
        "parameters": {"type": "object", "properties": {
            "suite_id": {"type": "string",
                         "description": "套件 id，从预注入的测试清单里选，如 mcp-smoke"},
        }, "required": ["suite_id"]},
    }},
    {"type": "function", "function": {
        "name": "read_file",
        "description": ("读源码或测试原文。判断「期望过时」还是「代码坏了」"
                        "必须真读源码，不能凭清单描述推断。"),
        "parameters": {"type": "object", "properties": {
            "path": {"type": "string", "description": "仓库内相对路径"},
            "max_lines": {"type": "integer", "description": "默认 200，上限 400"},
        }, "required": ["path"]},
    }},
    {"type": "function", "function": {
        "name": "edit_test",
        "description": ("改一个**测试文件**（源码会被拒绝）。只在「测试期望过时」"
                        "时用——代码是对的、测试还在断言旧行为。"
                        "代码真坏时只报不改。old 必须精确匹配，先 read_file 确认。"),
        "parameters": {"type": "object", "properties": {
            "suite_id": {"type": "string", "description": "要改的套件 id"},
            "old": {"type": "string",
                    "description": "要被替换的原文，必须精确匹配（含空白标点）"},
            "new": {"type": "string", "description": "替换成什么"},
        }, "required": ["suite_id", "old", "new"]},
    }},
]

TOOL_IMPL = {
    "run_suite": tool_run_suite,
    "read_file": tool_read_file,
    "edit_test": tool_edit_test,
}

# 折叠策略：与 chat_engine 同一条理由。
# run_suite 是**结论**（通过/失败 + 归因证据），折了专家就忘了自己刚跑过什么，
# 会重跑同一个套件。read_file 是原文，留 2 轮。
FOLD_ROUNDS = {"run_suite": -1, "read_file": 2, "edit_test": -1}


# ---------------------------------------------------------------- 主循环

def _call(env: dict, system: str, messages: list, tools: list,
          max_tokens: int = 4096) -> tuple[dict, dict]:
    """一次非流式调用。测试专家不需要流式推给前端——它是一次派发。"""
    import urllib.error
    import urllib.request

    base = (env.get("ZHIHU_LLM_BASE_URL")
            or "https://integrate.api.nvidia.com/v1")
    model = env.get("ZHIHU_LLM_MODEL") or "nvidia/nemotron-3.5-super-vl-120b-a12b"
    body = {
        "model": model,
        "messages": [{"role": "system", "content": system}] + messages,
        "temperature": 0,
        "max_tokens": max_tokens,
        "tool_choice": "auto" if tools else "none",
        "chat_template_kwargs": {"enable_thinking": False},
    }
    if tools:
        body["tools"] = tools
    req = urllib.request.Request(
        base.rstrip("/") + "/chat/completions",
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json",
                 "Authorization": f"Bearer {env.get('ZHIHU_LLM_API_KEY', '')}"},
        method="POST")
    try:
        with urllib.request.urlopen(req, timeout=240) as resp:
            obj = json.loads(resp.read().decode("utf-8", "replace"))
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", "replace")[:400]
        raise ExpertError(f"测试专家请求失败 HTTP {e.code}：{detail}") from e
    except urllib.error.URLError as e:
        raise ExpertError(f"测试专家连不上端点：{e.reason}") from e
    except json.JSONDecodeError as e:
        raise ExpertError(f"测试专家返回的不是 JSON：{e}") from e

    usage = obj.get("usage") or {}
    choices = obj.get("choices") or []
    if not choices:
        raise ExpertError(f"测试专家没有返回 choices：{str(obj)[:300]}")
    return choices[0].get("message") or {}, usage


def ask(question: str, env: dict, repo: str = "codeb",
        on_event=None) -> dict:
    """派发一次。返回结论文本 + 轨迹 + 代价。

    **不累积历史**：每次提问从「预注入上下文 + 这一问」重建。
    这样同一会话连派时前缀逐字节相同，KV cache 能命中；
    也不会因为上一问跑了 5 个套件而让这一问多付 20k。
    """
    if not question.strip():
        raise ExpertError("question 不能为空")

    t0 = time.time()
    ctx, ctx_tokens = build_context(repo)
    bind_ms = round((time.time() - t0) * 1000)

    messages: list[dict] = [{"role": "user", "content": f"{ctx}\n\n---\n\n## 问题\n\n{question}"}]
    trace: list[dict] = []
    total_usage: dict = {}
    answer = ""

    for turn in range(1, MAX_TURNS + 1):
        msg, usage = _call(env, SYSTEM, messages, TOOLS_SPEC,
                           MAX_ANSWER_TOKENS)
        for k, v in (usage or {}).items():
            if isinstance(v, int):
                total_usage[k] = total_usage.get(k, 0) + v
        tool_calls = msg.get("tool_calls") or []
        content = (msg.get("content") or "").strip()

        if not tool_calls:
            answer = content
            messages.append({"role": "assistant", "content": content})
            break

        messages.append(msg)
        for tc in tool_calls:
            fn = tc.get("function") or {}
            name = fn.get("name") or ""
            try:
                args = json.loads(fn.get("arguments") or "{}")
            except json.JSONDecodeError:
                args = {}
            if on_event:
                on_event({"type": "tool_call", "name": name, "args": args})
            impl = TOOL_IMPL.get(name)
            if impl is None:
                out = f"未知工具：{name}"
            else:
                try:
                    out = str(impl(**args))
                except TypeError as e:
                    out = f"参数不对：{e}"
                except Exception as e:  # noqa: BLE001
                    out = f"工具执行失败：{type(e).__name__}: {e}"
            trace.append({"turn": turn, "tool": name, "args": args,
                          "result_tokens": _tok(out),
                          "result_head": out[:300]})
            if on_event:
                on_event({"type": "tool_result", "name": name,
                          "result": out[:1200]})
            messages.append({"role": "tool", "tool_call_id": tc.get("id", ""),
                             "content": out})
    else:
        # 撞满轮次：收走工具再问一次，逼它开口。
        # 直接返回「轮次用尽」会让 leader 什么都没拿到——而它可能已经
        # 跑出了关键结论，只是还在继续查。
        if on_event:
            on_event({"type": "tool_call", "name": "（收束）",
                      "args": {"reason": f"{MAX_TURNS} 轮用尽"}})
        try:
            msg, usage = _call(
                env, SYSTEM,
                messages + [{"role": "user", "content":
                             "轮次用尽，工具已收回。就用上面已经跑出来的结果"
                             "直接给结论（按 A/B/C 归因）；缺的部分明确说缺什么。"}],
                [], MAX_ANSWER_TOKENS)
            answer = (msg.get("content") or "").strip()
            for k, v in (usage or {}).items():
                if isinstance(v, int):
                    total_usage[k] = total_usage.get(k, 0) + v
        except ExpertError as e:
            answer = f"（{MAX_TURNS} 轮用尽，收束时出错：{e}）"

    elapsed = round(time.time() - t0, 1)
    return {
        "answer": answer or "（测试专家没有给出回答）",
        "trace": trace,
        "ctx_tokens": ctx_tokens,
        "ctx_total": sum(ctx_tokens.values()),
        "bind_ms": bind_ms,
        "elapsed_s": elapsed,
        "turns": len([t for t in trace]) and max(t["turn"] for t in trace) or 0,
        "usage": total_usage,
        "edits": [t for t in trace if t["tool"] == "edit_test"],
        "ran": [t["args"].get("suite_id") for t in trace
                if t["tool"] == "run_suite"],
    }


def _tok(text: str) -> int:
    try:
        import kb
        return kb.est_tokens(text)
    except Exception:  # noqa: BLE001
        return len(text) // 3


def render_for_leader(res: dict) -> str:
    """渲染成 leader 读的文本。

    必须带「跑了什么、改了什么、花了多少」：leader 要看得出这次派发
    值不值、专家的结论有没有依据。只给答案文本等于让它无条件相信。
    """
    lines = ["【测试专家的结论】", "", res["answer"], "", "---"]
    ran = res.get("ran") or []
    lines.append(
        f"装订 {res['ctx_total']} tok（{res['bind_ms']} ms）· "
        f"{len(res.get('trace') or [])} 次工具调用 · "
        f"{res['elapsed_s']} s")
    if ran:
        lines.append(f"跑过的套件：{', '.join(f'`{s}`' for s in ran)}")
    else:
        lines.append("**一个套件都没跑**——如果结论里有「通过/失败」，它没有依据。")
    edits = res.get("edits") or []
    if edits:
        lines.append(f"改过的测试文件 {len(edits)} 处（测试期望过时，非源码）：")
        for e in edits:
            lines.append(f"  - `{e['args'].get('suite_id')}`")
    else:
        lines.append("未改动任何文件（只报不修）。")
    u = res.get("usage") or {}
    if u.get("prompt_tokens"):
        cached = ((u.get("prompt_tokens_details") or {}).get("cached_tokens")
                  or 0)
        extra = f"（命中缓存 {cached}）" if cached else ""
        lines.append(f"用量：prompt {u.get('prompt_tokens')}{extra} · "
                     f"completion {u.get('completion_tokens')}")
    return "\n".join(lines)


def spec_for_tool() -> dict:
    """给 leader 的工具 schema。**只有一个参数**：问题。

    成员（哪些套件）不在参数里——专家自己从清单里挑。
    leader 只负责说清「我改了什么、想知道什么」。
    """
    return {
        "type": "function",
        "function": {
            "name": "ask_test_expert",
            "description": (
                "把**测试相关的事**派给测试专家（独立 agent，有工具）。\n"
                "它会：按你的改动挑该跑的套件、真跑一遍、把结果归因成"
                "「代码坏了 / 测试期望过时 / 跑不动」三类，并负责维护测试文件"
                "（期望过时它会改，源码问题只报不修）。\n"
                "什么时候用：改完代码想知道有没有改坏、某个测试失败想知道"
                "该改代码还是该改测试、想知道改动该跑哪些测试。\n"
                "不需要你点名套件——它自己从清单里挑。"),
            "parameters": {
                "type": "object",
                "properties": {
                    "question": {
                        "type": "string",
                        "description": (
                            "写清：改了什么（文件路径）、想确认什么。"
                            "例：「我改了 webview/chat_engine.py 的工具面，"
                            "从 6 个砍到 3 个，该跑哪些测试？」"),
                    },
                },
                "required": ["question"],
            },
        },
    }


def main(argv: list[str] | None = None) -> int:
    """CLI：直接派发一次，便于手工验证。

    python -X utf8 webview/test_expert.py "我改了 chat_engine，该跑什么？"
    """
    import argparse
    ap = argparse.ArgumentParser("test_expert")
    ap.add_argument("question", nargs="?", default="")
    ap.add_argument("--repo", default="codeb")
    ap.add_argument("--context", action="store_true", help="只打印预注入上下文")
    args = ap.parse_args(argv)

    if args.context:
        ctx, tk = build_context(args.repo)
        print(ctx)
        print(f"\n〔合计 {sum(tk.values())} tok：{tk}〕", file=sys.stderr)
        return 0

    if not args.question:
        ap.error("需要 question（或 --context 只看上下文）")

    import chat_engine
    env = chat_engine.load_env()

    def ev(e):
        if e["type"] == "tool_call":
            print(f"  → {e['name']}({json.dumps(e['args'], ensure_ascii=False)[:120]})",
                  file=sys.stderr)
        else:
            print(f"    ← {e['result'][:200]}", file=sys.stderr)

    res = ask(args.question, env, repo=args.repo, on_event=ev)
    print(render_for_leader(res))
    return 0


if __name__ == "__main__":
    sys.exit(main())
