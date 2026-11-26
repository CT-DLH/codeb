"""执行专家：按 leader 给的方案改源码的**独立 agent**。

    leader（会话 agent）
      └── ask_subagent(agent=exec, question=方案, allowed=[...])
            └── 执行专家（独立 session）
                  ├── read_file    读现状
                  ├── edit_file    精确替换（allowed 内）
                  ├── write_file   新文件/整文件（allowed 内）
                  └── run_check    语法检查

三条边界，每条都是设计决定：

1. **写权限硬约束在 allowed。** 越界直接拒绝，不靠 prompt 自觉。
   与 Task.allowed「空 = 不限制」相反：执行专家是对话中临时派发的，
   方案文本可能含糊，权限必须由 leader 显式给。空 allowed 直接报错。

2. **只做方案里的改动。** 顺带重构、顺带修 bug、顺带加注释都要拒绝——
   diff 大了审核的人找不到重点，而且越权改动没法归因。

3. **不跑行为测试。** 语法检查（py_compile / node --check）到此为止；
   套件由 leader 另派测试专家。两者上下文不混，职责不串。

上下文成本：SYSTEM 约 1.3k + allowed 文件清单约 0.2-1k。
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
CODEB = HERE.parent
sys.path.insert(0, str(CODEB))

import kb  # noqa: E402

MAX_TURNS = 8
MAX_ANSWER_TOKENS = 3000
MAX_CONTEXT_FILES = 200

SYSTEM = (
    "你是 codeb 项目的**执行专家**。你的职责是把 leader 已经定好的方案\n"
    "落到代码上——不是重新设计方案，也不是扩大改动范围。\n"
    "\n"
    "## 写权限：只限 allowed 范围\n"
    "\n"
    "上下文里给了「本次允许改动的范围」。范围外的文件，读可以，写一律\n"
    "被拒绝。不要试图绕过（改路径、新建到别处都不行）。\n"
    "如果方案要求改一个范围外的文件，**停下来报告**「需要 leader 扩大\n"
    "allowed」，不要自己改。\n"
    "\n"
    "## 工作方式\n"
    "\n"
    "1. 先 read_file 确认要改的那段原文——**不要凭方案里的描述写 old**。\n"
    "   方案给的是意图，代码里是具体字符，两者经常差空白和标点。\n"
    "2. 用 edit_file(path, old, new) 精确替换。old 必须唯一匹配：\n"
    "   0 次说明原文不对，>1 次说明给得太短，都要补上下文重试。\n"
    "3. 新文件或整文件重写才用 write_file。能用 edit_file 就不要用它——\n"
    "   全量写会覆盖别人同时做的改动。\n"
    "4. 每改完一个文件，用 run_check(path) 做语法检查。\n"
    "   检查失败先看你自己的改动，不要急着再改别处。\n"
    "\n"
    "## 边界\n"
    "\n"
    "- **只做方案里明确要求的改动。** 顺手修复、顺手重构、顺手加注释都\n"
    "  要拒绝——那会让 diff 变大、让审核的人找不到重点。\n"
    "- 改动越界、old 不匹配、检查失败：报告具体卡在哪，不要猜着改。\n"
    "- **不跑测试。** 行为验证由 leader 另派测试专家。\n"
    "- 改不动就说改不动，不要为了「有个结果」去改别的地方。\n"
    "\n"
    "## 报告格式\n"
    "\n"
    "结论先行：改了几个文件、每处改了什么（文件 + 一句话）、语法检查结果。\n"
    "没改成的，写明卡在哪一步、需要什么。\n"
    "中文，简洁。不要复述方案原文。"
)

# 无条件禁写：这些目录要么是 git 元数据、要么是临时产物、
# 要么是知识库本体——代码执行专家不该碰。
DENIED_ALWAYS = (".git/", "_tmp/", "_kbwork/", "repo/", "node_modules/")


class ExpertError(Exception):
    """派发失败。消息直接给 leader 看。"""


# ---------------------------------------------------------------- 权限

def _norm(rel: str) -> str:
    """统一成 posix 相对路径。"""
    p = str(rel or "").replace("\\", "/").strip()
    while p.startswith("./"):
        p = p[2:]
    return p.strip("/")


def is_writable(rel: str, allowed, denied=()) -> tuple[bool, str]:
    """判断一个路径能不能写。**这是写权限的唯一判据。**

    与 test_expert.is_test_file 的区别：那里是固定白名单（测试文件），
    这里每次派发的 allowed 都不同，所以必须显式传入。
    """
    p = _norm(rel)
    if not p:
        return False, "路径为空"
    if ".." in p.split("/"):
        return False, f"路径含 ..：`{p}`"
    if not allowed:
        return False, "allowed 为空：执行专家必须显式授权可写范围"
    for pat in (*DENIED_ALWAYS, *(_norm(d) for d in denied)):
        base = pat.rstrip("/")
        if base and (p == base or p.startswith(base + "/")):
            return False, f"命中禁止清单 `{pat}`"
    for a in allowed:
        base = _norm(a).rstrip("/")
        if base and (p == base or p.startswith(base + "/")):
            return True, ""
    return False, f"越界：`{p}` 不在 allowed={list(allowed)} 内"


def _repo_root(repo: str = "codeb") -> Path:
    try:
        base = kb.repo_roots(CODEB).get(repo)
    except Exception:  # noqa: BLE001
        base = None
    return base if base and Path(base).is_dir() else CODEB


def _safe_path(rel: str, root: Path) -> Path:
    p = (root / _norm(rel)).resolve()
    try:
        p.relative_to(root)
    except ValueError as e:
        raise ExpertError(f"路径逃出仓库：{rel}") from e
    return p


def _read(p: Path) -> str:
    try:
        return p.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


# ---------------------------------------------------------------- 上下文

def build_context(allowed, repo: str = "codeb") -> tuple[str, dict]:
    """把 allowed 里的文件列成清单（路径 + 行数 + tok）。

    只列 allowed，不列整个目录树：执行专家的视野应该**等于它被授权
    改的范围**，多给只会诱导它顺手改。
    """
    root = _repo_root(repo)
    files: list[str] = []
    missing: list[str] = []
    for a in allowed or []:
        base = _norm(a)
        if not base:
            continue
        p = root / base
        if p.is_file():
            files.append(base)
        elif p.is_dir():
            for f in sorted(p.rglob("*")):
                if not f.is_file():
                    continue
                rp = f.relative_to(root)
                if any(part in kb.SRC_SKIP for part in rp.parts):
                    continue
                files.append(rp.as_posix())
        else:
            missing.append(base)

    files = list(dict.fromkeys(files))[:MAX_CONTEXT_FILES]
    lines = ["## 本次允许改动的范围", ""]
    for rel in files:
        text = _read(root / rel)
        n = text.count("\n") + (0 if text.endswith("\n") else 1)
        lines.append(f"- `{rel}`  {n} 行 · {kb.est_tokens(text)} tok")
    for m in missing:
        lines.append(f"- `{m}`  **不存在**（检查 allowed）")
    if not files and not missing:
        lines.append("（allowed 没匹配到任何文件）")
    lines.append("")
    lines.append("范围外的文件可以 read_file 看，但 write/edit 一律拒绝。")
    text = "\n".join(lines)
    return text, {"allowed": kb.est_tokens(text)}


# ---------------------------------------------------------------- 工具

def make_tools(allowed, repo: str = "codeb") -> dict:
    """工具实现。allowed 用闭包捕获——**不放进模型参数**。

    早先想过让模型自己传 allowed，那样越权只要改一个参数就行，
    等于没有权限。
    """
    root = _repo_root(repo)

    def read_file(path: str, offset: int = 1, max_lines: int = 200) -> str:
        p = _safe_path(path, root)
        if not p.is_file():
            return f"文件不存在：{path}"
        lines = _read(p).splitlines()
        start = max(1, int(offset or 1))
        end = min(len(lines), start - 1 + max(1, int(max_lines or 200)))
        body = "\n".join(f"{i:5d}  {ln}"
                         for i, ln in enumerate(lines[start - 1:end], start))
        return f"{path}  {len(lines)} 行（显示 {start}-{end}）\n{body}"

    def edit_file(path: str, old: str, new: str) -> str:
        ok, why = is_writable(path, allowed)
        if not ok:
            return f"拒绝写入：{why}"
        p = _safe_path(path, root)
        if not p.is_file():
            return f"文件不存在：{path}（新建请用 write_file）"
        text = _read(p)
        n = text.count(old)
        if n == 0:
            return ("old 不匹配（0 次）。先 read_file 看真实原文——"
                    "空白、标点、缩进都要一致。")
        if n > 1:
            return f"old 出现 {n} 次，不唯一。带上更多上下文再试。"
        p.write_text(text.replace(old, new, 1), encoding="utf-8")
        return f"已改 {path}：替换 1 处（{len(old)} → {len(new)} 字符）。"

    def write_file(path: str, content: str) -> str:
        ok, why = is_writable(path, allowed)
        if not ok:
            return f"拒绝写入：{why}"
        p = _safe_path(path, root)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
        return f"已写 {path}（{len(content)} 字符）。"

    def run_check(path: str) -> str:
        p = _safe_path(path, root)
        if not p.is_file():
            return f"文件不存在：{path}"
        suf = p.suffix.lower()
        if suf == ".py":
            cmd = [sys.executable, "-m", "py_compile", str(p)]
        elif suf in (".js", ".mjs", ".cjs"):
            node = shutil.which("node")
            if not node:
                return "没有 node，跳过 JS 语法检查"
            cmd = [node, "--check", str(p)]
        else:
            return f"{path}（{suf or '无后缀'}）没有语法检查器，跳过"
        try:
            r = subprocess.run(cmd, capture_output=True, text=True,
                               encoding="utf-8", errors="replace",
                               stdin=subprocess.DEVNULL, timeout=120)
        except (OSError, subprocess.SubprocessError) as e:
            return f"检查失败：{e}"
        if r.returncode == 0:
            return f"{path} 语法 OK"
        return f"{path} 语法 FAIL\n{(r.stderr or r.stdout or '')[:800]}"

    return {"read_file": read_file, "edit_file": edit_file,
            "write_file": write_file, "run_check": run_check}


TOOLS_SPEC = [
    {"type": "function", "function": {
        "name": "read_file",
        "description": ("读文件原文，带行号。改之前必须先读，"
                        "确认 old 的真实文本。"),
        "parameters": {"type": "object", "properties": {
            "path": {"type": "string", "description": "仓库内相对路径"},
            "offset": {"type": "integer", "description": "起始行，默认 1"},
            "max_lines": {"type": "integer", "description": "最多行数，默认 200"},
        }, "required": ["path"]},
    }},
    {"type": "function", "function": {
        "name": "edit_file",
        "description": ("精确替换一处。old 必须唯一匹配（0 次=原文不对，"
                        ">1 次=太短）。路径必须在 allowed 内。"),
        "parameters": {"type": "object", "properties": {
            "path": {"type": "string", "description": "仓库内相对路径"},
            "old": {"type": "string", "description": "要替换的原文，精确匹配"},
            "new": {"type": "string", "description": "替换成什么"},
        }, "required": ["path", "old", "new"]},
    }},
    {"type": "function", "function": {
        "name": "write_file",
        "description": ("新建文件或整文件重写。能用 edit_file 就不要用它。"
                        "路径必须在 allowed 内。"),
        "parameters": {"type": "object", "properties": {
            "path": {"type": "string", "description": "仓库内相对路径"},
            "content": {"type": "string", "description": "完整文件内容"},
        }, "required": ["path", "content"]},
    }},
    {"type": "function", "function": {
        "name": "run_check",
        "description": ("语法检查一个文件：.py→py_compile，"
                        ".js/.mjs→node --check。"),
        "parameters": {"type": "object", "properties": {
            "path": {"type": "string", "description": "仓库内相对路径"},
        }, "required": ["path"]},
    }},
]


# ---------------------------------------------------------------- 主循环

def _call(env: dict, system: str, messages: list, tools: list,
          max_tokens: int = 4096) -> tuple[dict, dict]:
    """一次非流式调用。执行专家是一次派发，不需要流式。"""
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
        raise ExpertError(f"执行专家请求失败 HTTP {e.code}：{detail}") from e
    except urllib.error.URLError as e:
        raise ExpertError(f"执行专家连不上端点：{e.reason}") from e
    except json.JSONDecodeError as e:
        raise ExpertError(f"执行专家返回的不是 JSON：{e}") from e

    usage = obj.get("usage") or {}
    choices = obj.get("choices") or []
    if not choices:
        raise ExpertError(f"执行专家没有返回 choices：{str(obj)[:300]}")
    return choices[0].get("message") or {}, usage


def ask(plan: str, allowed, env: dict, repo: str = "codeb",
        on_event=None) -> dict:
    """执行一次方案。返回结论 + 轨迹 + 代价。

    **不累积历史**：每次派发从「allowed 清单 + 这一份方案」重建。
    """
    if not (plan or "").strip():
        raise ExpertError("plan 不能为空")
    allowed = [a for a in (allowed or []) if str(a).strip()]
    if not allowed:
        raise ExpertError("allowed 不能为空：执行专家必须显式授权可写范围")

    t0 = time.time()
    ctx, ctx_tokens = build_context(allowed, repo)
    bind_ms = round((time.time() - t0) * 1000)
    tools = make_tools(allowed, repo)

    messages: list[dict] = [{"role": "user", "content":
                             f"{ctx}\n\n---\n\n## 要执行的方案\n\n{plan}"}]
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
            impl = tools.get(name)
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
                          "result_head": out[:300]})
            if on_event:
                on_event({"type": "tool_result", "name": name,
                          "result": out[:1200]})
            messages.append({"role": "tool", "tool_call_id": tc.get("id", ""),
                             "content": out})
    else:
        # 撞满轮次：收走工具再问一次，逼它开口。
        if on_event:
            on_event({"type": "tool_call", "name": "（收束）",
                      "args": {"reason": f"{MAX_TURNS} 轮用尽"}})
        try:
            msg, usage = _call(
                env, SYSTEM,
                messages + [{"role": "user", "content":
                             "轮次用尽，工具已收回。就用上面已经完成的改动"
                             "直接给结论：改了什么、检查结果如何；"
                             "没改完的明确说卡在哪、还差什么。"}],
                [], MAX_ANSWER_TOKENS)
            answer = (msg.get("content") or "").strip()
            for k, v in (usage or {}).items():
                if isinstance(v, int):
                    total_usage[k] = total_usage.get(k, 0) + v
        except ExpertError as e:
            answer = f"（{MAX_TURNS} 轮用尽，收束时出错：{e}）"

    elapsed = round(time.time() - t0, 1)
    return {
        "answer": answer or "（执行专家没有给出回答）",
        "trace": trace,
        "ctx_tokens": ctx_tokens,
        "ctx_total": sum(ctx_tokens.values()),
        "bind_ms": bind_ms,
        "elapsed_s": elapsed,
        "turns": max((t["turn"] for t in trace), default=0),
        "usage": total_usage,
        "edits": [t for t in trace if t["tool"] == "edit_file"],
        "writes": [t for t in trace if t["tool"] == "write_file"],
    }


def render_for_leader(res: dict) -> str:
    """渲染成 leader 读的文本：改了什么、检查结果、代价。"""
    lines = ["【执行专家的结果】", "", res["answer"], "", "---"]
    edits = res.get("edits") or []
    writes = res.get("writes") or []
    lines.append(
        f"改动 {len(edits) + len(writes)} 处 · 装订 {res['ctx_total']} tok"
        f"（{res['bind_ms']} ms）· {res['elapsed_s']}s · {res['turns']} 轮")
    for e in edits:
        a = e.get("args") or {}
        lines.append(f"  · edit `{a.get('path')}`  {e.get('result_head', '')[:70]}")
    for w in writes:
        a = w.get("args") or {}
        lines.append(f"  · write `{a.get('path')}`")
    if not edits and not writes:
        lines.append("  （没有文件被改动）")
    checks = [t for t in res.get("trace", []) if t["tool"] == "run_check"]
    if checks:
        lines += ["", "语法检查："]
        for c in checks:
            a = c.get("args") or {}
            lines.append(f"  · `{a.get('path')}`  {c.get('result_head', '')[:70]}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    import argparse
    ap = argparse.ArgumentParser(description="执行专家：按方案改源码")
    ap.add_argument("--plan", required=True, help="方案文本")
    ap.add_argument("--allowed", action="append", required=True,
                    help="允许写的文件或目录，可重复")
    ap.add_argument("--repo", default="codeb")
    args = ap.parse_args(argv)

    import chat_engine  # 延迟导入：chat_engine 会在 make_tools 里反向导入本模块
    env = chat_engine.load_env()
    try:
        res = ask(args.plan, args.allowed, env, args.repo)
    except ExpertError as e:
        print(f"执行专家失败：{e}", file=sys.stderr)
        return 1
    print(render_for_leader(res))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
