"""testtree：项目的**测试清单**。

一张表存「有什么测试」，一张表存「它证明什么」。**扫描碰不到说明，说明改不了结构。**

    test_suites   测试清单       ← scan 自动生成，程序唯一写者
    test_notes    每个测试的说明 ← 人 / agent 写，scan 永不触碰

为什么拆两张表：与 `projtree` 完全同一条理由。一张表里「覆盖结构」和
「保留说明」会打架——DELETE 重建就丢说明，UPSERT 保留就删不掉已废弃的测试。
拆开后：scan 可以整表重建，说明一行不动。

为什么和目录树共用一个库：`_kbwork/codeb-index.db` 已经是项目的派生索引
（project_files / file_notes / file_docs / doc_tree 都在这儿）。测试清单
是同一类东西——「项目的结构事实」——再开一个库只会让 `kb reindex` 的
口径分成两半。

用法：

    python -X utf8 distill/testtree.py scan                 # 重新清点
    python -X utf8 distill/testtree.py tree                 # 给专家看的清单
    python -X utf8 distill/testtree.py tree --run-after webview/chat_engine.py
    python -X utf8 distill/testtree.py set-note context-fix --proves "..."
    python -X utf8 distill/testtree.py stats

设计约束（每条都来自实测）：

1. **断言数是静态数的 `check()` 调用点，不是「跑过 N 条通过」**。
   两者不是一回事：循环里的 check 只算一个点，条件分支可能一条都不执行。
   把静态数当通过数报出去，就是「看起来有依据的错数字」——本项目最忌讳
   的错误形态。真通过数只能靠 `run` 之后解析输出得到。
2. **requires 从源码字面推断**（有没有 ZHIHU_LLM / 127.0.0.1 / 9333）。
   推断会错，所以它是个**提示**列，不是硬门禁；跑不动时专家该去读源码确认。
3. **扫描不判断「这个测试还有没有意义」**。它只如实登记存在的文件。
   判定废弃是人 / agent 的事，写进 `status`。
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sqlite3
import sys
import time
from pathlib import Path

CODEB = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(CODEB))


def db_path(root: Path | None = None) -> Path:
    """清单库固定放在本工具的 _kbwork 下，不跟着 --root 走。

    与 `projtree.db_path` 同一个理由：库属于工具，不属于被扫的仓库。
    """
    return (root or CODEB) / "_kbwork" / "codeb-index.db"


DDL = """
CREATE TABLE IF NOT EXISTS test_suites (
  repo         TEXT NOT NULL,
  suite_id     TEXT NOT NULL,      -- 稳定标识，从文件名推导（test_context_fix → context-fix）
  path         TEXT NOT NULL,      -- 相对仓库根，统一 / 分隔
  cmd          TEXT,               -- 完整可执行命令
  kind         TEXT,               -- unit / llm / e2e / browser / diag
  requires     TEXT,               -- JSON 数组：python / node / llm / server / chrome / agvenv
  n_checks     INTEGER,            -- **静态** check() 调用点数，不是通过数
  has_verdict  INTEGER,            -- 1 = 会打印 ALL PASS / 设置退出码，可自动判定
  status       TEXT NOT NULL DEFAULT 'active',  -- active / manual / scratch / retired
  run_after    TEXT,               -- JSON 数组：改了这些路径就该跑它
  timeout_s    INTEGER,
  content_hash TEXT,               -- 文件内容 sha256 前16位，变了说明清单描述可能过期
  doc          TEXT,               -- 文件自己的 docstring 首行（机器抓的，不是人写的）
  first_seen   TEXT NOT NULL,
  last_seen    TEXT NOT NULL,
  PRIMARY KEY (repo, suite_id)
);
CREATE INDEX IF NOT EXISTS idx_ts_kind   ON test_suites(repo, kind);
CREATE INDEX IF NOT EXISTS idx_ts_status ON test_suites(repo, status);

