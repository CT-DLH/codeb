"""file-doc：给每个代码文件生成一份 LLM 说明文档，落进 sqlite。

为什么单独成模块而不是塞进 kb.py：
  kb.py 有一条硬规则——stdlib-only（它要能在任何机器上直接跑，不带依赖）。
  这里要 import distill 的 LLM 后端，属于可选能力，所以放在独立模块，
  由 `python -m distill.filedoc` 调用；kb.py 只负责读它写出的表。

三层职责：
  1. collect  ：枚举代码文件（按 kb.py 的 SkipRules 口径）
  2. describe ：调项目既有的 call_llm 生成结构化说明
  3. store    ：写进 _kbwork/codeb-index.db 的 file_docs 表

设计约束（照项目既有教训）：
  - 不新建数据库文件：沿用 codeb-index.db，`kb reindex` 只 DELETE 它自己的
    pages/covers/blocks/meta，file_docs 不受影响。
  - 必须记 source_hash：说明文档是 LLM 产物，源码一改就过期。
    没有 hash 就无法区分「没生成」和「生成过但已过期」——这两者要的动作相反。
  - 失败必须显式落库（ok=0 + error），不许静默跳过。
    一个永远不进入循环的检查和一个永远通过的检查，在报告上无法区分。
  - 不传全文给模型：传「路径 + 符号大纲 + 头尾片段」，控制成本与噪声。
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sqlite3
import sys
import time
from pathlib import Path

# 代码文件口径：与 kb.py 的符号解析范围保持一致，只列会被当源码看的扩展名
CODE_EXTS = {
    ".py", ".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs",
    ".go", ".rs", ".java", ".kt", ".c", ".h", ".cpp", ".hpp", ".cc",
    ".cs", ".rb", ".php", ".swift", ".scala", ".sh", ".ps1", ".sql",
}
SKIP_DIRS = {
    "_kbwork", "_tmp", "__pycache__", "node_modules", ".git", "agvenv",
    ".venv", "venv", "dist", "build", ".next", ".mypy_cache", ".pytest_cache",
    # 本仓库里由 DSH 运行时自动生成的插件目录，不是本项目的源码
    ".dsh-created-plugins",
}

SCHEMA = {
    "type": "object",
    "properties": {
        "purpose": {"type": "string", "description": "一句话说明这个文件的存在理由（做什么，不解释怎么实现）"},
        "role": {"type": "string", "description": "在项目中的角色，如 CLI 入口/数据层/工具库/测试"},
        "inputs": {"type": "array", "items": {"type": "string"},
                   "description": "读什么：外部输入总览（保留兼容；细分类见 cli_args/env/files）"},
        "cli_args": {"type": "array", "items": {"type": "string"},
                     "description": "命令行参数、子命令、标志；没有就给空数组"},
        "env": {"type": "array", "items": {"type": "string"},
                "description": "代码里真实读取的环境变量名；一个都没有就给空数组，不许编"},
        "files": {"type": "array", "items": {"type": "string"},
                  "description": "读写的文件或目录；没有就给空数组"},
        "outputs": {"type": "array", "items": {"type": "string"}, "description": "产出什么：返回值、写盘、stdout、副作用"},
        "key_symbols": {"type": "array", "items": {"type": "string"},
                        "description": "该文件定义的对外符号，完整列出：函数、类、常量、导出的类型。不要截断，不要只挑重要的"},
        "deps": {"type": "array", "items": {"type": "string"}, "description": "依赖的其它模块（只看 import/require）"},
        "constraints": {"type": "array", "items": {"type": "string"}, "description": "改动时必须遵守的约束；没有就给空数组"},
        "confidence": {"type": "string", "enum": ["high", "medium", "low"], "description": "信息不足时如实给 low"},
    },
    "required": ["purpose", "role", "inputs", "cli_args", "env", "files",
                 "outputs", "key_symbols", "deps", "constraints", "confidence"],
}

DDL = """
CREATE TABLE IF NOT EXISTS file_docs (
  repo        TEXT NOT NULL,
  path        TEXT NOT NULL,          -- 仓库内相对路径，统一 / 分隔
  lang        TEXT,                   -- 由扩展名推得
  size        INTEGER,                -- 字节数
  lines       INTEGER,
  source_hash TEXT NOT NULL,          -- 源码 sha256 前16位；用于判断是否过期
  purpose     TEXT,
  role        TEXT,
  inputs      TEXT,                   -- JSON 数组（输入总览，保留兼容）
  cli_args    TEXT,                   -- JSON 数组：命令行参数/子命令/标志
  env         TEXT,                   -- JSON 数组：真实读取的环境变量名
  files       TEXT,                   -- JSON 数组：读写的文件/目录
  outputs     TEXT,
  key_symbols TEXT,
  deps        TEXT,
  constraints TEXT,
  confidence  TEXT,
  ok          INTEGER NOT NULL,       -- 1 成功 / 0 失败
  error       TEXT,                   -- 失败原因（ok=0 时必填）
  model       TEXT,                   -- 用的哪个模型
  elapsed_ms  INTEGER,
  doc_json    TEXT,                   -- 模型原始返回，留作审计
  updated_at  TEXT NOT NULL,
  PRIMARY KEY (repo, path)
);
CREATE INDEX IF NOT EXISTS idx_file_docs_hash ON file_docs(source_hash);
"""


def db_path(root: Path) -> Path:
    return root / "_kbwork" / "codeb-index.db"


def open_db(root: Path) -> sqlite3.Connection:
    p = db_path(root)
    p.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(p))
    conn.executescript(DDL)
    # 老库不会因为 DDL 改了就有新列（CREATE TABLE IF NOT EXISTS 直接跳过），
    # 所以这里必须显式补列；否则 INSERT 会因列不存在而整批失败。
    have = {r[1] for r in conn.execute("PRAGMA table_info(file_docs)")}
    for col, decl in (("cli_args", "TEXT"), ("env", "TEXT"), ("files", "TEXT")):
        if col not in have:
            conn.execute(f"ALTER TABLE file_docs ADD COLUMN {col} {decl}")
    conn.commit()
    return conn


def iter_code_files(root: Path) -> list[Path]:
    """按口径枚举代码文件；相对路径统一用 /。"""
    out: list[Path] = []
    for p in sorted(root.rglob("*")):
        if not p.is_file():
            continue
        rel_parts = p.relative_to(root).parts
        if any(part in SKIP_DIRS for part in rel_parts[:-1]):
            continue
        if p.suffix.lower() not in CODE_EXTS:
            continue
        out.append(p)
    return out


def source_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", "replace")).hexdigest()[:16]


def outline(text: str, limit: int = 4000) -> str:
    """做一份「大纲 + 头尾」，而不是塞全文。

    长文件塞全文会挤掉真正有信息量的头部声明与尾部入口；
    只取符号行能显著降 token，同时保住结构。
    """
    lines = text.splitlines()
    head = "\n".join(lines[:80])
    if len(text) <= limit:
        return text
    sig_re = re.compile(
        r"^\s*(?:async\s+)?(?:def|class|function|const|let|var|interface|type|"
        r"func|fn|struct|impl|public|private|protected|export|module|CREATE)\b"
        r"|^\s*(?:import|from|require|use|include|#include)\b"
    )
    syms = [ln for ln in lines if sig_re.search(ln)]
    mid = "\n".join(syms[:120])
    tail = "\n".join(lines[-40:])
    return (f"{head}\n\n... [中间省略；以下是符号行] ...\n{mid}\n\n"
            f"... [尾部] ...\n{tail}")[: limit * 3]


def build_prompt(rel: str, text: str) -> str:
    return f"""你在为一个代码知识库编写文件级说明。只根据给出的代码内容判断，不要推测文件里没有的东西。

