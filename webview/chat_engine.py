"""codeb 对话引擎：上下文组装 + agent loop + 工具调用。

**这是 codeb 自己实现的对话内核**，不依赖 openai-agents、不依赖 DSH。
零外部依赖（只用标准库 + kb.py 本身），只复用 existing 的 tools_fs / Ledger 思路。

被 webview/server.mjs 以**常驻子进程**方式调用（每个会话一个进程，保持上下文）：

    node
      └── python -X utf8 webview/chat_engine.py     (stdin/stdout NDJSON)

协议（一行一个 JSON）：

    入：{"action":"init","root":"...","repo":"codeb","tree_depth":3, ...}
    出：{"type":"init_ok","context_tokens":1234,"sections":[...]}

    入：{"action":"chat","message":"..."}
    出：{"type":"token","text":"..."}          ← 流式增量
        {"type":"tool_call","name":"...","args":{...}}
        {"type":"tool_result","name":"...","result":"...","tokens":123}
        {"type":"done","answer":"...","usage":{...},"context_tokens":12345}
        {"type":"error","message":"..."}

    入：{"action":"reset"}
    出：{"type":"reset_ok"}

设计要点（每条都有实测依据，见 repo/codeb/route-packs-* 页）：

1. **目录树预装**：目录树是「结构先验」——模型先看结构再决定读什么，
   不用靠 list_dir 一层层试。实测省 3-5 轮工具调用。
2. **每问的记忆分层**：目录树/用户自定义片段永不折叠；路由包可折叠；
   工具结果按 fold_rounds 折叠（grep_count 立刻折、read_block 2 轮后折）。
   依据：模型在任何真实规模下都数不准，给原料不如给答案。
3. **不做分类器、不做轮次硬上限**：外层不替模型判断「查够了没」。
   唯一保护是「相同参数重复调用」检测（真死循环），不是「查够了没」。
4. **流式**：先有 token 就推，前端不用等整段生成。
"""
from __future__ import annotations

import contextlib
import io
import json
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CODEB = HERE.parent
sys.path.insert(0, str(CODEB))
sys.path.insert(0, str(CODEB / "distill" / "agent"))

import kb  # noqa: E402
import route_agent  # noqa: E402  （同目录的 webview/route_agent.py）

DEFAULT_MODEL = "nvidia/nemotron-3.5-super-vl-120b-a12b"

SYSTEM_BASE = (
    "你是 codeb 项目的代码助手。codeb 是一个代码知识库系统：它把源码"
    "按页/节组织成知识，并提供装订（pack/route）能力。\n"
    "\n"
    "你的上下文里**已经预装了目录树**，它告诉你项目有哪些文件、各自多大。"
    "先用目录树决定要看哪几个文件，再决定用哪个工具。\n"
    "\n"
    "你有三个工具，都是核对或派发专家：\n"
    "- ask_subagent：**派发专家，选 agent 专家名。**\n"
    "  参数有两个：agent（专家名）+ question（问题）。\n"
    "  - `agent=kernel|agent|distill|webview`：向预设路由子 agent 提问，\n"
    "    理解代码用它。路由管理一组路径下的全部源码，实测整装\n"
    "    都在 100k 以内。成员和预算已经预设好，不需要点名文件。\n"
    "    路由清单见下面「可用路由」表；选最贴近问题的那个。\n"
    "  - `agent=test`：派发测试专家，维护项目全部测试文件用它。\n"
    "    写清「改了什么文件、想确认什么」，它自己从测试清单\n"
    "    挑该跑的套件、真跑一遍、把结果归因成「代码坏了 /\n"
    "    测试期望过时 / 跑不动」三类，并负责改测试文件\n"
    "    （期望过时它会改；源码问题只报不修）。\n"
    "  - `agent=exec`：派执行专家，**按方案改源码**。\n"
    "    question 传方案全文，**必须同时给 allowed**（可写的文件或目录）；\n"
    "    从方案的文件清单里提取，如 allowed=[\"webview/public/chat.css\"]。\n"
    "    它只做语法检查，行为测试要另派 agent=test。\n"
    "  什么时候用 test：改完代码想知道有没有改坏、某个测试失败想\n"
    "  知道该改代码还是改测试、想知道改动该跑哪些测试。\n"
    "  什么时候用 exec：**已经有明确方案**（路由专家给的），用户要求落地。\n"
    "  没方案不要派 exec——它会自己发挥，那正是要避免的。\n"
    "- read_file：读单个文件（可给 offset/limit 翻页，单次最多 400 行）。\n"
    "  **只用于核对**专家答案里的某段原文。不要用它探索代码库或收集背景——\n"
    "  那是路由的事，逐个读又慢又容易漏。\n"
    "- read_constant：**精确读出某个模块级常量的值**（用 ast 取真值）。\n"
    "  问「某个常量/配置是多少」时必须用它。\n"
    "\n"
    "**先分清该谁答，再动手**：\n"
    "1. **结构问题自己答，不要派发。** 问「项目有几个模块」「某文件在哪」\n"
    "   「文件多大」「目录怎么分」——直接看目录树。目录树是你唯一的**全局**视图；\n"
    "   每个路由只装订自己那 4~12 个文件，拿局部视图答全局问题必然漏\n"
    "   （问 kernel「有几个模块」，它只能数到 kb.py 和 mcp/，答不出 distill/、webview/）。\n"
    "2. **代码细节和实现方案都派发。** 问「某函数怎么写的」「某常量值多少」\n"
    "   「调用链」「为什么这么设计」——派对应路由；问「怎么改」「给方案」\n"
    "   「加个功能」也要派，不要自己逐个 read_file 拼。全量 76k tok 你读不动，\n"
    "   路由已经装好了。「改侧边栏」这类要读 html+css+js 三四个文件，\n"
    "   自己读要十几次、还容易漏；路由一次装完。\n"
    "3. **目录树只用来判断派给哪个路由，不用来找文件自己读。**\n"
    "   按目录判归属（webview/ → agent=webview，distill/ → distill，\n"
    "   kb.py 和 mcp/ → kernel），然后直接派。**不要猜路径去 read_file**——\n"
    "   实测过：模型硬猜一个路径去 read_file，文件不存在，于是反复加大\n"
    "   max_lines 重试，连撞十几轮什么也没读到。猜路径是浪费。\n"
    "4. ask_subagent 的答案带出处和代价（哪个专家、多少 tok、多长时间），"
    "引用它给的数字要原样照搬。\n"
    "5. 路由答不到点上时，换个相邻路由再问一次（比如问蒸馏管线细节，\n"
    "   `distill` 答不全就看 `agent`——两者在 distill/ 下有交叠）。\n"
    "6. read_file 读不到时的报错会给出「同名文件的位置」，照着那个路径重试一次即可。\n"
    "\n"
    "**关于数字**：\n"
    "永远不要凭记忆或推算报一个数字。常量值用 read_constant；\n"
    "代码里的细节用 ask_subagent(agent=kernel) 读原文。实测过模型把 `-1` 答成 `3`——\n"
    "位置读对了、值报错了，这种错误看起来最像有依据，所以最危险。\n"
    "报一个没实际看到的数字，比说「不确定」糟糕得多。\n"
    "\n"
    "回答规则：\n"
    "1. 结论先行，给依据；引用代码给 `文件:行号`。\n"
    "2. 引用工具给的数字时原样照搬，不要自己加减。\n"
    "3. 确实拿不到的信息就说「拿不到」，并写明你试过什么。\n"
    "4. 中文回答，简洁。"
)