CREATE TABLE IF NOT EXISTS test_notes (
  repo        TEXT NOT NULL,
  suite_id    TEXT NOT NULL,
  proves      TEXT,                -- 这个测试**证明**什么（一句话，人写的）
  detail      TEXT,                -- 可选：怎么读失败、已知局限
  note_hash   TEXT,                -- 写说明时的 content_hash
  source      TEXT NOT NULL,       -- human / agent
  model       TEXT,
  updated_at  TEXT NOT NULL,
  PRIMARY KEY (repo, suite_id)
);

CREATE TABLE IF NOT EXISTS test_runs (
  repo      TEXT NOT NULL,
  suite_id  TEXT NOT NULL,
  ran_at    TEXT NOT NULL,
  ok        INTEGER,               -- 1 通过 / 0 失败 / NULL 跑不动
  exit_code INTEGER,
  elapsed_s REAL,
  passed    INTEGER,               -- 从输出里解析出的通过数（解析不出就是 NULL）
  failed    INTEGER,
  tail      TEXT                   -- 输出尾部，失败归因用
);
CREATE INDEX IF NOT EXISTS idx_tr_suite ON test_runs(repo, suite_id, ran_at);
"""

# 扫描哪些路径。**都在当前位置上，不搬**（用户明确要求脚本先留着）。
# 真回归套件：默认 active，进注入清单。
DISCOVER = [
    "_tmp/test_*.py", "_tmp/test_*.mjs", "_tmp/test_*.cjs",
    "_tmp/cdp_*.cjs",
    "mcp/smoke.ts",
    "tests/**/*.py", "tests/**/*.mjs", "tests/**/*.cjs", "tests/**/*.ts",
    "test_*.py",
]

# 一次性脚本：_tmp 下的 measure / diag / patch / probe / exp / mini 等。
# **也登记**（用户要「全部测试文件」），但 status=scratch，默认不进注入清单。
# 理由：它们不是回归套件，跑它们不证明任何东西还慢；但它们的存在本身是信息
# （「这个问题我查过，脚本在这」），删掉就丢了线索。
DISCOVER_SCRATCH = ["_tmp/*.py", "_tmp/*.mjs", "_tmp/*.cjs", "_tmp/*.ts"]

# 明确排除：依赖包、构建产物、Chrome 用户目录
SKIP_PARTS = {"node_modules", "dist", "build", ".git", "_kbwork", ".kbwork",
              "__pycache__", "cdp-profile", "cdp-profile2", "chrome-prof",
              "chrome-prof2", "agvenv"}


def open_db(root: Path | None = None) -> sqlite3.Connection:
    p = db_path(root)
    p.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(p))
    conn.executescript(DDL)
    conn.commit()
    return conn


def h16(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", errors="replace")).hexdigest()[:16]


# ------------------------------------------------------------------ 识别

def suite_id_of(rel: str) -> str:
    """从相对路径推出稳定 id。

    用文件名而不是序号：id 出现在笔记和报告里，人得能认出它是哪个测试。
    `test_context_fix.py` → `context-fix`；`mcp/smoke.ts` → `mcp-smoke`；
    `cdp_boot.cjs` → `cdp-boot`。
    """
    p = Path(rel)
    stem = p.stem
    if stem.startswith("test_"):
        stem = stem[5:]
    if rel.replace("\\", "/").startswith("mcp/"):
        return f"mcp-{stem}"
    return stem.replace("_", "-")


def interpreter_of(rel: str) -> str:
    if rel.endswith(".py"):
        return "python"
    if rel.endswith((".mjs", ".cjs", ".js", ".ts")):
        return "node"
    return ""


def cmd_of(rel: str) -> str:
    """该测试的标准运行命令。

    `-X utf8` 不是装饰：Windows 默认 GBK，输出里带中文时 print 会抛
    UnicodeEncodeError，测试本身就是中文输出（[PASS]/[FAIL] 后面接中文说明）。
    """
    if rel.endswith(".py"):
        return f"python -X utf8 {rel}"
    if rel.endswith((".mjs", ".cjs", ".js", ".ts")):
        return f"node {rel}"
    return ""


# 依赖探测。**字面匹配，宁多勿漏**：漏报会让专家以为能跑，
# 报了跑不动它看一眼就知道是探错了。反过来的代价更大。
#
# 但有两类误报必须挡住，否则清单会骗人（都实测踩过）：
#   1. 文件**名字**出现在字符串/注释里（`test_tools_fix.py` 里有
#      "codeb/webview/route_agent.py" 这个路径字面量，不等于它调了 LLM）
#   2. 纯正则/纯逻辑判断（`test_qclass.py` 只测 needs_fact_lookup）
# 所以 rx 只认**调用形态**，不认裸名字。
RX_LLM = re.compile(
    r"ZHIHU_LLM|"
    r"\bask_preset\s*\(|\bask_route\s*\(|\bask\s*\(\s*['\"]|"
    r"\bcall_llm\s*\(|\b_post_stream\s*\(|"
    r"route_agent\.ask|route_ask\.(?:ask|run)")
RX_SERVER = re.compile(r"127\.0\.0\.1|localhost|/api/|\bBASE\b")
RX_CHROME = re.compile(r"9333|Runtime\.evaluate|Page\.navigate|CDP_HTTP")
RX_AGENTS = re.compile(r"^\s*(?:from|import)\s+(?:agents|codeb_agent|context_cache|"
                       r"session_log)\b", re.M)
RX_CHECK = re.compile(r"\bcheck\(")
# .cjs/.mjs 不用 check()，用 fail++ / process.exit / 断言字样
RX_CHECK_JS = re.compile(r"\bfail\s*(\+\+|\+=)|console\.assert|assert\.|\bassert\(")
RX_VERDICT = re.compile(r"ALL PASS|\bFAILED\b|sys\.exit\(|process\.exit\(")


def detect_requires(rel: str, src: str) -> list[str]:
    req: list[str] = []
    it = interpreter_of(rel)
    if it:
        req.append(it)
    if RX_CHROME.search(src):
        req.append("chrome")
    # chrome 测试必然连一个页面，页面就是服务；不重复报
    if RX_SERVER.search(src) and "chrome" not in req:
        req.append("server")
    if RX_LLM.search(src):
        req.append("llm")
    if RX_AGENTS.search(src):
        req.append("agvenv")
    return req


def count_checks(rel: str, src: str) -> int:
    """静态数「有几个断言点」。

    **这是调用点数，不是通过数**。两者不是一回事：循环里一个 check() 跑 9 次，
    条件分支可能一次都不执行。把调用点数当通过数报出去，就是「看起来有依据的
    错数字」。真通过数只能 run 完解析输出。
    """
    n = len(RX_CHECK.findall(src))
    if rel.endswith((".cjs", ".mjs", ".js", ".ts")):
        n += len(RX_CHECK_JS.findall(src))
    return n


def detect_kind(rel: str, src: str) -> str:
    """粗分类。**它是给人快速定位用的，不是门禁。**"""
    if RX_CHROME.search(src):
        return "browser"
    if RX_SERVER.search(src):
        return "e2e"
    if RX_LLM.search(src):
        return "llm"
    if not count_checks(rel, src) and not RX_VERDICT.search(src):
        return "diag"
    return "unit"


def first_doc(rel: str, src: str) -> str:
    """取文件自己的第一行说明。**这是机器抄的，不是人写的**——
    所以它进 `test_suites.doc`，不进 `test_notes.proves`。"""
    if rel.endswith(".py"):
        import ast
        try:
            d = ast.get_docstring(ast.parse(src)) or ""
        except SyntaxError:
            return ""
        line = d.strip().splitlines()[0] if d.strip() else ""
        return line[:120]
    m = re.search(r"/\*\*(.+?)\*/", src, re.S) or re.search(r"^\s*//\s*(.+)", src, re.M)
    if m:
        line = m.group(1).strip().splitlines()[0]
        return line.lstrip("* ").strip()[:120]
    return ""


def discover(root: Path) -> tuple[list[tuple[str, str]], int]:
    """返回 ([(相对路径, 是否是 scratch)], 被跳过的 _kbwork 临时测试数)。

    scratch = 不是回归套件的一次性脚本。**登记但默认不进注入清单**。
    """
    seen: set[str] = set()
    out: list[tuple[str, str]] = []

    def _add(pat: str, scratch: bool) -> None:
        for p in root.glob(pat):
            if not p.is_file():
                continue
            rel = p.relative_to(root).as_posix()
            if any(seg in SKIP_PARTS for seg in rel.split("/")):
                continue
            if any(s in rel for s in ("cdp-profile", "chrome-prof")):
                continue
            if rel in seen:
                continue
            seen.add(rel)
            out.append((rel, "scratch" if scratch else "active"))

    for pat in DISCOVER:
        _add(pat, False)
    for pat in DISCOVER_SCRATCH:
        _add(pat, True)

    skipped = sum(1 for p in (root / "_kbwork").glob("test_*.py") if p.is_file())
    return sorted(out), skipped


# ------------------------------------------------------------------ 命令

def cmd_scan(root: Path, repo: str, quiet: bool = False) -> int:
    files, skipped = discover(root)
    if not files:
        print("没扫到任何测试文件", file=sys.stderr)
        return 2

    now = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    conn = open_db(root)

    prev = {r[0]: r[1] for r in
            conn.execute("SELECT suite_id, content_hash FROM test_suites WHERE repo=?",
                         (repo,))}
    added, changed, same = [], [], []
    rows = []
    for rel, default_status in files:
        try:
            src = (root / rel).read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        sid = suite_id_of(rel)
        ch = h16(src)
        req = detect_requires(rel, src)
        n_checks = count_checks(rel, src)
        has_verdict = 1 if RX_VERDICT.search(src) else 0
        rows.append({
            "sid": sid, "path": rel, "cmd": cmd_of(rel),
            "kind": detect_kind(rel, src),
            "requires": req,
            "n_checks": n_checks, "has_verdict": has_verdict,
            "content_hash": ch, "doc": first_doc(rel, src),
            "default_status": default_status,
            "timeout_s": 300 if ("llm" in req or "chrome" in req) else 120,
        })
        if sid not in prev:
            added.append(sid)
        elif prev[sid] != ch:
            changed.append(sid)
        else:
            same.append(sid)

    for r in rows:
        # status / run_after 是**声明**，scan 只在首次登记时给默认值，
        # 之后不覆盖人/agent 改过的值（否则每次 scan 都把判定刷回去）
        old = conn.execute(
            "SELECT status, run_after, first_seen FROM test_suites "
            "WHERE repo=? AND suite_id=?", (repo, r["sid"])).fetchone()
        status = old[0] if old else r["default_status"]
        run_after = old[1] if old else None
        first_seen = old[2] if old else now
        conn.execute(
            "INSERT INTO test_suites (repo, suite_id, path, cmd, kind, requires,"
            " n_checks, has_verdict, status, run_after, timeout_s, content_hash,"
            " doc, first_seen, last_seen)"
            " VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"
            " ON CONFLICT(repo, suite_id) DO UPDATE SET"
            "   path=excluded.path, cmd=excluded.cmd, kind=excluded.kind,"
            "   requires=excluded.requires, n_checks=excluded.n_checks,"
            "   has_verdict=excluded.has_verdict, timeout_s=excluded.timeout_s,"
            "   content_hash=excluded.content_hash, doc=excluded.doc,"
            "   last_seen=excluded.last_seen",
            (repo, r["sid"], r["path"], r["cmd"], r["kind"],
             json.dumps(r["requires"], ensure_ascii=False), r["n_checks"],
             r["has_verdict"], status, run_after, r["timeout_s"],
             r["content_hash"], r["doc"], first_seen, now))

    # 已消失的：删结构行，**笔记保留**（文件回来时说明还在）
    live = {r["sid"] for r in rows}
    gone = [s for s in prev if s not in live]
    for s in gone:
        conn.execute("DELETE FROM test_suites WHERE repo=? AND suite_id=?", (repo, s))
    conn.commit()

    if not quiet:
        n_active = sum(1 for r in rows if r["default_status"] == "active")
        print(f"扫描 {len(rows)} 个文件"
              f"（回归套件 {n_active} + 一次性脚本 {len(rows) - n_active}；"
              f"另跳过 _kbwork 临时测试 {skipped} 个）")
        print(f"  新增 {len(added)}   变化 {len(changed)}   未变 {len(same)}"
              f"   消失 {len(gone)}")
        for s in changed:
            print(f"    变化：{s}（说明可能已过期，用 set-note 复核）")
        for s in gone:
            print(f"    消失：{s}（结构行已删，笔记保留）")
        with_assert = sum(1 for r in rows if r["has_verdict"])
        print(f"  自动可判定（有退出码/ALL PASS）{with_assert} 个；"
              f"其余需人看输出")
    return 0


def render_tree(root: Path, repo: str, only: str | None = None,
                run_after: str | None = None) -> str:
    """渲染成给**测试专家**读的清单。这就是注入上下文的那段文本。

    默认只列 active（真回归套件）。一次性脚本登记在库里但不注入——
    注入它的成本是每轮都付的，而它一次也不该被跑。
    """
    conn = open_db(root)
    q = ("SELECT s.suite_id, s.path, s.kind, s.requires, s.n_checks,"
         " s.has_verdict, s.status, s.run_after, s.timeout_s, s.doc,"
         " n.proves, n.detail"
         " FROM test_suites s LEFT JOIN test_notes n"
         "   ON n.repo=s.repo AND n.suite_id=s.suite_id"
         " WHERE s.repo=?")
    args: list = [repo]
    if only:
        q += " AND s.status=?"
        args.append(only)
    else:
        q += " AND s.status != 'scratch'"
    q += " ORDER BY s.kind, s.suite_id"
    rows = conn.execute(q, args).fetchall()
    if not rows:
        return ("（测试清单为空：先跑 `python -X utf8 distill/testtree.py scan`）")

    n_scratch = conn.execute(
        "SELECT COUNT(*) FROM test_suites WHERE repo=? AND status='scratch'",
        (repo,)).fetchone()[0]

    lines = [f"# 测试清单：{repo}（{len(rows)} 个套件）", ""]
    lines.append("`n_checks` 是**静态数出来的断言点数**（check() 调用点、"
                 "js 的 fail++），不是通过数。真通过数只能跑完看输出。")
    lines.append("")
    lines.append("| id | 类型 | 需要 | n_checks | 证明什么 |")
    lines.append("| :-- | :-- | :-- | --: | :-- |")
    for (sid, path, kind, req, nck, verdict, status, ra, tmo,
         doc, proves, detail) in rows:
        need = ", ".join(json.loads(req or "[]")) or "—"
        text = proves or doc or "（未写说明）"
        flag = "" if status == "active" else f"〔{status}〕"
        lines.append(f"| `{sid}`{flag} | {kind} | {need} | {nck or 0} | {text} |")
    lines.append("")

    if run_after:
        norm = run_after.replace("\\", "/")
        hit = []
        for (sid, path, kind, req, nck, verdict, status, ra, tmo,
             doc, proves, detail) in rows:
            targets = json.loads(ra or "[]")
            if any(norm == t or norm.startswith(t.rstrip("/") + "/") for t in targets):
                hit.append(sid)
        lines.append(f"## 改了 `{norm}` 该跑")
        lines.append("")
        if hit:
            for s in hit:
                lines.append(f"- `{s}`")
        else:
            lines.append("（清单里没有登记跑它的套件。这是清单的缺口，"
                         "说明这个改动还没有测试覆盖——**如实报缺口，不要猜一个套件去跑**。）")
        lines.append("")
        return "\n".join(lines)

    # 反向索引：改动 → 套件。这是清单真正的价值所在。
    rev: dict[str, list[str]] = {}
    for (sid, path, kind, req, nck, verdict, status, ra, tmo,
         doc, proves, detail) in rows:
        for t in json.loads(ra or "[]"):
            rev.setdefault(t, []).append(sid)
    if rev:
        lines.append("## 改了这些路径 → 该跑哪些")
        lines.append("")
        lines.append("| 改动路径 | 套件 |")
        lines.append("| :-- | :-- |")
        for t in sorted(rev):
            lines.append(f"| `{t}` | " +
                         ", ".join(f"`{s}`" for s in rev[t]) + " |")
        lines.append("")

    lines.append("## 怎么用")
    lines.append("")
    lines.append("- 跑：run_suite(suite_id)。它用自己的 cmd 和 timeout，不用你拼命令。")
    lines.append("- 问你该跑哪些：给出改动的文件路径，下面 run_after 的反向索引会告诉你。")
    lines.append("- 清单里没有的套件**不要去猜**：报「缺口」，那本身就是有价值的结论。")
    if n_scratch:
        lines.append(f"- 另有 {n_scratch} 个一次性脚本（measure/diag/probe）已登记但"
                     "`status=scratch`，**默认不跑也不注入**：它们不是回归套件，"
                     "跑它们不证明任何东西。要查历史线索可以用 list_suites(status=\"scratch\")。")
    missing = [r[0] for r in rows if not r[10]]
    if missing:
        lines.append(f"- 还有 {len(missing)} 个套件没写说明（{', '.join(missing[:6])}"
                     f"{'…' if len(missing) > 6 else ''}），"
                     "它们的「证明什么」是从文件 docstring 抄的，可信度低一档。")
    return "\n".join(lines)


def cmd_tree(root: Path, repo: str, only: str | None, run_after: str | None,
             json_out: bool) -> int:
    text = render_tree(root, repo, only, run_after)
    if json_out:
        import kb
        print(json.dumps({"text": text, "tokens": kb.est_tokens(text)},
                         ensure_ascii=False, indent=2))
    else:
        print(text)
        try:
            import kb
            print(f"\n〔{kb.est_tokens(text)} tok〕", file=sys.stderr)
        except Exception:
            pass
    return 0


def cmd_set_note(root: Path, repo: str, suite_id: str, proves: str | None,
                 detail: str | None, kind: str | None, run_after: str | None,
                 status: str | None, no_verify: bool) -> int:
    conn = open_db(root)
    row = conn.execute("SELECT content_hash FROM test_suites WHERE repo=? AND suite_id=?",
                       (repo, suite_id)).fetchone()
    if row is None:
        ids = [r[0] for r in conn.execute(
            "SELECT suite_id FROM test_suites WHERE repo=? ORDER BY suite_id", (repo,))]
        print(f"没有叫 `{suite_id}` 的套件。现有：{', '.join(ids)}", file=sys.stderr)
        return 2
    ch = row[0]

    if proves is not None or detail is not None:
        now = time.strftime("%Y-%m-%dT%H:%M:%S%z")
        old = conn.execute("SELECT proves, detail FROM test_notes WHERE repo=? AND suite_id=?",
                           (repo, suite_id)).fetchone()
        p = proves if proves is not None else (old[0] if old else None)
        d = detail if detail is not None else (old[1] if old else None)
        conn.execute(
            "INSERT INTO test_notes (repo, suite_id, proves, detail, note_hash,"
            " source, model, updated_at) VALUES (?,?,?,?,?,?,?,?)"
            " ON CONFLICT(repo, suite_id) DO UPDATE SET"
            "   proves=excluded.proves, detail=excluded.detail,"
            "   note_hash=excluded.note_hash, source=excluded.source,"
            "   model=excluded.model, updated_at=excluded.updated_at",
            (repo, suite_id, p, d, ch, "agent", None, now))

    sets, args = [], []
    if kind:
        sets.append("kind=?"); args.append(kind)
    if run_after is not None:
        targets = [t.strip() for t in run_after.split(",") if t.strip()]
        sets.append("run_after=?"); args.append(json.dumps(targets, ensure_ascii=False))
    if status:
        sets.append("status=?"); args.append(status)
    if sets:
        args += [repo, suite_id]
        conn.execute(f"UPDATE test_suites SET {', '.join(sets)}"
                     " WHERE repo=? AND suite_id=?", args)
    conn.commit()
    print(f"✓ {suite_id} 已更新")
    return 0


def cmd_stats(root: Path, repo: str) -> int:
    conn = open_db(root)
    rows = conn.execute(
        "SELECT kind, status, COUNT(*), SUM(n_checks), SUM(has_verdict)"
        " FROM test_suites WHERE repo=? GROUP BY kind, status"
        " ORDER BY kind, status", (repo,)).fetchall()
    if not rows:
        print("清单为空")
        return 0
    print(f"{'kind':10s} {'status':10s} {'套件':>5s} {'check点':>8s} {'可自动判定':>10s}")
    print("-" * 50)
    tot = [0, 0, 0]
    for k, s, n, ck, hv in rows:
        print(f"{k:10s} {s:10s} {n:5d} {ck or 0:8d} {hv or 0:10d}")
        tot[0] += n; tot[1] += ck or 0; tot[2] += hv or 0
    print("-" * 50)
    print(f"{'合计':10s} {'':10s} {tot[0]:5d} {tot[1]:8d} {tot[2]:10d}")
    n_notes = conn.execute("SELECT COUNT(*) FROM test_notes WHERE repo=?",
                           (repo,)).fetchone()[0]
    print(f"\n已写说明 {n_notes} / {tot[0]} 个套件")
    stale = conn.execute(
        "SELECT s.suite_id FROM test_suites s JOIN test_notes n"
        "  ON n.repo=s.repo AND n.suite_id=s.suite_id"
        " WHERE s.repo=? AND n.note_hash IS NOT NULL AND n.note_hash != s.content_hash",
        (repo,)).fetchall()
    if stale:
        print(f"说明可能过期（文件已改）{len(stale)} 个：" +
              ", ".join(r[0] for r in stale))
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser("testtree", description="项目测试清单（sqlite）")
    ap.add_argument("--root", default=None, help="项目根，默认本文件上一级")
    ap.add_argument("--repo", default="codeb")
    sub = ap.add_subparsers(dest="cmd", required=True)

    sc = sub.add_parser("scan", help="重新清点测试文件（不碰说明）")
    sc.add_argument("--quiet", action="store_true")

    tr = sub.add_parser("tree", help="渲染给测试专家读的清单")
    tr.add_argument("--only", default=None, help="只显示某个 status，如 active")
    tr.add_argument("--run-after", default=None,
                    help="给一个改动路径，只输出该跑哪些套件")
    tr.add_argument("--json", action="store_true")

    sn = sub.add_parser("set-note", help="写一个套件的说明/声明")
    sn.add_argument("suite_id")
    sn.add_argument("--proves", default=None, help="它证明什么（一句话）")
    sn.add_argument("--detail", default=None, help="补充：怎么读失败、已知局限")
    sn.add_argument("--kind", default=None, help="unit/llm/e2e/browser/diag")
    sn.add_argument("--run-after", default=None,
                    help="逗号分隔的路径前缀，改了它们就该跑这个套件")
    sn.add_argument("--status", default=None, help="active/manual/scratch/retired")
    sn.add_argument("--no-verify", action="store_true", help="（保留）不校验文件存在")

    sub.add_parser("stats", help="统计与过期说明")

    args = ap.parse_args(argv)
    root = Path(args.root).resolve() if args.root else CODEB
    if args.cmd == "scan":
        return cmd_scan(root, args.repo, args.quiet)
    if args.cmd == "tree":
        return cmd_tree(root, args.repo, args.only, args.run_after, args.json)
    if args.cmd == "set-note":
        return cmd_set_note(root, args.repo, args.suite_id, args.proves,
                            args.detail, args.kind, args.run_after,
                            args.status, args.no_verify)
    if args.cmd == "stats":
        return cmd_stats(root, args.repo)
    return 2


if __name__ == "__main__":
    sys.exit(main())