文件路径：{rel}

输出要求：所有文字字段一律用中文（代码符号名保持原样，不要翻译）。

要求：
- purpose 一句话，说清「这个文件为什么存在」，不写「实现了什么功能」这种空话。
- role 用 2-6 个字概括**这个文件本身**是什么，不要看它调用了谁。可选示例（不是穷举）：
  CLI 入口 / HTTP 服务 / MCP 服务 / agent 循环 / 数据层 / 工具库 / 测试 / 配置 /
  生成器 / 页面组件 / 提示词 / 索引构建。
  判断只看文件自身行为：起 http 端口才是 HTTP 服务；把函数包装成 MCP 工具才是 MCP 服务；
  只被 import 而不自己启动的是工具库。
- constraints 写「改动时容易踩的坑」，例如「保持 stdlib-only」「列名变更要同步迁移逻辑」。
  这一条最容易胡思乱想——只写代码里能看出来的，没有就给空数组。
  重要：constraints 比 key_symbols 更有价值，不要为了罗列符号而省略它。
  只要代码里存在「必须这样写否则会坏」的隐含约定（如只依赖标准库、路径必须相对仓库根、写库要先备份），就要写出来。
- key_symbols 完整列出该文件定义的对外符号（函数、类、常量、导出类型），**不要截断、不要只挑重要的**。
  只列真实定义在本文件里的；被 import 进来的不算。
