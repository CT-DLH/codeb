"""codeb 自己的 agent loop。零依赖：只用标准库 + kb.py 本身。

对比 pi-agent-core 的意义在于：pi 需要 Node + 106 个传递依赖 + 4.5 MB pi-ai
（它把所有 provider 都打进来了）。而我们真正要的能力只有三样：

  1. 多轮 tool loop
  2. 工具 = 进程内 Python 函数（直接调 kb.cmd_*，54ms 而不是 spawn 261ms）
  3. 折叠策略是我们自己量的（见 repo/codeb/fold-and-recall）

这份文件就是那三样，约 300 行，零安装。
"""
import sys, json, io, os, types, contextlib, urllib.request, urllib.error
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import kb

CODEB = Path(__file__).resolve().parents[2]


# ----------------------------------------------------------------- 凭据
def load_env() -> dict:
    """与 distill.py 同一真源：infohub/collector/.env 里的 ZHIHU_LLM_*。"""
    out = {}
    p = Path("D:/work/project/infohub/collector/.env")
    if not p.exists():
        return out
    for line in p.read_text(encoding="utf-8-sig", errors="replace").splitlines():
        s = line.strip()
        if not s or s.startswith("#") or "=" not in s:
            continue
        k, v = s.split("=", 1)
        k = k.strip()
        if k.startswith("ZHIHU_LLM_"):
            out.setdefault(k, v.strip().strip('"').strip("'"))
    return out


# ----------------------------------------------------------------- 工具
@dataclass
class Tool:
    """工具 = 名字 + schema + 一个 Python 函数。

    注意 schema 里**没有** retain 字段。折叠轮数由下面的 fold_rounds 声明，
    理由见 probe_fold_design2：10 个决定里 8 个是静态的。
    """
    name: str
    description: str
    params: dict                  # JSON Schema properties
    run: callable                 # (args) -> str
    fold_rounds: int = 2          # <0 表示永不折叠


@dataclass
class Block:
    """一条工具结果在上下文里的样子。折叠后就地换成墓碑。"""
    tool: str
    text: str
    born: int
    key: str = ""                 # 取回用的 id

    @property
    def tokens(self) -> int:
        return kb.est_tokens(self.text)


class Ledger:
    """上下文账本。折叠在这里发生，不在工具里。

    这就是与 pi 的最大架构差异：pi 把折叠做成 transformContext 钩子（只管
    消息数组），我们保留每条工具结果的结构化身份（tool/key/born），
    才能既折叠又取回。
    """
    TOMB = "（已折叠：{tool} {key}，kb.recall(\"{key}\") 取回）"

    def __init__(self):
        self.blocks: list[Block] = []
        self.n = 0
        self.folded: dict[str, Block] = {}

    def add(self, tool: str, text: str) -> Block:
        self.n += 1
        b = Block(tool=tool, text=text, born=self.n, key=f"{tool}#{self.n}")
        self.blocks.append(b)
        return b

    def sweep(self, policy: dict[str, int], default: int = 2) -> list[str]:
        """轮末折叠。返回这一轮被折叠的 key。

        语义（踩过坑才定下来的）：`fold_rounds=0` 表示**本轮之后立刻折**，
        不是「本轮之内折」。第一版写成 `self.n - b.born >= k`，k=0 时
        age 也是 0，于是刚加进来的块在同一轮就被折了——模型从头到尾
        没读到过内容，于是反复重调同一个工具，跑了 6 轮全是 kb_tree。
        所以判据必须是 `age > k`，给 born 那一轮留一次被读的机会。
        """
        hit = []
        for b in self.blocks:
            k = policy.get(b.tool, default)
            if k < 0 or b.key in self.folded:
                continue
            if self.n - b.born > k and b.tokens > 40:
                self.folded[b.key] = Block(b.tool, b.text, b.born, b.key)
                b.text = self.TOMB.format(tool=b.tool, key=b.key)
                hit.append(b.key)
        return hit

    def recall(self, key: str) -> str | None:
        b = self.folded.get(key)
        return b.text if b else None

    def messages(self) -> list[dict]:
        return [{"role": "user", "content": f"[{b.tool} {b.key}]\n{b.text}"}
                for b in self.blocks] or [{"role": "user", "content": "开始。"}]

    def total_tokens(self) -> int:
        return sum(b.tokens for b in self.blocks)


