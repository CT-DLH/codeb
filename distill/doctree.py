"""doctree：把一个文件的符号树 + 每个符号的功能说明存进 sqlite。

和 filedoc 的分工：
  filedoc  : 文件级一句话说明
  doctree  : 文件内部的符号树，每个节点一句功能说明

提取器用 LLM（见 symtree.py 的说明）：
  正则认不出多行装饰器、动态生成的符号、嵌套定义和闭包，
  也认不出「这个函数实际给谁用」——而这些正是目录树的价值所在。
  LLM 提取能一并给出层级、分组和说明，一次调用拿到全部。

节点由模型决定，但每个名字都回源码核实一次：
  实测模型会写出源码里根本不存在的符号（kb.py 的 _compiled_ignore、
  semantic_blocks.py 的 _purpose_max、sessions.py 的 decode_cli，出现次数均为 0）。
  树上一个不存在的函数会让人对整份文档失去信任，而这种错误极难用肉眼发现。
  核实只做一件事：确认这个字符串在文件里出现过。它不判断结构、不否决分组。

不维护行号：查实现时用名字搜源码即可，行号是会悄悄变错的字段，不留。
"""
from __future__ import annotations

import argparse
import json
import sqlite3
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from distill.symtree import (  # noqa: E402
    SCHEMA_DOCS_ONLY, SCHEMA_GROUPS_ONLY, SCHEMA_TREE, Sym,
    build_docs_prompt, build_groups_only_prompt, build_tree_prompt,
    extract_symbols_regex, flatten_text, parse_tree_response,
)

DDL = """
CREATE TABLE IF NOT EXISTS doc_tree (
  repo        TEXT NOT NULL,
  path        TEXT NOT NULL,
  node_id     TEXT NOT NULL,          -- 稳定标识：kind::name[@父名]
  parent_id   TEXT,                   -- 父节点 node_id；顶层为 NULL
  depth       INTEGER NOT NULL,       -- 0 = 顶层
  kind        TEXT NOT NULL,          -- file/class/function/method/property/constant...
  name        TEXT NOT NULL,
  grp         TEXT,                   -- 功能分组（LLM 给的，如「kb 只读调用」）
  doc         TEXT,                   -- 功能说明；空表示模型没给
  source_hash TEXT NOT NULL,
  updated_at  TEXT NOT NULL,
  PRIMARY KEY (repo, path, node_id)
);
CREATE INDEX IF NOT EXISTS idx_doc_tree_name ON doc_tree(repo, name);
CREATE INDEX IF NOT EXISTS idx_doc_tree_path ON doc_tree(repo, path);
CREATE INDEX IF NOT EXISTS idx_doc_tree_grp  ON doc_tree(repo, path, grp);
CREATE TABLE IF NOT EXISTS doc_tree_groups (
  repo       TEXT NOT NULL,
  path       TEXT NOT NULL,
  seq        INTEGER NOT NULL,        -- 阅读顺序
  name       TEXT NOT NULL,
  summary    TEXT,
  source_hash TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  PRIMARY KEY (repo, path, name)
);
CREATE TABLE IF NOT EXISTS doc_tree_raw (
  repo       TEXT NOT NULL,
  path       TEXT NOT NULL,
  source_hash TEXT NOT NULL,
  tree_raw   TEXT,                    -- 模型原始返回，出问题时可审计
  dropped    TEXT,                    -- 因源码中不存在而被丢弃的名字
  extractor  TEXT,                    -- llm / regex
  updated_at TEXT NOT NULL,
  PRIMARY KEY (repo, path)
);
"""


