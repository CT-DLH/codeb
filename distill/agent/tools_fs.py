"""codeb 子 agent 的**文件与命令工具**。

设计约束（都来自实测，不是想象）：

1. **必须能改文件**。`spawn.py` 早期只有 read/grep，只能做「读范围问问题」，
   任何真改代码的任务都派不动——这是它一直没能承接真实派发的原因。

2. **每个 agent 的写权限必须是显式的白名单**，由 leader 在派发时给出。
   工具层再挡一道：越界写入直接拒绝并返回明确错误，而不是让模型「知道不该改」
   然后靠自觉（自觉在长上下文里会失效）。

3. **目录是相对某个根的**，避免 agent 越到别的仓库去。

4. 每个工具的失败都**返回文本而不是抛异常**。抛异常会被 openai-agents
   记成 tool error，模型看不到可读的错误，只会重试同一次调用。
"""
from __future__ import annotations

import glob as _glob
import io
import contextlib
import os
import subprocess
import sys
from pathlib import Path

# 每个子 agent 能碰的仓库根。leader 派发时必须用这里的键来限定范围。
ROOTS: dict[str, Path] = {
    "codeb": Path("D:/work/project/codeb"),
    "infohub": Path("D:/work/project/infohub"),
    "atomkgraph": Path("D:/work/project/knowledge_map/atomkgraph"),
}

# 允许改动的文件后缀。其余一律只读，防止 agent 顺手改了构建产物/锁文件。
EDIT_EXT = {".py", ".ts", ".tsx", ".mjs", ".cjs", ".js", ".json", ".yaml", ".yml", ".md", ".txt", ".sql"}

# 永远不允许改的东西（构建产物、依赖、版本锁、二进制）。
DENY_PATTERNS = [
    "node_modules/", "dist/", "build/", ".git/", "package-lock.json",
    "pnpm-lock.yaml", "*.pb", "*.db", "*.sqlite",
]


def resolve(path: str, root: str) -> Path | None:
    """把 agent 给的相对路径解析到某个仓库根下；跨根或越界返回 None。"""
    base = ROOTS.get(root)
    if base is None:
        return None
    p = Path(path)
    if p.is_absolute():
        # 只允许指向该仓库根内的绝对路径
        try:
            p.resolve().relative_to(base.resolve())
            return p.resolve()
        except ValueError:
            return None
    target = (base / p).resolve()
    try:
        target.relative_to(base.resolve())
    except ValueError:
        return None
    return target


def _denied(path: str) -> bool:
    n = path.replace("\\", "/").lower()
    return any(p.lower().rstrip("*") in n for p in DENY_PATTERNS)


def _read(path: str, max_lines: int) -> str:
    """内部实现：不做根解析，供 read_file / edit_file 共用。"""
    return ""


# ---------------------------------------------------------------- 语义块索引
# 类比虚拟内存：一个代码文件不是整体装进上下文，而是切成「块」，
# 上下文里只放索引（目录），用到哪块再按 key 调进来（缺页中断）。
import re as _re

# Python: def/class（含 async）；TS/JS: function / class / interface / enum / arrow
# 关键：name 必须紧跟在关键字之后（允许空白），不能再跨过类型注解去猜——
# 早先版本把 `def resolve(...)` 抽成 `e@44`，就是因为贪婪组抓到了返回类型里的字符。
_BLOCK_SIG = _re.compile(
    r"^(?P<indent>[ \t]*)"
    r"(?:(?:export|default|async|declare|abstract|public|private|static)\s+)*"
    r"(?P<kind>def|class|function|interface|enum|type)\s+"
    r"(?P<name>[A-Za-z_$][\w$]*)"
    r"|"
    r"^(?P<indent2>[ \t]*)"
    r"(?:(?:export|default|declare)\s+)*"
    r"(?:const|let|var)\s+(?P<name2>[A-Za-z_$][\w$]*)\s*=\s*(?:async\s*)?"
    r"(?:\([^)]*\)|[A-Za-z_$][\w$]*)\s*=>"
)