- 输入分三类分别填，不要混：
  · cli_args 只填命令行参数/子命令/标志（如 --json、tree 子命令）
  · env 只填代码里真实读到的环境变量名（程序里出现 os.environ / getenv / process.env 才算）；没有就给空数组
  · files 只填读写的文件或目录路径
  特别注意：命令行参数不是环境变量。没读到环境变量时 env 必须是空数组，不要为了凑满而编。
- outputs 只写真实产出：返回值、写盘、stdout、DB 写入。
- deps 只写 import/require 到的模块名。
- confidence：内容被截断或信息不足时给 low，不要装作 confidence 高。

代码内容：
``` 
{text}
```"""


def describe(rel: str, text: str, mode: str, verbose: bool = False) -> tuple[dict | None, str]:
    """返回 (doc | None, error)。error 为空表示成功。"""
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
        from distill import distill as _d  # 延迟导入：本模块在包内时用相对路径即可
    except Exception:
        try:
            import distill as _d  # 直接以 distill/ 为 sys.path 时
        except Exception as e:  # pragma: no cover
            return None, f"无法导入 LLM 后端: {e}"

    prompt = build_prompt(rel, outline(text))
    try:
        res = _d.call_llm(prompt, mode, verbose=verbose, schema=SCHEMA)
    except Exception as e:
        return None, f"call_llm 抛异常: {e}"
    if not res:
        return None, "LLM 返回空（检查 ZHIHU_LLM_API_KEY / 网络）"
    if not isinstance(res, dict):
        return None, f"LLM 返回非对象: {type(res).__name__}"
    if not res.get("purpose"):
        return None, "LLM 返回缺少 purpose 字段"
    return res, ""


def _as_json(v) -> str:
    return json.dumps(v, ensure_ascii=False) if isinstance(v, (list, dict)) else json.dumps(
        [] if v is None else [str(v)], ensure_ascii=False)


# 模型对「1-5 个」这类软约束遵守得很差（早先实测给过 39 个符号）。
# 但 key_symbols 现在明确要求「完整列出」，不能再裁——截断等于直接丢掉可用信息。
# 只给其余字段留上限保护，防止模型把整份 import 清单或大段文字塞进来。
# 顺序有意义——保留模型给的先后顺序，它通常把最重要的放前面。
_CAP = {"deps": 12, "constraints": 8, "inputs": 8, "outputs": 8}


def _clip(field: str, v) -> str:
    lst = v if isinstance(v, list) else ([] if v is None else [str(v)])
    lst = [str(x).strip() for x in lst if str(x).strip()]
    n = _CAP.get(field)
    return json.dumps(lst[:n] if n else lst, ensure_ascii=False)


def store(conn: sqlite3.Connection, repo: str, rel: str, text: str,
          doc: dict | None, error: str, model: str, elapsed_ms: int) -> None:
    now = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    nlines = text.count("\n") + (0 if text.endswith("\n") else 1)
    d = doc or {}
    conn.execute(
        """INSERT OR REPLACE INTO file_docs
           (repo,path,lang,size,lines,source_hash,purpose,role,inputs,cli_args,env,files,
            outputs,key_symbols,deps,constraints,confidence,ok,error,model,elapsed_ms,
            doc_json,updated_at)
           VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (repo, rel, Path(rel).suffix.lstrip(".").lower(), len(text.encode("utf-8", "replace")),
         nlines, source_hash(text),
         d.get("purpose"), d.get("role"),
         _clip("inputs", d.get("inputs")),
         _clip("cli_args", d.get("cli_args")),
         _clip("env", d.get("env")),
         _clip("files", d.get("files")),
         _clip("outputs", d.get("outputs")),
         # key_symbols 不裁剪：完整符号清单是这份文档的主要价值
         _clip("key_symbols", d.get("key_symbols")), _clip("deps", d.get("deps")),
         _clip("constraints", d.get("constraints")), d.get("confidence"),
         1 if doc else 0, error or None, model, elapsed_ms,
         json.dumps(doc, ensure_ascii=False) if doc else None, now),
    )


