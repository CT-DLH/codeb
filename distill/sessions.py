#!/usr/bin/env python3
"""sessions.py —— 把 DSH 原始会话读成"结构化素材"。

定位：蒸馏流水线的第 0 段（sense）。纯 stdlib（zstandard 可选），
**不写知识库、不调模型、不判断值不值得写**。只回答便宜的问题：
这个会话属于哪个仓库、哪些文件烧掉了探索成本、哪里出现了预期与实际的差。

设计约束（DESIGN.md + codeb/overview 硬契约）：
- 输出是素材，不是知识。落盘永远由 kb upsert 这个唯一写入口完成。
- 信号必须机械可折叠（计数、路径、错误位），语义判断留给上层。
- 一次会话的素材要能整份装进一个 prompt：每条摘录都有截断上限。

实测到的事件形状（v4，别再猜）：
- 每行一个 JSON；`session` 事件的 cwd/createdAt/id 在**顶层**，不在 data 里。
- `user/message` 的 data 只有 content/source/role/id，**没有 turn**；
  要位置就用行号 seq。`assistant/message`、`tool/call`、`tool/result` 的 turn 在 data 里。
- `tool/result` 的中文在控制台渲染不了，但文件本身是 UTF-8，所以输出走文件。
- 事件会被 surface 折叠（surfaceOp / sourceEventSeqs）：同一事实可能只存在于
  condensed 记录里，所以摘录要容错，取不到就当缺失而不是报错。

用法：
    python distill/sessions.py list
    python distill/sessions.py material --cwd codeb -o out.jsonl
    python distill/sessions.py report --cwd codeb -o out.md --min-cost 3
"""
from __future__ import annotations

import argparse
import io
import json
import os
import re
import subprocess
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_HOME = Path(os.path.expanduser("~")) / ".dsh" / "sessions"
PROJECT_BASES = ["D:/work/project"]

