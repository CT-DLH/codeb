"""从源码提取符号树。

提取器默认用 LLM：
  llm   —— 把整份源码交给模型，让它输出节点清单（name/kind/line/parent/doc/group）。
           模型能认出正则认不出的东西：多行装饰器、动态生成的符号、嵌套函数与闭包、
           运行时才出现的属性，以及「这个函数实际是给谁用的」这种语义判断。
  regex —— 保留为离线/无 LLM 时的退化路径（--extractor regex）。

为什么 LLM 提取之后还要回源码核实一次：
  实测模型会写出源码里根本不存在的符号——kb.py 的 `_compiled_ignore`、
  semantic_blocks.py 的 `_purpose_max`、sessions.py 的 `decode_cli`，
  三者在各自源码里出现次数均为 0。树上一个不存在的函数，
  会让整份文档失去可信度，而这种错误人眼极难发现。
  所以：**节点由模型决定，但每个名字都要回源码确认它真的存在**。
  核实不是二次提取，只是确认这个字符串在文件里出现过——它不判断结构，
  不否决模型的分组和层级，只拦「凭空出现的名字」。

不维护行号：
  模型给的行号经常错位，而维护它需要在每次改名后重新对齐，成本高、收益低。
  查具体实现时用名字搜源码即可（`find` 给出文件路径，编辑器里一跳就到）。
  所以 Schema 里不问 line，库里也不存——不留一个会悄悄变错的字段。
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Sym:
    name: str
    kind: str = "function"   # function/class/method/property/constant/interface/type/file
    parent: str = ""         # 父符号名（空 = 顶层）
    children: list["Sym"] = field(default_factory=list)
    doc: str = ""
    group: str = ""


SCHEMA_GROUPS_ONLY = {
    "type": "object",
    "properties": {
        "groups": {
            "type": "array",
            "description": "按职责分的组，顺序即推荐阅读顺序",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "组名，8 字以内"},
                    "summary": {"type": "string", "description": "这组共同负责什么，20 字以内"},
                    "members": {"type": "array", "items": {"type": "string"},
                                "description": "该组包含的符号名，与给定清单逐字一致"},
                },
                "required": ["name", "summary", "members"],
            },
        },
    },
    "required": ["groups"],
}

SCHEMA_DOCS_ONLY = {
    "type": "object",
    "properties": {
        "nodes": {
            "type": "array",
            "description": "为给定的每个符号各返回一条说明",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "符号名，逐字照抄"},
                    "doc": {"type": "string", "description": "一句话说明，20 字以内"},
                },
                "required": ["name", "doc"],
            },
        },
    },
    "required": ["nodes"],
}

SCHEMA_TREE = {
    "type": "object",
    "properties": {
        "groups": {
            "type": "array",
            "description": "先分组：把这些符号按职责切开，顺序即推荐阅读顺序。每组 2-12 个符号",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "组名，8 字以内，如「kb 只读调用」"},
                    "summary": {"type": "string", "description": "这组共同负责什么，20 字以内"},
                    "members": {"type": "array", "items": {"type": "string"},
                                "description": "该组包含的符号名，必须与源码逐字一致"},
                },
                "required": ["name", "summary", "members"],
            },
        },
        "nodes": {
            "type": "array",
            "description": "文件里所有值得记录的符号，按源码出现顺序排列",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string",
                             "description": "符号名，必须与源码里的写法逐字一致"},
                    "kind": {"type": "string",
                             "enum": ["function", "class", "method", "property",
                                      "constant", "interface", "type", "variable"],
                             "description": "符号类型"},
                    "parent": {"type": "string",
                               "description": "所属类的名字；顶层符号留空字符串"},
                    "doc": {"type": "string",
                            "description": "一句话说明它为什么存在、给谁用，20 字以内"},
                    "group": {"type": "string",
                              "description": "所属组名，必须与 groups 里某个 name 完全一致，不许留空"},
                },
                "required": ["name", "kind", "doc", "group"],
            },
        },
    },
    "required": ["groups", "nodes"],
}


def build_groups_only_prompt(rel: str, names: list[str], file_doc: str = "") -> str:
    """第一阶段：只看符号名做分组。

    单独做分组而不是和写说明合并，是因为实测合并时模型会把
    40 多个符号塞进 3 个组——它的注意力被写说明占满了，
    分组这种「全局结构」判断就退化成敷衍的两三刀。
    只给名字让它分，它才会认真按职责切（kb.py 从 3 组变成 6 组）。
    """
    n = len(names)
    if n <= 5:
        lo, hi = 1, 2
    elif n <= 12:
        lo, hi = 2, 4
    elif n <= 25:
        lo, hi = 3, 6
    elif n <= 45:
        lo, hi = 4, 7
    else:
        lo, hi = 5, 9
    return f"""下面是一个代码文件里的全部符号名（{n} 个）。文件作用：{file_doc or '（未生成）'}