def _sig_info(line: str):
    """返回 (indent, name) 或 None。集中处理两个分支，避免调用方重复。"""
    m = _BLOCK_SIG.match(line)
    if not m:
        return None
    indent = m.group("indent") if m.group("indent") is not None else m.group("indent2")
    name = m.group("name") if m.group("name") is not None else m.group("name2")
    return len(indent.expandtabs(4)), name


def file_index(path: str, root: str = "infohub") -> str:
    """给一个代码文件建**语义块索引**：每块一行 `key:行号:签名`。

    这是「页表」——只放目录，不放正文。agent 预填充的上下文里放这个，
    需要某个块时再用 `read_block(key)` 把那一块调进来。

    **用语法树解析**（Python ast / TypeScript 编译器 API），不是正则：
      - key 带作用域前缀（`Scheduler._run_one`），解决同名 `__init__` 撞名
      - 边界精确（ast 的 end_lineno），不用猜缩进
      - 类块和方法块各有独立 key，是「可选粒度」而非重复入口
    """
    from semantic_blocks import parse_blocks, format_index

    p = resolve(path, root)
    if p is None:
        return f"路径越界或不存在：{path}（仓库 {root}）"
    if not p.exists():
        return f"文件不存在：{path}"
    if p.is_dir():
        return f"{path} 是目录（用 list_dir 看）"
    try:
        lines = p.read_text(encoding="utf-8", errors="replace").splitlines()
    except Exception as e:
        return f"读取失败：{type(e).__name__}: {e}"

    blocks, parser = parse_blocks(p)
    return format_index(path, blocks, parser, len(lines))


def read_block(path: str, key: str, root: str = "infohub") -> str:
    """按 `file_index` 给的 key 取一个语义块的完整正文（缺页中断）。

    边界来自语法树（ast 的 end_lineno / TS 编译器 API），不靠猜缩进。
    key 形如 `函数名@行号` 或 `类.方法@行号`（来自 file_index）。
    """
    from semantic_blocks import parse_blocks

    p = resolve(path, root)
    if p is None:
        return f"路径越界或不存在：{path}（仓库 {root}）"
    if not p.exists():
        return f"文件不存在：{path}"
    try:
        lines = p.read_text(encoding="utf-8", errors="replace").splitlines()
    except Exception as e:
        return f"读取失败：{type(e).__name__}: {e}"

    if "@" not in key:
        return f"key 格式应为 `名字@行号`（来自 file_index），收到：{key}"
    name, _, num = key.rpartition("@")
    try:
        start = int(num)
    except ValueError:
        return f"key 里的行号不是数字：{key}"

    blocks, parser = parse_blocks(p)
    # 优先按 name+start 精确匹配；退而按 start 匹配（兼容旧 key）
    block = next((b for b in blocks
                  if b["start"] == start and (b["name"] == name or b["raw_name"] == name)), None)
    if block is None:
        block = next((b for b in blocks if b["start"] == start), None)
    if block is None:
        near = [f"{b['name']}@{b['start']}" for b in blocks
                if abs(b["start"] - start) <= 5][:5]
        return (f"key 定位不到：{key}\n"
                f"  附近的 key：{near or '（无）'}\n"
                f"  用 file_index 重新取 key，不要凭旧行号猜。")

    s, e = block["start"], block["end"]
    body = "\n".join(f"{n:>5}  {lines[n-1]}" for n in range(s, min(e, len(lines)) + 1))
    return (f"{path}  块 {block['name']}@{s}（第 {s}-{e} 行，共 {e-s+1} 行，"
            f"{block['kind']}，解析器={parser}）\n{body}")