# ----------------------------------------------------------------- 工具实现
def _kb(args: list[str]) -> str:
    """进程内调用 kb.py，不起子进程。54ms vs 261ms。

    **不带 --json**：这条也是量出来的。kb tree 的文本是 3,433 tok，
    JSON 是 9,185 tok（2.7 倍）。MCP 层必须用 JSON（它有结构化消费者），
    但给模型读的东西一律用文本——JSON 的大括号、引号、重复键名全是白付的钱。

    **必须同时捕获 stderr**：kb.py 把错误写到 stderr（`_err`），只捕获 stdout
    的话模型拿到的是「退出码 2」这种没信息量的话，于是它会**继续瞎猜**——
    实测同一个错误仓库名被重试 3 次，因为第一次的错误里没有「可用仓库」那一行。
    错误信息本身就是工具输出的一部分，必须原样交给模型。
    """
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        rc = kb.main(args)
    body = out.getvalue().strip()
    if rc != 0:
        why = err.getvalue().strip() or body or f"kb 退出码 {rc}"
        raise RuntimeError(why)
    return body


def _s(v):
    """模型常把可选参数写成字符串 "None" / "null"，得吃掉。"""
    if v is None:
        return None
    s = str(v).strip()
    return None if s.lower() in ("", "none", "null", "undefined") else s


TOOLS = [
    Tool("kb_tree", "按目录列出知识**页面**（不是代码文件）。repo 只能是一级仓库名"
                    "（codeb / infohub / atomkgraph / _shared），省略则看全库。"
                    "问「某目录下有哪些代码文件 / 改之前注意什么」请用 kb_dispatch，"
                    "它便宜 10 倍且给出的是文件不是页面。",
         {"repo": {"type": "string", "description": "一级仓库名，可省略"}},
         lambda a: _kb(["tree"] + (["--repo", _s(a["repo"])] if _s(a.get("repo")) else [])),
         fold_rounds=0),
    Tool("kb_pack", "为一个代码范围装订上下文册子：源码 + 相关节 + 计划。"
                    "问「改 X 有哪些坑 / 要注意什么」时加 no_source=true，"
                    "省 75%（源码占大头，答案在知识节里）。",
         {"scope": {"type": "string"},
          "budget": {"type": "integer", "description": "token 预算，默认 13000"},
          "no_source": {"type": "boolean",
                        "description": "只要知识层不要源码。单文件可省约 75%"}},
         lambda a: _kb(["pack", _s(a["scope"])]
                       + (["--budget", str(int(a["budget"]))] if a.get("budget") else [])
                       + (["--no-source"] if a.get("no_source") in (True, "true", "True") else [])),
         fold_rounds=-1),
    Tool("kb_read", "读一页，或只读某一节。",
         {"page": {"type": "string"},
          "section": {"type": "string", "description": "小节标题，可省略"}},
         lambda a: _kb(["read", _s(a["page"])] +
                       (["--section", _s(a["section"])] if _s(a.get("section")) else [])),
         fold_rounds=2),
    Tool("kb_where", "反查哪些页面覆盖了这个源码路径。",
         {"path": {"type": "string"}},
         lambda a: _kb(["where", _s(a["path"])]),
         fold_rounds=0),
    # 「改这个目录之前要注意什么」的正确工具。
    # 实测：dispatch collector/kit/ 只要 115 tok 就能给出文件清单 + 认领页 +
    # 接口面 + 串行点；同样的问题用 kb_pack 要 8,432 tok（它把源码也装订了）。
    # 模型自己无法知道这个差别，所以工具分工必须靠 description 讲清楚。
    Tool("kb_dispatch", "改动前的检查：列出写范围内的文件、谁在描述它们、"
                        "有哪些派生文件必须重生成。比 kb_pack 便宜得多（115 tok），"
                        "问「这个目录有什么/要注意什么」先用它。",
         {"scopes": {"type": "array", "items": {"type": "string"},
                     "description": "写范围（仓库内相对路径，目录以 / 结尾）"}},
         lambda a: _kb(["dispatch"] + [str(s) for s in a["scopes"]]),
         fold_rounds=2),
]


# ----------------------------------------------------------------- LLM
def chat(messages: list[dict], tools: list[Tool], env: dict, *,
         system: str, max_tokens: int = 2048) -> dict:
    base = (env.get("ZHIHU_LLM_BASE_URL") or "https://integrate.api.nvidia.com/v1").rstrip("/")
    model = env.get("ZHIHU_LLM_MODEL") or "nvidia/nemotron-3.5-lightning-30b-a3b"
    key = env.get("ZHIHU_LLM_API_KEY")
    if not key:
        raise RuntimeError("没有 ZHIHU_LLM_API_KEY")

    payload = {
        "model": model,
        "messages": [{"role": "system", "content": system}] + messages,
        "temperature": 0,
        "max_tokens": max_tokens,
    }
    if tools:
        payload["tools"] = [{
            "type": "function",
            "function": {"name": t.name, "description": t.description,
                         "parameters": {"type": "object", "properties": t.params,
                                        "required": [k for k in t.params
                                                     if k in ("scope", "page", "path", "scopes")]}},
        } for t in tools]
    if "nvidia.com" in base:
        # 推理型模型必须关 thinking，否则 content 为空
        payload["chat_template_kwargs"] = {"enable_thinking": False}

    req = urllib.request.Request(
        f"{base}/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json",
                 "Authorization": f"Bearer {key}"})
    with urllib.request.urlopen(req, timeout=180) as r:
        return json.loads(r.read().decode("utf-8", "replace"))