{chr(10).join(names)}

请按**职责**把它们分组，顺序即推荐阅读顺序。

要求：
- 分成 {lo}-{hi} 组。这是按符号数量算出来的合理区间，请落在区间内。
  全塞进一两组等于没分组，读者看不出层次。
- 组名 8 字以内，**必须概括本文件里这些符号的具体职责**。
  按「这组符号一起完成什么」命名，例如「符号提取」「提示词构造」「降级调用」。
  不要用与本文件无关的通用标签——组名会进数据库被人按文件检索，
  一个不贴切的组名比没有分组更误导。
- 划分依据是**职责**：读写同一类资源的归一组，处理同一流程相邻阶段的归一组，
  对外暴露的入口归一组。不要按字母序、不要按函数/常量类型切。
- members 必须与给的符号名逐字一致，不许改名、不许发明清单外的名字。
- 每个符号必须且只能出现在一组里，一个都不能漏。数一遍再返回。
- 实在无法归类的，放进最后一个「其它」组。"""


def build_docs_prompt(rel: str, group_name: str, group_summary: str,
                      names: list[str], text: str, max_chars: int = 60_000) -> str:
    """第二阶段：为某一组的符号写说明，附上整份源码（不是片段）。

    给整份源码而不是按符号切片：模型只有看到函数体才知道它真做什么，
    而切片在嵌套结构里经常切错，反而误导。
    """
    body = text if len(text) <= max_chars else text[:max_chars]
    return f"""文件 {rel} 中属于「{group_name}」这组的符号（{group_summary}）。

请为每个符号写一句话说明，**20 字以内**：
- 说清它**为什么存在、给谁用**，不要复述实现细节
  （「返回规范化路径」好，「调用 strip 再正则替换」差）。
- 硬性限制 20 字：这一行要贴在函数名后面显示，超了就折断。
  宁可写「校验路径合法」也不要写「校验输入路径是否合法并返回规范化后的绝对路径」。
- 看不出用途就写「用途不明」，不要编。

要写说明的符号：
{chr(10).join('- ' + n for n in names)}

源码（供参考）：
```
{body}
```

返回 JSON：nodes 数组，每项含 name（逐字照抄上面的符号名）和 doc。"""


def build_tree_prompt(rel: str, text: str, file_doc: str = "",
                      max_chars: int = 200_000) -> str:
    body = text
    note = ""
    if len(text) > max_chars:
        # 超大文件才截断，且明确告知被截断的位置，避免模型对后半段凭空猜测
        body = text[:max_chars]
        note = (f"\n\n[注意：源码超过 {max_chars} 字符，这里只给了前 {max_chars} 字符。"
                f"你只能依据这部分内容回答，不要为看不到的部分编造符号。]")
    return f"""请阅读下面这个文件的完整源码，输出它的符号结构和功能分组。

文件：{rel}
已知文件作用：{file_doc or '（未生成）'}

先分组，再填每个符号：

1. groups —— 按**职责**把文件切开，顺序即推荐阅读顺序。
   - 组数按文件规模定：符号 10-20 个用 3-4 组，20-40 个用 4-6 组，40 个以上用 5-8 组。
     组数太少（全塞进一两组）等于没分组，让读者看不出层次。
   - 组名 8 字以内，要具体：写「kb 只读调用」「LLM 后端」「素材加载」「CLI 入口」这种，
     不要写「工具函数」「其它函数」这种废话。
   - 组的划分依据是**职责和调用关系**：都在解析环境变量和发 HTTP 的归一组；
     都在读写知识库页面的归一组；命令行入口归一组。不要按字母序或类型（函数/常量）切。
   - members 列出该组包含的符号名，必须与源码里的写法逐字一致。