def read_file(path: str, max_lines: int = 150, root: str = "infohub") -> str:
    """读一个文件，返回前 max_lines 行，并附总行数。

    root 是仓库名（codeb/infohub/atomkgraph），决定相对路径的起点。
    """
    p = resolve(path, root)
    if p is None:
        return f"路径越界或不存在：{path}（仓库 {root}）"
    if not p.exists():
        return f"文件不存在：{path}"
    if p.is_dir():
        return f"{path} 是目录，不是文件（用 list_dir 看）"
    try:
        lines = p.read_text(encoding="utf-8", errors="replace").splitlines()
    except Exception as e:
        return f"读取失败：{type(e).__name__}: {e}"
    head = "\n".join(lines[:max_lines])
    more = "\n…（后面还有 %d 行，用 offset 继续读）" % (len(lines) - max_lines) if len(lines) > max_lines else ""
    return f"{path}（共 {len(lines)} 行，显示前 {min(max_lines, len(lines))} 行）\n{head}{more}"


def read_file_range(path: str, offset: int, limit: int = 150, root: str = "infohub") -> str:
    """从 offset（1 起）读一段，用于读大文件的中段。"""
    p = resolve(path, root)
    if p is None:
        return f"路径越界或不存在：{path}（仓库 {root}）"
    if not p.exists():
        return f"文件不存在：{path}"
    lines = p.read_text(encoding="utf-8", errors="replace").splitlines()
    start = max(1, offset)
    chunk = lines[start - 1: start - 1 + limit]
    return f"{path} 第 {start}-{start + len(chunk) - 1} 行（共 {len(lines)} 行）\n" + "\n".join(chunk)


def list_dir(path: str = ".", pattern: str = "*", root: str = "infohub") -> str:
    """列目录（单层），带文件大小。"""
    p = resolve(path, root)
    if p is None:
        return f"路径越界或不存在：{path}（仓库 {root}）"
    if not p.exists():
        return f"目录不存在：{path}"
    if not p.is_dir():
        return f"{path} 不是目录"
    out = []
    for f in sorted(p.glob(pattern)):
        if f.is_file():
            try:
                sz = f.stat().st_size
                out.append(f"{f.relative_to(ROOTS[root]).as_posix()}  ({sz} B)")
            except OSError:
                out.append(f.relative_to(ROOTS[root]).as_posix())
        if len(out) >= 100:
            out.append("…（最多 100 条）")
            break
    return "\n".join(out) if out else "（空）"


def resolve_loose(path: str, root: str) -> tuple[Path | None, str]:
    """比 `resolve` 宽容的路径解析：模型写裸文件名时按 basename 找。

    为什么要它：实测模型会把文件写成 `path: "Sidebar.tsx"`、`path: "App.tsx"`，
    意思是「那个文件」。严格按目录解析会返回「目录不存在」，
    模型看到这句会换一个更离谱的 path 重试（实测连试 `/app` `/root` `/home`
    `/tmp` `/workspace` 五个都试了），7 轮烧完仍然答不出。
    **这类失败不是模型的错，是工具把「文件」当成了「目录」。**

    返回 (路径, 备注)。备注非空时应当回显给模型，让它知道自己指的是哪个文件。
    """
    p = resolve(path, root)
    if p is not None and p.exists():
        return p, ""
    base = ROOTS.get(root)
    if base is None:
        return None, ""
    # 退化 1：把 path 当 basename，在仓库里找同名文件
    name = Path(path).name
    if not name:
        return None, ""
    matches = [f for f in base.rglob(name)
               if f.is_file() and not any(
                   seg in f.parts for seg in ("node_modules", "dist", ".git", ".cache"))]
    if len(matches) == 1:
        rel = matches[0].relative_to(base).as_posix()
        return matches[0], f"（按文件名匹配到 {rel}；下次可以直接写完整相对路径）"
    if len(matches) > 1:
        show = ", ".join(m.relative_to(base).as_posix() for m in matches[:5])
        return None, (f"路径 `{path}` 不存在；仓库里有 {len(matches)} 个同名文件："
                      f"{show}\n请用完整相对路径指定其中一个。")
    return None, ""