def open_db(root: Path) -> sqlite3.Connection:
    p = root / "_kbwork" / "codeb-index.db"
    p.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(p))
    conn.executescript(DDL)
    # CREATE TABLE IF NOT EXISTS 不会给已存在的表补列，必须显式迁移。
    def add_col(tbl: str, col: str, decl: str) -> None:
        have = [r[1] for r in conn.execute(f"PRAGMA table_info({tbl})")]
        if have and col not in have:
            conn.execute(f"ALTER TABLE {tbl} ADD COLUMN {col} {decl}")

    add_col("doc_tree_raw", "tree_raw", "TEXT")
    add_col("doc_tree_raw", "extractor", "TEXT")
    # 新结构不再维护行号，删掉避免读者以为它可信
    cols = [r[1] for r in conn.execute("PRAGMA table_info(doc_tree)")]
    if "line" in cols:
        try:
            conn.execute("ALTER TABLE doc_tree DROP COLUMN line")
        except sqlite3.OperationalError:
            pass
    conn.commit()
    return conn


def _sid(kind: str, name: str, parent: str = "") -> str:
    return f"{kind}::{name}@{parent}" if parent else f"{kind}::{name}"


def _tidy_doc(s: str, limit: int = 26) -> str:
    """压缩过长的说明。

    提示词写了「20 字以内」，实测仍有 367/455 条超标，最长 168 字。
    光靠提示词拦不住，存储层必须兜底——否则渲染出来是一行折断的乱码。
    优先在句读处断开，保住语义完整；没有句读才硬截加省略号。
    """
    t = (s or "").strip().replace("\n", " ")
    if len(t) <= limit:
        return t
    for sep in ("；", "。", "，", ";", ",", "——", " - "):
        i = t.find(sep)
        if 0 < i <= limit:
            return t[:i].strip()
    return t[:limit].rstrip() + "…"


def store_tree(conn: sqlite3.Connection, repo: str, rel: str, syms: list[Sym],
               groups: list[dict], source_hash: str, tree_raw: str,
               dropped: list[str], extractor: str) -> int:
    """把符号树 + 分组写库。节点集合来自解析结果，此处不再增删。"""
    now = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    known = {s.name for _, s in flatten_text(syms)}

    # 丢掉「一个真实成员都没有」的组：模型会为只有 1 个符号的文件凭空编出
    # 4-7 个组（run_tasks.py 只有 TASKS，却被分了「loop 执行」「知识库交互」）。
    # 这种空组渲染出来是一串没有下辖节点的标题，比没有更糟——看起来像真有这些模块。
    kept: list[dict] = []
    names_now = {s.name for _, s in flatten_text(syms)}
    for g in groups:
        name = str(g.get("name", "") or "").strip()
        if not name:
            continue
        members = {s.name for _, s in flatten_text(syms) if s.group == name}
        members |= {m for m in g.get("members", []) if m in names_now}
        if not members:
            dropped.append(f"[组]{name}")
            continue
        kept.append({"name": name, "summary": str(g.get("summary", "") or "").strip()})

    conn.execute("DELETE FROM doc_tree WHERE repo=? AND path=?", (repo, rel))
    conn.execute("DELETE FROM doc_tree_groups WHERE repo=? AND path=?", (repo, rel))

    rows = []

    def walk(nodes: list[Sym], parent_id: str | None, depth: int) -> int:
        n = 0
        for s in nodes:
            nid = _sid(s.kind, s.name, s.parent)
            rows.append((repo, rel, nid, parent_id, depth, s.kind, s.name,
                         s.group or None, _tidy_doc(s.doc) or None, source_hash, now))
            n += 1
            if s.children:
                n += walk(s.children, nid, depth + 1)
        return n

    total = walk(syms, None, 0)
    conn.executemany(
        """INSERT OR REPLACE INTO doc_tree
           (repo,path,node_id,parent_id,depth,kind,name,grp,doc,source_hash,updated_at)
           VALUES (?,?,?,?,?,?,?,?,?,?,?)""", rows)

    conn.executemany(
        """INSERT OR REPLACE INTO doc_tree_groups
           (repo,path,seq,name,summary,source_hash,updated_at) VALUES (?,?,?,?,?,?,?)""",
        [(repo, rel, i, g["name"], g["summary"], source_hash, now)
         for i, g in enumerate(kept)])

    conn.execute(
        """INSERT OR REPLACE INTO doc_tree_raw
           (repo,path,source_hash,tree_raw,dropped,extractor,updated_at)
           VALUES (?,?,?,?,?,?,?)""",
        (repo, rel, source_hash, tree_raw,
         json.dumps(sorted(set(dropped)), ensure_ascii=False), extractor, now))
    conn.commit()
    return total


