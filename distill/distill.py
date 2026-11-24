#!/usr/bin/env python3
"""distill.py —— 会话素材 → 可落库的知识候选。

流水线（四段，前三段不需要模型）：

    sense  sessions.py 的素材（探索成本 / 纠正 / 失败 / 已落库）
    gate   阈值 + kb where 现算去重：已被覆盖的路径不再建议新建页
    draft  生成**预填好参数的 kb upsert 命令**；有 LLM 时由 LLM 写正文，
           没有 LLM 时给出带证据的结构骨架（人/在场 agent 只需补正文）
    commit 默认 dry-run 不落盘；--apply 才真的调 kb.py upsert

为什么默认不出正文：知识库的硬门槛是「读代码看不出来 / 对未来有用 / 改它的人必须知道」
（DESIGN.md）。摘要器最典型的退化是把"在 A 和 B 间选 A，因为 B 会撞上 X"压成
"选了 A"——被否掉的形态才是值钱的部分。所以 LLM 只被要求填 `rejected_alternative`
与 `why_not_obvious`，写不出这两项的候选直接丢弃，而不是硬凑一段总结。

后端选择（--llm）：
  nvidia     默认。读 infohub/collector/.env 的 ZHIHU_LLM_*，用 NVIDIA 端点，
             并自动传 chat_template_kwargs.enable_thinking=false
             （推理型 Nemotron 不关 thinking 会返回空 content）
  openai     同一实现，只是 env 可指向别家 base_url
  none       纯规则，只出骨架与命令
  cmd        外部命令：用临时文件传提示词与结果
             （避免 Windows 沙箱下 piped stdio 永久阻塞）

用法：
    python distill/sessions.py material --cwd codeb -o _kbwork/materials.jsonl
    python distill/distill.py --materials _kbwork/materials.jsonl \
        -o _kbwork/candidates.jsonl --report _kbwork/candidates.md
    python distill/distill.py --materials ... --only S1 --apply --id 3,7
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
import time
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent          # 知识库根（含 repo/）
KB = ROOT / "kb.py"

MIN_COST = 3               # 单文件探索成本门槛（S1）：3 次及以上读写才算"付过费"
MAX_CANDIDATES = 25

CJK = re.compile(r"[\u4e00-\u9fff]")


# ---------------------------------------------------------------- kb 只读调用

_TMP = Path(tempfile.mkdtemp(prefix="kbdistill_"))
_SEQ = [0]
_COVER_CACHE: dict[tuple[str, str], list[dict]] = {}


def _tmpout() -> Path:
    _SEQ[0] += 1
    return _TMP / f"out{_SEQ[0]}.json"


def run_kb(argv: list[str], timeout: int = 60) -> tuple[int, str, str]:
    """跑 kb.py 并拿到 (返回码, stdout, stderr)。

    Windows 沙箱坑（实测）：`subprocess.run(capture_output=True)` 走 piped stdio
    会 EPERM 阻塞——不是报错，是永远不返回，直到被 kill。
    所以这里一律把 stdout/stderr 重定向到临时文件再读，**不碰管道**。
    """
    out = _tmpout()
    err = out.with_suffix(".err")
    cmd = [sys.executable, str(KB), "--json"] + [str(a) for a in argv]
    try:
        with open(out, "wb") as fo, open(err, "wb") as fe:
            rc = subprocess.run(cmd, cwd=str(ROOT), stdout=fo, stderr=fe,
                                timeout=timeout).returncode
    except subprocess.TimeoutExpired:
        return 124, "", "timeout"
    text = out.read_text(encoding="utf-8", errors="replace") if out.exists() else ""
    etext = err.read_text(encoding="utf-8", errors="replace") if err.exists() else ""
    return rc, text, etext


def kb_json(argv: list[str], timeout: int = 60) -> dict | None:
    rc, out, _ = run_kb(argv, timeout)
    if rc != 0:
        return None
    try:
        return json.loads(out)
    except Exception:
        return None


def kb_alive(repo: str) -> bool:
    """自检：kb 调用到底通不通。

    不通就必须响亮地报错。`covered()` 的失败模式是"返回空"，
    而空 = "没有任何页面覆盖"，会让所有已覆盖的路径被误判成新知识，
    静默产出大量重复页——比崩溃更糟。
    """
    res = kb_json(["tree", "--repo", repo])
    return bool(res and res.get("items"))


def covered(repo: str, rel_path: str) -> list[dict]:
    """kb where：这个路径已经被哪些页覆盖。

    缓存：13 个会话 × 几十个路径 = 几百次 subprocess，不缓存会慢到不能用。
    知识库在一次蒸馏里不会变（我们不写它），所以缓存是安全的。
    """
    key = (repo, rel_path)
    if key not in _COVER_CACHE:
        res = kb_json(["where", rel_path, "--repo", repo]) or {}
        _COVER_CACHE[key] = res.get("hits") or []
    return _COVER_CACHE[key]


def merge_target(hits_by_path: dict[str, list[dict]]) -> str | None:
    """出现频次最高的页作为并入对象：同一条候选的证据若已散落在某页，就不该另起一页。"""
    cnt: dict[str, int] = {}
    for hits in hits_by_path.values():
        for h in hits:
            if h.get("cover", "").endswith("/"):      # 前缀覆盖 = 目录级页，更可能是归属
                cnt[h["rel"]] = cnt.get(h["rel"], 0) + 2
            else:
                cnt[h["rel"]] = cnt.get(h["rel"], 0) + 1
    if not cnt:
        return None
    best = max(cnt.items(), key=lambda kv: kv[1])
    return best[0] if best[1] >= 2 else None


def page_titles(repo: str) -> dict[str, str]:
    """repo 下已有页：rel -> title。`kb tree --json` 返回扁平 items（不是目录树对象）。"""
    tree = kb_json(["tree", "--repo", repo]) or {}
    return {i.get("rel", ""): i.get("title", "") for i in tree.get("items") or []}


def suggest_page(repo: str, texts: list[str]) -> str | None:
    """用 kb search 找"这条知识最该并进哪一页"。

    非 S1 的候选（纠正、死路、约束）几乎都该挂在已有页上：
    新建平铺页会让 tree 变长、让"该信哪页"更难判断（见 design/writing-pages 的
    「否定发现不单独开页」）。这一步把最贵的归属判断做掉，
    上层只需确认。取词：搜证据里最长的两个中文片段，命中率比整句高。
    """
    terms = []
    for t in texts:
        for frag in re.split(r"[，。；、,.!?！？\s]+", t or ""):
            if len(frag) >= 4:
                terms.append(frag[:12])
        if len(terms) >= 4:
            break
    hits: dict[str, int] = {}
    for term in terms[:4]:
        res = kb_json(["search", term, "--repo", repo]) or {}
        for h in res.get("hits") or []:
            rel = h.get("rel")
            if rel:
                hits[rel] = hits.get(rel, 0) + 1
    if not hits:
        return None
    return max(hits.items(), key=lambda kv: (kv[1], kv[0]))[0]


# ---------------------------------------------------------------- 素材

def load_materials(p: Path) -> list[dict]:
    mats = []
    for line in p.read_text(encoding="utf-8-sig").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            m = json.loads(line)
        except Exception:
            continue
        if m.get("kind") == "session_material":
            mats.append(m)
    mats.sort(key=lambda m: m.get("created") or "")
    return mats


UUID_RE = re.compile(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", re.I)


def short_id(sid: str) -> str:
    m = UUID_RE.search(sid or "")
    return m.group(0)[:8] if m else (sid or "")[:8]


def title_from(paths: list[str], limit: int = 3) -> str:
    """英文标题：内核 slugify 对中文会退化成 page-<hash>，所以标题必须给英文。"""
    names = []
    for p in paths[:limit]:
        n = p.rsplit("/", 1)[-1]
        n = re.sub(r"\.(md|py|ts|tsx|js|json|yml)$", "", n)
        if n not in names:
            names.append(n)
    return " / ".join(names) if names else "session notes"


# ---------------------------------------------------------------- 信号 → 候选

def cand_s1(mats: list[dict]) -> list[dict]:
    """S1 已付费的探索且 kb where miss：本工具的核心信号。

    实测教训：门槛只看 cost，不看"跨了几个回合"。同一回合内反复读同一个文件
    同样是付了费的探索（13 个会话里几乎所有 hot 路径都发生在单回合内），
    加 turns>=2 会把 S1 直接清空。
    """
    out = []
    for m in mats:
        for rrepo, items in (m.get("exploration") or {}).items():
            if rrepo == "external":
                continue                      # 仓库外的绝对路径不配当 covers
            hot = [i for i in items if i.get("cost", 0) >= MIN_COST]
            if not hot:
                continue
            uncov, hits_by_path = [], {}
            for i in hot:
                h = covered(rrepo, i["path"])
                if h:
                    hits_by_path[i["path"]] = h
                else:
                    uncov.append(i)
            if not uncov:
                continue                      # 全都已被覆盖：没有新知识，不硬凑一页
            paths = [i["path"] for i in uncov]
            out.append({
                "signal": "S1",
                "repo": rrepo,
                "kind": "understanding",
                "title_en": title_from(paths),
                "topic": (paths[0].split("/")[0] if "/" in paths[0] else None),
                "covers": paths,
                "target_page": merge_target(hits_by_path),
                "bar": (f"该会话为这 {len(paths)} 个文件付了 "
                        f"{sum(i['cost'] for i in uncov)} 次探索成本，"
                        f"而 kb where 显示没有任何页面覆盖它们——知识只在当时的上下文里"),
                "evidence": [f"{i['path']} 成本{i['cost']} / {i['turns']}回合" for i in uncov],
                "session": m["session_id"], "short": short_id(m["session_id"]),
                "created": m.get("created"),
                "questions": [
                    "这些文件合起来承担什么职责（一句话，读代码看不出来的那种）？",
                    "当时在两种理解之间选了哪一种，为什么？（rejected_alternative）",
                    "哪个不变量如果被破坏，不会立刻报错、但会让功能悄悄退化？",
                ],
            })
    return out


def cand_s3(mats: list[dict]) -> list[dict]:
    """S3 死路：失败过且不是瞬时抖动的，值得记"别这么干"。"""
    out = []
    for m in mats:
        repo = m.get("cwd_repo") or "?"
        groups: dict[str, int] = {}
        samples: dict[str, str] = {}
        for f in m.get("failures") or []:
            key = re.sub(r"\d+", "N", (f.get("excerpt") or "")[:60])
            groups[key] = groups.get(key, 0) + 1
            samples.setdefault(key, f.get("excerpt") or "")
        worth = [(k, n) for k, n in groups.items() if n >= 2 and "timed out" not in k]
        if not worth:
            continue
        out.append({
            "signal": "S3",
            "repo": repo,
            "kind": "dead-end",
            "title_en": f"dead-end {short_id(m['session_id'])}",
            "topic": "defects",
            "covers": [],
            "target_page": suggest_page(repo, [samples[k] for k, _ in worth]),
            "bar": f"同一失败在该会话里出现多次，说明不是抖动：" +
                   "; ".join(f"×{n}" for _, n in worth[:3]),
            "evidence": [samples[k][:200] for k, _ in worth[:5]],
            "session": m["session_id"], "created": m.get("created"),
            "questions": [
                "这条失败的真正原因是什么（不是错误信息本身）？",
                "正确的做法是什么？如果已经找到，应写进哪一页的"
                "「不要做什么」节而不是单独开页？",
            ],
        })
    return out


def cand_s2(mats: list[dict]) -> list[dict]:
    """S2 用户纠正：代码里永远读不出来的那类知识。

    **必须带源码证据**。踩过的坑：只给 LLM 用户原话，它会拿"这类项目通常怎么实现"
    去补，产出 `collector/entry.py::start_collection()` 这类根本不存在的模块
    （实测 9 个模块名全不存在）。所以这里把该会话真实读过的源码片段一起递进去，
    让模型有东西可核对，而不是有空间可发挥。
    """
    out = []
    for m in mats:
        repo = m.get("cwd_repo") or "?"
        cs = m.get("corrections") or []
        if not cs:
            continue
        # 该会话真实探索过的文件（已过滤知识页与已消失路径）→ 作为可核对的锚点
        anchors = [i["path"] for items in (m.get("exploration") or {}).values()
                   for i in items][:8]
        out.append({
            "signal": "S2",
            "repo": repo,
            "kind": "constraint",
            "title_en": f"user-constraint {short_id(m['session_id'])}",
            "topic": "invariants",
            "covers": anchors,
            "target_page": suggest_page(repo, [c["excerpt"] for c in cs]),
            "bar": f"该会话出现 {len(cs)} 处用户纠正——这类知识只存在于对话里，"
                   f"不写就永久丢失",
            "evidence": [c["excerpt"][:220] for c in cs[:6]],
            "anchors": anchors,
            "session": m["session_id"], "created": m.get("created"),
            "questions": [
                "这条纠正约束的是**写入规则**、**内容规则**还是**流程**？",
                "它应该并进哪一页的哪一节（先 kb heads，别新建页）？",
                "违反它的后果是静默失败还是立刻报错？（决定要不要进冒烟测试）",
            ],
        })
    return out


def cand_s7(mats: list[dict]) -> list[dict]:
    """S7 未落库的高投入会话：**审计线索，不是可落库的候选**。

    它只回答"哪些会话值得人回头看"，从不预测内容，因此 draft_ready 恒为 False。
    把它算作知识候选是错误用法——它没有 covers（仓库外的绝对路径不配当 covers），
    也没有可验证的判断。
    """
    out = []
    for m in mats:
        if m.get("kb_writes"):
            continue
        buckets = {k: v for k, v in (m.get("exploration") or {}).items()
                   if k != "external"}
        total = sum(i.get("cost", 0) for items in buckets.values() for i in items)
        if total < 20:
            continue
        repo = m.get("cwd_repo") or "?"
        paths = [i["path"] for items in buckets.values() for i in items][:6]
        out.append({
            "signal": "S7",
            "repo": repo,
            "kind": "audit",
            "title_en": f"unwritten {short_id(m['session_id'])}",
            "topic": None,
            "covers": paths,
            "draft_ready": False,
            "bar": f"{m.get('turns', 0)} 回合、探索成本合计 {total}、"
                   f"一次都没调用 kb upsert",
            "evidence": paths,
            "session": m["session_id"], "short": short_id(m["session_id"]),
            "created": m.get("created"),
            "questions": ["这个会话整体在解决什么问题？产出是否已被别的会话落库了？"],
        })
    return out


# ---------------------------------------------------------------- 第五道闸门：事实核对

# 正文里形如 `foo/bar.py`、`a/b.py::func`、`scripts/x.py` 的标识符
IDENT_RE = re.compile(r"`([A-Za-z0-9_./-]+\.(?:py|ts|tsx|js|mjs|cjs|json|yml|yaml|md|toml))"
                      r"(?:::[A-Za-z0-9_]+)?`")

# 常见的"编造高发"词：出现即要求有对应真实文件兜底
REPO_ROOTS = {
    "codeb": [ROOT],
    "infohub": [Path(r"D:\work\project\infohub")],
}


def repo_root(repo: str) -> Path | None:
    for p in REPO_ROOTS.get(repo, []):
        if p.is_dir():
            return p
    return None


def verify_facts(c: dict, max_missing: int = 0) -> list[str]:
    """核对正文里提到的每个文件路径是否真实存在。

    为什么必须有这道：实测 LLM 给一个 collector 子系统描述时，写出了
    `collector/entry.py::start_collection()`、`states.py`、`retry.py`、
    `circuit_breaker.py`、`plugin_manager.py::load_plugins()` 等 9 个模块，
    **一个都不存在**。它把"这类项目通常怎么实现"当成了"这个项目就是这样"。
    那种页面一旦进库，未来的读者会照着它去改不存在的文件。

    返回缺失列表；空列表 = 通过。只核对路径，不核对符号名（符号要解析 AST，
    成本远大于收益），但路径假的页面已经足够值得拦。
    """
    root = repo_root(c["repo"])
    if root is None:
        return ["没有该仓库的根目录，无法核对（按失败处理）"]
    text = c.get("draft_body") or ""
    seen, missing = set(), []
    for m in IDENT_RE.finditer(text):
        rel = m.group(1).strip()
        if rel in seen:
            continue
        seen.add(rel)
        if rel.startswith("./"):
            rel = rel[2:]
        cand = root / rel
        if cand.is_file():
            continue
        # 允许只写文件名：只要仓库里存在同名文件就算对上
        if (root / "collector" / rel).is_file() or any(root.glob(f"**/{Path(rel).name}")):
            continue
        missing.append(rel)
    if len(missing) > max_missing:
        return missing
    return []


# ---------------------------------------------------------------- 第六道闸门：内容实质
#
# 第五道（事实核对）能抓住"编造具体路径"，但抓不住"看起来完整其实是空壳"。
# 实测：两条通过事实闸门的候选，正文分别是
#   `[工具文件名 5]` … `[工具文件名 24]`（一整页占位）
#   `概念 A` / `[页面名称](/path/to/page)`（模板填空）
# 它们没编造任何路径，所以事实闸门放行了；但写进库比缺页更糟。
# 模型在证据不足时的默认行为就是"把模板填满"，这里必须显式拦。

SHELL_RE = re.compile(
    r"(\[[^\]]*(?:工具文件名|页面名称|简要功能描述|具体参数|概念 [A-Z]|待补|TODO|TBD|"
    r"填写|占位)[^\]]*\]"
    r"|/path/to/|\.\.\.$|用于\.\.\.|^-\s*\*\*[^*]+\*\*:\s*项目中特有的)"
    , re.M)


def substance_ok(c: dict) -> list[str]:
    """返回"空壳"证据列表；空列表 = 通过。

    判据都来自实测反例，不看文风只看有没有实质：
    1. 占位符方括号 / `/path/to/`
    2. 连续两行以 `...` 或"用于..."结束（模板填空的典型形状）
    3. 同一小标题重复 ≥3 次且内容结构完全一致（批量占位）
    """
    body = c.get("draft_body") or ""
    bad = []
    hits = SHELL_RE.findall(body)
    if hits:
        bad.append(f"占位符 {len(hits)} 处，如 {hits[0][:40]!r}")
    # 重复骨架：把每行去掉具体词后统计形状，形状重复过高即为模板
    lines = [ln.strip() for ln in body.splitlines() if ln.strip()]
    shapes = Counter()
    for ln in lines:
        shape = re.sub(r"[A-Za-z0-9_./-]+", "X", ln)
        shape = re.sub(r"[\u4e00-\u9fff]+", "中", shape)
        shapes[shape] += 1
    if lines:
        top, n = shapes.most_common(1)[0]
        if n >= 4 and n / len(lines) > 0.35:
            bad.append(f"重复骨架 {n}/{len(lines)} 行同形，如 {top[:50]!r}")
    # 只有标题没有正文
    if len(re.sub(r"\s", "", body)) < 120:
        bad.append(f"正文过短（{len(body)} 字）")
    return bad


# ---------------------------------------------------------------- 骨架与草案

SCHEMA = {
    "type": "object",
    "required": ["title_zh", "why_not_obvious", "rejected_alternative", "body_md"],
    "properties": {
        "title_zh": {"type": "string", "description": "中文页标题"},
        "title_en": {"type": "string", "description": "英文文件名 slug，短横线"},
        "topic": {"type": "string", "description": "折叠到的英文子目录"},
        "why_not_obvious": {"type": "string", "description": "为什么读代码看不出来"},
        "rejected_alternative": {"type": "string",
                                 "description": "当时考虑过但被否掉的形态；没有就写 NONE"},
        "body_md": {"type": "string", "description": "中文正文，不含 frontmatter"},
    },
}


def skeleton(c: dict) -> str:
    """无 LLM 时的正文骨架：把证据摆到位，让在场 agent 只需补判断。"""
    L = [f"# {c.get('title_zh') or c['title_en']}", ""]
    L.append("<!-- 由 distill.py 生成的骨架。证据是机械提取的，判断需要你补。 -->")
    L.append("")
    L.append("## 值得写的理由")
    L.append(c["bar"])
    L.append("")
    L.append("## 证据")
    for e in c["evidence"][:8]:
        L.append(f"- {e}")
    L.append("")
    L.append("## 待补（缺这些就别落库）")
    for q in c["questions"]:
        L.append(f"- [ ] {q}")
    if c["signal"] != "S1":
        L.append("")
        L.append("<!-- 非 S1 候选：优先考虑 kb upsert --page <已有页> --section ... 并进已有页，"
                 "不要新建平铺页。 -->")
    return "\n".join(L) + "\n"


PROMPT = """你在为代码知识库产出候选页面。读者是后续会话的 AI 模型，它不会去读源码。

