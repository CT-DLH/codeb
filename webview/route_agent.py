"""路由子 agent：把一批文件装订成包，让独立 LLM 读完作答。

**这是会话 agent 的「子 agent」**，形态参考 DSH：父 agent 不自己翻文件，
把「读一批文件并回答」这件事整个派下去，拿回一个答案。

与 `chat_engine.chat()` 的关键区别（两处，都是故意的）：

  1. 工具面：会话 agent 有 6 个读写工具；这里**一个都不给**。
     包已经装订好了，源码就在眼前，再给 grep 只会让它去扫包外的东西
     ——那不是这一层的职责。
  2. 历史：每次提问都是全新的 messages，从「包 + 这一问」重建。
     不带父会话历史，也不跨问题累积。这样同一个包上连问 N 题时，
     前缀（包 + SYSTEM）逐字节相同，服务端的 KV cache 能命中。
     实测 3 问连发，prompt_tokens 稳定在 19,760 左右不掉，
     但费用按 cached 折扣计——省的是钱不是 token 数。

为什么不用 `route_ask.py` 而是重写：那个文件的 `ask_one` 绑死了
「3 个工具 + 每问独立进程」，而这里要的是「0 工具 + 同进程 + 共享包」。
逻辑量不大（装订 → 拼包 → 一问），复用 `kb route` 与 `SYSTEM` 即可，
没必要为了复用去改一个正在被 CLI 和 MCP 使用的文件。
"""

import json
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
CODEB = HERE.parent

# 与 route_ask.py 保持同一份提示词。子 agent 的职责是「读懂包里的代码」，
# 不是「搜索」。原文强调「工具用不用自己判断」，这里删掉工具相关的句子，
# 因为这一层没有工具。
SUBSYSTEM = (
    "你在读一份 leader 装订好的上下文包，里面有源码原文（标 `full`）、"
    "函数级索引（标 `index`，只有签名）和签名（标 `outline`）。\n"
    "\n"
    "**包里没有的东西就是没有**——你没有搜索工具，也不要去猜包外的文件。"
    "如果答案确实不在包里，直接说「这个包里没有」，并指出还需要哪个文件。\n"
    "\n"
    "**行号规则（重要）**：\n"
    "包里的代码块可能被截断或重排，**块内看到的行号不是文件绝对行号**。\n"
    "实测过：本路由把 `HANDLERS` 报成第 1900 行，实际在 3302 行；\n"
    "把 `ROUTE_ROLES` 报成 1724 行，实际在 2105 行——错了一千多行，\n"
    "而且格式看起来很可信。所以：\n"
    "  - 只有当包内**明确给出了**绝对行号（形如 `文件.py:1234:` 这种带文件名的\n"
    "    完整标注）时，才可以引用行号。\n"
    "  - 否则**只引用函数名/常量名，不要写行号**。说「在 `cmd_route` 里」就够了，\n"
    "    不要编造一个数字。\n"
    "  - 需要精确行号时，明确说「需要 leader 用 read_constant 或 grep 确认行号」。\n"
    "\n"
    "回答规则：\n"
    "1. 结论先行，给依据。引用代码优先给**函数名/常量名**；\n"
    "   行号只在包内明确标注时照搬，否则不写。\n"
    "2. 标 `index` / `outline` 的成员只有签名，能看到「有哪些函数」但看不到函数体。"
    "基于签名能答的就答；必须看函数体才能答的，说明「需要 full 保真度」。\n"
    "3. 中文回答，简洁。\n"
    "4. 不要在回答里复述包的目录结构，直接给答案。"
)

# 单次 ask_route 的默认与上限。上限存在的理由：leader 可能一口气点 5 次，
# 每次 20k，不设限就是 100k 上下文悄悄烧掉。
DEFAULT_BUDGET = 40000
MAX_BUDGET = 160000
# 子 agent 的输出上限。它是「回答一个问题」，不是「写文档」。
MAX_ANSWER_TOKENS = 2000