def cmd_generate(root: Path, repo: str, paths: list[str], mode: str,
                 force: bool, limit: int, verbose: bool,
                 extractor: str = "llm") -> int:
    conn = open_db(root)
    from distill.filedoc import iter_code_files, source_hash as fhash

    if paths:
        targets = []
        for p in paths:
            fp = (root / p).resolve()
            if not fp.is_file():
                print(f"不存在: {p}", file=sys.stderr)
                return 2
            targets.append(fp)
    else:
        targets = iter_code_files(root)

    todo = []
    for p in targets:
        rel = p.relative_to(root).as_posix()
        text = p.read_text(encoding="utf-8", errors="replace")
        h = fhash(text)
        if not force:
            prev = conn.execute(
                "select source_hash from doc_tree where repo=? and path=? limit 1",
                (repo, rel)).fetchone()
            if prev and prev[0] == h:
                continue
        todo.append((rel, text, h))
    if limit:
        todo = todo[:limit]

    need_llm = extractor == "llm" and mode != "none"
    print(f"待生成目录树 {len(todo)} 个文件（提取器={extractor}）", file=sys.stderr)
    _d = None
    if need_llm:
        from distill import distill as _d  # noqa: F811

    ok = fail = 0
    for i, (rel, text, h) in enumerate(todo, 1):
        fd = conn.execute("select purpose from file_docs where repo=? and path=?",
                          (repo, rel)).fetchone()
        file_doc = (fd[0] if fd else "") or ""
        t0 = time.time()

        if need_llm:
            # 三阶段，每阶段一个单一目标。
            # 合并成「一次调用同时要结构+分组+说明」时，实测模型会把 40 多个
            # 符号塞进 3 个组——分组是需要全局视野的判断，被写说明挤掉后就退化成敷衍。
            # 拆开后：① 单次拿到节点清单与层级；② 只看名字分组；③ 逐组写说明。
            # 第一步重试两次：大文件偶尔返回空（kb.py / smoke.ts 各失败过一次），
            # 一次空就放弃会让整个文件在库里消失。
            res = None
            for attempt in range(3):
                res = _d.call_llm(build_tree_prompt(rel, text, file_doc),
                                  mode, verbose=verbose, schema=SCHEMA_TREE)
                if res and res.get("nodes"):
                    break
                if attempt < 2:
                    print(f"[{i}/{len(todo)}] 重试 {rel}（第 {attempt + 1} 次返回空）",
                          file=sys.stderr)
                    time.sleep(2 + attempt * 3)
            if not res or not res.get("nodes"):
                fail += 1
                print(f"[{i}/{len(todo)}] FAIL {rel}（模型连续 3 次未返回节点）")
                continue
            # 丢弃率过高 = 模型读错了文件（实测 doctree.py 一次返回了
            # get_kb/search_kb/parse_yaml 这些完全不属于它的名字，12 个只剩 1 个）。
            # 这时不能就这么落库——一个只有 1 个节点的树比没有更误导人，
            # 它让人以为这个文件真的只有一个函数。
            for attempt in range(2):
                probe, _, pdropped = parse_tree_response(res, text, rel)
                n_raw = len([n for n in (res.get("nodes") or []) if isinstance(n, dict)])
                if n_raw < 4 or len(pdropped) <= n_raw * 0.5:
                    break
                print(f"[{i}/{len(todo)}] 重试 {rel}"
                      f"（{len(pdropped)}/{n_raw} 个名字不属于此文件，疑似读错）",
                      file=sys.stderr)
                time.sleep(2)
                r2 = _d.call_llm(build_tree_prompt(rel, text, file_doc),
                                 mode, verbose=verbose, schema=SCHEMA_TREE)
                if r2 and r2.get("nodes"):
                    res = r2
            syms, groups, dropped = parse_tree_response(res, text, rel)
            raw = json.dumps(res, ensure_ascii=False)
            used = "llm"

            # ② 重新分组：只用符号名，给足全局视野
            all_syms = [s for _, s in flatten_text(syms)]
            names = [s.name for s in all_syms]
            g2 = _d.call_llm(build_groups_only_prompt(rel, names, file_doc),
                             mode, verbose=verbose, schema=SCHEMA_GROUPS_ONLY)
            if g2 and g2.get("groups"):
                groups = [{"name": str(g.get("name", "")).strip(),
                           "summary": str(g.get("summary", "")).strip(),
                           "members": [str(m).strip() for m in (g.get("members") or [])]}
                          for g in g2["groups"] if str(g.get("name", "")).strip()]
                # 以第二阶段的分组为准覆盖 node.group
                gmap: dict[str, str] = {}
                for g in groups:
                    for m in g["members"]:
                        gmap.setdefault(m, g["name"])
                for s in all_syms:
                    if s.name in gmap:
                        s.group = gmap[s.name]
                raw += "\n/* groups */ " + json.dumps(g2, ensure_ascii=False)

            # ③ 逐组写说明（带整份源码），补齐第一轮漏掉的
            by_name = {s.name: s for s in all_syms}
            for g in groups:
                members = [m for m in g.get("members", []) if m in by_name]
                if not members:
                    continue
                d2 = _d.call_llm(
                    build_docs_prompt(rel, g["name"], g.get("summary", ""),
                                      members, text),
                    mode, verbose=verbose, schema=SCHEMA_DOCS_ONLY)
                for nd in ((d2 or {}).get("nodes") or []):
                    if not isinstance(nd, dict):
                        continue
                    nm = str(nd.get("name", "")).strip()
                    txt = str(nd.get("doc", "") or "").strip()
                    if nm in by_name and txt:
                        by_name[nm].doc = txt
        else:
            syms = extract_symbols_regex(rel, text)
            groups, dropped, raw, used = [], [], "{}", "regex"

        if not syms:
            # 没有任何符号的文件（纯脚本、纯数据配置）：
            # 早先直接跳过，结果它在树里彻底不存在，用户按文件查会找不到，
            # 而「为什么缺一个」无从解释。改成用文件自身当一个叶子节点。
            leaf = Path(rel).name
            syms = [Sym(name=leaf, kind="file", doc=file_doc or "整个文件（无独立符号）")]
            groups = [{"name": "整个文件", "summary": file_doc[:20] if file_doc else ""}]
            syms[0].group = "整个文件"

        ms = int((time.time() - t0) * 1000)
        n = store_tree(conn, repo, rel, syms, groups, h, raw, dropped, used)
        ok += 1
        uniq = sorted(set(dropped))
        note = f"  ⚠ 丢弃不存在于源码的名字: {uniq}" if uniq else ""
        nog = sum(1 for _, s in flatten_text(syms) if not s.doc)
        if nog:
            note += f"  ⚠ {nog} 个节点缺说明"
        print(f"[{i}/{len(todo)}] OK   {rel}  {len(groups)} 组 / {n} 节点 ({ms}ms){note}")

    print(f"\n完成：成功 {ok}，失败 {fail}", file=sys.stderr)
    return 0 if fail == 0 else 1