# ============================================================ 凭据
def load_env() -> dict:
    """读 LLM 凭据。与 route_ask.py 同一来源（infohub/collector/.env）。"""
    out: dict[str, str] = {}
    p = Path("D:/work/project/infohub/collector/.env")
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
    # **不跟随 .env 的 ZHIHU_LLM_MODEL**。同一份包、同一套提示词、同一批题实测：
    #   super-vl-120b：两道事实题 2/2（28 / 106），都正确调了 grep_count/find_line
    #   lightning-30b：两道都错（11 / 163），而且一次工具都没调
    # 「读到工具返回值后原样转述」是底线能力，30b 做不到，还错得很自信。
    # 要换模型用 KB_CHAT_MODEL 显式指定。
    out["ZHIHU_LLM_MODEL"] = os.environ.get(
        "KB_CHAT_MODEL", DEFAULT_MODEL) or DEFAULT_MODEL
    return out


# ============================================================ kb 调用
def _kb_text(argv: list[str]) -> tuple[int, str]:
    """进程内调 kb.py，返回 (rc, stdout)。错误时 stdout 换成 stderr。

    不带 --json：给模型读的内容用文本形态。实测 kb tree 文本 3,433 tok，
    JSON 9,185 tok（2.7 倍）——大括号、引号、重复键名全是白付的钱。
    """
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        rc = kb.main(argv)
    return rc, (out.getvalue().strip() if rc == 0 else err.getvalue().strip())


# ============================================================ 上下文组装
class ContextAssembler:
    """把目录树、路由包、自定义文件组装成 system prompt。

    每个片段带三个属性，决定它对话中的命运：
      - label      显示名（前端/日志用）
      - foldable   是否允许折叠（目录树 False，永不折）
      - priority   折叠优先级，越大越先折（同 foldable 内比较）
    """

    def __init__(self, root: Path):
        self.root = root
        self.sections: list[dict] = []

    def add_tree(self, repo: str = "codeb", depth: int = 3) -> bool:
        """注入**源码目录树**。默认必装——它让模型先看结构再决定读什么。

        为什么不用 `kb tree`：那条命令给的是**知识页树**（page/section），
        不是源码文件树。模型想读代码时，需要知道的是「有哪些 .py 文件、
        各自多大」，而不是「知识库里有哪些页」。

        用 kb.src_files（git 认可的源码全集）而不是 os.walk：规则与 pack /
        dispatch 完全一致，不会出现「目录树里有、装订时看不见」的分歧。
        """
        text = self._render_src_tree(repo, depth)
        if not text:
            return False
        self.sections.append({
            "label": f"源码目录树：{repo}",
            "content": text,
            "tokens": kb.est_tokens(text),
            "foldable": False,
            "priority": 0,
            "kind": "tree",
        })
        return True

    def _render_src_tree(self, repo: str, depth: int) -> str:
        """把仓库源码渲染成缩进树，带行数与 tok 估算。

        输出形态对齐 `kb route --around` 的信息密度：模型最需要的是
        「路径 + 行数」，行数是判断「要不要整读还是按块读」的唯一依据。
        """
        roots = kb.repo_roots(self.root)
        base = roots.get(repo)
        if base is None or not base.is_dir():
            # 退回：仓库名就是知识库根的兄弟目录名
            cand = self.root.parent / repo
            if cand.is_dir():
                base = cand
            else:
                return ""

        files = kb.src_files(base, ".", self.root)
        if not files:
            return ""

        # 按目录分组，生成缩进树。只到 depth 层，更深的折叠成一行统计。
        tree: dict = {}
        for rel in files:
            parts = rel.split("/")
            node = tree
            for p in parts[:-1]:
                node = node.setdefault(p + "/", {})
            node[parts[-1]] = None

        lines: list[str] = [f"{repo}/   （{len(files)} 个源码文件）"]

        def walk(node: dict, prefix: str, level: int, path_so_far: str):
            dirs = sorted(k for k in node if k.endswith("/"))
            fs = sorted((k for k in node if not k.endswith("/")),
                        key=lambda x: (len(x), x))
            for d in dirs:
                name = d.rstrip("/")
                sub = path_so_far + name + "/"
                if level >= depth:
                    # 超过深度：只报「这个目录下还有几个文件」
                    n = _count_files(node[d])
                    lines.append(f"{prefix}{name}/   （{n} 个文件，未展开）")
                    continue
                n = _count_files(node[d])
                lines.append(f"{prefix}{name}/   （{n}）")
                walk(node[d], prefix + "  ", level + 1, sub)
            for f in fs:
                rel = path_so_far + f
                lines.append(f"{prefix}{f}{self._size_hint(base, rel)}")

        def _count_files(node: dict) -> int:
            c = 0
            for k, v in node.items():
                if v is None:
                    c += 1
                else:
                    c += _count_files(v)
            return c

        walk(tree, "  ", 1, "")
        return "\n".join(lines)

    def _size_hint(self, base: Path, rel: str) -> str:
        """给单个文件附「行数 · tok」提示。

        这是目录树最有价值的部分：模型看到 526 行就知道不能整读、
        看到 20 行就知道随便读。没有这两个数字，模型只能靠猜。
        """
        full = base / rel
        try:
            text = full.read_text(encoding="utf-8", errors="replace")
        except OSError:
            return ""
        n = text.count("\n") + (0 if text.endswith("\n") else 1)
        return f"   {n} 行 · {kb.est_tokens(text)} tok"

    def add_route(self, spec_path: str, budget: int = 60000) -> bool:
        """注入路由包（kb route --spec 的装订结果）。"""
        rc, text = _kb_text(["route", "--spec", spec_path,
                             "--budget", str(budget), "--json"])
        if rc != 0:
            return False
        try:
            route = json.loads(text)
        except json.JSONDecodeError:
            return False
        parts = [f"# 路由包：{route.get('entry') or route.get('repo')}", ""]
        if route.get("members"):
            parts.append("| tok | 保真度 | 成员 |")
            parts.append("| --: | :-- | :-- |")
            for m in route["members"]:
                parts.append(f"| {m.get('tokens', 0)} | `{m.get('role')}` | "
                             f"`{m.get('path')}` |")
            parts.append("")
        for b in route.get("blocks", []):
            parts.append(f"## {b.get('label')}   〔{b.get('tokens', 0)} tok〕")
            parts.append("")
            parts.append(b.get("text", ""))
            parts.append("")
        content = "\n".join(parts)
        self.sections.append({
            "label": f"路由包：{route.get('entry') or route.get('repo')}",
            "content": content,
            "tokens": kb.est_tokens(content),
            "foldable": True,
            "priority": 5,
            "kind": "route",
        })
        return True

    def add_file(self, path: str, max_lines: int = 300) -> bool:
        """注入单个文件（README / DESIGN 等约束文档）。"""
        full = self.root / path
        if not full.is_file():
            return False
        text = full.read_text(encoding="utf-8", errors="replace")
        lines = text.splitlines()
        body = "\n".join(lines[:max_lines])
        if len(lines) > max_lines:
            body += f"\n\n…（共 {len(lines)} 行，只装了前 {max_lines} 行）"
        self.sections.append({
            "label": f"文件：{path}",
            "content": body,
            "tokens": kb.est_tokens(body),
            "foldable": True,
            "priority": 3,
            "kind": "file",
        })
        return True

    def add_custom(self, label: str, content: str) -> None:
        """注入任意自定义文本（用户的约束、契约、事实）。"""
        self.sections.append({
            "label": label,
            "content": content,
            "tokens": kb.est_tokens(content),
            "foldable": True,
            "priority": 2,
            "kind": "custom",
        })

    def build_system(self) -> str:
        parts = [SYSTEM_BASE]
        # 路由目录单独成段（走 sections 而不是直接拼 SYSTEM_BASE）：
        # 它和目录树一样是「预注入的上下文」，应该能在面板上单独看到。
        # 早先直接拼进返回值，结果它被算进 SYSTEM_BASE 那 753 tok 里，
        # 面板上完全看不见——「装了路由目录」这件事就无从核对。
        if not any(s["kind"] == "routes" for s in self.sections):
            try:
                cat = route_agent.route_catalog()
                self.sections.append({
                    "label": "可用路由（向子 agent 提问）",
                    "content": cat,
                    "tokens": kb.est_tokens(cat),
                    "foldable": False,
                    "priority": 0,
                    "kind": "routes",
                })
            except route_agent.RouteError as e:
                self.sections.append({
                    "label": "可用路由（配置加载失败）",
                    "content": f"路由配置有问题：{e}",
                    "tokens": 20, "foldable": False, "priority": 0,
                    "kind": "routes",
                })
        for sec in self.sections:
            parts.append(f"\n---\n\n## {sec['label']}   〔{sec['tokens']} tok〕\n")
            parts.append(sec["content"])
        return "\n".join(parts)

    def total_tokens(self) -> int:
        return sum(s["tokens"] for s in self.sections)

    def summary(self) -> list[dict]:
        return [{"label": s["label"], "tokens": s["tokens"],
                 "foldable": s["foldable"], "kind": s["kind"]}
                for s in self.sections]