def cmd_generate(root: Path, repo: str, files: list[Path] | None,
                 limit: int, mode: str, force: bool, verbose: bool) -> int:
    conn = open_db(root)
    targets = files if files else iter_code_files(root)
    # 已是最新（hash 未变）且非 force 的，跳过——但要说清跳过了几个
    rows = {r[0]: (r[1], r[2]) for r in conn.execute(
        "SELECT path, source_hash, ok FROM file_docs WHERE repo=?", (repo,))}
    todo, skipped = [], 0
    for p in targets:
        rel = p.relative_to(root).as_posix()
        text = p.read_text(encoding="utf-8", errors="replace")
        h = source_hash(text)
        prev = rows.get(rel)
        if prev and prev[0] == h and prev[1] == 1 and not force:
            skipped += 1
            continue
        todo.append((rel, text, h))
        if limit and len(todo) >= limit:
            break

    print(f"目标 {len(targets)} 个；待生成 {len(todo)} 个；hash 未变跳过 {skipped} 个",
          file=sys.stderr)
    model = os.environ.get("ZHIHU_LLM_MODEL") or "(default)"
    ok = fail = 0
    for i, (rel, text, _h) in enumerate(todo, 1):
        t0 = time.time()
        doc, err = describe(rel, text, mode, verbose=verbose)
        ms = int((time.time() - t0) * 1000)
        store(conn, repo, rel, text, doc, err, model, ms)
        conn.commit()
        if doc:
            ok += 1
            print(f"[{i}/{len(todo)}] OK   {rel}  ({ms}ms) — {doc.get('purpose', '')[:60]}")
        else:
            fail += 1
            print(f"[{i}/{len(todo)}] FAIL {rel}  ({ms}ms) — {err}")
    print(f"\n完成：成功 {ok}，失败 {fail}，跳过 {skipped}", file=sys.stderr)
    # 只有真正失败才算非零退出。全部命中 hash 跳过（本次没干活）不是错误，
    # 否则「没有变化」和「生成失败」在 CI 里会得到同一个信号。
    return 0 if fail == 0 else 1


def _fmt_list(v, empty: str = "—") -> str:
    try:
        lst = json.loads(v) if isinstance(v, str) else (v or [])
    except Exception:
        return str(v)
    if not lst:
        return empty
    return " / ".join(str(x) for x in lst)


def cmd_show(root: Path, repo: str, limit: int, paths: list[str],
             full: bool, as_json: bool) -> int:
    """查看生成的说明。

    默认只打摘要（一屏能扫完）；给了具体路径就默认展开全部字段——
    因为下场要我查某个文件时，想看的正是 inputs/约束，而不是一句 purpose。
    """
    conn = open_db(root)
    cols = ("path,ok,confidence,role,purpose,inputs,cli_args,env,files,"
            "outputs,key_symbols,deps,constraints,error,source_hash,updated_at,"
            "model,elapsed_ms")
    if paths:
        # 路径按「仓库内相对路径」匹配：允许带 ./ 前缀、允许 Windows 反斜杠
        norm = [p.replace("\\", "/").lstrip("./") for p in paths]
        rows = []
        for n in norm:
            r = conn.execute(f"SELECT {cols} FROM file_docs WHERE repo=? AND path=?",
                             (repo, n)).fetchone()
            if r is None:
                print(f"未收录: {n}（可能还没生成，或路径前缀不对）", file=sys.stderr)
            else:
                rows.append(r)
        if not rows:
            print("没有匹配到任何记录。可用 `list` 看实际路径写法。", file=sys.stderr)
            return 2
        full = True
    else:
        rows = list(conn.execute(
            f"SELECT {cols} FROM file_docs WHERE repo=? ORDER BY ok DESC, path LIMIT ?",
            (repo, limit)))

    if not rows:
        print("（还没有任何 file_docs；先跑 generate）", file=sys.stderr)
        return 1

    if as_json:
        keys = [c.strip() for c in cols.split(",")]
        out = []
        for r in rows:
            d = dict(zip(keys, r))
            for k in ("inputs", "cli_args", "env", "files", "outputs",
                      "key_symbols", "deps", "constraints"):
                try:
                    d[k] = json.loads(d[k]) if d.get(k) else []
                except Exception:
                    pass
            d["stale"] = _is_stale(root, repo, d)
            out.append(d)
        print(json.dumps(out, ensure_ascii=False, indent=2))
        return 0

    for (path, ok, conf, role, purpose, inputs, cli, env, files, outputs, syms,
         deps, cons, err, h, ts, model, ms) in rows:
        print("=" * 74)
        print(f"{'OK ' if ok else 'ERR'} {path}")
        if not ok:
            print(f"    生成失败：{err}")
            print(f"    记录时间：{ts}")
            continue
        print(f"    角色：{role}   置信：{conf}   耗时：{(ms or 0) / 1000:.1f}s   生成于 {ts}")
        if _is_stale(root, repo, {"path": path, "source_hash": h}):
            print("    ⚠ 源码已改动，此说明已过期；跑 generate 刷新")
        print(f"    作用：{purpose}")
        if full:
            # 输入分三类显示。老记录只有合并的 inputs，此时退回显示它，
            # 避免升级后旧数据看起来像「没有输入」。
            if cli is None and env is None and files is None:
                print(f"    输入：{_fmt_list(inputs)}   （旧记录，未分类）")
            else:
                print(f"    命令行参数：{_fmt_list(cli)}")
                print(f"    环境变量：{_fmt_list(env, '无（代码里没有读取环境变量）')}")
                print(f"    读写文件：{_fmt_list(files)}")
            print(f"    输出：{_fmt_list(outputs)}")
            nsym = len(json.loads(syms)) if syms else 0
            print(f"    关键符号（{nsym} 个）：{_fmt_list(syms)}")
            print(f"    依赖：{_fmt_list(deps)}")
            print(f"    改动约束：{_fmt_list(cons)}")
    print("=" * 74)
    if not full:
        print("提示：指定文件路径可看完整字段，如  show kb.py")
        print("      加 --json 可给程序消费。")
    return 0