def render_tree(conn: sqlite3.Connection, repo: str, rel: str, max_width: int = 96) -> str:
    """按「分组 → 类层次」两级组织输出。

    分组在类层次之外：分组回答「这批符号一起负责什么」，
    缩进回答「这个方法属于哪个类」。两者独立，所以分开表达。
    """
    rows = list(conn.execute(
        "select node_id,parent_id,depth,kind,name,grp,doc from doc_tree "
        "where repo=? and path=? order by depth,name", (repo, rel)))
    if not rows:
        return ""
    gsum = {n: (s or "") for n, s in conn.execute(
        "select name,summary from doc_tree_groups where repo=? and path=? order by seq",
        (repo, rel))}
    gorder = list(gsum)

    def dwidth(s: str) -> int:
        return sum(2 if ord(c) > 0x2E80 else 1 for c in s)

    def sort_key(r):
        grp = r[5] or ""
        return (gorder.index(grp) if grp in gorder else len(gorder), r[2], r[4])

    out: list[str] = []
    last_grp = object()
    for nid, pid, depth, kind, name, grp, doc in sorted(rows, key=sort_key):
        if grp != last_grp:
            last_grp = grp
            if grp:
                summ = gsum.get(grp, "")
                out.append("")
                out.append(f"── {grp}" + (f"  ({summ})" if summ else "") + " " +
                           "─" * max(0, 64 - dwidth(grp) - dwidth(summ)))
        label = name + ("()" if kind in ("function", "method", "property") else "")
        left = "  " * (depth + 1) + label
        txt = doc or ""
        pad = max(2, max_width - dwidth(left) - dwidth(txt))
        out.append(f"{left} {'.' * pad} {txt}".rstrip())
    return "\n".join(out)