2. nodes —— 文件里**所有**值得记录的符号，按源码出现顺序排列。
   - 包括私有符号（下划线开头）、类的方法、模块级常量、接口/类型、嵌套定义。
     它们往往是理解文件的关键，不要因为「不重要」而省略。
   - **只写本文件定义的东西**。下面这些绝对不是符号，写就会被丢弃：
     import/require 语句（`import os`、`from pathlib import Path`）、
     函数调用（`print`、`len`、`sys.path.insert`）、循环变量（`for k, v in ...`）、
     代码片段或表达式（`s['calls']`、`f-string` 里的插值占位）、
     字面量（`74`、`=`、`块`）、被 import 进来的名字、`if __name__ == "__main__":`。
   - name 只写标识符本身：不要带参数签名（写 `call_llm` 不写 `call_llm(prompt, mode)`），
     不要带赋值（写 `MIN_COST` 不写 `MIN_COST = 3`），
     不要带类名前缀（方法用 parent 表达归属，不要写 `Class.method`）。
   - name 必须与源码里的写法**逐字一致**。不要美化、不要改名、不要合并重载。
     源码里没有的符号绝对不要写——每个名字都会被回源码核对，写错会被丢弃。
   - kind 从给定枚举里选。类的属性用 property，字典/列表形式的模块级配置用 constant。
     普通模块级变量用 variable。不确定时用 function。
   - parent 只在符号定义在某个类内部时填类名（方法、类属性），其余留空字符串。
     只填一层，不要写 "A.B" 这种路径。
   - doc 一句话说清它**为什么存在、给谁用**，25 字以内。不要复述实现细节
     （「返回规范化路径」好，「调用 strip 再正则替换」差）。看不出用途就写「用途不明」。
   - group 必须等于 groups 里某个 name，**不许留空、不许自造**。

一致性要求（很重要）：groups[i].members 里列出的符号，
恰好就是 node.group == groups[i].name 的那些 node。两种写法必须对得上，
不要只在 members 里列几个、却把几十个 node 都归到同一组。

