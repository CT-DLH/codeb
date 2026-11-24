"""overview：基于已生成的文件级说明，汇总出项目级说明。

关键立场：**不再读源码**。
  文件说明已经把「每个文件干什么」蒸馏过一遍了，二次读源码等于把最贵的一步
  又做一遍，而且会让项目说明和文件说明互相矛盾——两个真源。
  这里的输入只有 file_docs 表。
"""
from __future__ import annotations

import argparse
import json
import sqlite3
import sys
import time
from pathlib import Path

SCHEMA = {
    "type": "object",
    "properties": {
        "what": {"type": "string", "description": "这个项目是什么，2-3 句话，不写口号"},
        "why": {"type": "string", "description": "它解决什么问题；没有明确答案时如实说看不出"},
        "architecture": {"type": "array", "items": {"type": "string"},
                         "description": "分层/模块划分，每条形如「层名：由哪些文件构成，负责什么」"},
        "entrypoints": {"type": "array", "items": {"type": "string"},
                        "description": "用户从哪进入，形如「kb.py：命令行入口」"},
        "data_flow": {"type": "array", "items": {"type": "string"},
                      "description": "数据怎么流动，按顺序写"},
        "constraints": {"type": "array", "items": {"type": "string"},
                        "description": "跨文件的硬约束（从各文件 constraints 归纳，不要新增）"},
        "risks": {"type": "array", "items": {"type": "string"},
                  "description": "从文件说明里能看出的风险/缺口；没把握就给空数组"},
        "reading_order": {"type": "array", "items": {"type": "string"},
                          "description": "新人应该按什么顺序读，3-6 条，带文件名和一句理由"},
        "confidence": {"type": "string", "enum": ["high", "medium", "low"]},
    },
    "required": ["what", "why", "architecture", "entrypoints", "data_flow",
                 "constraints", "risks", "reading_order", "confidence"],
}

DDL = """
CREATE TABLE IF NOT EXISTS project_doc (
  repo        TEXT PRIMARY KEY,
  files_used  INTEGER,           -- 参与归纳的文件数
  files_total INTEGER,           -- 库里有几个成功文件
  digest      TEXT,              -- 送给模型的输入摘要（留档，便于复现）
  doc_json    TEXT,              -- 模型原始返回
  ok          INTEGER NOT NULL,
  error       TEXT,
  model       TEXT,
  elapsed_ms  INTEGER,
  updated_at  TEXT NOT NULL
);
"""


def open_db(root: Path) -> sqlite3.Connection:
    p = root / "_kbwork" / "codeb-index.db"
    p.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(p))
    conn.executescript(DDL)
    conn.commit()
    return conn


def build_digest(rows: list[dict], max_chars: int = 60000) -> str:
    """把文件说明拼成给模型看的清单。

    按「文件大小」降序取，不按路径序——大文件通常承载核心逻辑，
    预算不够时先保证它们在里面。但仍然要说明被略去多少，不能静默截断。
    """
    rows = sorted(rows, key=lambda r: r.get("lines") or 0, reverse=True)
    out, used = [], 0
    for r in rows:
        syms = _lst(r.get("key_symbols"))
        part = [f"## {r['path']}  ({r.get('lines')} 行, 角色: {r.get('role')})",
                f"- 作用: {r.get('purpose')}"]
        if r.get("deps"):
            part.append(f"- 依赖: {', '.join(_lst(r['deps']))[:200]}")
        if r.get("constraints"):
            part.append(f"- 约束: {'; '.join(_lst(r['constraints']))[:300]}")
        if syms:
            part.append(f"- 符号: {', '.join(syms[:40])}{' ...' if len(syms) > 40 else ''}")
        s = "\n".join(part)
        if used + len(s) > max_chars:
            out.append(f"\n[已省略 {len(rows) - len(out)} 个文件；预算 {max_chars} 字符]")
            break
        out.append(s)
        used += len(s)
    return "\n\n".join(out)


def _lst(v) -> list:
    if v is None:
        return []
    if isinstance(v, list):
        return v
    try:
        x = json.loads(v)
        return x if isinstance(x, list) else []
    except Exception:
        return []


def build_prompt(repo: str, digest: str) -> str:
    return f"""下面是一个代码仓库里每个文件各自的说明。请只根据这些说明，归纳出整个项目的说明。

仓库名：{repo}

要求：
- 所有文字用中文；代码文件名保持原样，并写相对仓库根的路径。
- what：2-3 句话，说清这是什么。不要写「本项目旨在」这种套话。
- why：它解决什么问题。如果从文件说明里看不出来，就直说看不出，不要编。
- architecture：分层描述，每条要提到具体文件。不要只写「数据层」而不说哪些文件是数据层。
- entrypoints：用户实际从哪里进入，看 role 里有 CLI 入口/HTTP 服务/MCP 服务的文件。
- data_flow：数据从输入到落地的顺序。
- constraints：只从各文件已声明的约束里归纳，**不要新增文件说明里没有的约束**。
- risks：只在说明里确实有依据时写；没有依据就给空数组。这一项最容易编。
- reading_order：3-6 条，新人按序读，每条带文件名和一句理由。
- confidence：文件说明覆盖不全、或大量文件 role 不明时给 low。

文件说明清单：
{digest}"""