def render_md(conn: sqlite3.Connection, repo: str, rel: str) -> str:
    rows = list(conn.execute(
        "select depth,kind,name,grp,doc from doc_tree "
        "where repo=? and path=? order by depth,name", (repo, rel)))
    if not rows:
        return ""
    gsum = {n: (s or "") for n, s in conn.execute(
        "select name,summary from doc_tree_groups where repo=? and path=? order by seq",
        (repo, rel))}
    gorder = list(gsum)

    def sort_key(r):
        grp = r[3] or ""
        return (gorder.index(grp) if grp in gorder else len(gorder), r[0], r[2])

    out = [f"### {rel}", ""]
    last = object()
    for depth, kind, name, grp, doc in sorted(rows, key=sort_key):
        if grp != last:
            last = grp
            if grp:
                s = gsum.get(grp, "")
                out.append("")
                out.append(f"**{grp}**" + (f" — {s}" if s else ""))
                out.append("")
        suffix = "()" if kind in ("function", "method", "property") else ""
        out.append(f"{'  ' * depth}- `{name}{suffix}` — {doc or ''}".rstrip())
    return "\n".join(out)


def cmd_show(root: Path, repo: str, rel: str, as_json: bool, as_md: bool) -> int:
    conn = open_db(root)
    rel = rel.replace("\\", "/").lstrip("./")
    if as_md:
        txt = render_md(conn, repo, rel)
        if not txt:
            print(f"没有 {rel} 的目录树；先跑 generate", file=sys.stderr)
            return 1
        print(txt)
        return 0
    if as_json:
        rows = [dict(zip(("node_id", "parent_id", "depth", "kind", "name", "grp", "doc"), r))
                for r in conn.execute(
                    "select node_id,parent_id,depth,kind,name,grp,doc from doc_tree "
                    "where repo=? and path=? order by depth,name", (repo, rel))]
        if not rows:
            print(f"没有 {rel} 的目录树", file=sys.stderr)
            return 1
        print(json.dumps({"path": rel, "nodes": rows}, ensure_ascii=False, indent=2))
        return 0
    txt = render_tree(conn, repo, rel)
    if not txt:
        print(f"没有 {rel} 的目录树；先跑 generate", file=sys.stderr)
        return 1
    print(f"{rel}")
    print(txt)
    return 0