ROUTES_FILE = HERE / "routes.json"


class RouteError(Exception):
    """装订或提问失败。消息直接给 leader 看，所以要写人话。"""


# ---------------------------------------------------------------- 预设路由目录
_route_cache: dict | None = None


def load_routes() -> dict:
    """读预设路由配置。

    **leader 不点成员**：它只看这张目录（name + desc，几百 tok），
    挑一个路由问。成员、保真度、预算全在配置里定好，
    既不会点错文件，也不会点出 214k 超预算。
    """
    global _route_cache
    if _route_cache is not None:
        return _route_cache
    if not ROUTES_FILE.is_file():
        raise RouteError(f"路由配置不存在：{ROUTES_FILE}")
    try:
        data = json.loads(ROUTES_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        raise RouteError(f"路由配置读不了：{e}") from e
    routes = data.get("routes") or []
    if not routes:
        raise RouteError("路由配置里 routes 是空的")
    by_name: dict[str, dict] = {}
    for r in routes:
        name = (r.get("name") or "").strip()
        if not name:
            continue
        if not r.get("paths") and not r.get("members"):
            raise RouteError(f"路由 {name} 既没有 paths 也没有 members")
        by_name[name] = r
    data["by_name"] = by_name
    _route_cache = data
    return data


def _expand_paths(r: dict) -> list[dict]:
    """把 paths glob 展开成 members（全部 full 整装）。

    **这就是「路由管理哪些路径下的文件」**：新增文件自动纳入，
    不需要手改 members 清单。exclude 可剔除测试脚本等噪音。
    """
    if r.get("members"):           # 兼容显式的老格式
        return [{"path": str(m["path"]),
                 "role": str(m.get("role") or "full")} for m in r["members"]]
    excluded = set(r.get("exclude") or [])
    seen: set[str] = set()
    out: list[dict] = []
    for pat in r.get("paths") or []:
        for p in sorted(Path(CODEB).glob(pat)):
            if not p.is_file():
                continue
            # 后缀不设白名单：装什么由 paths 的 glob 决定。早先这里硬编码
            # .py/.ts/.js，结果 webview 路由 9 个成员里 4 个前端文件
            # （chat.html/chat.css/style.css/index.html）被静默丢掉，子 agent
            # 据此回答「没有侧边栏、没有 CSS 文件」——它没说错，是装订没给它。
            # 补白名单只是打补丁，下次 .svg/.md 照样漏。噪音用 exclude 显式
            # 剔除（见 routes.json），不要用后缀去猜「什么算源码」。
            rel = p.relative_to(CODEB).as_posix()
            if rel in excluded or rel in seen:
                continue
            seen.add(rel)
            out.append({"path": rel, "role": "full"})
    if not out:
        raise RouteError(f"路由 {r.get('name')} 的 paths 没匹配到任何源码文件")
    return out


def route_catalog(repo: str = "codeb") -> str:
    """给 leader 看的路由目录：只有名字 + 描述 + 大致体量。

    这是**唯一**预注入会话上下文的路由信息，必须短。
    实测 7 个路由约 400 tok，而目录树本身要 443 tok。
    """
    data = load_routes()
    lines = ["# 可用路由（向对应子 agent 提问）", "",
             "每个路由装入其路径下的**全部源码**（实测均低于 100k，无需分级）。",
             "",
             "| 路由名 | 涵盖什么 | 预估 tok |",
             "| :-- | :-- | --: |"]
    for r in data["routes"]:
        lines.append(f"| `{r['name']}` | {r.get('desc', '')} | "
                     f"{r.get('est_tokens', '?')} |")
    lines.append("")
    lines.append("用法：调用 ask_route(route=路由名, question=问题)。"
                 "成员与预算已预设，不需要你点名。")
    lines.append("问题答不到点上时，换个相邻路由再问一次。")
    return "\n".join(lines)


def get_route(name: str) -> dict:
    """按名字取预设路由，找不到时给出可用的名字（可操作的错误）。"""
    data = load_routes()
    r = data["by_name"].get((name or "").strip())
    if r is None:
        names = ", ".join(f"`{n}`" for n in data["by_name"])
        raise RouteError(f"没有叫 `{name}` 的路由。可用：{names}")
    return r


def _spec_for(repo: str, entry: str, members: list[dict], budget: int,
              question: str) -> dict:
    return {
        "repo": repo,
        "entry": entry,
        "budget": budget,
        "members": members,
        "questions": [question],
    }


def bind_pack(repo: str, entry: str, members: list[dict], budget: int,
              question: str, timeout: int = 120) -> tuple[str, dict, float]:
    """装订上下文包。返回 (包文本, route 元数据, 耗时秒)。

    走 `kb route --spec --json` 子进程，而不是进程内调 `kb.main`：
    装订会读大量文件、跑 ast 解析，进程内调用会污染父进程的 stdout 缓冲
    和模块级缓存；子进程天然隔离，失败也只死一个子进程。
    代价是每次多 ~0.6-1.1 秒，这个数字要如实报给 leader。
    """
    spec = _spec_for(repo, entry, members, budget, question)
    spec_path = Path(CODEB) / "_tmp" / f"_ask_route_{int(time.time() * 1000)}.json"
    spec_path.parent.mkdir(exist_ok=True)
    spec_path.write_text(json.dumps(spec, ensure_ascii=False), encoding="utf-8")
    t0 = time.time()
    try:
        r = subprocess.run(
            [sys.executable, "-X", "utf8", str(Path(CODEB) / "kb.py"),
             "route", "--spec", str(spec_path), "--json"],
            cwd=str(CODEB),
            # stdin 必须切断：kb 内部会起 git 子进程，一旦继承到调用方
            # 那根永不关闭的管道，git 会挂在那里等输入（踩过，表现为整体卡死）
            stdin=subprocess.DEVNULL,
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            timeout=timeout,
        )
    except subprocess.TimeoutExpired as e:
        raise RouteError(f"装订超时（{timeout}s）：{len(members)} 个成员可能太大") from e
    finally:
        try:
            spec_path.unlink()
        except OSError:
            pass
    cost = time.time() - t0

    if r.returncode != 0:
        msg = (r.stderr or r.stdout or "").strip()
        # 把 kb 的报错原样带上去：它通常已经说清了哪个成员路径不对
        raise RouteError(f"装订失败：{msg[:600]}")
    try:
        route = json.loads(r.stdout)
    except json.JSONDecodeError as e:
        raise RouteError(f"装订输出不是 JSON：{(r.stdout or '')[:300]}") from e

    # 与 route_ask.py 同样的取舍：喂文本不喂 JSON。
    # 每个块在建 spec 时都带 prio/tokens 字段，那些是给人看的元信息，
    # JSON 形态实测比文本形态贵 2-3 倍。
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
    return "\n".join(parts), route, cost


def _post_stream(env: dict, system: str, user: str, model: str,
                 max_tokens: int, stop_flag=None) -> tuple[str, dict]:
    """一次非工具调用的流式请求。返回 (正文, usage)。

    自己拼 SSE 而不是用 openai SDK：`chat_engine.call_llm` 已经有一套
    流式 + 停止标志的实现，这里沿用同样的做法，避免为了子 agent 引入
    openai 这个依赖（chat_engine 全文件零外部依赖，这个性质要保住）。

    停止标志每读一行检查一次：子 agent 一次要跑 10-30 秒，
    不给中断的话用户点停止还得干等。
    """
    import urllib.error
    import urllib.request

    base = env.get("ZHIHU_LLM_BASE_URL") or "https://integrate.api.nvidia.com/v1"
    body = {
        "model": model,
        "messages": [{"role": "system", "content": system},
                     {"role": "user", "content": user}],
        "temperature": 0,
        "max_tokens": max_tokens,
        "stream": True,
        "stream_options": {"include_usage": True},
        # 关掉 thinking：路由问答不需要思维链，实测开着会让 120b
        # 把答案写在 reasoning_content 里，content 反而空
        "chat_template_kwargs": {"enable_thinking": False},
    }
    req = urllib.request.Request(
        base.rstrip("/") + "/chat/completions",
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json",
                 "Authorization": f"Bearer {env.get('ZHIHU_LLM_API_KEY', '')}"},
        method="POST",
    )
    chunks: list[str] = []
    usage: dict = {}
    try:
        with urllib.request.urlopen(req, timeout=180) as resp:
            for raw in resp:
                if stop_flag is not None and stop_flag.is_set():
                    break
                line = raw.decode("utf-8", errors="replace").strip()
                if not line.startswith("data:"):
                    continue
                payload = line[5:].strip()
                if payload == "[DONE]":
                    break
                try:
                    obj = json.loads(payload)
                except json.JSONDecodeError:
                    continue
                if obj.get("usage"):
                    usage = obj["usage"]
                for ch in obj.get("choices") or []:
                    piece = (ch.get("delta") or {}).get("content")
                    if piece:
                        chunks.append(piece)
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", errors="replace")[:400]
        raise RouteError(f"子 agent 请求失败 HTTP {e.code}：{detail}") from e
    except urllib.error.URLError as e:
        raise RouteError(f"子 agent 连不上端点：{e.reason}") from e
    return "".join(chunks).strip(), usage