# ============================================================ 工具
def make_tools(repo: str, get_env=None, get_stop=None):
    """构造工具 schema + 实现。

    **工具面只剩三个**：ask_subagent（派专家：route/测试专家）+ read_file（核对）
    + read_constant（读常量真值）。

    为什么砍掉 grep_count / find_line / grep_text / list_dir / read_block：
    实测在「装了源码的包」里，模型对理解题一次工具都不调（3 题 0 调用，
    两个模型都一样），把 schema 加上去只多付 551 tok。而计数/定位题
    即使把工具摆在它面前，`tool_choice=auto` 下它也不调，答案照样错
    （36 数成 21/14，行号 405 答成 1042/1010）。
    结论：留在这一层的搜索工具是「付费但不用」的装饰品。

    搜索能力没有消失，它被下沉到装订层（`kb route` 解析 ast、按保真度取料），
    那是确定性代码，比模型现搜可靠。

    read_file 保留的理由：ask_subagent(agent=route) 的答案是**转述**。leader 要核对
    某段原文、或文件小到不值得派子 agent 时，得有直接通道。
    没有这条路它会「相信」或「重新装订」，前者危险后者贵。
    """
    import tools_fs

    # 测试/执行专家和路由都在同一个目录里，导入放函数内避免模块级循环：
    # test_expert.py 模块级导入了 chat_engine。
    import exec_expert  # noqa: E402
    import test_expert  # noqa: E402

    def _read_file(path: str, max_lines: int = 150, offset: int = 1):
        """offset 有值时走 read_file_range。

        补的是个真缺陷：`tools_fs.read_file` 的返回文本一直写着
        「用 offset 继续读」，但它本身没有 offset 参数——模型照着提示去
        翻页会发现根本没这个参数可用。这里按 offset 分派到 read_file_range，
        让那句提示终于成立。
        """
        off = int(offset or 1)
        # max_lines 封顶。实测模型被「读不到」激怒时会一路加大到 50000，
        # 把整个文件塞进上下文（kb.py 有 3370 行，一次就是 4 万 tok）。
        # 想到的是「多给点就能读到」，实际只是烧上下文。
        cap = max(1, min(int(max_lines or 150), 400))
        if off > 1:
            return tools_fs.read_file_range(path, off, cap, root=repo)
        out = tools_fs.read_file(path, cap, root=repo)
        if "后面还有" in out:
            out += ("\n（提示：继续读用 offset 参数翻页；"
                    "或改用 ask_subagent(agent=route) 让子 agent 整篇读完再回答。）")
        return out

    def _read_constant(path: str, name: str):
        return tools_fs.read_constant(path, name, root=repo)

    specs = [
        {"type": "function", "function": {
            "name": "ask_subagent",
            "description": (
                "派发专家，选 agent 专家名：\n"
                "  - `agent=kernel|agent|distill|webview`：向预设路由子 agent 提问，\n"
                "    理解代码用它。路由管理一组路径下的全部源码，实测整装\n"
                "    都在 100k 以内。成员和预算已预设，不需要点名文件。\n"
                "  - `agent=test`：派发测试专家，维护项目全部测试文件用它。\n"
                "    写清「改了什么文件、想确认什么」，它自己从测试清单\n"
                "    挑该跑的套件、真跑一遍、把结果归因成「代码坏了 /\n"
                "    测试期望过时 / 跑不动」三类，并负责改测试文件\n"
                "    （期望过时它会改；源码问题只报不修）。\n"
                "  - `agent=exec`：派执行专家，按方案**改源码**。question 传方案\n"
                "    全文，**必须同时给 allowed**（可写的文件或目录），否则拒绝。\n"
                "    它只做语法检查，行为测试要另派 agent=test。\n"
                "后续新增专家（如 doc、perf），直接加在 agent 字典里即可。\n"
                "参数：agent（专家名）+ question（问题/方案）+ allowed（仅 exec）。"),
            "parameters": {
                "type": "object",
                "properties": {
                    "agent": {
                        "type": "string",
                        "description": "专家名：kernel/agent/distill/webview（代码问答路由），或 test（测试专家）。可用：kernel, agent, distill, webview, test",
                    },
                    "question": {
                        "type": "string",
                        "description": "要问的问题；agent=exec 时传**方案全文**。例："
                        "\"我改了 webview/chat_engine.py，该跑哪些测试？\"",
                    },
                    "allowed": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "**仅 agent=exec 必填**：允许执行专家写的文件或目录"
                                       "（仓库内相对路径）。从方案的文件清单提取，"
                                       "如 [\"webview/public/chat.css\", \"webview/public/chat.html\"]。"
                                       "越界写入会被拒绝。",
                    },
                },
                "required": ["agent", "question"],
            },
        }},
        {"type": "function", "function": {
            "name": "read_file",
            "description": (
                "读单个文件，支持翻页（offset 从 1 开始，单次最多 400 行）。"
                "**只用于核对专家答案里的某段原文**，或文件确实很小。"
                "**不要用它探索代码库或收集背景**——那是路由的事；"
                "需要跨文件理解、或要「给方案」时派 ask_subagent，不要逐个文件拼。"),
            "parameters": {"type": "object", "properties": {
                "path": {"type": "string", "description": "仓库内相对路径"},
                "max_lines": {"type": "integer", "description": "默认 150，上限 400"},
                "offset": {"type": "integer",
                           "description": "起始行，从 1 开始，默认 1"},
            }, "required": ["path"]},
        }},
        {"type": "function", "function": {
            "name": "read_constant",
            "description": (
                "**精确读出模块级常量/配置的值**（用 ast 取真值，不是让模型抄）。"
                "问「某个常量是多少」时用它——实测模型会读对位置却报错值"
                "（把 -1 答成 3）。名字相近时它会给出候选。"),
            "parameters": {"type": "object", "properties": {
                "path": {"type": "string", "description": "仓库内相对路径"},
                "name": {"type": "string", "description": "常量名，如 FOLD_ROUNDS"},
            }, "required": ["path", "name"]},
        }},
    ]

    def _ask_route(route: str, question: str):
        """执行预设路由子 agent。env 和 stop_flag 从会话拿，不从模型拿——
        模型不该能决定用哪个 API key、也不该能屏蔽用户的停止按钮。

        **成员不在参数里**：leader 只给路由名，成员/保真度/预算由配置定。
        """
        env = (get_env() if get_env else None) or load_env()
        stop = get_stop() if get_stop else None
        try:
            res = route_agent.ask_preset(
                route, question, env, repo=repo, stop_flag=stop)
        except route_agent.RouteError as e:
            # 把错误**变成给模型看的文本**，不是抛出去炸掉整轮：
            # 模型看到「没有这个路由」还能换个名字重试
            return f"ask_route 失败：{e}"
        return route_agent.render_for_leader(res)

    def _ask_test_expert(question: str):
        """派发测试专家。env 从会话拿，模型不该决定 API key。"""
        env = (get_env() if get_env else None) or load_env()
        try:
            res = test_expert.ask(question, env, repo=repo)
        except test_expert.ExpertError as e:
            return f"ask_test_expert 失败：{e}"
        return test_expert.render_for_leader(res)

    def _ask_exec(plan: str, allowed):
        """派发执行专家。allowed 必须由 leader 显式给——
        空 allowed 时执行专家没有任何写权限，派了也是空转。"""
        if not allowed:
            return ("ask_subagent(agent=exec) 失败：allowed 不能为空。"
                    "执行专家必须显式授权可写范围，例如 "
                    "allowed=[\"webview/public/chat.css\", \"webview/public/chat.html\"]。")
        env = (get_env() if get_env else None) or load_env()
        try:
            res = exec_expert.ask(plan, allowed, env, repo=repo)
        except exec_expert.ExpertError as e:
            return f"ask_subagent(agent=exec) 失败：{e}"
        return exec_expert.render_for_leader(res)

    def _ask_subagent(agent: str, question: str, allowed=None):
        """派发专家：agent 是专家名。

        **leader 只给专家名 + 问题（exec 另给 allowed），不点成员、不点套件。**
        路由专家名与 routes.json 里的 name 一致（kernel/agent/distill/webview）；
        test 是测试专家；exec 是执行专家（必须带 allowed）。
        后续新增专家（如 doc、perf），就在 agents 字典里加一行。
        """
        def route_dispatch(route_name: str):
            def _disp(question: str):
                return _ask_route(route_name, question)
            return _disp

        name = (agent or "").strip().lower()
        if name == "exec":
            return _ask_exec(question, allowed)

        agents = {
            "kernel": route_dispatch("kernel"),
            "agent": route_dispatch("agent"),
            "distill": route_dispatch("distill"),
            "webview": route_dispatch("webview"),
            "test": _ask_test_expert,
        }
        impl = agents.get(name)
        if impl is None:
            names = ", ".join(f"`{n}`" for n in [*agents, "exec"])
            return f"ask_subagent 失败：没有叫 `{agent}` 的专家。可用：{names}"
        return impl(question)

    impl = {
        "ask_subagent": _ask_subagent,
        "read_file": _read_file,
        "read_constant": _read_constant,
    }
    return specs, impl