必须同时满足三条件才写：读代码看不出来 / 对未来的读者有用 / 改这段代码的人必须知道。
宁缺毋滥：噪音页比缺页更糟，因为读者不知道信哪个。

会话素材的机械统计（信号 {signal}，仓库 {repo}）：
{evidence}

原始会话上下文片段（可能不全，事件被折叠过）：
{context}

请输出 JSON，字段见 schema。body_md 用中文。

**最重要的一条规则**：正文里不准出现任何你没在证据里见过的文件路径、模块名或函数名。
不要写"通常会有某某模块"、"建议在 x/y.py 中实现"这类话——读者会以为它已经存在。
如果你不知道某个细节，就不要写它；宁可只写两段确定的，也不要补成完整架构。
（实测反面教材：给一个采集子系统写描述时编出了 9 个模块名，仓库里一个都没有。）

其他约束：不要写行数、文件数、卡片数这类会随提交漂移的数字。不要贴源码。
正文里出现的每个文件路径都会被程序在磁盘上核对，核不到就整条作废。"""


def call_llm(prompt: str, mode: str, verbose: bool = False,
             schema: dict | None = None) -> dict | None:
    if mode == "none":
        return None
    if mode == "cmd":
        return _llm_cmd(prompt)
    return _llm_openai(prompt, verbose=verbose, schema=schema)  # nvidia / openai 同一实现


def _llm_cmd(prompt: str) -> dict | None:
    """外部命令后端：用临时文件传 stdin/stdout，绕开沙箱对 piped stdio 的限制。"""
    cmd = os.environ.get("KB_DISTILL_CMD")
    if not cmd:
        return None
    tin = Path(tempfile.mkdtemp()) / "prompt.md"
    tout = tin.with_name("out.json")
    tin.write_text(prompt, encoding="utf-8")
    try:
        subprocess.run(f'{cmd} "{tin}" "{tout}"' if "{tin}" not in cmd
                       else cmd.replace("{tin}", str(tin)).replace("{tout}", str(tout)),
                       shell=True, check=True, timeout=600,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return json.loads(tout.read_text(encoding="utf-8-sig"))
    except Exception:
        return None


# ---------------------------------------------------------------- LLM 后端
#
# 与 infohub 的 collector/llm/extract.py 保持同一套约定，因为那是本机唯一
# 已被验证可用的配置（同一个 NVIDIA 账号、同一个模型）。三处必须一致：
#   1) env 名：ZHIHU_LLM_API_KEY / ZHIHU_LLM_BASE_URL / ZHIHU_LLM_MODEL
#   2) 默认值：integrate.api.nvidia.com/v1 + nemotron
#   3) NVIDIA 专属参数 chat_template_kwargs.enable_thinking=false
#      —— 推理型 Nemotron 会先吐 reasoning_content 把 max_tokens 吃光，
#         content 变成空串。这不是可选优化，是能不能拿到结果的前提。

# infohub 的 .env 是这套配置的真源（它已被 infohub/.gitignore 排除）。
ENV_CANDIDATES = [
    Path(r"D:\work\project\infohub\collector\.env"),
    ROOT.parent / "infohub" / "collector" / ".env",
]

NVIDIA_BASE = "https://integrate.api.nvidia.com/v1"
NVIDIA_MODEL = "nvidia/nemotron-3.5-super-vl-120b-a12b"
# 0 = 不传 max_tokens，由服务端取模型上限。
# 原先固定 4096，对「一次返回几十个符号的 JSON」明显不够：
# 超限时不报错，只返回空或截断，表现和「模型没返回」完全一样，
# 之前几次「连续返回空」很可能就是这个原因。
DEFAULT_MAX_TOKENS = 0


def load_env(verbose: bool = False) -> dict[str, str]:
    """读 env：先看真实环境变量，再补 infohub 的 .env。

    只取 ZHIHU_LLM_*：那个 .env 里还有 BILI_COOKIE / XHS_COOKIE 等凭据，
    整文件加载会把无关密钥带进本进程。
    """
    out: dict[str, str] = {}
    for k in ("ZHIHU_LLM_API_KEY", "ZHIHU_LLM_BASE_URL", "ZHIHU_LLM_MODEL",
              "ZHIHU_LLM_MAX_TOKENS", "LLM_DISABLE_THINKING"):
        v = os.environ.get(k)
        if v:
            out[k] = v.strip()
    if out.get("ZHIHU_LLM_API_KEY"):
        return out
    for p in ENV_CANDIDATES:
        if not p.is_file():
            continue
        try:
            # utf-8-sig：Windows 上手工编辑的 .env 常带 BOM，strip 掉才认得出键名
            text = p.read_text(encoding="utf-8-sig", errors="replace")
        except Exception:
            continue
        for line in text.splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            k = k.strip()
            if k.startswith("ZHIHU_LLM_") or k == "LLM_DISABLE_THINKING":
                out.setdefault(k, v.strip().strip('"').strip("'"))
        if out.get("ZHIHU_LLM_API_KEY"):
            if verbose:
                print(f"llm: 使用 {p} 中的配置（model={out.get('ZHIHU_LLM_MODEL')}）")
            break
    return out


def _extra_body(base: str, env: dict) -> dict:
    """推理型模型要关掉 thinking，否则 content 为空。

    与 infohub 一致：只在 base_url 指向 nvidia 且未显式禁用时加。
    """
    if "nvidia.com" in base and not env.get("LLM_DISABLE_THINKING"):
        return {"chat_template_kwargs": {"enable_thinking": False}}
    return {}


def _post(url: str, payload: dict, key: str, timeout: int) -> tuple[int, dict]:
    """裸 HTTP POST，返回 (status, json)。4xx 不抛，交给调用方决定是否降级。"""
    import urllib.error
    import urllib.request
    req = urllib.request.Request(
        url, data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json",
                 "Accept": "application/json",
                 "Authorization": f"Bearer {key}"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, json.loads(r.read().decode("utf-8", "replace"))
    except urllib.error.HTTPError as e:
        body = ""
        try:
            body = e.read().decode("utf-8", "replace")
        except Exception:
            pass
        return e.code, {"error": body or str(e)}
    except Exception as e:
        return 0, {"error": str(e)}


def _content_of(data: dict) -> tuple[str, str]:
    """取出正文，并说明为什么是空的（reasoning 吃满 token 是最常见的坑）。"""
    try:
        choice = (data.get("choices") or [{}])[0]
        msg = choice.get("message") or {}
    except Exception:
        return "", "bad shape"
    content = (msg.get("content") or "").strip()
    if content:
        return content, ""
    reasoning = (msg.get("reasoning_content") or "").strip()
    finish = choice.get("finish_reason")
    if reasoning and finish == "length":
        return "", "reasoning 吃满了 max_tokens（应设 enable_thinking=false）"
    return "", f"empty content (finish_reason={finish})"


def _format_rejected(status: int, err: str) -> bool:
    """只有"服务端不认识 response_format"才降级；超时/网络错误应当重试。"""
    if status not in (400, 404, 422):
        return False
    low = (err or "").lower()
    return any(t in low for t in ("response_format", "json_schema", "unsupported",
                                  "not supported", "unknown field"))


def _llm_openai(prompt: str, verbose: bool = False,
                schema: dict | None = None) -> dict | None:
    env = load_env(verbose)
    key = env.get("ZHIHU_LLM_API_KEY")
    if not key:
        if verbose:
            print("llm: 没有 ZHIHU_LLM_API_KEY（环境变量和 infohub/.env 都没有）")
        return None
    base = (env.get("ZHIHU_LLM_BASE_URL") or NVIDIA_BASE).rstrip("/")
    model = env.get("ZHIHU_LLM_MODEL") or NVIDIA_MODEL
    max_tokens = int(env.get("ZHIHU_LLM_MAX_TOKENS") or DEFAULT_MAX_TOKENS)
    url = f"{base}/chat/completions"
    extra = _extra_body(base, env)

    sys_msg = ("你是代码知识库的编辑。只输出 JSON 对象，不要 markdown 代码围栏，"
               "不要任何解释性前缀。")
    # 三级降级：json_schema → json_object → 纯文本抠 JSON。
    # NVIDIA 端点对 json_schema 的支持不稳定，所以按实际报错降级而不是预先猜。
    attempts = [
        {"type": "json_schema",
         "json_schema": {"name": "kb_candidate", "strict": False,
                         "schema": schema or SCHEMA}},
        {"type": "json_object"},
        None,
    ]
    last_err = ""
    for rf in attempts:
        payload = {
            "model": model,
            "messages": [{"role": "system", "content": sys_msg},
                         {"role": "user", "content": prompt}],
            "temperature": 0,
            **extra,
        }
        # 0 表示不限：不传这个字段，让服务端用模型自身的输出上限。
        # 传一个很大的数字反而可能被端点拒绝。
        if max_tokens > 0:
            payload["max_tokens"] = max_tokens
        if rf:
            payload["response_format"] = rf
        for backoff in (0, 5, 10):
            if backoff:
                time.sleep(backoff)        # 429 退避，与 infohub 一致
            status, data = _post(url, payload, key, timeout=180)
            if status == 429:
                last_err = "429 rate limited"
                continue
            if status != 200:
                err = str(data.get("error", ""))[:300]
                last_err = f"HTTP {status}: {err}"
                if _format_rejected(status, err):
                    break                  # 换下一级 response_format
                if verbose:
                    print(f"llm: {last_err}")
                return None
            content, why = _content_of(data)
            if not content:
                last_err = why
                if verbose:
                    print(f"llm: {why}")
                break
            m = re.search(r"\{.*\}", content, re.S)
            if not m:
                last_err = "no JSON in content"
                break
            try:
                return json.loads(m.group(0))
            except Exception as e:
                last_err = f"bad JSON: {e}"
                break
    if verbose:
        print(f"llm: 全部尝试失败（{last_err}）")
    return None


def enrich(c: dict, mats_by_id: dict[str, dict], mode: str, verbose: bool = False) -> dict:
    """有 LLM 时补正文；没有就保留骨架。丢弃不合格草案。"""
    if mode == "none":
        c["draft_body"] = skeleton(c)
        c["drafted_by"] = "skeleton"
        c["draft_ready"] = False
        return c
    m = mats_by_id.get(c["session"], {})
    ctx = []
    for key in ("corrections", "claims", "failures"):
        for it in (m.get(key) or [])[:4]:
            ctx.append(f"[{key}] {it.get('excerpt','')}")
    draft = call_llm(
        PROMPT.format(signal=c["signal"], repo=c["repo"],
                      evidence="\n".join(f"- {e}" for e in c["evidence"][:10]),
                      context="\n".join(ctx)[:4000]),
        mode, verbose)
    if not draft:
        c["draft_body"] = skeleton(c)
        c["drafted_by"] = "skeleton(llm failed)"
        c["draft_ready"] = False
        return c
    # 门槛：写不出"为什么不是显而易见"与"被否掉的形态"的候选不予采用
    why = (draft.get("why_not_obvious") or "").strip()
    rej = (draft.get("rejected_alternative") or "").strip()
    body = (draft.get("body_md") or "").strip()
    if len(why) < 8 or not rej or rej.upper() == "NONE" or len(body) < 80:
        c["draft_body"] = skeleton(c)
        c["drafted_by"] = "skeleton(rejected by bar)"
        c["draft_ready"] = False
        c["llm_reject"] = f"why={why[:60]!r} rejected={rej[:40]!r} body={len(body)}"
        return c
    c["title_zh"] = draft.get("title_zh") or c.get("title_zh")
    c["draft_body"] = body
    c["drafted_by"] = mode
    # 第五道闸门：正文里提到的文件必须真实存在。
    # 这一步放在 LLM 成功之后、任何落库之前。实测它能抓住"把通用架构
    # 当成这个项目实际结构"那类造假——正文读起来完全合格，路径全是编的。
    missing = verify_facts(c)
    if missing:
        c["draft_ready"] = False
        c["facts_unverified"] = missing
        c["drafted_by"] = f"{mode}(rejected: facts)"
        return c
    # 第六道闸门：内容实质。防"没编造路径但是空壳"——证据不足时模型的默认行为
    # 是把模板填满（实测出现 `[工具文件名 5]`…`[工具文件名 24]` 整页占位）。
    hollow = substance_ok(c)
    if hollow:
        c["draft_ready"] = False
        c["hollow"] = hollow
        c["drafted_by"] = f"{mode}(rejected: hollow)"
        return c
    # 审计线索（S7）永远不可落库：它只说明"这个会话值得人回头看"，
    # 不对应任何可验证的知识。LLM 能给它写出一段像模像样的正文，
    # 但这恰恰是最危险的情形——看起来合格的假知识。
    # 所以 draft_ready 由信号的 kind 决定，不让 LLM 的成功覆盖它。
    c["draft_ready"] = (c.get("kind") != "audit")
    if c.get("kind") == "audit":
        c["draft_ready_note"] = "审计线索：正文仅供人读，不可落库"
    return c


# ---------------------------------------------------------------- 可执行命令

def upsert_argv(c: dict) -> list[str]:
    """预填好的 kb upsert。标题必须英文（中文会让内核退化成 page-<hash> 文件名）。"""
    argv = ["upsert"]
    if c.get("target_page"):
        # 并进已有页：只追加一节，不重写整页（--replace 会丢掉未写进 body 的节）
        argv += [c["target_page"], "--append"]
    else:
        argv += ["--repo", c["repo"]]
        if c.get("topic"):
            argv += ["--topic", c["topic"]]
        argv += ["--title", c["title_en"]]
    if c["covers"]:
        argv += ["--covers"] + list(c["covers"])
    return [str(KB)] + argv


def write_bodies(cands: list[dict], outdir: Path) -> None:
    outdir.mkdir(parents=True, exist_ok=True)
    for c in cands:
        p = outdir / f"{c['signal']}-{c['repo']}-{re.sub(r'[^a-zA-Z0-9_-]','_',c['title_en'])[:40]}.md"
        p.write_bytes((c["draft_body"].replace("\r\n", "\n")).encode("utf-8"))
        c["body_file"] = str(p)


def render_md(cands: list[dict], mode: str) -> str:
    ready = [c for c in cands if c.get("draft_ready")]
    L = ["# 知识候选", "",
         f"候选 {len(cands)} 条，其中**可直接落库 {len(ready)} 条**（正文来源 `{mode}`）。",
         f"骨架类只能当线索：`draft_ready=false` 的候选被 --apply 拒绝，"
         f"必须有人或在场 agent 补完判断再落库——噪音页比缺页更糟。", ""]
    by_sig: dict[str, list] = {}
    for c in cands:
        by_sig.setdefault(c["signal"], []).append(c)
    for sig in sorted(by_sig):
        L.append(f"## {sig}（{len(by_sig[sig])} 条）")
        for c in by_sig[sig]:
            L.append(f"- **#{c['id']}** `{c['repo']}`"
                     + (f" / {c['topic']}" if c.get("topic") else "")
                     + f" — {c.get('title_zh') or c['title_en']}"
                     + ("  [可落库]" if c.get("draft_ready") else "  [骨架]")
                     + ("  [审计线索·不可落库]" if c["kind"] == "audit" else ""))
            L.append(f"    - 值得写：{c['bar']}")
            if c.get("target_page"):
                L.append(f"    - 建议并入已有页：`{c['target_page']}`（--append，不重写整页）")
            if c.get("llm_reject"):
                L.append(f"    - 被门槛拦下：{c['llm_reject']}")
            L.append(f"    - 正文：{c['drafted_by']}，{len(c['draft_body'])} 字 "
                     f"→ `{c.get('body_file','')}`")
            if c["kind"] == "audit":
                L.append("    - 这是审计线索，不对应一页知识：看会话本身决定要不要补，"
                         "**不要**照抄成 upsert 命令")
            else:
                L.append(f"    - 命令：`{' '.join(upsert_argv(c))} "
                         f"--body-file {c.get('body_file','...')}`")
            for q in c["questions"][:2]:
                L.append(f"    - 待答：{q}")
        L.append("")
    return "\n".join(L) + "\n"


# ---------------------------------------------------------------- apply

def apply_one(c: dict, force: bool = False) -> dict:
    """落盘：只走 kb upsert 这个唯一写入口，绝不直接写 md。

    骨架正文（含 `[待补]` 清单与生成注释）默认拒绝——它是线索，不是知识。
    真要把骨架也写进库，必须显式 --force，且只能写成 `--topic pending`，
    这样 kb tree 会把它折叠成一个独立子节点，而不是污染已有页。
    """
    if not c.get("draft_ready") and not force:
        return {"id": c["id"], "ok": False, "skipped": "draft_ready=false（骨架）"}
    clone = dict(c)
    if force and not c.get("draft_ready"):
        # 骨架不许并进真实页：转到 pending 主题下新建，[待补] 不会污染已有页，
        # 且在 kb tree 里自成一个折叠子节点，一眼能清。
        clone["target_page"] = None
        clone["topic"] = "pending"
    argv = upsert_argv(clone)[1:] + ["--body-file", clone["body_file"]]
    rc, out, _err = run_kb(argv, timeout=120)
    try:
        payload = json.loads(out)
    except Exception:
        payload = {"stdout": out[:400]}
    return {"id": c["id"], "ok": rc == 0, "argv": argv, "result": payload}


# ---------------------------------------------------------------- CLI

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="会话素材 → 知识候选")
    ap.add_argument("--materials", type=Path, required=True)
    ap.add_argument("-o", "--out", type=Path, default=None, help="候选 JSONL")
    ap.add_argument("--report", type=Path, default=None, help="人读报告 md")
    ap.add_argument("--bodies", type=Path, default=None, help="正文目录")
    ap.add_argument("--llm", choices=["none", "cmd", "openai", "nvidia"],
                    default="nvidia",
                    help="默认 nvidia：读 infohub/collector/.env 用同一套 NVIDIA 配置")
    ap.add_argument("--verbose", action="store_true", help="打印 LLM 失败原因")
    ap.add_argument("--only", default=None, help="只出这些信号，如 S1,S2")
    ap.add_argument("--max", type=int, default=MAX_CANDIDATES)
    ap.add_argument("--apply", action="store_true", help="真的落库（默认只预演）")
    ap.add_argument("--id", default=None, help="要落库的候选号，如 3,7")
    ap.add_argument("--force", action="store_true",
                    help="允许把骨架落进 pending 主题（默认拒绝）")
    args = ap.parse_args(argv)

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    mats = load_materials(args.materials)
    repos = sorted({m.get("cwd_repo") or "?" for m in mats if m.get("cwd_repo")})
    probe = repos[0] if repos else "codeb"
    if not kb_alive(probe):
        print(f"错误：kb 不可用（repo={probe}）。kb where 去重闸门无法生效，"
              f"继续跑会产出重复页。检查 {KB} 与 {ROOT}", file=sys.stderr)
        return 2
    by_id = {m["session_id"]: m for m in mats}
    sigs = {s.strip().upper() for s in args.only.split(",")} if args.only else None

    pool = []
    for fn in (cand_s1, cand_s2, cand_s3, cand_s7):
        rows = fn(mats)
        pool.extend(rows if not sigs else [r for r in rows if r["signal"] in sigs])

    # 去重 + 排序。两条规则，都是踩过的坑：
    #
    # 1) 去重键必须含 session：S2/S3 的 covers 是空的，只按 (repo, covers) 去重
    #    会让所有会话的 S2 共享同一个键而互相吞掉，最后只剩一条。
    # 2) 排序必须让"可落库的知识"排在"审计线索"前面，并按信号可信度排。
    #    曾经按 -len(covers) 排，结果是 covers 多但不可落库的 S7 挤满前排，
    #    而 covers 为空的 S2（用户纠正，价值最高）被 --max 直接截断——方向正好反了。
    SIG_RANK = {"S2": 0, "S1": 1, "S3": 2, "S7": 9}
    seen: set = set()
    dedup = []
    for c in sorted(pool, key=lambda x: (SIG_RANK.get(x["signal"], 8),
                                        x["kind"] == "audit",
                                        -len(x["covers"]))):
        k = (c["signal"], c["repo"], c.get("session"), tuple(sorted(c["covers"])))
        if k in seen:
            continue
        seen.add(k)
        dedup.append(c)
    # 配额：审计线索不许挤占可落库候选的名额
    budget = args.max
    real = [c for c in dedup if c["kind"] != "audit"]
    audit = [c for c in dedup if c["kind"] == "audit"]
    keep = real[:budget]
    if len(keep) < budget:
        keep += audit[:budget - len(keep)]
    dedup = keep

    for n, c in enumerate(dedup, 1):
        c["id"] = n
        c["title_zh"] = c.get("title_zh") or c["title_en"]
        enrich(c, by_id, args.llm, args.verbose)

    bodies = args.bodies or (args.report.parent / "bodies" if args.report
                             else HERE / "out" / "bodies")
    write_bodies(dedup, bodies)

    report = render_md(dedup, args.llm)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_bytes(report.replace("\r\n", "\n").encode("utf-8"))
        print(f"wrote {args.report}")
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_bytes("\n".join(json.dumps(c, ensure_ascii=False)
                                       for c in dedup).encode("utf-8"))
        print(f"wrote {args.out} ({len(dedup)} candidates)")
    else:
        print(report)

    if args.apply:
        ids = {int(x) for x in (args.id or "").split(",") if x.strip().isdigit()}
        targets = [c for c in dedup if not ids or c["id"] in ids]
        results = [apply_one(c, args.force) for c in targets]
        out = Path(os.environ.get("TEMP", ".")) / "kb_apply_results.json"
        out.write_bytes(json.dumps(results, ensure_ascii=False, indent=2).encode("utf-8"))
        ok = sum(1 for r in results if r["ok"])
        sk = sum(1 for r in results if r.get("skipped"))
        print(f"applied {ok}/{len(results)} (skipped {sk}); details: {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