源码：
```
{body}
```{note}"""


def normalize_name(raw: str) -> tuple[str, str]:
    """把模型给的名字规范化成 (name, parent)。

    模型经常不按「纯名字」返回，实测三种常见写法：
      `call_llm(prompt, mode, verbose, schema)`  —— 带完整签名
      `SessionLog.append`                        —— 类名.方法
      `DEFAULT_DIR = Path("_kbwork/agent-logs")` —— 常量连同赋值
    这些名字本身是**真实存在的符号**，但整串拿去源码里搜索必然找不到
    （distill.py 曾因此把 call_llm / cand_s1 / covered 等 40 多个真函数全部误丢）。
    所以先剥壳再核实，剥完仍找不到才算编造。
    """
    s = str(raw or "").strip()
    if not s:
        return "", ""
    s = s.split("  #")[0].strip()          # 去掉行尾注释
    # 直接照抄了整行定义：`def get_enc(name: str):` / `async def f()` / `class C:`
    # 实测 tokenstat.py 的 17 个符号全被写成这种形式，剥不掉就全被当成编造。
    m = re.match(r"^(?:async\s+)?(?:def|class|function)\s+([A-Za-z_$][\w$]*)", s)
    if m:
        return m.group(1), ""
    # `NAME = value` 或 `NAME: T = value` → NAME
    m = re.match(r"^([A-Za-z_$][\w$]*)\s*(?::[^=]*)?=", s)
    if m and "==" not in s.split("=")[0]:
        s = m.group(1)
    # `name(args)` → name
    m = re.match(r"^([A-Za-z_$][\w$]*)\s*\(", s)
    if m:
        s = m.group(1)
    # `Class.method` → parent=Class, name=method
    parent = ""
    if re.fullmatch(r"[A-Za-z_$][\w$]*(\.[A-Za-z_$][\w$]*)+", s):
        parts = s.split(".")
        parent, s = parts[-2], parts[-1]
    return s, parent


# 判断「这一行是否在定义一个符号」。核实只做两件事：
#   ① 字符串在源码里出现过（挡编造）
#   ② 它以「定义形态」出现（挡把 import、表达式、循环变量当成符号）
# 第二件事必须做：`import os`、`for label, task in TASKS`、`74`、`=`、`块`
# 这些字符串确实存在于源码，只查 ① 会让它们全部通过。
# 实测跑完整仓库时，distill.py 的 19 个节点里有 8 个是 import 语句，
# run_tasks.py 的 24 个节点里几乎全是循环变量和字面量片段。
_DEF_PATTERNS = [
    # def f(...) / async def f(...)
    r"^\s*(?:async\s+)?def\s+{N}\s*\(",
    # class C / class C(...) / class C:
    r"^\s*class\s+{N}\b",
    # NAME = ... / NAME: T = ...（模块级或类级赋值）
    r"^\s*{N}\s*(?::[^=\n]+)?=",
    # export const NAME / const NAME = / let NAME / var NAME
    r"^\s*(?:export\s+)?(?:default\s+)?(?:const|let|var)\s+{N}\b",
    # function NAME / async function NAME
    r"^\s*(?:export\s+)?(?:default\s+)?(?:async\s+)?function\s+{N}\b",
    # interface NAME / type NAME = / enum NAME
    r"^\s*(?:export\s+)?(?:interface|type|enum)\s+{N}\b",
    # 类的属性声明：  name: T;  /  private name: T;
    r"^\s*(?:public|private|protected|static|readonly)?\s*{N}\s*[?!]?\s*:",
    # PowerShell: function Name
    r"^\s*function\s+{N}\b",
    # 类方法简写（TS）：  name(args) {   —— 必须带修饰符，
    # 否则缩进的函数调用 `print(...)`、列表元素 `Path(...)` 都会被当成方法。
    r"^\s{2,}(?:public|private|protected|static|async|readonly|get|set)\s+{N}\s*\(",
]


def looks_like_definition(text: str, name: str) -> bool:
    """名字是否以「定义」形态出现在源码里。

    刻意偏严：宁可漏一个真符号，也不要把 import、表达式片段放上树。
    漏掉的代价是树里少一行；放错的代价是读者照着树去找 `块`、`74`、`=`。
    """
    esc = re.escape(name)
    pats = [re.compile(p.replace("{N}", esc)) for p in _DEF_PATTERNS]
    for ln in text.splitlines():
        if not ln.strip():
            continue
        # 排除 import / from import：它们不是本文件定义的符号
        st = ln.lstrip()
        if st.startswith(("import ", "from ", "#", "//", "/*", "*")):
            continue
        for p in pats:
            if p.match(ln):
                return True
    return False


VALID_KINDS = {"function", "class", "method", "property", "constant",
               "interface", "type", "variable", "file"}


def coerce_kind(raw: str) -> str:
    """把模型给的 kind 收进合法枚举。

    模型会自造 `regex`、`dataclass`、`module`、`field` 这类值，
    而 enum 约束在部分后端并不强制执行。非法 kind 会让渲染时
    的「函数加 ()」判断失效，也让按 kind 统计失去意义。
    """
    k = str(raw or "").strip().lower()
    if k in VALID_KINDS:
        return k
    if any(x in k for x in ("class", "dataclass", "struct", "record")):
        return "class"
    if "interface" in k or "protocol" in k:
        return "interface"
    if "type" in k or "alias" in k or "typedef" in k:
        return "type"
    if any(x in k for x in ("prop", "attr", "field")):
        return "property"
    if any(x in k for x in ("const", "regex", "literal", "config")):
        return "constant"
    if "var" in k or "global" in k:
        return "variable"
    if "method" in k:
        return "method"
    return "function"


def parse_tree_response(res: dict, text: str,
                        rel: str = "") -> tuple[list[Sym], list[dict], list[str]]:
    """把模型返回的扁平 nodes 还原成树，并逐个回源码核实。

    返回 (顶层符号列表, 分组列表, 被丢弃的名字)。
    被丢弃 = 源码里找不到这个名字。这是唯一会否决模型的地方。
    """
    dropped: list[str] = []
    raw_nodes = [n for n in ((res or {}).get("nodes") or []) if isinstance(n, dict)]
    src = text

    verified: list[Sym] = []
    seen: set[tuple[str, str]] = set()
    for n in raw_nodes:
        raw_name = str(n.get("name", "") or "").strip()
        if not raw_name:
            continue
        name, derived_parent = normalize_name(raw_name)
        if not name:
            continue
        # 剥壳后再核实。两级验证：
        #   ① 名字在源码里出现（挡完全编造的名字）
        #   ② 它以定义形态出现（挡 import、循环变量、字面量片段）
        # 只做 ① 时，`import os`、`74`、`=`、`块` 全都会通过——它们确实在源码里。
        if not re.search(r"\b" + re.escape(name) + r"\b", src):
            dropped.append(raw_name)      # 编造
            continue
        if not looks_like_definition(src, name):
            dropped.append(raw_name)      # 存在但不是定义
            continue
        parent = str(n.get("parent", "") or "").strip() or derived_parent
        key = (parent, name)
        if key in seen:
            continue
        seen.add(key)
        verified.append(Sym(
            name=name,
            kind=coerce_kind(str(n.get("kind", "") or "")),
            parent=parent,
            doc=str(n.get("doc", "") or "").strip(),
            group=str(n.get("group", "") or "").strip(),
        ))

    # 还原层级：parent 只在同文件内解析；父不存在就降级为顶层，
    # 而不是丢掉这个节点（丢节点比层级错更难发现）
    by_name: dict[str, Sym] = {}
    for s in verified:
        by_name.setdefault(s.name, s)
    tops: list[Sym] = []
    for s in verified:
        if s.parent and s.parent in by_name and s.parent != s.name:
            p = by_name[s.parent]
            if s not in p.children:
                p.children.append(s)
        else:
            s.parent = ""
            tops.append(s)

    groups = []
    for g in ((res or {}).get("groups") or []):
        if not isinstance(g, dict):
            continue
        gn = str(g.get("name", "") or "").strip()
        if gn:
            groups.append({"name": gn, "summary": str(g.get("summary", "") or "").strip(),
                           "members": [str(m).strip() for m in (g.get("members") or [])
                                       if str(m).strip()]})

    # 补全分组：两种来源都可能缺。
    #   ① node.group 有值（最可靠，直接采信）
    #   ② 否则从 groups[].members 反查——实测模型常把分组信息只写进 members，
    #      把每个 node 的 group 留空，只认 ① 会因为「组里找不到成员」整组被丢弃。
    from_members: dict[str, str] = {}
    for g in groups:
        for m in g["members"]:
            from_members.setdefault(m, g["name"])
    for s in verified:
        if not s.group:
            s.group = from_members.get(s.name, "")

    # 若模型连 groups 都没给，用 node.group 出现顺序补一份
    if not groups:
        seen_g: dict[str, str] = {}
        for s in verified:
            if s.group:
                seen_g.setdefault(s.group, "")
        groups = [{"name": k, "summary": v, "members": []} for k, v in seen_g.items()]
    return tops, groups, dropped


def flatten_text(syms: list[Sym], depth: int = 0) -> list[tuple[int, Sym]]:
    out: list[tuple[int, Sym]] = []
    for s in syms:
        out.append((depth, s))
        if s.children:
            out.extend(flatten_text(s.children, depth + 1))
    return out


# --------------------------------------------------------------------------
# 以下为 --extractor regex 的退化路径：离线、或不想花 LLM 调用时使用。
# 它认不出多行装饰器、动态符号和嵌套定义，只作为兜底，不再是默认路径。
# --------------------------------------------------------------------------

PATTERNS: dict[str, list[tuple[str, str]]] = {
    "py": [
        ("class", r"^\s*class\s+([A-Za-z_]\w*)\s*[\(:]"),
        ("function", r"^\s*(?:async\s+)?def\s+([A-Za-z_]\w*)\s*\("),
        ("constant", r"^(_*[A-Z][A-Z0-9_]{2,})\s*(?::[^=]+)?="),
    ],
    "ts": [
        ("class", r"^\s*(?:export\s+)?(?:default\s+)?(?:abstract\s+)?class\s+([A-Za-z_$][\w$]*)"),
        ("interface", r"^\s*(?:export\s+)?interface\s+([A-Za-z_$][\w$]*)"),
        ("type", r"^\s*(?:export\s+)?type\s+([A-Za-z_$][\w$]*)\s*="),
        ("function", r"^\s*(?:export\s+)?(?:default\s+)?(?:async\s+)?function\s+([A-Za-z_$][\w$]*)"),
        ("function", r"^\s*(?:export\s+)?const\s+([A-Za-z_$][\w$]*)\s*(?::[^=]+)?=\s*(?:async\s*)?\("),
        ("constant", r"^\s*(?:export\s+)?const\s+([A-Z][A-Z0-9_]{2,})\s*(?::[^=]+)?="),
    ],
    "mjs": [
        ("class", r"^\s*(?:export\s+)?(?:default\s+)?class\s+([A-Za-z_$][\w$]*)"),
        ("function", r"^\s*(?:export\s+)?(?:async\s+)?function\s+([A-Za-z_$][\w$]*)"),
        ("function", r"^\s*(?:export\s+)?const\s+([A-Za-z_$][\w$]*)\s*=\s*(?:async\s*)?\("),
        ("constant", r"^\s*const\s+([A-Z][A-Z0-9_]{2,})\s*="),
    ],
    "ps1": [
        ("function", r"^\s*function\s+([A-Za-z_][\w-]*)"),
    ],
}

METHOD_PATTERNS = {
    "py": r"^\s+(?:async\s+)?def\s+([A-Za-z_]\w*)\s*\(",
    "ts": r"^\s{2,}(?:public\s+|private\s+|protected\s+|static\s+|async\s+|get\s+|set\s+)*([A-Za-z_$][\w$]*)\s*\(",
    "mjs": r"^\s{2,}(?:static\s+|async\s+|get\s+|set\s+)*([A-Za-z_$][\w$]*)\s*\(",
}

NOT_METHODS = {
    "if", "for", "while", "switch", "catch", "return", "function", "constructor",
    "else", "try", "do", "with", "super", "this", "new", "await", "typeof",
}


def _lang(rel: str) -> str:
    ext = Path(rel).suffix.lower().lstrip(".")
    return {"py": "py", "ts": "ts", "tsx": "ts", "js": "ts", "jsx": "ts",
            "mjs": "mjs", "cjs": "mjs", "ps1": "ps1"}.get(ext, "")


def extract_symbols_regex(rel: str, text: str) -> list[Sym]:
    lang = _lang(rel)
    if not lang:
        return []
    pats = PATTERNS.get(lang, [])
    mpat = METHOD_PATTERNS.get(lang)
    lines = text.splitlines()

    syms: list[Sym] = []
    seen: set[str] = set()
    cur_class: Sym | None = None
    class_indent = -1

    def _doc(line_no: int) -> str:
        return ""

    for i, ln in enumerate(lines, 1):
        if not ln.strip() or ln.lstrip().startswith(("#", "//", "/*", "*")):
            continue
        indent = len(ln) - len(ln.lstrip())
        if cur_class is not None and indent <= class_indent:
            cur_class = None

        if indent == 0 or cur_class is None:
            matched_top = False
            for kind, pat in pats:
                m = re.match(pat, ln)
                if not m:
                    continue
                name = m.group(1)
                matched_top = True
                if name in seen:
                    break
                seen.add(name)
                s = Sym(name=name, kind=kind)
                if kind == "class":
                    cur_class, class_indent = s, indent
                syms.append(s)
                break
            if matched_top:
                continue

        if cur_class is None or mpat is None:
            continue
        if indent > class_indent:
            m = re.match(mpat, ln)
            if m:
                name = m.group(1)
                if name in NOT_METHODS or name in seen:
                    continue
                seen.add(name)
                kind = "method"
                j = i - 2
                while j >= 0 and not lines[j].strip():
                    j -= 1
                if j >= 0 and lines[j].strip().startswith("@property"):
                    kind = "property"
                cur_class.children.append(
                    Sym(name=name, kind=kind, parent=cur_class.name))
    return syms


def dumps_groups(groups: list[dict]) -> str:
    return json.dumps(groups, ensure_ascii=False)