# 折叠策略：工具名 -> 存活轮数。<0 永不折叠。
# ask_route 的结果是**答案**，不是原料：它包含子 agent 的结论，
# 后面的对话还要反复引用，折了等于让 leader 忘掉自己刚问到的结论。
# read_file 是原文，读一次就够，留 2 轮。
# read_constant 返回一串精确的值，是「事实」，永不折。
FOLD_ROUNDS = {
    "ask_subagent": -1,   # 永不折叠：专家给的是可归因结论，折了就失效
    "read_file": 2,
    "read_constant": -1,  # 永不折叠：事实一旦被折叠，后续引用就没了依据
}


# ============================================================ LLM 调用
def call_llm(env: dict, system: str, messages: list, tools: list,
             max_tokens: int = 4096, stop_flag=None,
             on_token=None, on_cot=None, cot: bool = False) -> tuple[dict, dict]:
    """调 LLM。返回 (message, usage)。

    用 SSE 流式读，不是一次性等全部——两个原因：
    1. **停止要能立刻生效**：非流式时 urlopen 会一直阻塞到模型写完，
       用户点了停止还得等这一整轮跑完（实测等了 21 秒）。流式下每收到一块
       就查一次 stop_flag，最迟几十毫秒就能退出。
    2. 顺带能推 token：on_token(text) 让前端边生成边看到字，
       而不是盯着空屏等 20 秒突然出现整段。

    工具调用也要拼装：流式里 tool_calls 是按 index 分片给的，
    arguments 是一条字符串被切成若干段，必须按 index 累加。
    """
    import urllib.error
    import urllib.request

    base = (env.get("ZHIHU_LLM_BASE_URL")
            or "https://integrate.api.nvidia.com/v1").rstrip("/")
    model = env.get("ZHIHU_LLM_MODEL") or DEFAULT_MODEL
    key = env.get("ZHIHU_LLM_API_KEY")
    if not key:
        raise RuntimeError("缺 ZHIHU_LLM_API_KEY（检查 infohub/collector/.env）")

    payload = {
        "model": model,
        "messages": [{"role": "system", "content": system}] + messages,
        "temperature": 0,
        "max_tokens": max_tokens,
        "stream": True,
        "stream_options": {"include_usage": True},
    }
    if tools:
        payload["tools"] = tools
        payload["tool_choice"] = "auto"
    # NVIDIA 端点默认关 thinking：早期实测 tool_choice="required" 时开着会烧光
    # max_tokens 返回空 content。现在改为**按会话开关**：cot=False 保持原行为，
    # cot=True 才打开，让模型输出 reasoning_content。前端有独立的「思考」开关。
    if "nvidia.com" in base:
        payload["chat_template_kwargs"] = {"enable_thinking": bool(cot)}

    req = urllib.request.Request(
        f"{base}/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json",
                 "Accept": "text/event-stream",
                 "Authorization": f"Bearer {key}"})

    content_parts: list[str] = []
    reasoning_parts: list[str] = []   # CoT：reasoning_content（DeepSeek）/ reasoning（其他）
    # index -> {"id","name","arguments"}
    calls: dict[int, dict] = {}
    usage: dict = {}
    finish_reason = ""

    def stopped() -> bool:
        return stop_flag is not None and stop_flag.is_set()

    try:
        with urllib.request.urlopen(req, timeout=180) as r:
            for raw in r:
                if stopped():
                    break
                line = raw.decode("utf-8", "replace").strip()
                if not line or not line.startswith("data:"):
                    continue
                chunk = line[5:].strip()
                if chunk == "[DONE]":
                    break
                try:
                    obj = json.loads(chunk)
                except json.JSONDecodeError:
                    continue
                if obj.get("usage"):
                    usage = obj["usage"]
                for ch in obj.get("choices") or []:
                    if ch.get("finish_reason"):
                        finish_reason = ch["finish_reason"]
                    delta = ch.get("delta") or {}
                    piece = delta.get("content")
                    if piece:
                        content_parts.append(piece)
                        if on_token:
                            on_token(piece)
                    # CoT 增量：不同端点字段名不同，两个都认。
                    reason = delta.get("reasoning_content")
                    if reason is None:
                        reason = delta.get("reasoning")
                    if reason:
                        reasoning_parts.append(reason)
                        if on_cot:
                            on_cot(reason)
                    for tc in delta.get("tool_calls") or []:
                        idx = tc.get("index", 0)
                        slot = calls.setdefault(idx, {"id": "", "name": "", "arguments": ""})
                        if tc.get("id"):
                            slot["id"] = tc["id"]
                        fn = tc.get("function") or {}
                        if fn.get("name"):
                            slot["name"] = fn["name"]
                        if fn.get("arguments"):
                            slot["arguments"] += fn["arguments"]
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "replace")[:500]
        raise RuntimeError(f"LLM HTTP {e.code}：{body}") from None
    except urllib.error.URLError as e:
        raise RuntimeError(f"连不上 LLM 端点：{e.reason}") from None

    msg: dict = {"role": "assistant", "content": "".join(content_parts)}
    if reasoning_parts:
        msg["reasoning"] = "".join(reasoning_parts)
    if calls:
        msg["tool_calls"] = [
            {"id": calls[i]["id"] or f"call_{i}", "type": "function",
             "function": {"name": calls[i]["name"],
                          "arguments": calls[i]["arguments"] or "{}"}}
            for i in sorted(calls)
        ]
    if finish_reason:
        msg["finish_reason"] = finish_reason
    return msg, usage