def cmd_find(root: Path, repo: str, keyword: str, exact: bool, limit: int) -> int:
    """按符号名查：它是什么、在哪个文件、属于哪个分组。

    这是这棵树最实用的查询——「HANDLERS 在哪」比「kb.py 有什么」高频得多。
    """
    conn = open_db(root)
    if exact:
        rows = list(conn.execute(
            "select path,kind,name,grp,doc from doc_tree "
            "where repo=? and name=? order by path", (repo, keyword)))
    else:
        rows = list(conn.execute(
            "select path,kind,name,grp,doc from doc_tree "
            "where repo=? and name like ? order by path,name limit ?",
            (repo, f"%{keyword}%", limit)))
    if not rows:
        print(f"没有匹配「{keyword}」的符号", file=sys.stderr)
        return 1
    for path, kind, name, grp, doc in rows:
        suffix = "()" if kind in ("function", "method", "property") else ""
        print(f"{name}{suffix}")
        print(f"  文件  : {path}")
        print(f"  类型  : {kind}" + (f"   分组: {grp}" if grp else ""))
        print(f"  说明  : {doc or '（缺）'}")
    return 0


def cmd_stats(root: Path, repo: str) -> int:
    conn = open_db(root)
    files = conn.execute("select count(distinct path) from doc_tree where repo=?",
                         (repo,)).fetchone()[0]
    nodes = conn.execute("select count(*) from doc_tree where repo=?", (repo,)).fetchone()[0]
    nodoc = conn.execute(
        "select count(*) from doc_tree where repo=? and (doc is null or trim(doc)='')",
        (repo,)).fetchone()[0]
    print(f"repo={repo} 有树的文件={files} 节点总数={nodes} 缺说明={nodoc}")

    fd = {r[0] for r in conn.execute(
        "select path from file_docs where repo=? and ok=1", (repo,))}
    dt = {r[0] for r in conn.execute(
        "select distinct path from doc_tree where repo=?", (repo,))}
    if fd - dt:
        print(f"有文件说明但无目录树: {sorted(fd - dt)}")
    if dt - fd:
        print(f"有目录树但无文件说明: {sorted(dt - fd)}")

    for path, n, m in conn.execute(
            "select path, count(*), sum(doc is null or trim(doc)='') from doc_tree "
            "where repo=? group by path order by path", (repo,)):
        print(f"  {n:4d} 节点  缺{int(m or 0):3d}  {path}")
    return 0


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(
        prog="python -m distill.doctree",
        description="为文件内部符号生成目录树（LLM 提取），存入 sqlite")
    ap.add_argument("--root", default=".")
    ap.add_argument("--repo", default="codeb")
    sub = ap.add_subparsers(dest="cmd", required=True)
    g = sub.add_parser("generate")
    g.add_argument("paths", nargs="*")
    g.add_argument("--mode", default="openai", choices=["openai", "cmd", "none"])
    g.add_argument("--extractor", default="llm", choices=["llm", "regex"],
                   help="llm=让模型提取结构与说明（默认）；regex=离线兜底，不含说明")
    g.add_argument("--force", action="store_true")
    g.add_argument("--limit", type=int, default=0)
    g.add_argument("-v", "--verbose", action="store_true")
    s = sub.add_parser("show")
    s.add_argument("path")
    s.add_argument("--json", dest="as_json", action="store_true")
    s.add_argument("--md", action="store_true")
    f = sub.add_parser("find", help="按符号名查")
    f.add_argument("keyword")
    f.add_argument("--exact", action="store_true")
    f.add_argument("--limit", type=int, default=20)
    sub.add_parser("stats")
    args = ap.parse_args(argv)
    root = Path(args.root).resolve()
    if args.cmd == "show":
        return cmd_show(root, args.repo, args.path, args.as_json, args.md)
    if args.cmd == "find":
        return cmd_find(root, args.repo, args.keyword, args.exact, args.limit)
    if args.cmd == "stats":
        return cmd_stats(root, args.repo)
    return cmd_generate(root, args.repo, args.paths, args.mode, args.force,
                        args.limit, args.verbose, args.extractor)


if __name__ == "__main__":
    raise SystemExit(main())