MAX_EXCERPT = 380
MAX_LISTS = 30
UUID_RE = re.compile(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", re.I)
SKIP_FILES = re.compile(r"(^|/)(node_modules|\.git|\.svelte-kit|dist|build|__pycache__)(/|$)")

# 用户纠正：短、直、不需要理解语义就能认出来
CORRECTION_RE = re.compile(
    r"(不对|不是这样|别写|不要|为什么不|怎么没|又重新|搞错|弄错|漏了|忘了|说了多少遍|请立即生效|规则变更)")
# 取舍句式：决策类知识的指纹
TRADEOFF_RE = re.compile(
    r"(而不是|刻意|因为|取舍|两种方案|选择了|之所以|代价是|省一个数量级|退化|宁可|不要|必须)")
# 自动生成的注入消息不是人的话，不能当"用户纠正"
AUTOMATED_RE = re.compile(r"^(This is an automatically generated checkpoint|Agent .* sent a message:)")


# ---------------------------------------------------------------- 解码

def decode_bytes(raw: bytes) -> bytes:
    """zstd skippable-frame 会话文件 → 明文。

    实测：`zstandard` 的 stream_reader 能整包解出；Node v24 的
    zlib.zstdDecompressSync 只解首帧（15MB 只回 279 字节），**所以解码必须走 Python**。
    zstandard 不在时退回 zstd CLI，用**文件重定向**而不是管道
    （Windows 沙箱下捕获 piped stdio 会 EPERM）。
    """
    try:
        import zstandard  # type: ignore
    except ImportError:
        return _decode_cli(raw)
    return zstandard.ZstdDecompressor().stream_reader(io.BytesIO(raw)).read()


def _decode_cli(raw: bytes) -> bytes:
    tmp_in = Path(os.environ.get("TEMP", ".")) / "kb_distill_in.zst"
    tmp_out = tmp_in.with_suffix(".out")
    tmp_in.write_bytes(raw)
    exe = None
    for cand in ("zstd", r"D:\Install\conda\Library\bin\zstd.exe"):
        try:
            subprocess.run([cand, "--version"], check=True,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            exe = cand
            break
        except Exception:
            continue
    if exe is None:
        raise RuntimeError("既没有 zstandard 模块也没有 zstd CLI，无法解码会话")
    with open(tmp_out, "wb") as fh:
        subprocess.run([exe, "-d", str(tmp_in), "-o", str(tmp_out)], check=True)
    return tmp_out.read_bytes()


def session_file(dirpath: Path) -> Path | None:
    for name in ("session.v4.jsonl.zstd", "session.v4.jsonl"):
        p = dirpath / name
        if p.is_file():
            return p
    return None


def parse_ts(value) -> datetime | None:
    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        except Exception:
            return None
    if not isinstance(value, (int, float)):
        return None
    sec = value / 1000.0 if value > 1e11 else float(value)
    return datetime.fromtimestamp(sec, tz=timezone.utc)


# ---------------------------------------------------------------- 路径归一

def norm_slash(p: str) -> str:
    return p.replace("\\", "/").rstrip("/")


def to_posix(p: Path) -> str:
    return str(p).replace("\\", "/")


def abs_path(target: str, cwd: str | None) -> str:
    """把会话里的路径参数变绝对（posix 斜杠），供分仓库与判文件用。"""
    t = target.strip().strip('"').strip("'")
    p = Path(t)
    if not p.is_absolute():
        base = Path(cwd) if cwd else Path.cwd()
        try:
            p = (base / t).resolve()
        except Exception:
            p = base / t
    return to_posix(p)


def repo_of(abs_posix: str, cwd: str | None) -> tuple[str | None, str]:
    """绝对路径 → (仓库名, 仓库内相对路径)。

    仓库名优先由**会话 cwd** 决定（cwd 就是那个仓库，这是最可靠的一手信息），
    再用项目基目录兜底跨仓库路径（例如在 codeb 会话里读 infohub 的文件）。
    都不命中 → (None, 原路径)，上层归到 external 桶，由人决定是否建仓库目录。
    """
    n = norm_slash(abs_posix)
    if cwd:
        c = norm_slash(cwd)
        if n.lower().startswith(c.lower() + "/"):
            head = Path(c).name.lower()
            return head, n[len(c) + 1:]
    for base in PROJECT_BASES:
        b = norm_slash(base)
        if n.lower().startswith(b.lower() + "/"):
            parts = n[len(b) + 1:].split("/")
            if len(parts) >= 2:
                return parts[0], "/".join(parts[1:])
    return None, n


def basename_of(p: str) -> str:
    return norm_slash(p).rsplit("/", 1)[-1]


def call_target(name: str, args: dict) -> str | None:
    for key in ("file_path", "path", "notebook_path"):
        v = args.get(key)
        if isinstance(v, str) and v.strip():
            return v
    return None


# ---------------------------------------------------------------- 文本

def text_of(content) -> str:
    """message.content[] → 纯文本。跳过 reasoning：它是草稿，不能当证据引用。"""
    if isinstance(content, str):
        return content
    out = []
    for blk in content or []:
        if isinstance(blk, dict) and blk.get("type") == "text":
            out.append(str(blk.get("text", "")))
    return "\n".join(out).strip()


def parse_args_field(raw):
    if isinstance(raw, dict):
        return raw
    if isinstance(raw, str):
        try:
            v = json.loads(raw)
            return v if isinstance(v, dict) else {}
        except Exception:
            return {}
    return {}


def excerpt(s: str, limit: int = MAX_EXCERPT) -> str:
    return re.sub(r"\s+", " ", s or "").strip()[:limit]


# ---------------------------------------------------------------- 折叠

def short_id(sid: str) -> str:
    """会话短名：去掉目录名里的 `session-` 前缀，只留 uuid 头 8 位。"""
    m = UUID_RE.search(sid or "")
    return m.group(0)[:8] if m else (sid or "")[:8]


def fold_session(path: Path, sid: str) -> dict:
    data = decode_bytes(path.read_bytes()) if path.suffix == ".zstd" else path.read_bytes()
    lines = data.decode("utf-8", "replace").splitlines()

    meta = {"session_id": sid, "compressed_bytes": path.stat().st_size,
            "raw_bytes": len(data), "lines": len(lines)}
    cwd: str | None = None

    file_cost: Counter = Counter()      # 绝对路径 → 探索成本
    cost_turns: dict[str, set] = defaultdict(set)
    dir_probed: Counter = Counter()
    edits: list[dict] = []
    failures: list[dict] = []
    corrections: list[dict] = []
    claims: list[dict] = []
    kb_writes: list[dict] = []
    kb_reads: Counter = Counter()
    tool_names: Counter = Counter()
    turns: set = set()
    model = None
    last_turn = None

    for i, line in enumerate(lines, 1):
        line = line.strip()
        if not line:
            continue
        try:
            ev = json.loads(line)
        except Exception:
            continue
        t = ev.get("type", "")
        d = ev.get("data") or {}
        turn = d.get("turn") if isinstance(d, dict) else None
        if isinstance(turn, int):
            turns.add(turn)
            last_turn = turn

        if t == "session":                       # 字段在顶层
            cwd = ev.get("cwd") or cwd
            meta["created_at"] = (parse_ts(ev.get("createdAt")) or
                                  parse_ts(ev.get("time")) or meta.get("created_at"))
            meta["parent"] = ev.get("parentSession")
            meta["version"] = ev.get("version")
        elif t == "session/title":
            meta["title"] = (d.get("title") if isinstance(d, dict) else None) or ev.get("title")
        elif t == "assistant/message":
            msg = d.get("message") or {}
            model = model or ((msg.get("source") or {}).get("model"))
            txt = text_of(msg.get("content"))
            if txt and len(claims) < MAX_LISTS * 3 and TRADEOFF_RE.search(txt):
                claims.append({"turn": turn, "seq": i, "excerpt": excerpt(txt)})
        elif t == "user/message":
            txt = text_of(d.get("content")) if isinstance(d, dict) else ""
            src = ((d.get("source") or {}).get("kind") if isinstance(d, dict) else None) or "user"
            if txt and src == "user" and not AUTOMATED_RE.search(txt) \
                    and CORRECTION_RE.search(txt):
                corrections.append({"turn": last_turn, "seq": i,
                                    "excerpt": excerpt(txt, 240)})
        elif t == "tool/call":
            name = d.get("name", "")
            tool_names[name] += 1
            a = parse_args_field(d.get("arguments"))
            tgt = call_target(name, a)
            if tgt and not SKIP_FILES.search(norm_slash(tgt)):
                ap = abs_path(tgt, cwd)
                is_file = Path(ap).is_file()
                if name in {"read"}:
                    file_cost[ap] += 1
                    cost_turns[ap].add(turn)
                elif name in {"edit", "write"}:
                    edits.append({"turn": turn, "seq": i, "path": ap,
                                  "new": name == "write", "on_file": is_file})
                elif name in {"grep", "glob"}:
                    if is_file:
                        file_cost[ap] += 2      # 对着单文件搜 = 真在读它
                        cost_turns[ap].add(turn)
                    else:
                        dir_probed[ap] += 1
            elif name == "mcp__codeb__kb_upsert":
                kb_writes.append({"turn": turn, "seq": i,
                                  "repo": a.get("repo"), "page": a.get("page"),
                                  "title": a.get("title"), "topic": a.get("topic"),
                                  "section": a.get("section"),
                                  "append": bool(a.get("append")),
                                  "find": excerpt(str(a.get("find") or ""), 80),
                                  "covers": a.get("covers")})
            elif name.startswith("mcp__codeb__"):
                kb_reads[name.replace("mcp__codeb__", "")] += 1
        elif t == "tool/result":
            msg = d.get("message") or {}
            if msg.get("isError"):
                failures.append({"turn": turn, "seq": i, "tool": d.get("name", ""),
                                 "excerpt": excerpt(text_of(msg.get("content")), 240)})

    # 按仓库聚合探索成本
    #
    # 实测偏差（必须过滤，否则 S1 全是假阳性）：
    #   1) 知识库自身的页（repo/<x>/...md）被读，是"用库"不是"产出库"，
    #      绝不能当成待沉淀的探索成本——但自读次数本身有价值，单独计数。
    #   2) 临时文件/已删除文件（.dsh/tmp-*, 早期存在后来没了的 src/**）
    #      在磁盘上已不存在，无法作为 covers，也没有可核对的对象。
    per_repo: dict[str, list[dict]] = defaultdict(list)
    dirs_per_repo: dict[str, list[dict]] = defaultdict(list)
    kb_page_reads = 0
    stale_reads = 0
    for tgt, n in file_cost.most_common():
        nrel = norm_slash(tgt)
        if "/repo/" in nrel or nrel.endswith("/repo"):
            kb_page_reads += n
            continue
        if not Path(tgt).is_file():
            stale_reads += n
            continue
        repo, rel = repo_of(tgt, cwd)
        per_repo[repo or "external"].append({
            "path": rel, "abs": tgt, "cost": n,
            "turns": len({x for x in cost_turns[tgt] if x is not None}),
        })
    for tgt, n in dir_probed.most_common(12):
        repo, rel = repo_of(tgt, cwd)
        dirs_per_repo[repo or "external"].append({"path": rel, "cost": n})

    created = meta.get("created_at")
    return {
        "kind": "session_material",
        "session_id": sid,
        "cwd": cwd,
        "cwd_repo": (basename_of(cwd).lower() if cwd else None),
        "title": meta.get("title"),
        "created": created.strftime("%Y-%m-%d %H:%M") if created else None,
        "turns": len(turns),
        "model": model,
        "size": {"compressed": meta["compressed_bytes"], "raw": meta["raw_bytes"],
                 "lines": meta["lines"]},
        "tools": dict(tool_names.most_common(20)),
        "kb_reads": dict(kb_reads),
        "kb_page_reads": kb_page_reads,     # 读自己库的页数（在用库，不是在产出库）
        "stale_reads": stale_reads,         # 路径已不存在，不可作为 covers
        "kb_writes": kb_writes[-MAX_LISTS:],
        "exploration": {r: v[:MAX_LISTS] for r, v in per_repo.items()},
        "dirs_probed": dirs_per_repo,
        "edits": [{**e, "path": e["path"]} for e in edits[:MAX_LISTS]],
        "failures": failures[:20],
        "corrections": corrections[:20],
        "claims": claims[:MAX_LISTS],
    }


# ---------------------------------------------------------------- 发现

def discover(home: Path, cwd_filter: str | None) -> list[tuple[Path, str, str]]:
    out = []
    if not home.is_dir():
        return out
    for slug_dir in sorted(home.iterdir()):
        if not slug_dir.is_dir():
            continue
        if cwd_filter and cwd_filter.lower() not in slug_dir.name.lower():
            continue
        for sd in sorted(slug_dir.iterdir()):
            if not sd.is_dir():
                continue
            f = session_file(sd)
            if f:
                out.append((f, slug_dir.name, sd.name))
    return out


def material_index(home: Path, cwd_filter: str | None) -> list[dict]:
    """便宜清单：不解码正文。"""
    rows = []
    for f, slug, sid in discover(home, cwd_filter):
        st = f.stat()
        rows.append({"session_id": sid, "slug": slug, "bytes": st.st_size,
                     "mtime": datetime.fromtimestamp(st.st_mtime).strftime("%Y-%m-%d %H:%M")})
    rows.sort(key=lambda r: -r["bytes"])
    return rows


# ---------------------------------------------------------------- 报告

def render_report(mats: list[dict], min_cost: int) -> str:
    L = ["# 会话素材报告", ""]
    L.append(f"会话 {len(mats)} 个，合计 {sum(m['size']['raw'] for m in mats)/1e6:.1f} MB 明文。"
             f"门槛：单文件探索成本 ≥ {min_cost}。")
    unwritten = [m for m in mats if not m["kb_writes"]]
    L.append(f"其中 **{len(unwritten)} 个会话一次都没调用过 kb upsert**"
             f"——这些会话的知识只存在于当时的上下文里。")
    for m in mats:
        L.append("")
        L.append(f"## {m['created'] or '?'} — {m['title'] or m['session_id'][:8]}")
        L.append(f"- cwd `{m['cwd']}` (repo `{m['cwd_repo']}`) / turns {m['turns']}"
                 f" / 明文 {m['size']['raw']/1e6:.1f}MB / model {m['model']}")
        if m.get("kb_page_reads") or m.get("stale_reads"):
            L.append(f"- 已剔除：读知识库自己的页 {m['kb_page_reads']} 次（在用库，不是产出库）"
                     f"、路径已不存在 {m['stale_reads']} 次")
        if m["kb_writes"]:
            got = ", ".join((w.get("page") or w.get("title") or w.get("topic") or "?")
                            for w in m["kb_writes"])
            L.append(f"- 已落库：{got}")
        else:
            L.append("- 已落库：**无**")
        for repo, items in sorted(m["exploration"].items(), key=lambda kv: -len(kv[1])):
            hot = [i for i in items if i["cost"] >= min_cost]
            if not hot:
                continue
            L.append(f"- 探索成本（仓库 `{repo}`）：")
            for i in hot[:12]:
                L.append(f"    - {i['cost']:>3}  {i['path']}  （{i['turns']} 回合）")
        for repo, items in m["dirs_probed"].items():
            if items:
                L.append(f"- 目录级搜索（仓库 `{repo}`，不算文件成本）："
                         + ", ".join(f"{i['path']}×{i['cost']}" for i in items[:6]))
        if m["corrections"]:
            L.append(f"- 用户纠正 {len(m['corrections'])} 处（S2，最高价值）：")
            for c in m["corrections"][:6]:
                L.append(f"    - t{c['turn']}/#{c['seq']}: {c['excerpt'][:180]}")
        if m["failures"]:
            L.append(f"- 失败 {len(m['failures'])} 次（S3 死路候选）：")
            for f in m["failures"][:6]:
                L.append(f"    - {f['tool']} t{f['turn']}: {f['excerpt'][:180]}")
        if m["claims"]:
            L.append(f"- 取舍句式 {len(m['claims'])} 处（S4 决策候选）：")
            for c in m["claims"][:4]:
                L.append(f"    - t{c['turn']}/#{c['seq']}: {c['excerpt'][:180]}")
    return "\n".join(L) + "\n"


# ---------------------------------------------------------------- CLI

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="DSH 会话 → 结构化素材")
    ap.add_argument("cmd", choices=["list", "material", "report"])
    ap.add_argument("--home", type=Path, default=DEFAULT_HOME)
    ap.add_argument("--cwd", default=None, help="按目录 slug 过滤（子串，如 codeb）")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--min-cost", type=int, default=3, dest="min_cost")
    ap.add_argument("-o", "--out", type=Path, default=None)
    args = ap.parse_args(argv)

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    if args.cmd == "list":
        txt = "\n".join(json.dumps(r, ensure_ascii=False)
                        for r in material_index(args.home, args.cwd))
    else:
        found = sorted(discover(args.home, args.cwd), key=lambda x: -x[0].stat().st_size)
        if args.limit:
            found = found[:args.limit]
        mats = []
        for f, _slug, sid in found:
            try:
                mats.append(fold_session(f, sid))
            except Exception as e:              # 单个会话坏掉不拖垮整批
                mats.append({"kind": "error", "session_id": sid, "error": str(e),
                             "size": {"raw": 0}, "kb_writes": [], "exploration": {},
                             "dirs_probed": {}, "turns": 0, "created": None})
        mats.sort(key=lambda m: m.get("created") or "")
        if args.cmd == "material":
            txt = "\n".join(json.dumps(m, ensure_ascii=False) for m in mats)
        else:
            txt = render_report([m for m in mats if m.get("kind") == "session_material"],
                                args.min_cost)

    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        # 约定：UTF-8 + LF + 无 BOM，输出走文件（控制台渲染不了中文）
        args.out.write_bytes(txt.replace("\r\n", "\n").encode("utf-8"))
        print(f"wrote {args.out} ({len(txt)} chars)")
    else:
        print(txt)
    return 0


if __name__ == "__main__":
    sys.exit(main())