# ----------------------------------------------------------------- loop
def run(task: str, *, max_turns: int = 6, verbose: bool = True) -> dict:
    env = load_env()
    ledger = Ledger()
    policy = {t.name: t.fold_rounds for t in TOOLS}
    by_name = {t.name: t for t in TOOLS}
    system = ("你是代码知识库助手。需要知识库内容时调用工具，不要猜。"
              "回答简短，用中文。")

    ledger.add("task", task)
    stats = {"turns": 0, "calls": 0, "cumulative_ctx": 0,
             "folded": [], "errors": [], "seen": [], "dups": 0,
             "seen_sigs": set()}

    for turn in range(max_turns):
        stats["turns"] = turn + 1
        msgs = ledger.messages()
        stats["cumulative_ctx"] += sum(kb.est_tokens(m["content"]) for m in msgs)

        data = chat(msgs, TOOLS, env, system=system)
        msg = (data.get("choices") or [{}])[0].get("message") or {}
        calls = msg.get("tool_calls") or []
        if not calls:
            ledger.add("answer", (msg.get("content") or "").strip())
            break

        for c in calls:
            fn = (c.get("function") or {})
            name = fn.get("name")
            try:
                args = json.loads(fn.get("arguments") or "{}")
            except Exception:
                args = {}
            stats["calls"] += 1
            tool = by_name.get(name)
            if not tool:
                ledger.add("error", f"未知工具 {name}")
                stats["errors"].append(f"未知工具 {name}")
                continue

            # 重复调用检测：同样的参数再调一次，结果必然一样。
            # 实测「约束类」任务把 kb_dispatch 同一个参数调了 3 次——它不是想
            # 重试，是**没意识到上次已经回答过**（答案里没有它问的那一项）。
            # 再执行一遍只会让上下文膨胀，且不会带来新信息，所以直接回一条
            # 提示，把模型推向「换个问法」。
            sig = f"{name}|{json.dumps(args, ensure_ascii=False, sort_keys=True)}"
            if sig in stats["seen_sigs"]:
                msg_txt = (f"（这个调用已经执行过，结果在上下文里。"
                           f"如果你在找的内容不在上面，说明 {name} 回答不了这个问题——"
                           f"换工具或换参数，不要重复调用。）")
                ledger.add("notice", msg_txt)
                stats["dups"] += 1
                if verbose:
                    print(f"  [{turn+1}] {name} 重复调用 → 已拦下")
                continue
            stats["seen_sigs"].add(sig)

            try:
                out = tool.run(args)
            except Exception as e:
                out = f"工具失败：{e}"
                stats["errors"].append(f"{name}: {e}")
            led = ledger.add(name, out)
            stats["seen"].append(f"{name}({json.dumps(args, ensure_ascii=False)[:40]})")
            if verbose:
                print(f"  [{turn+1}] {name}({json.dumps(args, ensure_ascii=False)[:70]})"
                      f" -> {led.tokens} tok")

        hit = ledger.sweep(policy)
        stats["folded"].append(hit)
        if verbose and hit:
            print(f"      折叠 {len(hit)} 块：{', '.join(hit)}")

    stats["ctx_tokens"] = ledger.total_tokens()
    stats["blocks"] = len(ledger.blocks)
    stats["folded_total"] = len(ledger.folded)
    return stats


if __name__ == "__main__":
    tk = sys.argv[1] if len(sys.argv) > 1 else \
        "告诉我们这个知识库有几个仓库、infohub 下一个采集器要用哪份站点规范。"
    print(f"任务：{tk}\n")
    s = run(tk)
    print(f"\n轮数 {s['turns']} · 工具调用 {s['calls']} · "
          f"最终上下文 {s['ctx_tokens']} tok · 折叠 {s['folded_total']} 块")
    print(f"累计上下文成本 {s['cumulative_ctx']} tok")
    if s["errors"]:
        print("错误：", s["errors"])