def cmd_build(root: Path, repo: str, mode: str, verbose: bool) -> int:
    conn = open_db(root)
    cols = ["path", "role", "purpose", "deps", "constraints", "key_symbols",
            "lines", "confidence"]
    rows = [dict(zip(cols, r)) for r in conn.execute(
        f"SELECT {','.join(cols)} FROM file_docs WHERE repo=? AND ok=1", (repo,))]
    if not rows:
        print("库里没有成功的文件说明；先跑 filedoc generate", file=sys.stderr)
        return 2

    total = conn.execute("SELECT COUNT(*) FROM file_docs WHERE repo=? AND ok=1",
                         (repo,)).fetchone()[0]
    digest = build_digest(rows)
    print(f"参与归纳 {len(rows)} 个文件说明（共 {total} 个成功记录），"
          f"摘要 {len(digest)} 字符", file=sys.stderr)

    import os
    t0 = time.time()
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
        from distill import distill as _d
    except Exception:
        try:
            import distill as _d
        except Exception as e:
            print(f"无法导入 LLM 后端: {e}", file=sys.stderr)
            return 2

    try:
        res = _d.call_llm(build_prompt(repo, digest), mode, verbose=verbose, schema=SCHEMA)
        err = "" if res else "LLM 返回空"
    except Exception as e:
        res, err = None, f"call_llm 抛异常: {e}"
    ms = int((time.time() - t0) * 1000)

    now = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    conn.execute(
        """INSERT OR REPLACE INTO project_doc
           (repo,files_used,files_total,digest,doc_json,ok,error,model,elapsed_ms,updated_at)
           VALUES (?,?,?,?,?,?,?,?,?,?)""",
        (repo, len(rows), total, digest,
         json.dumps(res, ensure_ascii=False) if res else None,
         1 if res else 0, err or None,
         os.environ.get("ZHIHU_LLM_MODEL") or "(default)", ms, now))
    conn.commit()
    if not res:
        print(f"生成失败：{err}", file=sys.stderr)
        return 1
    print(f"OK 项目说明已写入 project_doc（{ms}ms）", file=sys.stderr)
    return 0


def cmd_show(root: Path, repo: str, as_json: bool) -> int:
    conn = open_db(root)
    r = conn.execute(
        "SELECT files_used,files_total,doc_json,ok,error,model,elapsed_ms,updated_at,digest "
        "FROM project_doc WHERE repo=?", (repo,)).fetchone()
    if not r:
        print("还没有项目说明；先跑 build", file=sys.stderr)
        return 1
    used, total, doc_json, ok, err, model, ms, ts, digest = r
    if not ok:
        print(f"上次生成失败：{err}（{ts}）", file=sys.stderr)
        return 1
    d = json.loads(doc_json)
    if as_json:
        print(json.dumps({"repo": repo, "files_used": used, "files_total": total,
                          "updated_at": ts, **d}, ensure_ascii=False, indent=2))
        return 0
    print("=" * 74)
    print(f"项目说明：{repo}   （归纳自 {used}/{total} 个文件说明，{ts}）")
    print("=" * 74)
    print(f"\n【是什么】\n{d.get('what', '')}")
    print(f"\n【为什么】\n{d.get('why', '')}")
    for key, title in (("architecture", "架构"), ("entrypoints", "入口"),
                       ("data_flow", "数据流"), ("constraints", "硬约束"),
                       ("risks", "风险"), ("reading_order", "建议阅读顺序")):
        items = d.get(key) or []
        print(f"\n【{title}】")
        if not items:
            print("  （无）")
        for i, x in enumerate(items, 1):
            print(f"  {i}. {x}")
    print(f"\n置信度：{d.get('confidence')}   模型：{model}   耗时：{ms / 1000:.1f}s")
    return 0


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(
        prog="python -m distill.filedoc_overview",
        description="用已生成的文件说明归纳项目说明（不再读源码）")
    ap.add_argument("--root", default=".")
    ap.add_argument("--repo", default="codeb")
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build", help="生成/刷新项目说明")
    b.add_argument("--mode", default="openai", choices=["openai", "cmd", "none"])
    b.add_argument("-v", "--verbose", action="store_true")
    s = sub.add_parser("show", help="查看项目说明")
    s.add_argument("--json", dest="as_json", action="store_true")
    args = ap.parse_args(argv)
    root = Path(args.root).resolve()
    if args.cmd == "show":
        return cmd_show(root, args.repo, args.as_json)
    return cmd_build(root, args.repo, args.mode, args.verbose)


if __name__ == "__main__":
    raise SystemExit(main())