def _iter_files_under(path: str, root: str) -> tuple[list[Path], str]:
    """枚举要搜的文件，附带一条需要回显的说明（路径被宽松解析时非空）。"""
    p, note = resolve_loose(path, root)
    if p is None:
        return [], note
    if p.is_file():
        return [p], note
    out = []
    for f in sorted(p.rglob("*")):
        if not f.is_file() or f.suffix not in EDIT_EXT | {".toml"}:
            continue
        if "node_modules" in f.parts or "dist" in f.parts or ".git" in f.parts:
            continue
        out.append(f)
    return out, note


def _compile_or_literal(pattern: str):
    """正则优先；非法则退回字面子串。

    模型天然写正则（`^export function|^function`），只做字面匹配会让它
    「每次都没命中」，然后不断换写法。反过来，字面量里含 `(` `)` `[` 时
    正则编译会报错——所以必须两条路都留。
    """
    try:
        return _re.compile(pattern), ""
    except _re.error as e:
        return None, f"（正则非法，按字面匹配：{e}）"


def grep_text(pattern: str, path: str = ".", max_hits: int = 20, root: str = "infohub") -> str:
    """在目录（或单个文件）里搜，返回 路径:行号:内容。

    pattern 支持正则，非法时退回字面子串。
    path 可以是目录、相对路径，或裸文件名（实测模型常写后者）。
    """
    files, note = _iter_files_under(path, root)
    if not files:
        p = resolve(path, root)
        if p is not None and p.exists():
            return f"{path} 下没有可搜索的源码文件"
        return (f"路径不存在：{path}（仓库 {root}）"
                + (f"\n{note}" if note else "")
                + "\n可以用相对仓库根的路径，例如 apps/web/src/components/Sidebar.tsx；"
                  "或直接给文件名（会按 basename 匹配）。")
    rx, note2 = _compile_or_literal(pattern)
    base = ROOTS[root]
    out: list[str] = []
    for f in files:
        try:
            for i, line in enumerate(
                f.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
                hit = bool(rx.search(line)) if rx else (pattern in line)
                if hit:
                    try:
                        rel = f.relative_to(base).as_posix()
                    except ValueError:
                        rel = f.name
                    out.append(f"{rel}:{i}: {line.strip()[:120]}")
                    if len(out) >= max_hits:
                        head = f"命中已达上限 {max_hits} 条{note}{note2}"
                        return head + "\n" + "\n".join(out)
        except OSError:
            continue
    if not out:
        return (f"没有命中 `{pattern}`{note}{note2}\n"
                "（确认 pattern：它在别的仓库吗？大小写不同？需要正则吗？）")
    return f"命中 {len(out)} 条{note}{note2}\n" + "\n".join(out)


# ---------------------------------------------------------------- 归约型查询工具
#
# 这两个工具的存在理由是**实测出来的**，不是设计推导：
# 同一批「第几行 / 几个」的题，在 155k 全文上下文里答对 0/3；
# 给 grep（返回命中行）后只升到 1/3——模型拿到 30 行原料，自己数，数错；
# 换成直接返回条数的 grep_count 后升到 3/3。
#
# 所以：**让模型自己数，等于没算**。这与「算出来的信息不给，等于没算」
# （kb_dispatch 说「6 个文件」却不列出，被同一参数重调 3 次）是同一条教训的两面：
# 前者是「算了不给」，后者是「给了不给归约结果」。

def _iter_files(path: str, root: str):
    """按 kb 的选型口径枚举候选文件（只用 tools_fs 已有的 EDIT_EXT）。

    走 resolve_loose：模型写裸文件名时按 basename 找，而不是报「目录不存在」。
    """
    files, _note = _iter_files_under(path, root)
    yield from files


def _rel_to(f: Path, root: str) -> str:
    try:
        return f.relative_to(ROOTS[root]).as_posix()
    except ValueError:
        return f.name


def grep_count(pattern: str, path: str = ".", root: str = "infohub",
               max_show: int = 20) -> str:
    """**直接返回命中条数**——回答「有几个」时用它，不要自己数 grep 的输出。

    pattern 是 Python 正则（非法时退回字面子串匹配：模型常写 `let x =` 这种
    含正则元字符的字面量，直接报错会让它重试同一个调用）。
    """
    try:
        rx = _re.compile(pattern)
    except _re.error as e:
        rx = None
        compile_note = f"（正则非法，按字面匹配：{e}）"
    else:
        compile_note = ""

    n = 0
    where: list[str] = []
    files, note = _iter_files_under(path, root)
    if not files:
        return (f"路径不存在或没有可搜的源码：{path}（仓库 {root}）"
                + (f"\n{note}" if note else ""))
    for f in files:
        try:
            for i, line in enumerate(
                    f.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
                hit = bool(rx.search(line)) if rx else (pattern in line)
                if hit:
                    n += 1
                    if len(where) < max_show:
                        where.append(f"{_rel_to(f, root)}:{i}: {line.strip()[:100]}")
        except OSError:
            continue

    head = f"命中 {n} 条{note}{compile_note}"
    if n == 0:
        return head + (f"\n（没有命中 `{pattern}`。检查是否含不该有的正则元字符，"
                       "或换个路径）")
    return head + "\n" + "\n".join(where) + (
        f"\n…还有 {n - len(where)} 条未列出" if n > len(where) else "")


def find_line(literal: str, path: str = ".", root: str = "infohub",
              max_hits: int = 10) -> str:
    """定位一个字面量出现的 **文件:行号**——回答「第几行」时用它。

    与 grep_count 互补：那个给数量，这个给位置。两者都**不做算术**，
    模型只负责转述。
    """
    hits: list[str] = []
    files, note = _iter_files_under(path, root)
    if not files:
        return (f"路径不存在或没有可搜的源码：{path}（仓库 {root}）"
                + (f"\n{note}" if note else ""))
    for f in files:
        try:
            for i, line in enumerate(
                    f.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
                if literal in line:
                    hits.append(f"{_rel_to(f, root)}:{i}: {line.strip()[:120]}")
                    if len(hits) >= max_hits:
                        return (f"命中 {len(hits)} 处（已达上限 {max_hits}）{note}\n"
                                + "\n".join(hits))
        except OSError:
            continue
    if not hits:
        return (f"没有找到 `{literal}`{note}\n"
                "（确认一下字面量：是否多了空格、是否只是大小写不同、是否在别的仓库）")
    return f"命中 {len(hits)} 处{note}\n" + "\n".join(hits)


def _check_allowed(path: str, root: str, allowed: list[str], denied: list[str]) -> str | None:
    if _denied(path):
        return f"拒绝写入（命中永久禁止清单）：{path}"
    p = resolve(path, root)
    if p is None:
        return f"拒绝写入（路径越界或不存在）：{path}（仓库 {root}）"
    if p.suffix not in EDIT_EXT:
        return f"拒绝写入（后缀不在可改清单）：{path}"
    rel = p.relative_to(ROOTS[root]).as_posix()
    # 白名单为空 = 不限制；否则必须命中
    if allowed and not _match_any(rel, allowed):
        return (
            f"拒绝写入（不在本次白名单内）：{rel}\n"
            f"  白名单：{allowed}\n"
            f"  **不要重试、不要改用其他写法绕过、不要用 read_file 或其他工具间接改这个文件。**\n"
            f"  白名单之外你无权改动。请跳过这一步，在报告里明确写出「X 文件不在白名单内，未改动」，然后继续你白名单范围内的工作。"
        )
    for pat in denied:
        if _match_any(rel, [pat]):
            return (
                f"拒绝写入（命中派发时的禁止清单）：{rel}\n"
                f"  **不要重试、不要绕过。** 在报告里说明「X 文件被禁止改动，未改动」。"
            )
    return None


def _match_any(rel: str, patterns: list[str]) -> bool:
    """判断相对路径是否命中任一模式。

    支持三种写法：
      - `dir/`      目录前缀（含其下所有内容）
      - `*.ts`      fnmatch 通配（匹配完整相对路径或文件名）
      - `a/b.ts`    精确匹配
    """
    import fnmatch
    for pat in patterns:
        if pat.endswith("/"):
            if rel == pat or rel.startswith(pat) or rel.startswith(pat.rstrip("/") + "/"):
                return True
            continue
        if fnmatch.fnmatch(rel, pat) or fnmatch.fnmatch(Path(rel).name, pat):
            return True
    return False


# ---------------------------------------------------------------------------
# 写前快照与回滚（source of truth 在 session log，文件改动可撤销）。
# 每个文件每次写前存一份原文到 sidecar，失败/误改时按 snapshot_id 恢复。
# ---------------------------------------------------------------------------
import hashlib as _hashlib
import time as _time

SNAPSHOT_BASE = Path("D:/work/project/codeb/_kbwork/file-snapshots")


def _snapshot_dir(path: str, root: str) -> Path:
    """某个文件的快照目录（路径 hash，避免目录名里有斜杠）。"""
    h = _hashlib.sha1(f"{root}/{path}".encode("utf-8")).hexdigest()[:12]
    return SNAPSHOT_BASE / h


def _snapshot(path: str, root: str) -> str | None:
    """写前存原文快照，返回 snapshot_id；文件不存在返回 None。"""
    p = resolve(path, root)
    if p is None or not p.exists():
        return None
    d = _snapshot_dir(path, root)
    d.mkdir(parents=True, exist_ok=True)
    sid = "%012d" % int(_time.time() * 1e6)
    snap = d / f"{sid}.txt"
    try:
        snap.write_text(p.read_text(encoding="utf-8"), encoding="utf-8")
    except Exception:
        return None
    return sid


def rollback_file(path: str, root: str = "infohub",
                  snapshot_id: str | None = None) -> str:
    """把文件恢复到某次写前的原文。不传 snapshot_id 就取最近一次快照。"""
    chk = _check_allowed(path, root, [], [])
    if chk:
        return chk
    p = resolve(path, root)
    if p is None:
        return f"回滚失败：路径越界 {path}"
    d = _snapshot_dir(path, root)
    if not d.exists():
        return f"回滚失败：{path} 没有快照记录"
    if snapshot_id:
        snap = d / f"{snapshot_id}.txt"
        if not snap.exists():
            return f"回滚失败：快照 {snapshot_id} 不存在（可用 snap_list 查）"
    else:
        snaps = sorted(d.glob("*.txt"))
        if not snaps:
            return f"回滚失败：{path} 没有快照记录"
        snap = snaps[-1]
    try:
        p.write_text(snap.read_text(encoding="utf-8"), encoding="utf-8")
    except Exception as e:
        return f"回滚失败：{type(e).__name__}: {e}"
    return f"✓ 已回滚 {path} ← 快照 {snap.stem}"


def snap_list(path: str, root: str = "infohub") -> str:
    """列出某文件的所有快照 id（最新在后）。"""
    d = _snapshot_dir(path, root)
    if not d.exists():
        return f"（无快照：{path}）"
    snaps = sorted(s.stem for s in d.glob("*.txt"))
    return f"{path} 快照 {len(snaps)} 个：" + ", ".join(snaps[-10:]) if snaps else f"（无快照：{path}）"


def edit_file(path: str, old: str, new: str, root: str = "infohub",
              allowed: list[str] = [], denied: list[str] = [],
              replace_all: bool = False) -> str:
    """在文件里把 old 字面替换成 new。

    old 必须**精确匹配**（含空白标点）。找不到就报错，绝不静默不动——
    静默不动会让 agent 以为改成功了，然后基于错误前提继续写。
    """
    chk = _check_allowed(path, root, allowed, denied)
    if chk:
        return chk
    p = resolve(path, root)
    try:
        text = p.read_text(encoding="utf-8")
    except Exception as e:
        return f"读取失败：{type(e).__name__}: {e}"
    n = text.count(old)
    if n == 0:
        return (f"替换失败：在 {path} 里找不到这段原文（必须精确匹配，含空白标点）\n"
                f"  找原文用 read_file / grep_text，不要凭记忆写。")
    if n > 1 and not replace_all:
        return (f"替换中止：这段原文在 {path} 里出现 {n} 次。\n"
                f"  请用更精确的 old（带上前后几行）或显式传 replace_all=true。")
    sid = _snapshot(path, root)
    p.write_text(text.replace(old, new, -1 if replace_all else 1), encoding="utf-8")
    return f"✓ 已替换 {path}（{n} 处）" + (f" [快照 {sid}]" if sid else "")


def write_file(path: str, content: str, root: str = "infohub",
               allowed: list[str] = [], denied: list[str] = []) -> str:
    """新建或整篇覆盖一个文件。"""
    chk = _check_allowed(path, root, allowed, denied)
    if chk:
        return chk
    p = resolve(path, root)
    sid = _snapshot(path, root)
    try:
        p.write_text(content, encoding="utf-8")
    except Exception as e:
        return f"写入失败：{type(e).__name__}: {e}"
    return (f"✓ 已写入 {path}（{len(content.splitlines())} 行）"
            + (f" [快照 {sid}]" if sid else ""))


def append_file(path: str, content: str, root: str = "infohub",
                allowed: list[str] = [], denied: list[str] = []) -> str:
    """往文件末尾追加（自动空行分隔）。"""
    chk = _check_allowed(path, root, allowed, denied)
    if chk:
        return chk
    p = resolve(path, root)
    sid = _snapshot(path, root)
    try:
        with p.open("a", encoding="utf-8") as f:
            f.write("\n" + content.rstrip() + "\n")
    except Exception as e:
        return f"追加失败：{type(e).__name__}: {e}"
    return f"✓ 已追加到 {path}" + (f" [快照 {sid}]" if sid else "")


def run_cmd(cmd: str, root: str = "infohub", cwd: str = ".",
            timeout_sec: int = 180) -> str:
    """在仓库里跑一条命令，返回退出码与输出。

    只给子 agent 跑验证类命令（tsc / 测试 / 构建）。**不是通用 shell**：
    没有 cd 之外的 shell 解析，cwd 必须是仓库内的相对路径。
    """
    base = ROOTS.get(root)
    if base is None:
        return f"未知仓库：{root}（可用：{', '.join(ROOTS)}）"
    work = (base / cwd).resolve() if cwd not in (".", "") else base.resolve()
    try:
        work.relative_to(base.resolve())
    except ValueError:
        return f"cwd 越界：{cwd}"
    # Windows 上用 shell 启动，让 node/npx/pnpm 能找到
    try:
        r = subprocess.run(cmd, shell=True, cwd=str(work), capture_output=True,
                           text=True, encoding="utf-8", errors="replace",
                           timeout=timeout_sec)
    except subprocess.TimeoutExpired:
        return f"超时（>{timeout_sec}s）：{cmd}"
    out = (r.stdout + ("\n[stderr]\n" + r.stderr if r.stderr.strip() else "")).strip()
    if len(out) > 6000:
        out = out[:6000] + "\n…（输出过长已截断）"
    if r.returncode != 0:
        return f"退出码 {r.returncode}\n{out}"
    return f"退出码 0\n{out}"


def diff_summary(path: str, root: str = "infohub") -> str:
    """读一个文件的行数与首尾几行，用于报告「改了什么」。"""
    p = resolve(path, root)
    if p is None or not p.exists():
        return f"（不存在：{path}）"
    lines = p.read_text(encoding="utf-8", errors="replace").splitlines()
    head = "\n".join(lines[:6])
    tail = "\n".join(lines[-6:]) if len(lines) > 12 else ""
    return f"{path}（{len(lines)} 行）\n--- 头部 ---\n{head}\n--- 尾部 ---\n{tail}"