def _is_stale(root: Path, repo: str, d: dict) -> bool:
    p = root / d["path"]
    if not p.is_file():
        return True
    try:
        return source_hash(p.read_text(encoding="utf-8", errors="replace")) != d["source_hash"]
    except Exception:
        return True


def cmd_stats(root: Path, repo: str) -> int:
    conn = open_db(root)
    total = conn.execute("SELECT COUNT(*) FROM file_docs WHERE repo=?", (repo,)).fetchone()[0]
    okn = conn.execute("SELECT COUNT(*) FROM file_docs WHERE repo=? AND ok=1", (repo,)).fetchone()[0]
    # 过期 = 已生成成功、但磁盘上的源码 hash 与记录不同。
    # 必须现场重算，不能靠表内自比：主键是 (repo,path)，同一文件只有一行。
    stale = missing = 0
    for rel, h in conn.execute(
            "SELECT path, source_hash FROM file_docs WHERE repo=? AND ok=1", (repo,)):
        p = root / rel
        if not p.is_file():
            missing += 1
            continue
        if source_hash(p.read_text(encoding="utf-8", errors="replace")) != h:
            stale += 1
    on_disk = len(iter_code_files(root))
    print(f"repo={repo} 记录={total} 成功={okn} 失败={total - okn} "
          f"过期={stale} 文件已删={missing} 磁盘代码文件={on_disk} 未覆盖={max(0, on_disk - total)}")
    return 0


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(prog="python -m distill.filedoc",
                                 description="用项目 LLM 为每个代码文件生成说明文档，存入 sqlite")
    ap.add_argument("--root", default=".", help="仓库根（含 .codeb）")
    ap.add_argument("--repo", default="codeb", help="repo 名，写入表主键")
    sub = ap.add_subparsers(dest="cmd", required=True)

    g = sub.add_parser("generate", help="生成/刷新说明文档")
    g.add_argument("paths", nargs="*", help="只处理这些文件（相对仓库根）；省略=全部")
    g.add_argument("--limit", type=int, default=0, help="最多处理几个（0=不限，测试用）")
    g.add_argument("--mode", default="openai", choices=["openai", "cmd", "none"],
                   help="LLM 后端；none 用于离线校验写入链路")
    g.add_argument("--force", action="store_true", help="hash 未变也重新生成")
    g.add_argument("-v", "--verbose", action="store_true")

    s = sub.add_parser("show", help="查看已生成的说明")
    s.add_argument("paths", nargs="*", help="要看的文件（相对仓库根）；省略=列最近 N 条摘要")
    s.add_argument("--limit", type=int, default=20, help="不指定路径时最多列几条")
    s.add_argument("--json", dest="as_json", action="store_true", help="输出 JSON，便于程序消费")
    sub.add_parser("stats", help="统计覆盖/失败/过期数量")
    sub.add_parser("list", help="列出将被处理的代码文件")

    args = ap.parse_args(argv)
    root = Path(args.root).resolve()
    if args.cmd == "list":
        fs = iter_code_files(root)
        for p in fs:
            print(p.relative_to(root).as_posix())
        print(f"\n共 {len(fs)} 个", file=sys.stderr)
        return 0
    if args.cmd == "show":
        return cmd_show(root, args.repo, args.limit, args.paths, False, args.as_json)
    if args.cmd == "stats":
        return cmd_stats(root, args.repo)
    files = None
    if args.paths:
        files = [root / p for p in args.paths]
        missing = [p for p in files if not p.is_file()]
        if missing:
            for m in missing:
                print(f"不存在: {m}", file=sys.stderr)
            return 2
    return cmd_generate(root, args.repo, files, args.limit, args.mode, args.force, args.verbose)


if __name__ == "__main__":
    raise SystemExit(main())