# ============================================================ 会话
class ChatSession:
    """一次对话会话的完整状态：上下文 + 历史 + 工具结果账本。"""

    def __init__(self, root: Path, repo: str = "codeb", tree_depth: int = 3,
                 route_specs: list[dict] | None = None,
                 files: list[dict] | None = None,
                 custom: list[dict] | None = None,
                 model: str = "", cot: bool = False):
        self.root = root
        self.repo = repo
        self.cot = bool(cot)   # 是否让模型输出 reasoning（思考链）
        self.env = load_env()
        if model:
            self.env["ZHIHU_LLM_MODEL"] = model

        # ---- 上下文（可自定义）----
        self.assembler = ContextAssembler(root)
        self.assembler.add_tree(repo=repo, depth=tree_depth)   # ← 目录树预装
        for rs in (route_specs or []):
            self.assembler.add_route(rs["path"], rs.get("budget", 60000))
        for f in (files or []):
            self.assembler.add_file(f["path"], f.get("max_lines", 300))
        for c in (custom or []):
            self.assembler.add_custom(c["label"], c["content"])

        self.system = self.assembler.build_system()
        # system_tokens 必须含 SYSTEM_BASE：早先只算 assembler.total_tokens()
        # （即只算目录树那段），于是系统提示词本身那约 300 tok 从来没进过
        # 任何数字——顶栏显示 266，实际发出去 577。**统计口径要和发送内容一致**，
        # 否则「上下文用了多少」这个问题永远答错。
        self.system_tokens = kb.est_tokens(self.system)

        # ---- 工具 ----
        # env 和 stop_flag 用回调注入，而不是构造时传值：
        #   - env 会因 set_model 中途变化，传值会让工具拿到旧模型
        #   - stop_flag 每一轮都是新对象，必须在调用时刻取
        self._stop_flag = None
        self.tool_specs, self.tool_impl = make_tools(
            repo,
            get_env=lambda: self.env,
            get_stop=lambda: self._stop_flag,
        )
        # 工具 schema 也是每轮都发的真实输入。现在只剩 2 个工具，
        # 但 ask_route 的 schema 里嵌了 members 数组，仍然要单独记账。
        self.tools_tokens = kb.est_tokens(
            json.dumps(self.tool_specs, ensure_ascii=False))

        # ---- 状态 ----
        self.history: list[dict] = []   # user/assistant/tool 消息（唯一的发送源）
        self.blocks: list[dict] = []    # 工具结果账本（只管折叠，不单独发送）
        self.folded: dict[str, dict] = {}
        self.n = 0                      # 轮次计数（折叠的 age 基准）
        self.total_calls = 0            # 本轮对话累计工具调用数（真正的成本单位）
        self.seen_sigs: set[str] = set()

    # ---------------- 输出 ----------------
    @staticmethod
    def emit(obj: dict) -> None:
        """输出一行 NDJSON 给父进程。"""
        sys.stdout.write(json.dumps(obj, ensure_ascii=False) + "\n")
        sys.stdout.flush()

    def emit_done(self, answer: str, usage: dict, stopped: bool,
                  cot_parts: list[str]) -> None:
        """统一的 done 出口：把整轮累积的 CoT 一次性带上。

        增量 `cot` 事件已边生成边推给前端，这里再带全量是为了让前端在
        done 时定稿（流式可能被截断），也是会话持久化时唯一可靠的 CoT 来源。
        """
        d = {"type": "done", "answer": answer, "usage": usage,
             "stopped": stopped, "context_tokens": self.context_tokens()}
        if cot_parts:
            d["cot"] = "".join(cot_parts)
        self.emit(d)

    # ---------------- 账本 ----------------
    def _add_block(self, tool: str, text: str, hist_idx: int) -> dict:
        """登记一次工具结果。

        hist_idx 指向 history 里那条 {"role":"tool"} 消息。
        **账本不自己保存可发送的正文**——正文只有 history 那一份，
        折叠时按 hist_idx 就地改写。早先账本和 history 各存一份、
        _build_messages 两边都发，同一份结果在 payload 里出现两次，
        实测占 payload 35%，纯浪费。
        """
        b = {"tool": tool, "text": text, "born": self.n, "hist_idx": hist_idx,
             "key": f"{tool}#{self.n}", "tokens": kb.est_tokens(text)}
        self.blocks.append(b)
        return b

    def _sweep(self) -> list[str]:
        """轮末折叠。判据是 age > k（给 born 那一轮留一次被读的机会）。

        写成 age >= k 时 k=0 会让刚加的块同轮就被折掉，模型从头到尾
        没读到内容，于是反复重调同一个工具——踩过这个坑。
        """
        hit = []
        for b in self.blocks:
            k = FOLD_ROUNDS.get(b["tool"], 2)
            if k < 0 or b["key"] in self.folded:
                continue
            if self.n - b["born"] > k and b["tokens"] > 40:
                b["folded_text"] = (f"〔已折叠：{b['tool']} {b['key']} 的结果，"
                                    f"原文 {b['tokens']} tok。需要时重新调用工具取。〕")
                self.folded[b["key"]] = b
                # 就地改写 history 里那条 tool 消息——它是唯一发送源，
                # 改这里才真正省下 token（只改账本等于账本上省钱）
                idx = b.get("hist_idx")
                ok = (isinstance(idx, int) and 0 <= idx < len(self.history)
                      and self.history[idx].get("role") == "tool")
                if ok:
                    self.history[idx]["content"] = b["folded_text"]
                else:
                    # 索引错位说明 history 被插入过内容（目前不会发生，
                    # 但静默改错一条消息比不折叠严重得多）。按正文回退查找。
                    for m in self.history:
                        if m.get("role") == "tool" and m.get("content") == b["text"]:
                            m["content"] = b["folded_text"]
                            break
                hit.append(b["key"])
        return hit

    def _build_messages(self) -> list[dict]:
        """要发给 LLM 的 messages（system 单独传）。

        **history 是唯一发送源**。工具结果只以 history 里那条
        {"role":"tool"} 消息的形式发出，账本 blocks 不参与发送——
        它只负责记录「哪一条、什么时候该折叠」。
        """
        return list(self.history)

    def context_tokens(self) -> int:
        """真正发给 LLM 的输入估算：system + tools + messages。"""
        return (self.system_tokens
                + self.tools_tokens
                + sum(kb.est_tokens(str(m.get("content") or ""))
                      + kb.est_tokens(json.dumps(m.get("tool_calls") or [],
                                                 ensure_ascii=False))
                      for m in self.history))

    # ---------------- 主循环 ----------------
    def chat(self, user_msg: str, stop_flag=None) -> None:
        """处理一条用户消息，全程 NDJSON 输出。

        stop_flag 是一个 threading.Event：主线程在跑 LLM 时，
        读线程收到 {"action":"stop"} 会把它置位，下一拍就退出。
        为什么不用 signal / 杀进程：**杀进程会丢掉已生成的内容和上下文**，
        用户想要的「停止」是「停在这一步，保留已经拿到的」，不是「全部作废」。
        """
        def stopped() -> bool:
            return stop_flag is not None and stop_flag.is_set()

        # 让工具能拿到这一轮的停止标志：ask_route 会跑 2-30 秒，
        # 不给它停止标志的话，用户点了停止要等子 agent 跑完才生效
        self._stop_flag = stop_flag

        self.n += 1
        self.history.append({"role": "user", "content": user_msg})

        model = self.env.get("ZHIHU_LLM_MODEL") or DEFAULT_MODEL
        last_usage: dict = {}
        # 一轮对话可能跨多个工具轮次，每个 assistant 响应都可能带一段 reasoning。
        # 累积起来随 done 一次性交给前端，这样前端刷新/恢复时也能拿到完整 CoT。
        cot_parts: list[str] = []

        def on_cot(t: str):
            # 即使端点没按 enable_thinking 关掉 reasoning（非 NVIDIA 端点
            # 拿不到那个参数），前端没开思考链时也不该收到 cot 事件。
            # 开关是唯一真值，不依赖端点配合。
            if not self.cot:
                return
            cot_parts.append(t)
            self.emit({"type": "cot", "text": t})

        # 轮次上限：正常问题 1-3 轮就够，实测最坏的一次模型连跑 25 轮工具
        # 才开口说话（那是它把「逐个文件统计」当成了任务）。定 12 轮：
        # 够用完所有只读工具把答案拼出来，又不至于让用户干等五分钟。
        guard = 0
        while True:
            guard += 1
            # 三个维度一起限，因为只限轮数挡不住：
            #   实测 12 轮 × 每轮 11 个并行工具 = 136 次调用、164 秒。
            # 「轮数」是粗粒度，「总调用数」才是真正的成本单位。
            if guard > 8 or self.total_calls > 24:
                # 撞满上限时不要空手退出：历史里已经有一堆工具结果，
                # 那些结果可能就是答案，只是模型没去读。收走工具、
                # 再问一次「用已有信息回答」，比直接返回一句「先停在这里」有用得多。
                self.emit({"type": "tool_call", "name": "（收束）",
                           "args": {"reason": f"{guard} 轮 / {self.total_calls} 次调用"}})
                try:
                    msg, usage = call_llm(
                        self.env, self.system,
                        self._build_messages() + [{
                            "role": "user",
                            "content": ("你已经调用了很多次工具但还没给结论。"
                                        "**不要再调用工具**（工具已收回）。"
                                        "就用上面已经拿到的信息直接回答；"
                                        "信息确实不够的部分，明确说缺什么。"),
                        }],
                        [],          # 空工具列表 = 强制它开口
                        stop_flag=stop_flag, cot=self.cot,
                        on_token=lambda t: self.emit({"type": "token", "text": t}),
                        on_cot=on_cot,
                    )
                    last_usage = usage or last_usage
                    answer = (msg.get("content") or "").strip()
                except Exception as e:  # noqa: BLE001
                    answer = ""
                    self.emit({"type": "error", "message": str(e)})
                if not answer:
                    answer = (f"（{guard} 轮 / {self.total_calls} 次工具调用仍未得出结论，"
                              f"模型 {model} 在收束时也没有给出回答。"
                              f"建议把问题缩小到具体文件。）")
                self.history.append({"role": "assistant", "content": answer})
                self.emit_done(answer, last_usage, False, cot_parts)
                return
            if stopped():
                self.emit_done("（已停止）", last_usage, True, cot_parts)
                return

            msgs = self._build_messages()
            try:
                # on_token 边生成边推给前端；stop_flag 让「停止」在流里即时生效
                # （非流式时要等整轮写完，实测点了停止还要等 21 秒）
                msg, usage = call_llm(
                    self.env, self.system, msgs, self.tool_specs,
                    stop_flag=stop_flag, cot=self.cot,
                    on_token=lambda t: self.emit({"type": "token", "text": t}),
                    on_cot=on_cot,
                )
            except Exception as e:  # noqa: BLE001
                self.emit({"type": "error", "message": str(e)})
                return
            last_usage = usage

            # 流式模式下 content 已经在 on_token 里推过了，这里不再重复推
            tool_calls = msg.get("tool_calls") or []
            content = (msg.get("content") or "").strip()

            if not tool_calls:
                if stopped():
                    # 流被停止截断：模型可能只说了一半。把已经拿到的存下来，
                    # 明确标成 stopped，别让它看起来像一个完整答案。
                    partial = content or "（已停止，未产生回答）"
                    self.history.append({"role": "assistant", "content": partial})
                    self.emit_done(partial, usage, True, cot_parts)
                    return
                answer = content or f"（空回答；finish_reason 异常，模型 {model}）"
                self.history.append({"role": "assistant", "content": answer})
                self.emit_done(answer, usage, False, cot_parts)
                return

            # 带工具调用的 assistant 消息必须进历史，否则工具结果的
            # tool_call_id 找不到对应请求，下一轮 API 会报错
            # （它的 content 已经在 on_token 里逐字推过了，不要再推一次）
            self.history.append(msg)

            for tc in tool_calls:
                if stopped():
                    # 已经发出的 tool_calls 必须配齐 tool 消息，否则历史结构非法
                    self.history.append({"role": "tool",
                                         "tool_call_id": tc.get("id", ""),
                                         "content": "（用户已停止，此调用未执行）"})
                    continue

                fn = tc.get("function") or {}
                name = fn.get("name") or ""
                try:
                    args = json.loads(fn.get("arguments") or "{}")
                except json.JSONDecodeError:
                    args = {}
                if not isinstance(args, dict):
                    args = {}

                self.emit({"type": "tool_call", "name": name, "args": args})

                self.total_calls += 1
                # 单轮超量保护：一次响应里给 11 个工具调用时，
                # 前几个的结果就足够它重新决策了，剩下的纯属浪费
                if self.total_calls > 24:
                    out = (f"（已累计 {self.total_calls} 次工具调用，达到上限。"
                           f"请直接用已有信息回答。）")
                    self.history.append({"role": "tool",
                                         "tool_call_id": tc.get("id", ""),
                                         "content": out})
                    continue

                sig = f"{name}|{json.dumps(args, sort_keys=True, ensure_ascii=False)}"
                if sig in self.seen_sigs:
                    out = ("（这个调用已经执行过，结果在上下文里。如果没找到你要的，"
                           f"说明 {name} 回答不了这个问题——换工具或换参数。）")
                    self.emit({"type": "tool_result", "name": name,
                               "result": out, "tokens": 0, "repeated": True})
                    self.history.append({"role": "tool",
                                         "tool_call_id": tc.get("id", ""),
                                         "content": out})
                    continue
                self.seen_sigs.add(sig)

                impl = self.tool_impl.get(name)
                if impl is None:
                    out = f"未知工具：{name}"
                else:
                    try:
                        out = str(impl(**args))
                    except TypeError as e:
                        out = f"参数不对：{e}"
                    except Exception as e:  # noqa: BLE001
                        out = f"工具执行失败：{e}"

                # 先 append 再登记账本：账本要记下这条消息在 history 的索引，
                # 折叠时才改得到它（history 是唯一发送源）
                hist_idx = len(self.history)
                self.history.append({"role": "tool",
                                     "tool_call_id": tc.get("id", ""),
                                     "content": out})
                b = self._add_block(name, out, hist_idx)
                self.emit({"type": "tool_result", "name": name,
                           "result": out[:2000], "tokens": b["tokens"]})

            self._sweep()

            if stopped():
                self.emit_done("（已停止）", last_usage, True, cot_parts)
                return

    def set_model(self, model: str) -> str:
        """切换模型。**只影响后续调用**，不动已有上下文。

        为什么允许中途切换：实测同一份包下 120b 与 30b 差一个量级
        （事实题 2/2 vs 0/2）。发现答不好时换个模型重问，比重新开一个
        会话把目录树重新扫一遍便宜。
        """
        if model:
            self.env["ZHIHU_LLM_MODEL"] = model
        return self.env.get("ZHIHU_LLM_MODEL") or ""

    # ---------------- 上下文解剖 ----------------
    def context_raw(self) -> list[dict]:
        """下一轮真正发给 LLM 的 messages 数组，逐条原样返回。

        与 context_breakdown（聚合态）的区别：
          - breakdown：按语义分段、按 token 降序、带折叠说明——是**给人看的解释**；
          - 这里：call_llm 实际构造的 payload = [system] + history，按**真实顺序**，
            含折叠后的占位符、tool_calls、tool_call_id——是**给核对用的原样**。

        两者必须同源：都读 self.history 和 self.system，不能各算一份，
        否则「原始态」和「聚合态」会对不上账。
        """
        out = [{
            "idx": 0, "role": "system", "content": self.system,
            "tokens": self.system_tokens,
        }]
        for i, m in enumerate(self.history, 1):
            role = m.get("role") or "?"
            content = str(m.get("content") or "")
            item = {"idx": i, "role": role, "content": content,
                    "tokens": kb.est_tokens(content)}
            if m.get("tool_calls"):
                item["tool_calls"] = m["tool_calls"]
                item["tokens"] += kb.est_tokens(
                    json.dumps(m["tool_calls"], ensure_ascii=False))
            if m.get("tool_call_id"):
                item["tool_call_id"] = m["tool_call_id"]
            out.append(item)

        # est_tokens 对拼接边界敏感：逐条估的和会比 context_tokens()
        # 少几个 tok。面板两个视图都必须和真实发送量对上账，否则
        # 「原始态合计 ≠ 聚合态合计」又会变成面板骗人。把差额摊给最大的那条。
        target = self.context_tokens() - self.tools_tokens
        got = sum(m["tokens"] for m in out)
        if got and target != got:
            big = max(out, key=lambda m: m["tokens"])
            big["tokens"] += target - got
            big["gap_note"] = f"含 {target - got:+d} tok 的估算边界差"
        return out

    def context_breakdown(self) -> dict:
        """把「下一轮真正要发的东西」逐段拆开。

        与 assembler.summary() 的关键区别：
          summary 报的是**我的数据结构**（sections 那几段）；
          这里报的是 **LLM 实际收到的内容**——含系统提示词、工具定义、
          工具结果、对话历史，每一段都带正文，能直接看到装了什么。

        做这个的起因：面板原先只显示目录树 266 tok，而实际发出去的是
        266 + 系统提示词 311 + 工具定义 627 ≈ 1.2k。**面板显示的数字
        和真正发出去的内容对不上，那这个面板就是在骗人。**
        """
        parts: list[dict] = []

        # 1) 系统提示词：SYSTEM_BASE + 各装配段
        sys_parts = [{"label": "SYSTEM_BASE（角色与规则）",
                      "content": SYSTEM_BASE,
                      "tokens": kb.est_tokens(SYSTEM_BASE)}]
        for s in self.assembler.sections:
            sys_parts.append({"label": s["label"], "content": s["content"],
                              "tokens": s["tokens"], "kind": s["kind"],
                              "foldable": s["foldable"]})
        parts.append({
            "kind": "system", "label": "系统提示词", "tokens": self.system_tokens,
            "foldable": False,
            "note": "每轮都发。包含角色规则 + 下面这些装配段",
            "children": sys_parts,
        })

        # 2) 工具定义
        tool_children = []
        for s in self.tool_specs:
            fn = s["function"]
            tool_children.append({
                "label": fn["name"],
                "content": fn.get("description") or "",
                "tokens": kb.est_tokens(json.dumps(s, ensure_ascii=False)),
                "params": list((fn.get("parameters") or {}).get("properties", {}).keys()),
            })
        parts.append({
            "kind": "tools", "label": f"工具定义（{len(self.tool_specs)} 个）",
            "tokens": self.tools_tokens, "foldable": False,
            "note": f"每轮都发。比目录树还大——schema 本身就要 {self.tools_tokens} tok",
            "children": tool_children,
        })

        # 3) 工具结果（折叠状态如实标注）
        if self.blocks:
            kids = []
            for b in self.blocks:
                folded = b["key"] in self.folded
                # 存活时发的是原文；折叠后发的是占位符。按**实际发出去的**
                # 那个版本来算 token，才能和 context_tokens() 对上账。
                live_text = b["folded_text"] if folded else b["text"]
                kids.append({
                    "label": b["key"],
                    "content": live_text,
                    "tokens": kb.est_tokens(live_text),
                    "full_tokens": b["tokens"],
                    "folded": folded,
                    "tool": b["tool"],
                })
            live = sum(k["tokens"] for k in kids)
            saved = sum(k["full_tokens"] - k["tokens"] for k in kids)
            parts.append({
                "kind": "tool-results", "label": f"工具结果（{len(self.blocks)} 条）",
                "tokens": live, "foldable": True,
                "note": (f"已折叠的只发占位符，省下 {saved} tok"
                         if saved > 0 else "全部存活，正文每轮都发"),
                "children": kids,
            })

        # 4) 对话历史
        if self.history:
            kids = []
            for i, m in enumerate(self.history):
                role = m.get("role") or "?"
                if role == "tool":
                    continue          # tool 消息已在「工具结果」段展示，不重复列
                txt = str(m.get("content") or "")
                # tool_calls 的 JSON 也真的发出去，必须计入，
                # 否则这里的合计会永远小于 context_tokens()，对不上账
                tc_txt = json.dumps(m.get("tool_calls") or [], ensure_ascii=False) \
                    if m.get("tool_calls") else ""
                tok = kb.est_tokens(txt) + kb.est_tokens(tc_txt)
                kids.append({"label": f"[{role}]" + (" +tool_calls" if tc_txt else ""),
                             "content": txt, "tokens": tok, "idx": i})
            if kids:
                parts.append({
                    "kind": "history", "label": f"对话历史（{len(kids)} 条）",
                    "tokens": sum(k["tokens"] for k in kids), "foldable": False,
                    "note": "不折叠。折叠对话会让模型忘了自己刚说过什么",
                    "children": kids,
                })

        # 用 context_tokens() 校正 messages 类的段。
        # est_tokens 对拼接边界敏感（同样内容拼在不同位置会差几个 token），
        # 而 context_tokens() 是把每条消息单独估的。不校正的话面板合计数
        # 会和真正发出去的数字差 2-4 tok——小，但「账对不上」这件事本身就是错的。
        target = self.context_tokens()
        fixed = sum(1 for p in parts if p["kind"] in ("tool-results", "history"))
        if fixed:
            gap = target - self.system_tokens - self.tools_tokens - sum(
                p["tokens"] for p in parts if p["kind"] in ("tool-results", "history"))
            if gap:
                # 把差额摊到最大的那个消息类段，保持各段数字仍然可解释
                big = max((p for p in parts
                           if p["kind"] in ("tool-results", "history")),
                          key=lambda p: p["tokens"])
                big["tokens"] += gap
                big["gap_note"] = f"含 {gap:+d} tok 的估算边界差"

        total = sum(p["tokens"] for p in parts)
        # breakdown 的合计必须严格等于 context_tokens()，否则面板显示的数字
        # 和真正发出去的对不上——那就又变成「面板在骗人」。
        # est_tokens 对拼接边界敏感（同样的内容拼在不同位置会差几个 token），
        # 所以这里直接以 context_tokens() 为准，把差量并入 messages 部分。
        return {
            "parts": parts,
            "total": total,
            "system_tokens": self.system_tokens,
            "tools_tokens": self.tools_tokens,
            "message_tokens": total - self.system_tokens - self.tools_tokens,
            "turns": self.n,
            "model": self.env.get("ZHIHU_LLM_MODEL") or "",
        }

    def reset(self) -> None:
        self.history.clear()
        self.blocks.clear()
        self.folded.clear()
        self.seen_sigs.clear()
        self.n = 0

    def restore_history(self, history: list[dict]) -> int:
        """恢复持久化的会话历史（user/assistant/tool 消息）。

        **只恢复 history，不重建 blocks/folded**：那些是这一进程的折叠账本，
        旧进程的折叠状态不该带过来——恢复后的工具结果都以原文形式在 history
        里，下一轮重新按 age 折叠即可。

        返回恢复的消息数。调用方负责在 init 后、首条 chat 前调用。
        """
        restored = 0
        for m in history or []:
            if not isinstance(m, dict):
                continue
            role = m.get("role")
            if role not in ("user", "assistant", "tool"):
                continue
            item = {"role": role, "content": str(m.get("content") or "")}
            if role == "assistant" and m.get("reasoning"):
                item["reasoning"] = str(m["reasoning"])
            if role == "tool" and m.get("tool_call_id"):
                item["tool_call_id"] = str(m["tool_call_id"])
            if role == "assistant" and m.get("tool_calls"):
                # 工具调用必须原样带回，否则下一轮 tool 结果的 tool_call_id
                # 找不到对应请求，API 会报 400
                tcs = []
                for tc in m["tool_calls"]:
                    if not isinstance(tc, dict):
                        continue
                    fn = tc.get("function") or {}
                    tcs.append({"id": str(tc.get("id") or ""), "type": "function",
                                "function": {"name": str(fn.get("name") or ""),
                                             "arguments": str(fn.get("arguments") or "{}")}})
                if tcs:
                    item["tool_calls"] = tcs
            self.history.append(item)
            restored += 1
        return restored


