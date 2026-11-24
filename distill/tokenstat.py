"""tokenstat：统计一个仓库的源码，作为 LLM 输入要花多少 token。

为什么单独成工具，而不是并进 filedoc：
  这是一个**纯测量**工具，不写库、不调 LLM、不改任何源码。
  测量工具要能被反复跑、被信任，就不能夹带副作用。

两种口径都给，因为它们的用途不同：
  exact ：tiktoken 真分词。准确，但要加载 BPE 词表（首次约 30s，之后有缓存）。
  est   ：复用 kb.py 的 est_tokens（CJK 1 tok/字，其余 3.5 字符/tok）。
          粗糙但和项目内部所有预算判断同口径——两边数字应当对得上。

选型口径完全复用 kb.py，不另起一套：
  CODE_EXT / CONF_EXT / SRC_SKIP，以及 .kbignore。
  自己再写一遍过滤规则，就一定会和 kb pack 的「源码」定义漂移，
  然后两个工具报出两个不同的「本项目有多少 token」。
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import kb  # noqa: E402  复用选型口径与 est_tokens

# kb.SRC_SKIP 没覆盖的、本机运行时产物。不改 kb.SRC_SKIP 本身：
# 那会影响 kb pack / reindex 的既有行为，属于「统计工具顺手改了别人的口径」。
# 只在这里追加，因为这些东西确实不是本项目源码，算进 token 会虚高。
EXTRA_SKIP = {".dsh-created-plugins", "_kbwork", "_tmp", ".mypy_cache"}


# 常用编码：不同模型分词不同，报错时差距可达 20% 以上，所以允许切换。
ENCODINGS = {
    "cl100k_base": "GPT-4 / GPT-3.5 系列（也用近似多数 OpenAI 兼容端点）",
    "o200k_base": "GPT-4o / o1 系列",
    "p50k_base": "Codex / 早期代码模型",
}

_CACHE: dict[str, object] = {}


def get_enc(name: str):
    if name not in _CACHE:
        import tiktoken
        _CACHE[name] = tiktoken.get_encoding(name)
    return _CACHE[name]


def collect_files(root: Path, exts: set[str], use_ignore: bool = True) -> list[Path]:
    """按 kb.py 的口径枚举文件（含 SRC_SKIP 与 .kbignore）。"""
    base = root
    rules = None
    if use_ignore:
        rules = kb.IgnoreRules.load(root)
        if len(rules) == 0:
            rules = None

    out: list[Path] = []
    stack = [("", base)]
    while stack:
        rel_dir, cur = stack.pop()
        try:
            entries = list(cur.iterdir())
        except OSError:
            continue
        for e in entries:
            if not e.is_file():
                if e.is_dir() and not e.is_symlink():
                    stack.append((f"{rel_dir}/{e.name}" if rel_dir else e.name, e))
                continue
            if any(part in kb.SRC_SKIP or part in EXTRA_SKIP for part in e.parts):
                continue
            if e.suffix not in exts:
                continue
            rel = f"{rel_dir}/{e.name}" if rel_dir else e.name
            if rules is not None:
                if rules.ignored(f"{base.name}/{rel}"):
                    continue
            out.append(e)
    return sorted(out)


def measure(root: Path, exts: set[str], enc_name: str | None,
            use_ignore: bool = True) -> dict:
    files = collect_files(root, exts, use_ignore)
    enc = get_enc(enc_name) if enc_name else None

    rows = []
    tot_chars = tot_bytes = tot_exact = tot_est = 0
    t0 = time.time()
    for f in files:
        try:
            text = kb._read_text_robust(f)
        except Exception as e:  # 读到一半失败也要留痕，不静默跳过
            rows.append({"path": f.relative_to(root).as_posix(), "error": str(e)[:120]})
            continue
        ch = len(text)
        by = len(text.encode("utf-8", "replace"))
        ex = len(enc.encode(text, disallowed_special=())) if enc else 0
        es = kb.est_tokens(text)
        tot_chars += ch
        tot_bytes += by
        tot_exact += ex
        tot_est += es
        rows.append({
            "path": f.relative_to(root).as_posix(),
            "chars": ch, "bytes": by,
            "tokens": ex if enc else es,
            "tokens_exact": ex, "tokens_est": es,
            "lines": text.count("\n") + 1,
            "ext": f.suffix,
        })
    return {
        "root": str(root), "repo": root.name, "encoding": enc_name,
        "files": len(rows), "elapsed_s": round(time.time() - t0, 2),
        "totals": {"chars": tot_chars, "bytes": tot_bytes,
                   "tokens": tot_exact if enc else tot_est,
                   "tokens_exact": tot_exact, "tokens_est": tot_est},
        "rows": rows,
    }


def _fmt(n: int) -> str:
    return f"{n:,}"


def print_report(res: dict, by_ext: bool, by_file: int, as_json: bool) -> None:
    if as_json:
        print(json.dumps(res, ensure_ascii=False, indent=2))
        return
    t = res["totals"]
    print("=" * 78)
    print(f"仓库：{res['repo']}   ({res['root']})")
    print("=" * 78)
    print(f"文件数          : {_fmt(res['files'])}")
    print(f"字符数          : {_fmt(t['chars'])}")
    print(f"UTF-8 字节      : {_fmt(t['bytes'])}")
    if res["encoding"]:
        print(f"tokens(exact)   : {_fmt(t['tokens_exact'])}   "
              f"[{res['encoding']}]")
        print(f"tokens(est)     : {_fmt(t['tokens_est'])}   "
              f"[kb.est_tokens，差 {t['tokens_exact'] - t['tokens_est']:+,}]")
        if t["tokens_est"]:
            print(f"est 相对 exact 偏差: {(t['tokens_exact'] / t['tokens_est'] - 1):+.1%}")
    else:
        print(f"tokens(est)     : {_fmt(t['tokens_est'])}   [kb.est_tokens]")
    print(f"耗时            : {res['elapsed_s']}s")

    if by_ext:
        agg: dict[str, list[int]] = {}
        for r in res["rows"]:
            if "error" in r:
                continue
            a = agg.setdefault(r["ext"] or "(无扩展名)", [0, 0, 0])
            a[0] += 1
            a[1] += r["chars"]
            a[2] += r["tokens"]
        print(f"\n{'扩展名':12s} {'文件数':>7s} {'字符':>12s} {'tokens':>12s} {'占比':>7s}")
        total = sum(v[2] for v in agg.values()) or 1
        for ext, (n, ch, tk) in sorted(agg.items(), key=lambda kv: -kv[1][2]):
            print(f"{ext:12s} {n:7d} {_fmt(ch):>12s} {_fmt(tk):>12s} {tk / total:7.1%}")

    if by_file:
        valid = [r for r in res["rows"] if "error" not in r]
        print(f"\n-- tokens 最多的 {min(by_file, len(valid))} 个文件 --")
        for r in sorted(valid, key=lambda x: -x["tokens"])[:by_file]:
            print(f"{_fmt(r['tokens']):>10s}  {r['path']}")

    errs = [r for r in res["rows"] if "error" in r]
    if errs:
        print(f"\n读取失败 {len(errs)} 个（未计入合计）：")
        for r in errs[:10]:
            print(f"  {r['path']}: {r['error']}")


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(
        prog="python -m distill.tokenstat",
        description="统计仓库源码作为 LLM 输入要消耗多少 token")
    ap.add_argument("repos", nargs="+", help="仓库路径，可给多个")
    ap.add_argument("--encoding", default="cl100k_base",
                    choices=list(ENCODINGS) + ["none"],
                    help="分词器；none=只用 kb.est_tokens 粗估（不加载词表，快）")
    ap.add_argument("--code-only", action="store_true",
                    help="只算代码文件（不含 yaml/json/sql 等配置）")
    ap.add_argument("--ext", action="append", default=None,
                    help="额外指定扩展名，如 --ext .md（可重复）")
    ap.add_argument("--by-ext", action="store_true", help="按扩展名分组")
    ap.add_argument("--by-file", type=int, default=0, metavar="N",
                    help="列出 tokens 最多的 N 个文件")
    ap.add_argument("--no-ignore", action="store_true", help="忽略 .kbignore")
    ap.add_argument("--json", dest="as_json", action="store_true")
    args = ap.parse_args(argv)

    exts = set(kb.CODE_EXT if args.code_only else kb.SRC_EXT)
    if args.ext:
        exts |= {e if e.startswith(".") else "." + e for e in args.ext}

    enc = None if args.encoding == "none" else args.encoding
    rc = 0
    for r in args.repos:
        root = Path(r).resolve()
        if not root.is_dir():
            print(f"不是目录: {root}", file=sys.stderr)
            rc = 2
            continue
        res = measure(root, exts, enc, use_ignore=not args.no_ignore)
        print_report(res, args.by_ext, args.by_file, args.as_json)
        print()
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