def ask(repo: str, entry: str, members: list[dict], question: str,
        env: dict, budget: int = DEFAULT_BUDGET, stop_flag=None,
        route_name: str = "") -> dict:
    """装订 + 提问。返回给 leader 的完整结果（含出处与代价）。

    返回 dict 而不是字符串，因为调用方要把「花了多少、包多大、
    是否被停止」单独记账——只把答案文本交给 leader 会丢掉这些。
    """
    budget = max(4000, min(int(budget or DEFAULT_BUDGET), MAX_BUDGET))
    if not members:
        raise RouteError("members 不能为空：至少要点名一个文件")
    if not question.strip():
        raise RouteError("question 不能为空")
    # 注意：这里**不再限成员数**。早先加过 MAX_MEMBERS=8 的上限，
    # 那是为「leader 临时点名」设计的；现在路由是预设的，成员由 paths
    # 自动展开（agent 路由有 12 个文件），上限反而会把它拦下来。
    # 真正该限的是预算，而预算在配置里定好、装订时由 kb route 强制。
    # 兜底：成员可能是纯字符串，统一成 {path, role}
    norm_members = []
    for m in members:
        if isinstance(m, str):
            norm_members.append({"path": m, "role": "full"})
        elif isinstance(m, dict) and m.get("path"):
            role = str(m.get("role") or "full").lower()
            if role not in ("full", "index", "outline"):
                role = "full"
            norm_members.append({"path": str(m["path"]), "role": role})
        else:
            raise RouteError(f"成员格式不对：{m!r}（要 {{path, role}}）")
    if entry is None:
        entry = norm_members[0]["path"]

    pack, route, bind_cost = bind_pack(repo, entry, norm_members, budget,
                                       question)

    model = env.get("ZHIHU_LLM_MODEL") or "nvidia/nemotron-3.5-super-vl-120b-a12b"
    t0 = time.time()
    answer, usage = _post_stream(
        env, SUBSYSTEM, f"{pack}\n\n---\n\n## 问题\n\n{question}",
        model, MAX_ANSWER_TOKENS, stop_flag=stop_flag)
    ask_cost = time.time() - t0
    stopped = stop_flag is not None and stop_flag.is_set()

    pack_tokens = sum(b["tokens"] for b in route.get("blocks", []))
    return {
        "answer": answer or ("（子 agent 没有给出回答" +
                            ("，已被停止）" if stopped else "）")),
        "members": [{"path": m["path"], "role": m["role"],
                     "tokens": m["tokens"]} for m in route.get("members", [])],
        "blocks": len(route.get("blocks", [])),
        "pack_tokens": pack_tokens,
        "bind_ms": round(bind_cost * 1000),
        "ask_ms": round(ask_cost * 1000),
        "usage": usage,
        "model": model,
        "stopped": stopped,
        "route_name": route_name,
    }