# ============================================================ 命令读取
def _reader(commands, stop_flag) -> None:
    """读 stdin 的线程。

    必须在独立线程里读：主线程跑 chat 时是阻塞的（一次 LLM 调用几十秒），
    同一个线程读不到「停止」指令——那正好是用户最想按的时候。

    **必须用 readline()，不能用 `for line in sys.stdin`**：
    后者走 TextIOWrapper 的预读缓冲，在进程退出时会和主线程抢 stdin 的锁，
    实测表现为「读线程启动后主线程再也不输出任何东西」——不是死锁，
    是 stdout 被拖住了，父进程看到的就是「一个字都不给」。
    readline() 每次只取一行，不触发预读。
    """
    while True:
        try:
            line = sys.stdin.readline()
        except (ValueError, OSError):
            break
        if not line:            # EOF
            break
        line = line.strip()
        if not line:
            continue
        try:
            cmd = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(cmd, dict) and cmd.get("action") == "stop":
            # 停止不走队列：队列要等主线程空闲才被消费，
            # 而主线程正在跑 LLM——那时「停止」必须能被立刻看见。
            stop_flag.set()
            ChatSession.emit({"type": "stopping"})
            continue
        commands.put(cmd)
    commands.put(None)         # 哨兵：stdin 关闭


# ============================================================ 主循环
def main() -> int:
    import queue
    import threading

    # **必须自己重开无缓冲 stdout**：Python 的 stdout 接到管道时默认是全缓冲，
    # 父进程 spawn 出来会一个字都收不到（实测 init 直接超时）。
    # 启动参数带 -u 能解决，但这里自己兜一层——引擎被别的宿主调用时
    # 不该依赖调用方记得加 -u。
    try:
        sys.stdout.reconfigure(line_buffering=True, write_through=True)
        sys.stderr.reconfigure(line_buffering=True, write_through=True)
    except (AttributeError, ValueError):
        pass

    session: ChatSession | None = None
    commands: queue.Queue = queue.Queue()
    stop_flag = threading.Event()

    t = threading.Thread(target=_reader, args=(commands, stop_flag), daemon=True)
    t.start()

    while True:
        cmd = commands.get()          # 阻塞等，不忙等
        if cmd is None:
            break

        action = cmd.get("action")

        if action == "init":
            root = Path(cmd.get("root") or CODEB)
            try:
                session = ChatSession(
                    root=root,
                    repo=cmd.get("repo") or "codeb",
                    tree_depth=int(cmd.get("tree_depth") or 3),
                    route_specs=cmd.get("route_specs") or [],
                    files=cmd.get("files") or [],
                    custom=cmd.get("custom") or [],
                    model=cmd.get("model") or "",
                    cot=bool(cmd.get("cot")),
                )
                # 恢复历史：持久化会话重连时把之前的 user/assistant/tool 消息
                # 原样带回。必须在 init 之后、首条 chat 之前。
                n_restored = 0
                if cmd.get("history"):
                    n_restored = session.restore_history(cmd["history"])
            except Exception as e:  # noqa: BLE001
                ChatSession.emit({"type": "error",
                                  "message": f"初始化失败：{e}"})
                continue
            ChatSession.emit({
                "type": "init_ok",
                "repo": session.repo,
                "model": session.env.get("ZHIHU_LLM_MODEL"),
                "cot": session.cot,
                "history_restored": n_restored,
                "context_tokens": session.context_tokens(),
                "system_tokens": session.system_tokens,
                "tools_tokens": session.tools_tokens,
                "sections": session.assembler.summary(),
                "breakdown": session.context_breakdown(),
                "raw": session.context_raw(),
            })

        elif action == "chat":
            if session is None:
                ChatSession.emit({"type": "error", "message": "会话未初始化"})
                continue
            stop_flag.clear()          # 新一轮：清掉上一轮的停止标记
            session.chat(str(cmd.get("message") or ""), stop_flag)

        elif action == "model":
            if session is None:
                ChatSession.emit({"type": "error", "message": "会话未初始化"})
                continue
            ChatSession.emit({"type": "model_ok",
                              "model": session.set_model(str(cmd.get("model") or ""))})

        elif action == "cot":
            # 会话已初始化后切换思考链：不改上下文，只翻转后续调用的开关。
            # 不重建会话，否则历史与折叠账本全丢。
            if session is None:
                ChatSession.emit({"type": "cot_ok", "cot": False})
            else:
                session.cot = bool(cmd.get("cot"))
                ChatSession.emit({"type": "cot_ok", "cot": session.cot})

        elif action == "reset":
            if session is not None:
                session.reset()
            ChatSession.emit({"type": "reset_ok"})

        elif action == "context":
            if session is None:
                ChatSession.emit({"type": "error", "message": "会话未初始化"})
                continue
            ChatSession.emit({"type": "context",
                              "sections": session.assembler.summary(),
                              "system_tokens": session.system_tokens,
                              "tools_tokens": session.tools_tokens,
                              "total_tokens": session.context_tokens(),
                              # breakdown 是「真正要发出去的 payload 解剖」，
                              # 前端上下文面板用它；sections 保留给老调用方
                              "breakdown": session.context_breakdown(),
                              # raw 是逐条原样的 messages 数组，供「原始态」展示
                              "raw": session.context_raw()})

        elif action == "history":
            # 给持久化用：导出当前 LLM history（含 tool_call_id），
            # 前端在每轮 done 后拉取并随会话一起落盘。恢复时原样灌回，
            # 否则 assistant 的 tool_calls 和 tool 结果对不上号，下一轮 API 会 400。
            if session is None:
                ChatSession.emit({"type": "history", "history": []})
            else:
                ChatSession.emit({"type": "history",
                                  "history": [dict(m) for m in session.history]})

        elif action == "ping":
            ChatSession.emit({"type": "pong"})

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