def ask_preset(route_name: str, question: str, env: dict, repo: str = "codeb",
               stop_flag=None) -> dict:
    """预设路由入口：leader 只给路由名 + 问题。

    成员、保真度、预算全部来自配置，不再让 leader 临时点名。
    """
    cfg = get_route(route_name)
    members = _expand_paths(cfg)
    budget = int(cfg.get("budget") or data_budget())
    entry = cfg.get("entry") or members[0]["path"]
    return ask(repo, entry, members, question, env, budget=budget,
               stop_flag=stop_flag, route_name=route_name)


def data_budget() -> int:
    """从配置读全局预算。"""
    try:
        return int(load_routes().get("budget") or DEFAULT_BUDGET)
    except RouteError:
        return DEFAULT_BUDGET


def render_for_leader(res: dict) -> str:
    """把结果渲染成 leader 读的文本。

    必须带出处与代价：leader 要能判断这个答案可信不可信、
    值不值得再问一次。只给答案文本等于让它无条件相信一个黑盒。
    """
    title = res.get("route_name") or "路由"
    lines = [f"【{title} 的回答】", "", res["answer"], ""]
    lines.append("---")
    usage = res.get("usage") or {}
    lines.append(
        f"装订 {len(res['members'])} 成员 → {res['blocks']} 块 · "
        f"{res['pack_tokens']} tok 入包 · "
        f"装订 {res['bind_ms']} ms + 作答 {res['ask_ms']} ms")
    if usage.get("prompt_tokens"):
        cached = ((usage.get("prompt_tokens_details") or {}).get("cached_tokens")
                  or 0)
        extra = f"（其中 {cached} tok 命中缓存）" if cached else ""
        lines.append(f"子 agent 用量：prompt {usage.get('prompt_tokens')} tok"
                     f"{extra} · completion {usage.get('completion_tokens')} tok")
    lines.append("")
    lines.append("| 保真度 | 成员 | tok |")
    lines.append("| :-- | :-- | --: |")
    for m in res["members"]:
        lines.append(f"| `{m['role']}` | `{m['path']}` | {m['tokens']} |")
    if res.get("stopped"):
        lines.append("")
        lines.append("（被用户停止，答案可能不完整）")
    return "\n".join(lines)


def spec_for_tool() -> dict:
    """给 leader 看的工具 schema。**只有两个参数**：路由名 + 问题。

    成员、保真度、预算全在 routes.json 里预设。
    leader 看路由目录选一个即可，不再临时点名——那是它做不好的事
    （实测点出 27 个成员、214k tok 超预算）。
    """
    names = ", ".join(f"`{n}`" for n in load_routes()["by_name"])
    return {
        "type": "function",
        "function": {
            "name": "ask_route",
            "description": (
                "向一个预设的路由子 agent 提问。**主力工具**："
                "需要理解代码、跨文件分析、问某功能怎么实现，都用这个。\n"
                f"可用路由：{names}。\n"
                "从上下文里预注入的「可用路由」目录选一个，把问题写具体。"
                "路由的成员和预算已预设，不需要你点名。"
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "route": {
                        "type": "string",
                        "description": "路由名，从可用路由目录里选",
                    },
                    "question": {
                        "type": "string",
                        "description": "要问的问题，写具体，指明你要什么",
                    },
                },
                "required": ["route", "question"],
            },
        },
    }
