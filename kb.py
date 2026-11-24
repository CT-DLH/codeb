#!/usr/bin/env python3
"""codeb core —— 多仓库知识库的基座。

目录约定（唯一的强制结构）：

    <root>/
    ├── .codeb                根标记，工具据此向上查找
    └── repo/
        ├── _shared/          跨仓库通用知识
        └── <repo-name>/      每个仓库一个目录，用英文名
            └── <topic>/...   主题按路径折叠，不堆在同一层

页面就是 .md 文件，标题随意组织。工具只做四件事：
下行浏览、读一页、读一节、从源码文件上行反查。再加上「命中即更新、miss 即补充」的 upsert。

命令：
  tree     下行浏览（按路径折叠展示）
  read     读一页，或按标题只取一节
  heads    列出一页的所有标题
  search   全库搜词
  where    上行反查：源码文件被哪些页面覆盖
  upsert   命中即更新、miss 即补充（模型维护知识库的唯一写入口）
  init     初始化库骨架

输出：默认人读文本；`--json` 给程序（MCP 层依赖它，字段一旦变更需同步改 TS）。
"""

from __future__ import annotations

import argparse
import contextlib
import hashlib
import json
import math
import os
import re
import sqlite3
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

ROOT_MARKER = ".codeb"
REPO_DIR = "repo"
SHARED = "_shared"
INDEX_NAME = "codeb-index.db"          # sqlite 派生索引（md 仍是 source of truth）
INDEX_SCHEMA_VERSION = 2   # v2：blocks 增加 purpose / purpose_src

# sqlite 是 stdlib，不破坏 kb.py 零外部依赖的约束。
# 表设计对应「页表」比喻：blocks = 源码页表，covers/pages = 知识页表。
INDEX_DDL = """
CREATE TABLE IF NOT EXISTS meta (
  key TEXT PRIMARY KEY,
  value TEXT
);
CREATE TABLE IF NOT EXISTS pages (
  repo TEXT NOT NULL,
  rel  TEXT NOT NULL,
  title TEXT,
  updated TEXT,
  path TEXT NOT NULL,            -- repo 内相对路径（含 .md）
  PRIMARY KEY (repo, rel)
);
CREATE TABLE IF NOT EXISTS covers (
  repo TEXT NOT NULL,
  page_rel TEXT NOT NULL,        -- 指向 pages.rel
  path TEXT NOT NULL,            -- covers 声明的源码路径（裸或带仓库前缀）
  is_dir INTEGER NOT NULL DEFAULT 0,
  PRIMARY KEY (repo, page_rel, path)
);
CREATE TABLE IF NOT EXISTS blocks (
  repo TEXT NOT NULL,
  file TEXT NOT NULL,            -- 仓库内相对路径
  key TEXT NOT NULL,             -- Class.method@line
  name TEXT NOT NULL,
  kind TEXT NOT NULL,
  start INTEGER NOT NULL,
  end INTEGER NOT NULL,
  sig TEXT,
  scope TEXT,
  purpose TEXT,                  -- 用途（docstring 首行 / 紧邻注释）；取不到为空
  purpose_src TEXT,              -- docstring | comment | 空
  PRIMARY KEY (repo, file, key)
);
CREATE INDEX IF NOT EXISTS idx_blocks_name ON blocks(repo, name);
CREATE INDEX IF NOT EXISTS idx_covers_path ON covers(repo, path);
CREATE INDEX IF NOT EXISTS idx_pages_path ON pages(repo, path);
"""


def index_db_path(root: Path) -> Path:
    """派生索引路径：_kbwork/codeb-index.db。"""
    return root / "_kbwork" / INDEX_NAME


def open_index(db_path: Path):
    """打开（必要时建表）sqlite 索引，返回 connection。

    老库升级：CREATE TABLE IF NOT EXISTS 不会给已有表加列，
    所以这里显式补列——否则 v1 的库永远没有 purpose 字段。
    """
    import sqlite3
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.executescript(INDEX_DDL)
    have = {r[1] for r in conn.execute("PRAGMA table_info(blocks)")}
    for col, decl in (("purpose", "TEXT"), ("purpose_src", "TEXT")):
        if col not in have:
            conn.execute(f"ALTER TABLE blocks ADD COLUMN {col} {decl}")
    conn.commit()
    return conn
SKIP_PREFIX = (".", "_")

_CJK = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff\u3040-\u30ff]")
_SLUG_BAD = re.compile(r"[^a-z0-9]+")


class IgnoreRules:
    """兼容层：`.kbignore` 已停用，选型规则的唯一来源是 git。

    原先另立 `.kbignore` 当「第二套真值」，两份规则会互相矛盾——实测
    `webview/` 的 8 个文件都已进 git，却被 `.kbignore` 排除，`pack/dispatch`
    报「0 个代码文件」，而 `route --around` 又能看见它们。两条路径对同一批
    文件给出相反结论，正是双真值的代价。

    现在 `ignored()` 恒为 False；`prune_dir()` 只保留依赖/产物目录的兜底跳过，
    它们在 git 不可用时仍需挡住 node_modules/dist 这类噪音。
    """

    def __init__(self, rules: list | None = None):
        self._rules = rules or []

    def __len__(self) -> int:
        return len(self._rules)

    @classmethod
    def load(cls, root: Path | None = None) -> "IgnoreRules":
        return cls([])

    @classmethod
    def parse(cls, text: str) -> "IgnoreRules":
        return cls([])

    def ignored(self, rel: str) -> bool:
        return False

    def excluded(self, rel: str) -> bool:
        return False

    def prune_dir(self, rel: str) -> bool:
        parts = rel.replace("\\", "/").split("/")
        return any(part in SRC_SKIP for part in parts)

    def walk(self, base: Path, exts: set[str], repo: str = "") -> list[str]:
        out = []
        for f in sorted(base.rglob("*")):
            if f.is_file() and f.suffix in exts and not self.prune_dir(
                    f.relative_to(base).as_posix()):
                out.append(f.relative_to(base).as_posix())
        return out


def est_tokens(text: str) -> int:
    """粗估 token：CJK 1 字符 1 tok，其余 3.5 字符 1 tok（偏保守，安全方向）。"""
    cjk = len(_CJK.findall(text))
    return math.ceil(cjk + (len(text) - cjk) / 3.5)


def slugify(text: str) -> str:
    """英文 slug。中文标题会退化成空串，交给调用方回退。"""
    s = _SLUG_BAD.sub("-", text.lower()).strip("-")
    return s[:60]


def fallback_slug(text: str) -> str:
    """中文标题的稳定文件名：取内容哈希前 10 位。

    不能用随机数或序号——同一标题重复 upsert 必须落到同一个文件名，否则幂等失效。
    """
    import hashlib
    return "page-" + hashlib.sha1(text.encode("utf-8")).hexdigest()[:10]


# --------------------------------------------------------------------- 路径

def find_root(explicit: str | None) -> Path:
    if explicit:
        return Path(explicit).resolve()
    cur = Path.cwd().resolve()
    for d in (cur, *cur.parents):
        if (d / ROOT_MARKER).exists():
            return d
    return cur


def repo_root(root: Path) -> Path:
    return root / REPO_DIR


def skipped(name: str) -> bool:
    return name.startswith(SKIP_PREFIX)


def norm(p: str) -> str:
    p = p.replace("\\", "/").strip()
    while p.startswith("./"):
        p = p[2:]
    return p.strip("/")


# --------------------------------------------------------------- 页面解析

_HEAD = re.compile(r"^(#{1,6})[ \t]+(.+?)[ \t]*#*[ \t]*$")


def iter_headings(body: str):
    """产出 (行号, 级别, 标题)。跳过代码围栏内的伪标题。"""
    in_fence, fence = False, ""
    for i, line in enumerate(body.splitlines()):
        s = line.lstrip()
        if s.startswith("```") or s.startswith("~~~"):
            marker = s[:3]
            if not in_fence:
                in_fence, fence = True, marker
            elif marker == fence:
                in_fence, fence = False, ""
            continue
        if in_fence:
            continue
        m = _HEAD.match(line)
        if m:
            yield i, len(m.group(1)), m.group(2).strip()


def split_frontmatter(text: str) -> tuple[dict, str]:
    """极简 frontmatter：只支持 `key: value`、行内数组与 `- item` 列表。"""
    lines = text.splitlines()
    if not lines or lines[0].strip() not in ("---", "+++"):
        return {}, text
    end = None
    for i in range(1, len(lines)):
        if lines[i].strip() in ("---", "+++"):
            end = i
            break
    if end is None:
        return {}, text

    meta: dict = {}
    key = None
    for line in lines[1:end]:
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        m = re.match(r"^([A-Za-z0-9_-]+)\s*:\s*(.*)$", line)
        if m:
            key, val = m.group(1), m.group(2).strip()
            if val == "":
                meta[key] = []
            elif val.startswith("[") and val.endswith("]"):
                meta[key] = [v.strip().strip("'\"") for v in val[1:-1].split(",") if v.strip()]
            else:
                meta[key] = val.strip("'\"")
            continue
        m2 = re.match(r"^\s*-\s+(.+)$", line)
        if m2 and key is not None:
            if not isinstance(meta.get(key), list):
                meta[key] = []
            meta[key].append(m2.group(1).strip().strip("'\""))
    return meta, "\n".join(lines[end + 1:])


@dataclass
class Page:
    path: Path
    rel: str               # 相对 repo/ 的路径，不含 .md：infohub/collector/architecture
    title: str
    covers: list[str] = field(default_factory=list)
    body: str = ""
    parent: str = ""       # 拆分来源页的 rel；空表示顶层页
    disk: str = ""         # 该仓库代码在磁盘上的根（frontmatter 的 root:）

    @property
    def repo(self) -> str:
        return self.rel.split("/")[0]

    @property
    def topic_dir(self) -> str:
        parts = self.rel.split("/")[:-1]
        return "/".join(parts)

    def hint(self, limit: int = 44) -> str:
        """取正文首段的普通句子，用于在英文标题旁给一行中文提示。

        跳过标题、列表项、表格、代码、引用——它们截断后读起来不知所云。
        """
        in_fence = False
        for line in self.body.splitlines():
            s = line.strip()
            if s.startswith("```") or s.startswith("~~~"):
                in_fence = not in_fence
                continue
            if in_fence or not s:
                continue
            if s[:1] in "#|-*>0123456789":
                continue
            s = re.sub(r"[*_\[\]]", "", s)
            s = s.replace("`", "")                  # 保留行内代码的内容，只去掉反引号
            s = re.sub(r"\([^)]*\)", "", s).strip()
            if len(s) < 8:
                continue
            return s[:limit] + ("…" if len(s) > limit else "")
        return ""


def load_page(root: Path, path: Path) -> Page:
    # utf-8-sig 去 BOM；统一成 LF——Windows 上手工编辑常留下 CRLF，
    # 而 CRLF 会让「按行切片」把小节切错，是跨平台最隐蔽的一类 bug。
    text = _read_text_robust(path)
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    meta, body = split_frontmatter(text)
    # 标题优先取 frontmatter 的 title:（显式声明），回退到正文首个 H1，
    # 最后才是文件名。
    # 必须优先用 frontmatter：正文 H1 常被写成中文，而「标题用英文」是硬规则
    # （中文标题会撞 fallback_slug 哈希文件名的缺陷）。回退到 H1 会把
    # 这个规则的成败交给正文写法，于是正文改一个字就破坏了标题规范。
    title = str(meta.get("title") or "").strip().strip("'\"")
    if not title:
        title = next((t for _, _, t in iter_headings(body)), path.stem)
    covers = meta.get("covers") or []
    if isinstance(covers, str):
        covers = [covers]
    # parent 表达「这一页是从哪一页拆出来的」，是弱引用：指向不存在的页
    # 不阻断（与 covers「意图不是存在断言」一致），只在 tree 里报警。
    parent = meta.get("parent") or ""
    if isinstance(parent, list):
        parent = parent[0] if parent else ""
    parent = str(parent).strip().strip("'\"")
    if parent.endswith(".md"):
        parent = parent[:-3]
    # root: 是「坐标」不是「分类」。它指向这个仓库的代码在磁盘上的位置，
    # 推不出来（atomkgraph 的代码在 knowledge_map/ 下，不与仓库同名）。
    # 它与 manifest.toml 的区别正在这里：坐标写错会立刻表现为「源码不可读」，
    # 而分类标签填错没人看得出来。
    disk = meta.get("root") or ""
    if isinstance(disk, list):
        disk = disk[0] if disk else ""
    disk = str(disk).strip().strip("'\"")
    base = repo_root(root)
    return Page(path=path, rel=path.relative_to(base).as_posix()[:-3],
                title=title, covers=list(covers), body=body,
                parent=norm(parent) if parent else "", disk=disk)


def repo_dirs(root: Path) -> list[Path]:
    """repo/ 下的一级目录。`_shared` 是保留目录，要显式放行。"""
    base = repo_root(root)
    if not base.is_dir():
        return []
    out = []
    for d in sorted(base.iterdir()):
        if not d.is_dir():
            continue
        if d.name == SHARED or not skipped(d.name):
            out.append(d)
    return out


def all_pages(root: Path):
    base = repo_root(root)
    for d in repo_dirs(root):
        for md in sorted(d.rglob("*.md")):
            rel_parts = md.relative_to(base).parts
            # 只跳过以 . / _ 开头的**子目录**，_shared 这一级已由 repo_dirs 放行
            if any(skipped(p) for p in rel_parts[1:-1]):
                continue
            yield load_page(root, md)


def resolve_page(root: Path, target: str) -> tuple[Path | None, list[str]]:
    """返回 (命中页, 歧义候选)。歧义时不猜——静默选错页比报错更糟。"""
    want = norm(target)
    if want.endswith(".md"):
        want = want[:-3]
    base = repo_root(root)
    direct = base / (want + ".md")
    if direct.is_file():
        return direct, []

    exact, fuzzy = [], []
    for page in all_pages(root):
        bare = page.rel.split("/", 1)[1] if "/" in page.rel else page.rel
        if page.rel == want or bare == want:
            exact.append(page.path)
        elif bare.endswith("/" + want) or page.rel.endswith("/" + want):
            fuzzy.append(page.path)
    hits = exact or fuzzy
    if len(hits) == 1:
        return hits[0], []
    if len(hits) > 1:
        return None, sorted(p.relative_to(base).as_posix() for p in hits)
    return None, []


def pick_page(root: Path, target: str) -> Path | None:
    path, ambiguous = resolve_page(root, target)
    if ambiguous:
        print(f"“{target}” 指向多个页面，请写全路径：", file=sys.stderr)
        for a in ambiguous:
            print(f"  repo/{a}", file=sys.stderr)
        return None
    if path is None:
        print(f"页面不存在：{target}", file=sys.stderr)
        # 路径混用高发处：模型会把代码路径（collector/kit/paging.py）当页面名，
        # 因为「读这个文件」和「读描述这个文件的页」在它看来是一件事。
        # 光说「不存在」它不会想到换工具——实测它会先去 kb_tree 绕两圈再回来。
        raw = norm(target)
        if "/" in raw and Path(raw).suffix in SRC_EXT:
            print(f"  这是一个代码路径，不是知识页：", file=sys.stderr)
            print(f"    看源码 + 相关知识：kb pack {raw}", file=sys.stderr)
            print(f"    只看相关知识：      kb pack {raw} --no-source", file=sys.stderr)
            hits = [p.rel for p in all_pages(root)
                    if any(cover_match(c, raw) for c in p.covers)]
            if hits:
                print(f"    描述它的页：{', '.join(hits[:5])}", file=sys.stderr)
        elif "." not in raw.rsplit("/", 1)[-1]:
            # 也可能把仓库子目录当页面名
            first = raw.split("/")[0]
            owners = [d.name for d in repo_dirs(root) if (d / first).is_dir()]
            if owners:
                print(f"  {raw} 是 {owners[0]} 仓库下的子目录。", file=sys.stderr)
                print(f"    列文件：kb dispatch {raw}/", file=sys.stderr)
                print(f"    看源码：kb pack {raw}/", file=sys.stderr)
    return path


# ------------------------------------------------------------------ 匹配

def cover_match(cover: str, target: str) -> bool:
    c = norm(cover)
    if not c:
        return False
    if cover.strip().endswith("/"):
        return target == c or target.startswith(c + "/")
    return target == c or target.endswith("/" + c)


# ------------------------------------------------------------------ 命令

def check_repo(root: Path, name: str) -> str | None:
    """校验 --repo 是一级仓库名。返回错误文本，None 表示合法。

    三个命令都会静默过滤掉「不存在的仓库」，然后输出一个看起来正常的空结果：
      kb tree   -> 「0 页」（模型以为仓库是空的）
      kb where  -> 「没有页面覆盖 X」（模型以为无人认领，于是新建重复页）
      kb search -> 「没有命中」
    后两个尤其危险：空结果本身是合法答案，但前提是仓库名拼对了。
    这里统一在入口挡掉，且把可用仓库名一起印出来。

    **光列仓库名不够。** 实测：让 agent 查 `collector/kit/`，它先试
    `--repo collector`（拿到「可用：_shared, atomkgraph, codeb, infohub」），
    再试 `--repo codeb`，最后放弃——4 轮全废。它真正缺的信息是
    「collector 是 infohub 下的子目录，该用什么命令查子目录」。
    所以错误里必须做路径归属推断并指出替代命令。
    """
    known = [d.name for d in repo_dirs(root)]
    if name in known:
        return None

    msg = f"没有名为 {name} 的仓库。可用：{', '.join(known)}"

    # 路径归属推断：这个名字是某个仓库下的真实目录吗？
    # 两种写法都要认：`collector`（一级子目录）和 `collector/kit`（多级路径）。
    # 漏掉后者会让模型在「collector/kit 到底属于谁」上原地打转。
    probe = norm(name)
    first = probe.split("/")[0]
    owner = None
    for d in repo_dirs(root):
        if (d / probe).is_dir() or (d / first).is_dir():
            owner = d.name
            break
    if owner:
        msg += (f"\n  {name} 是 {owner} 仓库下的子目录，不是仓库。"
                f"\n  要看这个子目录：kb dispatch {probe.rstrip('/')}/   "
                f"（文件清单 + 谁在描述它，约 115 tok）"
                f"\n  要看它的源码上下文：kb pack {probe.rstrip('/')}/")
    elif "/" in name or "\\" in name:
        msg += "\n  （仓库是 repo/ 下的一级目录；子目录不是仓库）"
    return msg


def cmd_tree(root: Path, args) -> int:
    items: list[dict] = []
    tokens = 0

    def walk(d: Path, depth: int) -> None:
        try:
            entries = sorted(d.iterdir(), key=lambda p: (p.is_file(), p.name))
        except OSError:
            return
        for e in entries:
            if skipped(e.name):
                continue
            if e.is_dir():
                if depth < args.depth:
                    walk(e, depth + 1)
            elif e.suffix == ".md":
                page = load_page(root, e)
                n = est_tokens(page.title)
                nonlocal tokens
                tokens += n
                items.append({"rel": page.rel, "title": page.title,
                              "covers": page.covers, "tokens": n,
                              "hint": page.hint(), "parent": page.parent})

    dirs = repo_dirs(root)
    if args.repo:
        # 静默失败高发处：--repo 给的是子目录名（collector/kit）或路径时，
        # 过滤结果为空，命令仍 rc=0 输出「0 页」。模型会认为「这个仓库没内容」，
        # 然后反复重试或换工具——实测一个判断类任务因此白烧 4 轮。
        bad = check_repo(root, args.repo)
        if bad:
            _err(bad)
            return 2
        dirs = [d for d in dirs if d.name == args.repo]
    for d in dirs:
        walk(d, 1)

    if args.json:
        print(json.dumps({"root": str(root), "items": items,
                          "stats": {"pages": len(items), "tokens": tokens}},
                         ensure_ascii=False, indent=2))
        return 0

    # 文本输出：真正的目录树递归。先建 dir → (子目录, 页面) 的结构再递归打印。
    # 早期版本按「深度 + 目录名」排序后平铺输出，导致 codeb/design/ 被印到
    # infohub/ 那一块下面——层级是错的，而错得很像对的，看不出问题。
    #
    # parent 折叠：拆页后子页挂在父页下面显示，而不是散落在目录里。
    # 这是「文档太大就拆成根节点 + 子节点」在阅读侧的体现。
    # 折叠只影响**显示**，不影响 rel：covers / where / read 仍用真实路径。
    by_rel = {it["rel"]: it for it in items}
    kids_of: dict[str, list[dict]] = {}
    dangling: list[str] = []
    for it in items:
        par = it.get("parent") or ""
        if not par:
            continue
        if par in by_rel:
            kids_of.setdefault(par, []).append(it)
        else:
            # 悬空 parent：与 covers 一致，不阻断，但必须报出来。
            # 静默忽略会让"拆了一半"的页看起来像正常顶层页。
            dangling.append(f"{it['rel']} → {par}")
    shown: set[str] = set()

    children: dict[str, list[str]] = {}
    pages_in: dict[str, list[dict]] = {}
    for it in items:
        d = it["rel"].rsplit("/", 1)[0]
        pages_in.setdefault(d, []).append(it)
        while "/" in d:
            parent = d.rsplit("/", 1)[0]
            kids = children.setdefault(parent, [])
            if d not in kids:
                kids.append(d)
            d = parent

    def sort_key(x: dict) -> tuple[int, str]:
        # 总览页永远第一（它是对这一层的入口），其余按文件名。
        # 标题大小写混杂，文件名才是稳定的排序键。
        stem = x["rel"].rsplit("/", 1)[-1].lower()
        return (0 if stem in ("overview", "readme", "index") else 1, stem)

    def emit_page(it: dict, indent: str, depth: int) -> None:
        if it["rel"] in shown:
            return
        shown.add(it["rel"])
        hint = it.get("hint") or ""
        # --flat：完全忽略 parent，子页与普通页同级同缩进。
        print(f"{indent if not args.flat else ''}{it['title']}"
              + (f"  —  {hint}" if hint else ""))
        if args.flat or depth > 6:
            return
        for kid in sorted(kids_of.get(it["rel"], []), key=sort_key):
            emit_page(kid, indent + "  ", depth + 1)

    def emit(d: str, depth: int) -> None:
        indent = "  " * depth
        label = d if d == SHARED else d.rsplit("/", 1)[-1]
        print(f"{indent}{label}/")
        for it in sorted(pages_in.get(d, []), key=sort_key):
            emit_page(it, indent + "  ", depth + 1)
        for kid in sorted(children.get(d, []), key=str.lower):
            emit(kid, depth + 1)

    tops = [d for d in repo_dirs(root) if not args.repo or d.name == args.repo]
    for d in tops:
        emit(d.name, 0)

    print(f"\n{len(items)} 页 · 标题共约 {tokens} tok")
    nested = sum(len(v) for v in kids_of.values())
    if nested and not args.flat:
        print(f"（其中 {nested} 页是拆分的子页，已折叠显示在父页下）")
    if dangling:
        # 走 _err()：GBK 控制台下直接 print 中文会乱码，见 _err 的说明
        _err(f"警告：{len(dangling)} 处 parent 指向不存在的页（不阻断）")
        for d in dangling:
            _err(f"    {d}")
        _err("  改 parent 或建该页即可消除")
    return 0


def cmd_read(root: Path, args) -> int:
    path = pick_page(root, args.page)
    if path is None:
        return 2
    page = load_page(root, path)
    if not args.section:
        if args.json:
            print(json.dumps({"rel": page.rel, "title": page.title,
                              "covers": page.covers, "body": page.body},
                             ensure_ascii=False, indent=2))
        else:
            print(page.body, end="" if page.body.endswith("\n") else "\n")
        return 0

    q = re.sub(r"\s+", "", args.section.lower())
    heads = list(iter_headings(page.body))
    src = page.body.splitlines()
    for i, (ln, level, title) in enumerate(heads):
        if q not in re.sub(r"\s+", "", title.lower()):
            continue
        end = len(src)
        for ln2, level2, _ in heads[i + 1:]:
            if level2 <= level:
                end = ln2
                break
        section = "\n".join(src[ln:end]).rstrip()
        if args.json:
            print(json.dumps({"rel": page.rel, "section": title, "content": section},
                             ensure_ascii=False, indent=2))
        else:
            print(section)
        return 0

    print(f"没有匹配的标题：{args.section}", file=sys.stderr)
    if heads:
        print("可用标题：", file=sys.stderr)
        for _, _, t in heads:
            print(f"  {t}", file=sys.stderr)
    return 2


def cmd_heads(root: Path, args) -> int:
    path = pick_page(root, args.page)
    if path is None:
        return 2
    page = load_page(root, path)
    heads = [{"level": lv, "title": t} for _, lv, t in iter_headings(page.body)]
    if args.json:
        print(json.dumps({"rel": page.rel, "headings": heads},
                         ensure_ascii=False, indent=2))
        return 0
    if not heads:
        print("(此页没有标题)")
        return 0
    for h in heads:
        print(f"{'  ' * (h['level'] - 1)}{'#' * h['level']} {h['title']}")
    return 0


def cmd_search(root: Path, args) -> int:
    needle = re.sub(r"\s+", "", args.term.lower())
    if not needle:
        print("搜索词为空。", file=sys.stderr)
        return 2
    if args.repo:
        bad = check_repo(root, args.repo)
        if bad:
            _err(bad)
            return 2
    hits: list[dict] = []
    for page in all_pages(root):
        if args.repo and page.repo != args.repo:
            continue
        for i, line in enumerate(page.body.splitlines(), 1):
            if needle in re.sub(r"\s+", "", line.lower()):
                hits.append({"rel": page.rel, "line": i, "text": line.strip()})
                break
    if args.json:
        print(json.dumps({"term": args.term, "hits": hits[: args.limit]},
                         ensure_ascii=False, indent=2))
        return 0
    if not hits:
        print("没有命中。")
        return 0
    for h in hits[: args.limit]:
        print(f"{h['rel']}:{h['line']}: {h['text']}")
    if len(hits) > args.limit:
        print(f"\n（共 {len(hits)} 页命中，已显示前 {args.limit} 页）")
    return 0


def cmd_graph(root: Path, args) -> int:
    """把 covers 的二部图投影成页间图，输出三类结构性信号。

    为什么不是"再存一张索引图"：图已经存在。59 页共用 114 条 covers 路径，
    其中 29 条被 2 个以上页面共同覆盖——这些共享路径就是页间关系。
    新建 index.md / graph.json 只会多一份会静默漂移的副本，
    而这里每次现场从 covers 算出来，永远不会过期。

    投影规则：两页共享任一 covers 路径即相邻。注意由此得到的**不是树**：
    一个源文件天然被多个页面从不同角度描述（实测 infohub/pitfalls 度数 12），
    强行规定唯一父节点会逼人删掉正确的知识。所以树用 parent 表达，
    关联用这张图表达，两者不互相替代。

    三类信号各自的用途：
      - hub：度数高 = 事实上的入口页。它可能自己不知道，值得显式加路由。
      - 孤立：有 covers 却无邻居 = 与其它知识脱节，是拆分或补链接的首选。
      - 重复覆盖：同一路径被多页描述，是"说法不一致"的排查入口。
    """
    pages = [p for p in all_pages(root) if not args.repo or p.repo == args.repo]

    # 路径 -> 覆盖它的页面（保持确定性顺序，输出才可 diff）
    by_path: dict[str, list[str]] = {}
    for p in sorted(pages, key=lambda x: x.rel):
        for c in p.covers:
            by_path.setdefault(c, []).append(p.rel)

    # 投影成页间邻接：共享路径即一条边
    adj: dict[str, dict[str, list[str]]] = {p.rel: {} for p in pages}
    for c, rels in by_path.items():
        if len(rels) < 2:
            continue
        for i, a in enumerate(rels):
            for b in rels[i + 1:]:
                adj[a].setdefault(b, []).append(c)
                adj[b].setdefault(a, []).append(c)

    title_of = {p.rel: p.title for p in pages}
    ties = sorted(((len(v), k) for k, v in adj.items()), key=lambda t: (-t[0], t[1]))
    hubs = [{"rel": k, "degree": d, "title": title_of[k]} for d, k in ties
            if d >= args.hub]
    isolated = [{"rel": p.rel, "title": p.title, "covers": p.covers}
                for p in sorted(pages, key=lambda x: x.rel)
                if p.covers and not adj.get(p.rel)]
    uncovered = sorted(p.rel for p in pages if not p.covers)
    shared = [{"cover": c, "pages": rels} for c, rels in sorted(by_path.items())
              if len(rels) >= 2]
    edges = {tuple(sorted((a, b))) for a, nbrs in adj.items() for b in nbrs}

    if args.json:
        print(json.dumps({
            "pages": len(pages),
            "covers_paths": len(by_path),
            "edges": len(edges),
            "hubs": hubs,
            "isolated": isolated,
            "no_covers": uncovered,
            "shared_covers": shared,
        }, ensure_ascii=False, indent=2))
        return 0

    print(f"{len(pages)} 页 · {len(by_path)} 条 covers 路径 · {len(edges)} 条页间边\n")

    print(f"## hub（被 ≥{args.hub} 页通过共享路径连通）")
    if hubs:
        for h in hubs:
            print(f"  {h['degree']:2}  {h['rel']}  —  {h['title']}")
        print("  这些是事实上的入口页。若正文没有指向邻居的路由，读者会到此迷路。")
    else:
        print("  无。")

    print(f"\n## 孤立页（有 covers 但没有共享者：{len(isolated)}）")
    for it in isolated:
        print(f"  {it['rel']}  —  {it['title']}")
    if isolated:
        print("  覆盖了真实代码却与其它知识不相连：优先考虑拆页或补 covers。")
    if uncovered:
        print(f"\n## covers 为空（{len(uncovered)}）")
        for r in uncovered:
            print(f"  {r}")

    print(f"\n## 重复覆盖（同一路径被多页描述：{len(shared)}）")
    for s in shared[:args.top]:
        print(f"  {s['cover']}  ({len(s['pages'])})")
        for r in s["pages"]:
            print(f"      - {r}")
    if len(shared) > args.top:
        print(f"  …另有 {len(shared) - args.top} 条，用 --top 调整")
    if shared:
        print("  同一文件被多页描述是正常的（多视角），但要确认说法不互相矛盾。")
    return 0


# ------------------------------------------------------------------ 计划条目
#
# 计划不是独立文档，而是散落在各页 `## 计划` 小节里的条目——和知识同构。
# 一个页面描述哪块代码，它的待办就待在那块代码旁边，不另建计划树。
#
# 最关键的约定：**只有 [ ] 和 [-] 两个可写框，不允许 [x]**。
# 「已实现」是关于代码的断言，而代码的真值只能来自代码本身。
# 手写 [x] 会在功能被回退、重命名或从未真正落地时静默过期，
# 读者却以为已经有了——这与当年的 manifest.toml 是同一类失败：
# 把能现场算出来的派生状态写进文件。所以状态一律由 done: 锚点现算。

PLAN_ITEM_RE = re.compile(r"^\s*[-*]\s*\[([ xX~\-])\]\s+(P-[A-Za-z0-9_.\-]+)\s+(.+?)\s*$")
# 锚点边界只认行内空白，**不能用 \s**（它包含换行）。
# 曾用 \s 导致锚点贪婪跨行吃掉下一条条目：7 条计划只解析出 5 条，
# 且错误信息里粘着下一条的开头（`... \parent- [ ] P-cleanup ...`）。
PLAN_ANCHOR_RE = re.compile(r"(?:—|--|-|[ \t])\s*done:[ \t]*(.+?)\s*$")
ANCHOR_GREP_RE = re.compile(r"grep[ \t]+(\S+)[ \t]+`([^`]+)`")
ANCHOR_PATH_RE = re.compile(r"path[ \t]+(.+?)$")
PLAN_SECTION_RE = re.compile(r"(?m)^##+\s*计划\s*$")


def parse_plan_item(line: str) -> tuple[dict | None, str]:
    """解析一行计划条目，返回 (item, 错误说明)。

    [x] / [~] 一律报错而不是接受：它们声称了只有代码才能证实的事。
    """
    m = PLAN_ITEM_RE.match(line)
    if not m:
        return None, ""
    box, pid, rest = m.group(1), m.group(2), m.group(3)
    if box.lower() in ("x", "~"):
        return None, (f"{pid}: 不许写 [{box}]——「已实现」由 done: 锚点现场核对，"
                      f"不写进文件（写 [x] 会在代码被回退后静默骗人）")
    am = PLAN_ANCHOR_RE.search(rest)
    if am:
        intent = rest[:am.start()].rstrip(" —-").strip()
        anchor = am.group(1).strip()
    else:
        intent, anchor = rest.strip(), ""
    return {"id": pid, "box": box, "intent": intent, "anchor": anchor}, ""


def plan_section_body(body: str) -> str:
    """取出页面里 `## 计划` 小节正文（到下一个同级或更高级标题为止）。"""
    m = PLAN_SECTION_RE.search(body)
    if not m:
        return ""
    rest = body[m.end():]
    out = []
    for ln in rest.splitlines():
        if re.match(r"^##+\s", ln) or re.match(r"^#{1,2}\s", ln):
            break
        out.append(ln)
    return "\n".join(out)


def anchor_status(root: Path, anchor: str) -> tuple[str, list[str]]:
    """按锚点现场核对代码，返回 (状态, 证据)。

    状态是四种之一：
      landed  锚点已匹配 = 代码里已经有它 → 该删条目
      partial 部分路径存在 → 做了一半
      no-code 核不到 → 真正待办
      manual  锚点缺失/看不懂 → 交人判

    锚点缺失时判 manual 而不是 no-code 是刻意的：误报成「未实现」会让人
    重做已经做过的事，误报成「已实现」会让人以为不必做。两种误报里，
    指向人工复核的代价最小。
    """
    a = (anchor or "").strip()
    if not a or a.lower() in ("none", "manual"):
        return "manual", ["没有可自动核对的锚点"]

    g = ANCHOR_GREP_RE.search(a)
    if g:
        rel, pat = norm(g.group(1)), g.group(2)
        f = root / rel
        if not f.is_file():
            return "no-code", [f"{rel} 不存在"]
        try:
            txt = _read_text_robust(f)
        except OSError:
            return "no-code", [f"{rel} 读不了"]
        try:
            hit = re.search(pat, txt) is not None
        except re.error as e:
            return "manual", [f"正则写错了：{e}"]
        return ("landed", [f"{rel} 里匹配到 /{pat}/"]) if hit else \
               ("no-code", [f"{rel} 里没有 /{pat}/"])

    p = ANCHOR_PATH_RE.search(a)
    if p:
        paths = [norm(x) for x in p.group(1).split(",") if x.strip()]
        have = [x for x in paths if (root / x).exists()]
        miss = [x for x in paths if not (root / x).exists()]
        if not have:
            return "no-code", [f"{x} 不存在" for x in miss]
        if miss:
            return "partial", [f"{x} 不存在" for x in miss]
        return "landed", [f"{x} 存在" for x in paths]

    return "manual", [f"锚点看不懂：{a[:60]}"]


def collect_plan(root: Path, repo: str | None = None) -> tuple[list[dict], list[str]]:
    """扫描所有页面的 `## 计划` 小节，返回 (条目列表, 格式错误列表)。

    条目散落在各页，所以这里必然要遍历全库；plan.md 只是"还没有知识页的
    新功能"的默认归宿，没有任何特权。
    """
    items, errors = [], []
    for pg in all_pages(root):
        if repo and pg.repo != repo:
            continue
        sect = plan_section_body(pg.body)
        if not sect:
            continue
        for line in sect.splitlines():
            item, err = parse_plan_item(line)
            if err:
                errors.append(f"{pg.rel}: {err}")
                continue
            if not item:
                continue
            st, ev = anchor_status(root, item["anchor"])
            if item["box"] == "-":
                st, ev = "dropped", ["已否决（保留以防重新提议）"]
            item.update({"page": pg.rel, "title": pg.title, "status": st,
                         "evidence": ev, "repo": pg.repo})
            items.append(item)
    return items, errors


def cmd_plan(root: Path, args) -> int:
    """列出计划条目，按「现场算出来的」状态分桶。"""
    if getattr(args, "plan_cmd", None) == "close":
        return cmd_plan_close(root, args)

    items, errors = collect_plan(root, args.repo)
    # 去重检查：ID 在同一仓库内必须唯一，否则 close 时无法定位
    seen: dict[tuple[str, str], str] = {}
    dupes = []
    for it in items:
        k = (it["repo"], it["id"])
        if k in seen:
            dupes.append(f"{it['repo']}/{it['id']} 同时在 {seen[k]} 与 {it['page']}")
        else:
            seen[k] = it["page"]

    # anchor_status 返回的「机器状态」→「用户看的桶」。
    # landed 必须映射成 stale（= 代码里已经有了，该删条目）。
    # 漏掉这个映射时 landed 条目会**整条消失**——不报错、不显示，
    # 看起来像"计划都做完了所以没有待办"，是最坏的一种静默失败。
    BUCKET_OF = {"no-code": "open", "landed": "stale",
                 "partial": "partial", "manual": "manual", "dropped": "dropped"}

    buckets = {"open": [], "partial": [], "manual": [], "stale": [], "dropped": []}
    unknown = []
    for it in items:
        key = BUCKET_OF.get(it["status"])
        if key is None:
            unknown.append(f"{it['id']} 状态未知：{it['status']}")
            key = "manual"
        buckets[key].append(it)

    if unknown:
        _err(f"警告：{len(unknown)} 条状态无法归类（已放进 manual）")
        for u in unknown:
            _err(f"    {u}")

    if args.json:
        print(json.dumps({
            "total": len(items),
            "counts": {k: len(v) for k, v in buckets.items()},
            "items": items,
            "errors": errors,
            "duplicates": dupes,
        }, ensure_ascii=False, indent=2))
        return 0

    want = args.only
    order = ["open", "partial", "manual", "stale", "dropped"]
    if want:
        order = [want]
    label = {"open": "待做（锚点核不到代码）",
             "partial": "做了一半（部分路径已有）",
             "manual": "需人工判断（无锚点或锚点看不懂）",
             "stale": "代码里已存在 → 该收编进知识后删掉条目",
             "dropped": "已否决（留着防重新提议）"}
    for k in order:
        rows = buckets.get(k, [])
        if not rows:
            continue
        print(f"\n## {label[k]}（{len(rows)}）")
        for it in rows:
            print(f"  {it['id']}  [{it['page']}]  {it['intent']}")
            for e in it["evidence"][:2]:
                print(f"      · {e}")

    counts = " · ".join(f"{label[k].split('（')[0]} {len(buckets.get(k, []))}"
                        for k in order if buckets.get(k))
    print(f"\n共 {len(items)} 条" + (f"（{counts}）" if counts else ""))
    if buckets.get("stale"):
        print("  stale 是清理提示，不是成就墙：先把「为什么」并进正页正文，"
              "再 kb plan close 删条目。")
    if dupes:
        _err(f"警告：ID 重复 {len(dupes)} 处（close 时会定位不到）")
        for d in dupes:
            _err(f"    {d}")
    if errors:
        _err(f"警告：{len(errors)} 行格式有问题（已跳过）")
        for e in errors:
            _err(f"    {e}")
    return 0


def cmd_plan_close(root: Path, args) -> int:
    """关闭一条计划：**先落知识，再删条目**。

    顺序不可颠倒，而且必须由一条命令保证：
      - 只删行 → 丢掉最有价值的部分（为什么当初要做它），且事后无处可查
      - 只写正文 → 条目残留，读者仍以为待办
    所以这里先写正文（走 kb upsert 的唯一写入口），成功后才动条目行；
    任一步失败都不产生「已完成但知识没落地」的中间状态。
    """
    if not args.into:
        _err("close 必须给 --into <页>：知识要落到哪一页")
        return 2
    if not args.body_file:
        _err("close 必须给 --body-file：要并进正文的内容")
        return 2

    pid = args.id
    items, _ = collect_plan(root, args.repo)
    hits = [it for it in items if it["id"] == pid]
    if not hits:
        _err(f"找不到计划条目 {pid}")
        return 2
    if len(hits) > 1:
        _err(f"{pid} 命中 {len(hits)} 条，无法确定关哪一条：")
        for h in hits:
            _err(f"    [{h['page']}] {h['intent']}")
        return 2
    it = hits[0]

    try:
        body = Path(args.body_file).read_bytes().decode("utf-8-sig")
    except OSError as e:
        _err(f"读不了 --body-file：{e}")
        return 2
    if len(body.strip()) < 20:
        _err("--body-file 内容太短：这里要写「背景 + 结论 + 放弃了什么」，"
             "不是一句话交差")
        return 2

    # 必须在动手之前确认目标页真的存在。
    # 否则 upsert 会走「新建页」分支并返回 0 —— close 会误以为知识已落地，
    # 于是把条目删掉，而知识其实写进了一个刚被凭空造出来的空页。
    # 实测过这个洞：--into 指向不存在的页时 rc=0、条目被删、源页被改。
    target = norm(args.into)
    tpath = repo_root(root) / (target + ".md")
    if not tpath.is_file():
        _err(f"--into 指向的页不存在：repo/{target}.md")
        _err("close 只把知识并进**已有**页面。先决定它该属于哪一页"
             "（kb where / kb tree 找一个），或先建好那页再 close。")
        return 2

    # 第一步：把知识写进正页（仍然经由 kb upsert，不直接改文件）
    # 关键：_upsert_locked 用 args.page 判断「更新已有页」还是「新建页」。
    # 只给 --rel 不给 page 会走新建分支，于是对已存在的页报
    # 「页面已存在」并返回 2 —— 知识没写成。所以这里必须把 page 也指过去。
    up = argparse.Namespace(
        page=target, repo=None, title=None, parent=None, rel=None,
        covers=None, section=args.section, body=None, body_file=args.body_file,
        append=not args.section, replace=False, find=None, expect=None,
        topic=None, json=False,
    )
    rc = cmd_upsert(root, up)
    if rc != 0:
        _err("知识没写成功，条目保留（不会出现「完成了但知识没落地」的状态）")
        return rc

    # 第二步：删掉条目行。用 --find + --expect 1，必须精确命中一条。
    line = f"[{it['box']}] {it['id']} {it['intent']}"
    err = _drop_plan_line(root, it["page"], it["id"])
    if err:
        _err(f"知识已写入，但条目没删掉：{err}")
        _err("请手动删除该行，或重跑 close（正文会重复，需先检查）")
        return 2
    print(f"已关闭 {it['id']}：知识写入 {args.into}"
          + (f"#{args.section}" if args.section else "")
          + f"，条目已从 {it['page']} 删除")
    return 0


def _drop_plan_line(root: Path, page_rel: str, pid: str) -> str:
    """从页面删掉指定 ID 的条目行。返回错误说明，空串表示成功。"""
    path = repo_root(root) / (page_rel + ".md")
    if not path.is_file():
        return f"{page_rel}.md 不存在"
    with write_lock(root):
        text = _read_text_robust(path).replace("\r\n", "\n")
        lines = text.splitlines()
        keep, removed = [], 0
        for ln in lines:
            it, _ = parse_plan_item(ln)
            if it and it["id"] == pid:
                removed += 1
                continue
            keep.append(ln)
        if removed == 0:
            return "没有匹配到该条目行"
        if removed > 1:
            return f"匹配到 {removed} 行，不确定删哪一行"
        new = "\n".join(keep).rstrip("\n") + "\n"
        _atomic_write(path, new.encode("utf-8"))
    return ""


# --------------------------------------------------------------- 上下文装订
#
# 册子是「写范围 + 知识 + 源码」的一次投影，必须现场算、且不落盘：
# 一旦落盘就多一份要手工同步的真源，而工单改了却没重生成时，册子会静默说谎。
# 照着错册子开工，比没有册子更糟。
#
# 分层与降级顺序是这里唯一的设计。预算不够时先砍最可替代的东西：
#   1 兄弟文件大纲 → 2 弱相关知识节 → 3 强相关知识节 → 4 目标源码大纲 → 5 目标源码全文
# 目标源码永远最后降级，且每次降级都写进「有意省略」——边界可见比装得更全更能
# 减少 agent 的试探性 search。

CODE_EXT = (".py", ".ts", ".tsx", ".js", ".jsx", ".mjs", ".mts", ".cjs", ".cts")
# 配置也算源码：sites/<family>/<kind>.yaml 这种文件就是任务的交付物本身，
# 只认 .py/.ts 会让「加一个新站点」的册子里没有样板的 YAML。
CONF_EXT = (".yaml", ".yml", ".json", ".toml", ".sql")
# 锁文件与生成清单体积大且与任务无关，混进来会挤掉真正要看的源码。
CONF_SKIP_NAMES = {
    "package-lock.json", "pnpm-lock.yaml", "yarn.lock", "package.json",
    "tsconfig.json", "tsconfig.tsbuildinfo", "capabilities.json",
}
SRC_EXT = CODE_EXT + CONF_EXT
SRC_SKIP = {
    "node_modules", ".git", "dist", "build", "out", ".venv", "venv",
    "__pycache__", ".next", "coverage", ".turbo", ".cache", ".trash",
    ".backup", ".quarantine", ".staging", ".scratch", ".conflicts",
    ".svelte-kit", ".repowise", ".vscode", ".workbuddy", ".dsh",
    "site-packages", ".pytest_cache", ".ruff_cache", "参考项目",
}
OUTLINE_LINE_LIMIT = 400   # 大纲模式的参考线；真正的判决看预算，见 render_source
TARGET_BUDGET_SHARE = 0.6  # 目标源码最多占预算的这个比例，超了退大纲
SIBLING_MAX_FILES = 12     # 同目录文件超过这个数就不给兄弟大纲：那不是「兄弟」是一整个仓库
SIBLING_MAX_TOKENS = 300   # 单个兄弟大纲的上限，超了它自己也只剩噪音
PACK_BUDGET = 13000

# 派生文件的标记：必须是「点名了一个脚本」+「一个强产物词」同时出现。
#
# 只用「自动生成 / 不要手改」会大面积误报，实测三类假阳性都长这样：
#   capabilities.py 里那行 note 字符串（它就是生成器本身）
#   enrich_batch.py 的 `--plan` 说明（它生成的**输入**由别人产出，它自己不是产物）
#   web.py 里「由 web 源接管，会生成…」的散文
# 真描述「本文件是产物」的句子，两者一定同时出现。
DERIVED_MARK = re.compile(
    r"(?:[\w./-]*/)?[\w.-]+\.(?:py|ts|mjs|js|sh)[^\n]{0,60}?"
    r"(?:--write|生成|generated)[^\n]{0,80}?"
    r"(?:不要手改|请勿手改|切勿手改|DO NOT EDIT|do not edit|auto-?generated)", re.I)
_SCRIPT_IN = re.compile(r"([\w./-]+\.(?:py|ts|mjs|js|sh))")

PY_SIG = re.compile(r"^[ \t]*(?:async[ \t]+)?(?:def|class)[ \t]+([A-Za-z_]\w*)")


def pathlib_name(rel: str) -> str:
    return rel.rsplit("/", 1)[-1]
TS_SIG = re.compile(
    r"^[ \t]*(?:export[ \t]+)?(?:default[ \t]+)?(?:declare[ \t]+)?"
    r"(?:async[ \t]+)?(?:function|class|interface|type|enum|const|let|var)[ \t]+"
    r"([A-Za-z_$][\w$]*)")


@dataclass
class Block:
    """装订的一个块。prio 越大越先被丢。"""
    prio: int
    label: str
    text: str
    tokens: int = 0

    def __post_init__(self):
        self.tokens = est_tokens(self.text)


def repo_roots(root: Path) -> dict[str, Path]:
    """仓库名 → 磁盘根。

    优先取仓库页面 frontmatter 的 `root:`；没写的退回「知识库根的兄弟目录」，
    因为 infohub / codeb 恰好放在那里。两者都不成立时不猜——让 pack 直接报
    「源码不可读」，而不是装订出一份没有源码却看着很完整的册子。
    """
    base = Path(root).resolve()
    out: dict[str, Path] = {}
    for pg in all_pages(root):
        if pg.disk:
            out.setdefault(pg.repo, Path(pg.disk))
    for d in repo_dirs(root):
        if d.name in out:
            continue
        sib = base.parent / d.name
        if sib.is_dir():
            out[d.name] = sib
    return out


def scope_repo(roots: dict[str, Path], scope: str) -> tuple[str | None, Path | None]:
    """把 scope 解析成 (仓库名, 磁盘根)。允许写 `infohub/collector/kit/` 或 `collector/kit/`。"""
    head, _, rest = scope.partition("/")
    if rest and head in roots and (roots[head] / rest).exists():
        return head, roots[head]
    for name in sorted(roots):
        if (roots[name] / scope).exists():
            return name, roots[name]
    return None, None


def git_files(base: Path) -> set[str] | None:
    """返回仓库内被 git 认可的 posix 路径集合；git 不可用时返回 None。

    选「已跟踪 + 未跟踪但未忽略」：
      --cached                 已跟踪（进 git 的就是重要的）
      --others --exclude-standard  新建但未被 .gitignore 排除的
    这样刚建好、还没 add 的源码也能进包，而 .gitignore 仍然生效——
    选型规则的唯一真值回到 git 自己，不再有 .kbignore 这第二份清单。
    """
    if not (base / ".git").exists():
        return None
    try:
        r = subprocess.run(
            ["git", "-C", str(base), "ls-files",
             "--cached", "--others", "--exclude-standard", "-z"],
            capture_output=True, timeout=60,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if r.returncode != 0:
        return None
    return {x for x in r.stdout.decode("utf-8", "replace").split("\0") if x}


def src_files(base: Path, rel: str, root: Path | None = None) -> list[str]:
    """目录下的源码与配置，返回相对仓库根的路径。

    选型规则的唯一来源是 git：进入 git 的就是重要内容。
      - git 可用：只取 git 认可的文件（已跟踪 + 未跟踪未忽略），
        `.kbignore` 完全不看。
      - git 不可用 / 无 .git：退回扫整个项目，但仍跳过依赖/产物目录
        （node_modules / dist / .git / _kbwork 等），否则包会被噪音淹没。

    这里**不**过滤锁文件与生成清单：它们是写范围的一部分，dispatch 必须看见
    才能报出串行点。是否装进册子由调用方按 CONF_SKIP_NAMES 决定。
    """
    d = base / rel
    if not d.is_dir():
        return []

    # 先确定候选池：git 认可的文件，或整个项目（兜底）
    tracked = git_files(base)

    out: list[str] = []
    for f in sorted(d.rglob("*")):
        if not f.is_file() or f.suffix not in SRC_EXT:
            continue
        # d 已经是目标目录，f 必在 d 下，无需再做前缀过滤
        r = f.relative_to(base).as_posix()
        # 依赖/产物目录永远跳过（无论 git 是否可用）
        if any(part in SRC_SKIP for part in f.parts):
            continue
        # git 可用时，只保留它认可的文件；否则保留全部
        if tracked is not None and r not in tracked:
            continue
        out.append(r)
    return out


def file_outline(path: Path) -> tuple[str, int]:
    """只取签名行，带行号——行号让 agent 能直接跳到目标位置，不用整文件读。"""
    try:
        text = _read_text_robust(path).replace("\r\n", "\n")
    except OSError:
        return "", 0
    lines = text.splitlines()
    sig = []
    for i, line in enumerate(lines, 1):
        if PY_SIG.match(line) or TS_SIG.match(line):
            sig.append(f"{i:>5}  {line.rstrip()[:110]}")
    return "\n".join(sig), len(lines)


# ---------------------------------------------------------------------------
# 语义块索引：通过 subprocess 调用 semantic_blocks.py（保持 kb.py stdlib-only）。
# semantic_blocks.py 自身用 ast（Python）+ node/typescript（TS/JS）+ regex 回退。
# ---------------------------------------------------------------------------
_SEMANTIC_BLOCKS_PY = Path(__file__).resolve().parent / "distill" / "agent" / "semantic_blocks.py"


def _source_index_block(path: Path, rel: str) -> Block | None:
    """源码的**语义块索引块**：每块一行 `Class.method@行号  L起-止  kind  签名`。

    这是虚拟内存的「页表」——只放目录，正文由 agent 用 read_block 按需调入。
    调用 distill/agent/semantic_blocks.py 子进程：Python 用 ast、TS/JS 用
    node+typescript，其余语言 regex 回退；scope 前缀避免撞名，边界精确到 end_lineno。
    subprocess 失败或超时则退回 None（上游走 file_outline 兜底）。
    """
    import json as _json
    import subprocess as _sp
    import sys as _sys
    try:
        r = _sp.run(
            [_sys.executable, "-X", "utf8", str(_SEMANTIC_BLOCKS_PY), str(path), "--json"],
            capture_output=True, text=True, timeout=15,
        )
        if r.returncode != 0:
            return None
        data = _json.loads(r.stdout)
    except Exception:
        return None
    blocks = data.get("blocks", [])
    parser = data.get("parser", "?")
    total = data.get("total", 0)
    lines_out = [
        f"# {rel}  语义块索引 · 解析器={parser}（共 {total} 行）",
        "",
        "> 用 `read_block(path, \"Class.method@行号\")` 按需调入块正文（上下文即 cache）。",
        "",
    ]
    for b in blocks:
        key = f"{b['name']}@{b['start']}"
        scope_hint = f" [{b['scope']}]" if b["scope"] else ""
        lines_out.append(
            f"  {key:<36} L{b['start']:<5}-{b['end']:<5} "
            f"{b['kind']:<10}{scope_hint:<20} {b['sig']}"
        )
    if not blocks:
        lines_out.append("  （没有识别到语义块，用 read_file_range 按行号读）")
    return Block(4, f"{rel}  {total} 行  语义块索引 · {parser}",
                 "\n".join(lines_out))


def render_source(path: Path, rel: str, prio_full: int, prio_out: int,
                  allowance: int = 0) -> Block | None:
    """一个源码/配置文件的装订形态。

    配置给全文：YAML 的 value 就是内容本身，抽签名会抽成空。
    代码按**预算**决定全文还是大纲——行数是代理指标，不是判据：
    `kb.py` 1432 行给大纲是因为它 17k tok 装不下，而 906 行的 blob.py
    在 13k 预算里给全文仍然合理。写死行数阈值会把这两种情况判反。

    allowance > 0 时，全文超过它就退大纲。
    """
    suffix = path.suffix
    try:
        text = _read_text_robust(path).replace("\r\n", "\n")
    except OSError:
        return None
    nl = len(text.splitlines())
    full = Block(prio_full, f"{rel}  {nl} 行  全文", text)
    if suffix in CONF_EXT:
        return full
    if allowance and full.tokens <= allowance:
        return full
    if not allowance and nl <= OUTLINE_LINE_LIMIT:
        return full
    sig, nl = file_outline(path)
    if not sig:
        # 抽不出签名（纯数据文件等）：宁给全文也不给空块
        return full
    return Block(prio_out, f"{rel}  {nl} 行  大纲（只给签名）", sig)


def page_sections(pg: Page) -> list[tuple[int, str, str]]:
    """(级别, 标题, 该节正文)。与 `kb read --section` 同一套切片规则。"""
    src = pg.body.splitlines()
    heads = list(iter_headings(pg.body))
    res = []
    for i, (ln, level, title) in enumerate(heads):
        end = len(src)
        for ln2, level2, _ in heads[i + 1:]:
            if level2 <= level:
                end = ln2
                break
        res.append((level, title, "\n".join(src[ln:end]).rstrip()))
    return res


def claiming_pages(pages: list[Page], scope: str, target: str | None = None) -> list[tuple[Page, str]]:
    """哪些页认领了这个范围，以及精度（exact = 精确到这条路径，dir = 只到目录）。

    `scope` 是**裸的仓库内相对路径**（如 `apps/web/src/x.ts`），而页面的
    `covers` 通常写**带仓库前缀**的完整路径（`atomkgraph/apps/web/src/x.ts`）。
    两者直接比相等永远不命中——`kb where` 用 cover_match 能兜住，`kb pack`
    却只比相等，于是 `kb where` 说「有页认领」而 `kb pack` 报「精度 none、
    0 块 0 tok」，两个命令互相打脸。

    因此这里复用 cover_match 的后缀匹配语义，并额外用 `target`（带仓库名的
    完整范围）再比一次，保证两处判定口径一致。
    """
    out = []
    # keys 同时放裸 scope 与带仓库前缀的 scope：页面 covers 两种写法都有。
    keys = [scope]
    if target and target != scope:
        keys.append(target)
    scope_is_dir = scope.endswith("/")
    for pg in pages:
        kind = ""
        for c in pg.covers:
            cc = norm(c)
            if not cc:
                continue
            is_dir = c.strip().endswith("/")
            dir_hit = is_dir or scope_is_dir
            for k in keys:
                if cover_match(c, k):
                    exact = (cc == norm(k)) and (dir_hit or not is_dir)
                    kind = "exact" if exact else (kind or "dir")
                    if kind == "exact":
                        break
            if kind == "exact":
                break
        if kind:
            out.append((pg, kind))
    return out


def shallow_files(base: Path, rel: str, include_skip: bool = False) -> list[str]:
    """只列一层（不递归）。用于找聚合型产物，不能用来找源码——
    递归扫仓库根在 infohub 上是 25 万文件，dispatch 会直接挂住。

    include_skip=True 时不过滤 CONF_SKIP_NAMES：找派生物恰恰要包括
    capabilities.json 这类被排除在装订之外、但必须串行重生成的东西。
    """
    d = base / rel if rel else base
    if not d.is_dir():
        return []
    out = []
    try:
        for f in sorted(d.iterdir()):
            if not f.is_file() or f.suffix not in SRC_EXT:
                continue
            if not include_skip and f.name in CONF_SKIP_NAMES:
                continue
            out.append(f.relative_to(base).as_posix())
    except OSError:
        return []
    return out


def derived_note(path: Path, head: int = 4000) -> str:
    """读文件头部找「本文件由某脚本生成」的标记。命中就是串行点。

    光看「自动生成 / 不要手改」会大面积误报：生成器自己的说明字符串里就有那句话
    （capabilities.py 里写着「由 capabilities.py --write 生成，不要手改」）。
    必须要求标记点名一个脚本，且那个脚本名**不是文件自己**——
    是自己在描述产物，不是自己就是产物。
    """
    try:
        text = _read_bytes_retry(path)[:head].decode("utf-8", "replace")
    except OSError:
        return ""
    m = DERIVED_MARK.search(text)
    if not m:
        return ""
    named = _SCRIPT_IN.match(m.group(0))
    # 比完整文件名而不是 stem：生成器与产物常常同名不同后缀
    # （capabilities.py 生成 capabilities.json），比 stem 会把产物误判成生成器。
    if named and named.group(1).rsplit("/", 1)[-1] == path.name:
        return ""          # 自己就是那个生成器
    return m.group(0)[:80]


def cmd_pack(root: Path, args) -> int:
    raw_scope = args.scope
    scope = norm(args.scope)
    roots = repo_roots(root)
    pages = list(all_pages(root))
    repo, base = scope_repo(roots, scope)
    if base is None:
        _err(f"scope 定位不到磁盘根：{scope}")
        known = ", ".join(f"{k} → {v}" for k, v in sorted(roots.items())) or "（无）"
        _err(f"已知仓库根：{known}")
        _err("补法：在 repo/<仓库>/overview.md 的 frontmatter 写一行 root: <磁盘绝对路径>")
        return 2

    # scope 可能带着仓库前缀（`infohub/collector/sites/`），而 covers 里既可能
    # 写裸路径（`collector/sites/`）也可能写带前缀的完整路径。剥掉前缀得到
    # 仓库内相对路径 rel_scope，两种 key 一起喂给 claiming_pages，避免双重前缀。
    rel_scope = scope
    if repo and scope.startswith(repo + "/"):
        rel_scope = scope[len(repo) + 1:]

    target = base / rel_scope
    # 原始输入若带尾斜杠，说明调用方在装订**目录**，据此把同目录 covers 判为 exact。
    if raw_scope.strip().endswith("/"):
        scope_key = rel_scope + "/"
    else:
        scope_key = rel_scope
    claim_target = f"{repo}/{rel_scope}" if repo else rel_scope
    claims = claiming_pages(pages, scope_key, claim_target)
    precision = "none"
    if any(k == "exact" for _, k in claims):
        precision = "exact"
    elif claims:
        precision = "dir"

    is_file = target.is_file()
    stem = target.name if is_file else ""
    budget = args.budget or PACK_BUDGET
    blocks: list[Block] = []
    used_pages: set[str] = set()

    # --no-source：只要知识，不要源码。
    # 这个问题真实存在——用户问「改 X 有哪些坑，别贴源码」时，
    # 源码 5204 tok 全是白付，而 agent 无法表达「我只要知识层」：
    # 降预算会先把知识丢光（分层顺序如此），挤压源码额度又没有开关。
    # 实测该场景 agent 自己找到 pack 后仍花了 7183 tok，其中 72% 是源码。
    no_source = bool(getattr(args, "no_source", False))
    index_only = bool(getattr(args, "index", False))
    # 提前定义：下面的「0 块」错误分支要判断「目录里到底有没有源码」，
    # 而它原先只存在于 else 分支里，单文件路径会 NameError。
    files: list[str] = []

    # L1 目标源码：单文件按预算决定全文/大纲，目录按同一预算分摊
    # --index：只给函数级索引（页表），正文用 read_block 按需调入。
    # 索引只占几十行，省下的预算全留给知识层——这正是「上下文=cache」的装配形态。
    if is_file:
        if not no_source:
            if index_only:
                b = _source_index_block(target, rel_scope)
            else:
                b = render_source(target, rel_scope, 5, 4,
                                  allowance=int(budget * TARGET_BUDGET_SHARE))
            if b:
                blocks.append(b)
    else:
        # **必须传 rel_scope，不能传 scope**。`scope` 可能带仓库前缀
        # （`atomkgraph/apps/web/src/components/`），而 `src_files` 按仓库根相对路径
        # 找目录，带前缀时恒返回空列表 → 装出一份 0 块 0 tok 的空册子且 rc=0。
        # 单文件那条路径不受影响（它用 target，本来就是剥过前缀的），
        # 所以这个 bug 只出现在「带前缀的目录」上，实测才被发现。
        files = [r for r in src_files(base, rel_scope, root)
                 if pathlib_name(r) not in CONF_SKIP_NAMES]
        share = int(budget * TARGET_BUDGET_SHARE / max(len(files), 1))
        for rel in files:
            if no_source:
                break
            if index_only:
                b = _source_index_block(base / rel, rel)
            else:
                b = render_source(base / rel, rel, 4, 4, allowance=share)
            if b:
                blocks.append(b)

    # L2 知识节：只取点名了目标文件的二级小节；H1 横跨整页，不取
    for pg, kind in claims:
        for level, title, body in page_sections(pg):
            if level <= 1:
                continue
            if is_file:
                n = title.count(stem) + body.count(stem)
                if n == 0:
                    continue
                prio = 3 if stem in title else (3 if n >= 2 else 2)
            else:
                prio = 3 if kind == "exact" else 2
            blocks.append(Block(prio, f"{pg.rel} :: {title}", body))
            used_pages.add(pg.rel)

    # L3 兄弟文件大纲：单文件任务才有——同目录其它文件只要签名。
    # 但「兄弟」有前提：目录里文件不多。`kb.py` 的兄弟是整个 codeb 仓库，
    # 那不叫兄弟，那是又来一份全库目录。
    if is_file:
        sib_dir = target.parent.relative_to(base).as_posix()
        # 比 rel_scope 而不是 scope：`r` 是仓库内相对路径，`scope` 可能带仓库前缀，
        # 二者永不相等，于是落点文件会被当成自己的兄弟再装一份大纲。
        # 实测 `pack atomkgraph/.../ui/button.tsx` 多出 prio1 的同名块（43 tok），
        # 裸路径写法没有——一重一轻，所以它不报错，只是白付 token。
        sibs = [r for r in src_files(base, sib_dir, root)
                if r != rel_scope and pathlib_name(r) not in CONF_SKIP_NAMES]
        if len(sibs) <= SIBLING_MAX_FILES:
            for rel in sibs:
                sig, nl = file_outline(base / rel)
                if sig:
                    b = Block(1, f"{rel}  {nl} 行", sig)
                    if b.tokens <= SIBLING_MAX_TOKENS:
                        blocks.append(b)

    # L4 计划：这几页还有哪些事没做。永不丢——它是「接下来干什么」的唯一来源
    for pg, _ in claims:
        sect = plan_section_body(pg.body)
        if sect:
            blocks.append(Block(0, f"{pg.rel} :: 计划", sect))
            used_pages.add(pg.rel)

    budget = args.budget or PACK_BUDGET
    budget = args.budget or PACK_BUDGET
    total = sum(b.tokens for b in blocks)
    dropped: list[Block] = []
    if total > budget:
        for prio in (1, 2, 3, 4, 5):
            if total <= budget:
                break
            keep = []
            for b in blocks:
                if b.prio == prio and total > budget:
                    total -= b.tokens
                    dropped.append(b)
                else:
                    keep.append(b)
            blocks = keep

    silent = [pg.rel for pg, _ in claims if pg.rel not in used_pages]
    # 知识层被整层丢光是「册子还成立但已经开始骗人」的分界线：
    # agent 会照着源码开工，却不知道那些「不要修正」的站点事实。
    # 这时必须明说，而不是安静地交出一份看着完整的册子。
    know_lost = not any(b.prio in (2, 3) for b in blocks)

    # 0 块 0 tok 是硬错误，不是「空结果」。两种情况必须分开报：
    #   (a) 目录/文件真的没有源码     → 范围给错了
    #   (b) 路径压根没解析出来         → 实现有 bug
    # 合并报「0 块」会让 (b) 伪装成 (a)。前缀归一那个 bug 就是这么藏住的：
    # 带前缀的目录恒装出 0 块，而 rc=0，看起来像「这个目录没东西」。
    # --no-source 是显式只要知识层，此时 0 块合理，不在此列。
    if total == 0 and not no_source:
        _err(f"装订结果是 0 块 / 0 tok：{scope}")
        if is_file:
            _err(f"  这个文件存在（{target}），但抽不出任何内容——检查后缀是否在 SRC_EXT 里")
        elif not files:
            _err(f"  目录存在（{target}），但按 SRC_EXT 没扫到任何源码文件。")
            _err(f"  若里面有源码，检查它是否被 .gitignore 排除，或后缀是否在 SRC_EXT 里。")
        return 2

    if args.json:
        print(json.dumps({
            "scope": scope, "repo": repo, "root": str(base),
            "precision": precision, "budget": budget, "total": total,
            "knowledge_lost": know_lost,
            "blocks": [{"prio": b.prio, "label": b.label,
                        "tokens": b.tokens, "text": b.text} for b in blocks],
            "dropped": [{"label": b.label, "tokens": b.tokens} for b in dropped],
            "claims": [{"page": pg.rel, "kind": k} for pg, k in claims],
        }, ensure_ascii=False, indent=2))
        return 0

    out = [f"# 上下文包：{scope}", ""]
    out.append(f"仓库 `{repo}` · 精度 **{precision}** · 预算 {budget} · "
               f"实装 {total} tok · {len(blocks)} 块")
    if know_lost and claims:
        out.append("")
        out.append(f"> ⚠ **知识层被预算挤光了**：{len(claims)} 页认领了这个范围，"
                   f"但一节都没装进去。")
        out.append(f"> 现在这份册子只有源码，不含那些「改了会静默出错」的约束。")
        out.append(f"> 要么把预算提到 8000 左右，要么先 `kb read {claims[0][0].rel}`。")
    note = derived_note(target) if is_file else ""
    if note:
        out.append("")
        out.append(f"> ⚠ 这是派生文件（命中标记：`{note}`）。**不要手改**："
                   f"改生成器再重跑；同批有别人也碰它时必须串行。")
    out.append("")
    if precision == "none":
        out.append("> 没有任何知识页认领这个范围，下面只有源码。")
        out.append("> 干完活补一页，否则下一个 agent 还是从零开始。")
        out.append("")
    for b in blocks:
        out.append(f"## {b.label}   〔{b.tokens} tok〕")
        out.append("")
        out.append(b.text)
        out.append("")

    out.append("## 有意省略")
    out.append("")
    out.append(f"装进 {len(blocks)} 块 / {total} tok（预算 {budget}）。"
               "下面是**没装的东西和取它的命令**——要深入时用它们，不要再 search。")
    out.append("")
    for b in dropped:
        out.append(f"- 预算不足已丢：`{b.label}`（{b.tokens} tok）")
    for rel in silent:
        out.append(f"- `{rel}` 认领了该范围但没有点名这个目标的二级小节 —— `kb read {rel}`")
    if is_file and target.suffix in CODE_EXT:
        nl = len(_read_text_robust(target).splitlines())
        if nl > OUTLINE_LINE_LIMIT:
            out.append(f"- `{scope}` 全文 {nl} 行未装，只给了大纲 —— 需要时直接开文件")
    print("\n".join(out))
    return 0


def cmd_agent(root: Path, args) -> int:
    """在 codeb 里组装并运行子 agent（单任务或按计划多任务）。

    **kb.py 必须保持零依赖**（stdlib only），所以这里不 import agents，
    而是转发给 distill/agent/codeb_agent.py，由它那边的 venv 提供 openai-agents。

    组装依然走 kb 自己（子进程里调 kb pack / kb dispatch），所以「上下文来自
    codeb」这条不受影响——依赖方向始终是 agent → kb，不能反过来。

    两种模式：
      · 单任务（--scope/--task）：一次派一个 agent
      · 计划（--plan FILE）：多个任务，带 depends_on 与并发上限，走 Scheduler
    """
    import subprocess

    script = Path(__file__).resolve().parent / "distill" / "agent" / "codeb_agent.py"
    if not script.exists():
        _err(f"找不到 {script}（agent 层未安装）")
        return 2

    py = args.python
    if not py:
        venv_py = Path(__file__).resolve().parent / "_kbwork" / "agvenv" / "Scripts" / "python.exe"
        py = str(venv_py) if venv_py.exists() else sys.executable
    if not Path(py).exists():
        _err(f"python 解释器不存在：{py}（先建 _kbwork/agvenv 或用 --python 指定）")
        return 2

    # ---- 计划模式：直接把计划文件交给 run-plan，scope/task 不参与 ----
    if args.plan:
        argv = [py, "-X", "utf8", str(script), "run-plan", args.plan,
                "--concurrency", str(args.concurrency), "--json"]
        if args.persist:
            argv.append("--persist-all")
        return _run_agent_proc(argv, args.json, multi=True)

    if not args.scope or not args.task:
        _err("单任务模式需要 --scope 和 --task；或用 --plan 指定计划文件")
        return 2

    # repo 省略时由 scope 推导：scope 的第一段常常就是仓库名
    repo = args.repo
    if not repo:
        roots = repo_roots(root)
        repo, base = scope_repo(roots, norm(args.scope))
        if base is None:
            _err(f"{args.scope} 定位不到（先在仓库 overview 页写 root: <磁盘路径>）")
            return 2

    argv = [py, "-X", "utf8", str(script), "run",
            "--scope", norm(args.scope),
            "--repo", repo,
            "--task", args.task,
            "--budget", str(args.budget or PACK_BUDGET),
            *(["--max-turns", str(args.max_turns)] if args.max_turns is not None else []),
            "--json"]
    for a in args.allow:
        argv += ["--allow", a]
    for d in args.deny:
        argv += ["--deny", d]
    if args.no_source:
        argv.append("--no-source")
    if args.no_cmd:
        argv.append("--no-cmd")
    if args.note:
        argv += ["--note", args.note]
    if args.route:
        argv += ["--route", args.route]
        if args.route_degrade:
            argv.append("--route-degrade")
    if args.persist:
        argv.append("--persist")
    return _run_agent_proc(argv, args.json, multi=False)


def _run_agent_proc(argv: list[str], as_json: bool, multi: bool) -> int:
    """起子进程跑 agent，解析 JSON 并输出。

    单独抽出来是因为单任务和计划模式的收尾逻辑一致：
    都必须把失败原因的**已完成步骤**打出来——那正是「部分结果」的价值。
    """
    import subprocess

    env = dict(os.environ)
    env.setdefault("PYTHONIOENCODING", "utf-8")
    try:
        r = subprocess.run(argv, capture_output=True, text=True,
                           encoding="utf-8", errors="replace", env=env)
    except OSError as e:
        _err(f"启动 agent 失败：{e}")
        return 2

    out = (r.stdout or "").strip()
    if not out:
        _err(f"agent 无输出（退出码 {r.returncode}）\n{(r.stderr or '')[:800]}")
        return 1
    try:
        res = json.loads(out)
    except json.JSONDecodeError:
        print(out)
        if r.stderr.strip():
            print(r.stderr.strip()[:800], file=sys.stderr)
        return r.returncode or 1

    if as_json:
        print(json.dumps(res, ensure_ascii=False, indent=2))
        return 0 if (res.get("ok") if not multi else res.get("ok")) else 1

    if multi:
        results = res.get("results") or []
        for one in results:
            _print_agent_result(one)
            print()
        ok_n = sum(1 for x in results if x.get("ok"))
        skip_n = sum(1 for x in results if x.get("skipped"))
        print(f"合计 {len(results)} 个任务：成功 {ok_n} · 跳过 {skip_n} · "
              f"失败 {len(results) - ok_n - skip_n}")
        return 0 if res.get("ok") else 1

    if not res.get("ok"):
        _err(f"子 agent 失败：{res.get('error')}")
        steps = res.get("steps") or []
        if steps:
            print(f"\n已完成的 {len(steps)} 步（文件可能已被部分修改）：")
            for s in steps:
                print(f"  · {s['tool']}  {s['args'][:100]}")
        return 1

    _print_agent_result(res)
    return 0


def _print_agent_result(res: dict) -> None:
    mark = "✓" if res.get("ok") else ("⤼ 跳过" if res.get("skipped") else "✗ 失败")
    print(f"=== {mark} {res.get('name')}  {res.get('scope')} ===")
    if res.get("error"):
        print(f"  错误：{res['error']}")
    print(f"  耗时 {res.get('seconds', 0)}s · 上下文 {res.get('context_tokens', 0)} tok · "
          f"工具调用 {len(res.get('tool_calls') or [])} 次")
    if res.get("tool_calls"):
        print(f"  调用：{res['tool_calls']}")
    if res.get("answer"):
        print()
        print(res["answer"])


def _run_agent_proc(argv: list[str], as_json: bool, multi: bool) -> int:
    """起子进程跑 agent，解析 JSON 并输出。

    单独抽出来是因为单任务和计划模式的收尾逻辑一致：
    都必须把失败原因的**已完成步骤**打出来——那正是「部分结果」的价值。
    """
    import subprocess

    env = dict(os.environ)
    env.setdefault("PYTHONIOENCODING", "utf-8")
    try:
        r = subprocess.run(argv, capture_output=True, text=True,
                           encoding="utf-8", errors="replace", env=env)
    except OSError as e:
        _err(f"启动 agent 失败：{e}")
        return 2

    out = (r.stdout or "").strip()
    if not out:
        _err(f"agent 无输出（退出码 {r.returncode}）\n{(r.stderr or '')[:800]}")
        return 1
    try:
        res = json.loads(out)
    except json.JSONDecodeError:
        # 非 JSON（比如启动即崩）→ 原样透出，便于排查
        print(out)
        if r.stderr.strip():
            print(r.stderr.strip()[:800], file=sys.stderr)
        return r.returncode or 1

    if as_json:
        print(json.dumps(res, ensure_ascii=False, indent=2))
        return 0 if res.get("ok") else 1

    if multi:
        results = res.get("results") or []
        for one in results:
            _print_agent_result(one)
            print()
        ok_n = sum(1 for x in results if x.get("ok"))
        skip_n = sum(1 for x in results if x.get("skipped"))
        print(f"合计 {len(results)} 个任务：成功 {ok_n} · 跳过 {skip_n} · "
              f"失败 {len(results) - ok_n - skip_n}")
        return 0 if res.get("ok") else 1

    if not res.get("ok"):
        _err(f"子 agent 失败：{res.get('error')}")
        steps = res.get("steps") or []
        if steps:
            print(f"\n已完成的 {len(steps)} 步（文件可能已被部分修改）：")
            for s in steps:
                print(f"  · {s['tool']}  {s['args'][:100]}")
        return 1

    _print_agent_result(res)
    return 0


def cmd_dispatch(root: Path, args) -> int:
    """派发前的地面检查：写范围互斥、共享知识、接口面、派生文件。"""
    roots = repo_roots(root)
    pages = list(all_pages(root))
    scopes = [norm(s) for s in args.scopes]
    info = []
    for scope in scopes:
        repo, base = scope_repo(roots, scope)
        # target 必须用剥过前缀的路径。`base` 已经是该仓库的磁盘根，
        # 再拼一次带前缀的 scope 就变成 `<root>/atomkgraph/apps/...` → 不存在。
        # 这会让 dispatch 对「带前缀目录」直接报错，而 pack 却能跑（它用了
        # rel_scope），两个命令对同一个 scope 给出相反结论。
        rel = scope[len(repo) + 1:] if (repo and scope.startswith(repo + "/")) else scope
        target = (base / rel) if base is not None else None
        if base is None or target is None or not target.exists():
            _err(f"{scope} 定位不到（先在仓库 overview 页写 root: <磁盘路径>）")
            return 2
        # files 也用 rel：src_files 按仓库根相对路径找目录，带前缀恒返回空。
        files = [rel] if target.is_file() else src_files(base, rel, root)
        info.append({"scope": scope, "repo": repo, "base": base, "files": files,
                     "claims": claiming_pages(pages, scope)})

    conflicts = []
    for i in range(len(info)):
        for j in range(i + 1, len(info)):
            inter = sorted(set(info[i]["files"]) & set(info[j]["files"]))
            if inter:
                conflicts.append((scopes[i], scopes[j], inter))
    shared: dict[str, set[str]] = {}
    for item in info:
        for pg, _ in item["claims"]:
            shared.setdefault(pg.rel, set()).add(item["scope"])

    # 派生文件：范围内（要标串行）与范围外（改完还要重生成）。
    # 范围外那批必须单独算：典型是 capabilities.json —— 加一份站点 spec 就要
    # 重生成它，但它既不在 sites/ 里，也不在任何人的写范围里，
    # 只看写范围永远发现不了，于是两个并行任务里先加的那个静默消失。
    for it in info:
        mine = set(it["files"])
        it["derived_in"] = [(f, derived_note(it["base"] / f)) for f in it["files"]
                            if derived_note(it["base"] / f)]
        outside, seen_out = [], set()
        for d in ("", it["scope"].rsplit("/", 1)[0] if "/" in it["scope"] else ""):
            if d in seen_out:
                continue
            seen_out.add(d)
            for f in shallow_files(it["base"], d, include_skip=True):
                if f in mine:
                    continue
                n = derived_note(it["base"] / f)
                if n:
                    outside.append((f, n))
        it["derived_out"] = outside

    # 同一个派生物被 ≥2 个范围命中 = 硬冲突，不只是「各自卡片上提醒一下」。
    # capabilities.json 就是活例：加一个站点要重生成它，collector 下 7 个子范围
    # 全都这样。7 个 agent 并行各跑一次 `--write`，最后只剩一个人的结果，
    # 其余 6 个新站从能力清单里静默消失——而每个人的卡片上都只写着「注意串行」，
    # 没有人负责真的串起来。
    hot: dict[str, set[str]] = {}
    for it in info:
        for f, _ in it["derived_out"]:
            hot.setdefault(f, set()).add(it["scope"])
        for f, _ in it["derived_in"]:
            hot.setdefault(f, set()).add(it["scope"])
    serial_bottlenecks = {f: sorted(s) for f, s in hot.items() if len(s) >= 2}

    if args.json:
        print(json.dumps({
            "scopes": [{"scope": it["scope"], "repo": it["repo"],
                        "files": it["files"],
                        "claims": [pg.rel for pg, _ in it["claims"]],
                        "derived_in": [{"file": f, "mark": n} for f, n in it["derived_in"]],
                        "derived_out": [{"file": f, "mark": n} for f, n in it["derived_out"]]}
                       for it in info],
            "conflicts": [{"a": a, "b": b, "files": f} for a, b, f in conflicts],
            "shared_pages": {k: sorted(v) for k, v in shared.items()},
            "serial_bottlenecks": serial_bottlenecks,
        }, ensure_ascii=False, indent=2))
        return 0

    out = ["# 派发检查", ""]
    if conflicts:
        out.append("## ✗ 写范围冲突（不能并行派发）")
        out.append("")
        for a, b, files in conflicts:
            out.append(f"- `{a}` × `{b}` 同时写 {len(files)} 个文件：")
            for f in files[:10]:
                out.append(f"  - {f}")
        out.append("")
    else:
        out.append(f"## ✓ 写范围两两互斥（{len(scopes)} 个范围，0 冲突）")
        out.append("")

    shared2 = {k: v for k, v in shared.items() if len(v) >= 2}
    if shared2:
        out.append("## 共享知识（每个包都必须装，否则各改各的接口）")
        out.append("")
        for rel, who in sorted(shared2.items(), key=lambda kv: -len(kv[1])):
            out.append(f"- `{rel}` ← {len(who)} 个范围都认领它")
        out.append("")

    if serial_bottlenecks:
        out.append("## ⚠ 全局串行点（这些派生物被多个范围同时命中）")
        out.append("")
        for f, who in sorted(serial_bottlenecks.items(), key=lambda kv: -len(kv[1])):
            out.append(f"- `{f}` ← {len(who)} 个范围：{', '.join('`' + w + '`' for w in who)}")
        out.append("")
        out.append("**处理办法**：各 agent 只改自己的源文件，**不要**在自己分支里跑生成器。")
        out.append("全部并回后由 leader 跑一次重生成，否则后跑的会覆盖先跑的，"
                   "先完成的那部分从派生物里静默消失。")
        out.append("")

    for it in info:
        out.append(f"## 任务卡：{it['scope']}")
        out.append("")
        out.append(f"仓库 `{it['repo']}` · 写范围 {len(it['files'])} 个代码文件")
        out.append("")
        # 必须把文件列出来。原先只写「6 个代码文件」，而 agent 问的恰恰是
        # 「这个目录下有什么」——信息明明算出来了却不给，它只能重新试一遍。
        # 实测同一句提问因此重复 3 次，其中 2 次被去重拦下。
        if it["files"]:
            for f in it["files"][:30]:
                out.append(f"- `{f}`")
            if len(it["files"]) > 30:
                out.append(f"- …还有 {len(it['files']) - 30} 个")
            out.append("")
        own = {pg.rel for pg, _ in it["claims"]}
        mine = set(it["files"])
        probe = []
        for f in it["files"]:
            for pg in pages:
                if pg.rel in own:
                    continue
                for c in pg.covers:
                    if norm(c) == norm(f):
                        probe.append(f"{f}  ← `{pg.rel}` 也在描述它")
                        break
        if probe:
            out.append("### 接口面（改这些文件的签名要通知对方）")
            out.append("")
            for p in sorted(set(probe))[:12]:
                out.append(f"- {p}")
            out.append("")
        if it["derived_in"]:
            out.append("### ⚠ 串行点（派生文件：同批只能由一人重生成）")
            out.append("")
            for f, n in it["derived_in"]:
                out.append(f"- {f}（命中 `{n}`）")
            out.append("")
        if it["derived_out"]:
            out.append("### 写范围之外的派生物（改完可能还要重生成）")
            out.append("")
            for f, n in it["derived_out"][:8]:
                out.append(f"- {f}（命中 `{n}`）")
            out.append("")
        if not it["files"]:
            out.append("_写范围为空：目录里没有代码或配置文件。_")
            out.append("")
        out.append(f"装订：`kb pack {it['scope']}`")
        out.append("")
    print("\n".join(out))
    return 0


def cmd_where(root: Path, args) -> int:
    target = norm(args.path)
    if args.repo:
        bad = check_repo(root, args.repo)
        if bad:
            _err(bad)
            return 2
    hits: list[dict] = []
    for page in all_pages(root):
        if args.repo and page.repo != args.repo:
            continue
        for c in page.covers:
            if cover_match(c, target):
                hits.append({"rel": page.rel, "title": page.title, "cover": c})
                break
    if args.json:
        print(json.dumps({"target": target, "hits": hits}, ensure_ascii=False, indent=2))
        return 0
    if not hits:
        print(f"没有页面覆盖 {target}（用 kb upsert 补一页，记下 covers）")
        return 0
    print(f"{target} 被 {len(hits)} 页覆盖：")
    for h in hits:
        print(f"  {h['rel']}  —  {h['title']}")
    return 0


# ------------------------------------------------------------------ 路由装订
#
# 装订单位从「一个范围」扩到「一条路由」：成员集 + 每成员保真度。
#
# 为什么不复用 cmd_pack 的目录分支：那个分支按「预算 ÷ 文件数」平分额度，
# 于是给了 200k 预算，最大的那几个文件仍然只给大纲——实测 apps/web 43 个
# 文件在 200k 下 share=2790，19 个文件（含 20111 tok 的 QuestionPanel）被降级。
# 路由的判据不是「平均」，是「leader 点名了这个文件，所以他最知道要看多细」。
#
# 一条不变式：**成员清单永不丢**。预算不够只降档（full→index→outline），
# 实测按 prio 阶梯压预算时，5383 tok 的落点文件会被整块删掉，留下 830 tok 的
# 小文件——agent 会以为「这个范围只有这些」。

ROUTE_ROLES = ("full", "index", "outline")
# 每档在预算压力下的丢弃顺序。数字越小越先降级。
ROUTE_ROLE_PRIO = {"outline": 1, "index": 2, "full": 3}


def _route_member_block(base: Path, rel: str, role: str) -> Block | None:
    """按角色装订一个成员。三档各复用现成实现，不重写抽取逻辑。

    任何一档都**不允许返回 None**（文件存在的前提下）：成员清单永不丢是
    路由的硬不变式，而 `_source_index_block` 在子进程失败/超时时会返回 None——
    那会让成员整块消失，且 `members[]` 里它还在，只显示 0 tok。
    实测就发生过：同一个规格，CLI 跑出 3 个成员，MCP 跑出来只有 2 个块。
    """
    p = base / rel
    if not p.is_file():
        return None
    if role == "index":
        b = _source_index_block(p, rel)
        if b is not None:
            return b
        # 索引抽取失败：退回大纲，并在块头写明，别让 agent 以为拿到了索引
        sig, nl = file_outline(p)
        return Block(2, f"{rel}  {nl} 行  大纲（语义块索引抽取失败，退大纲）",
                     sig or "（无签名可抽，用 read_file_range 按行号读）")
    if role == "outline":
        sig, nl = file_outline(p)
        if not sig:
            # 抽不出签名（纯数据文件等）：给全文，不交空块
            try:
                text = _read_text_robust(p).replace("\r\n", "\n")
            except OSError:
                return None
            return Block(5, f"{rel}  {nl} 行  全文（无法抽签名，退全文）", text)
        return Block(5, f"{rel}  {nl} 行  大纲（只给签名）", sig)
    # full：**必须给一个大 allowance 或直接读文本**。
    # render_source(allowance=0) 不是「不限」，是「按 400 行启发式」——
    # 526 行的文件会拿到大纲（809 tok）而不是全文（5383 tok）。
    # 默认值有语义时，省略参数就是一次误表达（同 --with-source 那次）。
    try:
        text = _read_text_robust(p).replace("\r\n", "\n")
    except OSError:
        return None
    nl = len(text.splitlines())
    return Block(5, f"{rel}  {nl} 行  全文", text)


def _route_degrade_role(role: str) -> str:
    """降一档：full→index→outline→outline（到底了就停在 outline）。"""
    return {"full": "index", "index": "outline"}.get(role, "outline")


def cmd_route(root: Path, args) -> int:
    """按路由规格装订：显式成员集 + 每成员保真度 + 知识层，成员清单永不丢。"""
    spec_path = Path(args.spec)
    try:
        spec = json.loads(_read_text_robust(spec_path))
    except OSError as e:
        _err(f"读不到路由规格：{spec_path}（{e}）")
        return 2
    except json.JSONDecodeError as e:
        _err(f"路由规格不是合法 JSON：{spec_path}\n  {e}")
        return 2
    if not isinstance(spec, dict):
        _err("路由规格必须是对象：{repo, entry, budget, members[]}")
        return 2

    members_raw = spec.get("members") or []
    if not isinstance(members_raw, list) or not members_raw:
        _err("路由规格缺 members[]（至少一个 {path, role}）")
        return 2

    repo = spec.get("repo") or ""
    entry = norm(spec.get("entry") or "")
    roots = repo_roots(root)
    if not repo:
        repo, base = scope_repo(roots, entry)
    else:
        base = roots.get(repo)
    if base is None:
        _err(f"仓库 `{repo or '?'}` 定位不到磁盘根。已知：{', '.join(sorted(roots)) or '（无）'}")
        return 2

    # 成员归一：允许写 `atomkgraph/apps/web/...`，内部一律用剥过前缀的 rel。
    members: list[dict] = []
    for i, m in enumerate(members_raw):
        if not isinstance(m, dict) or not m.get("path"):
            _err(f"members[{i}] 缺 path")
            return 2
        raw = norm(m["path"])
        rel = raw[len(repo) + 1:] if repo and raw.startswith(repo + "/") else raw
        role = (m.get("role") or "full").lower()
        if role not in ROUTE_ROLES:
            _err(f"members[{i}].role 只能是 {ROUTE_ROLES}，收到 `{role}`")
            return 2
        members.append({"path": rel, "role": role, "why": m.get("why") or ""})

    missing = [m["path"] for m in members if not (base / m["path"]).is_file()]
    if missing:
        # 规格落盘的是**意图**，所以文件被删时必须立刻报错——
        # 册子落盘才会静默说谎（照着旧内容开工）。
        _err(f"路由里有 {len(missing)} 个成员在磁盘上不存在：")
        for p in missing[:10]:
            _err(f"  {p}")
        _err(f"（仓库 `{repo}` → {base}）")
        return 2

    # leader 预设的问题。必须尽早取出：JSON 输出里也要带上它，
    # 否则走 MCP 的 agent 看不到问题清单（那条路径只转发 JSON）。
    questions = [str(q) for q in (spec.get("questions") or []) if str(q).strip()]

    budget = args.budget or spec.get("budget") or PACK_BUDGET
    blocks: list[Block] = []
    for m in members:
        b = _route_member_block(base, m["path"], m["role"])
        if b:
            b.prio = ROUTE_ROLE_PRIO[m["role"]]
            blocks.append(b)

    # 知识层：每个成员各自反查，按 (页, 节) 去重。
    # 只取正文/标题里点名了该文件 stem 的小节——与 pack 同一判据。
    pages = list(all_pages(root))
    seen_sec: set[tuple[str, str]] = set()
    know_blocks: list[Block] = []
    for m in members:
        stem = pathlib_name(m["path"])
        for pg, _kind in claiming_pages(pages, m["path"], f"{repo}/{m['path']}"):
            for level, title, body in page_sections(pg):
                if level <= 1:
                    continue
                if stem not in title and stem not in body:
                    continue
                key = (pg.rel, title)
                if key in seen_sec:
                    continue
                seen_sec.add(key)
                know_blocks.append(Block(0, f"{pg.rel} :: {title}", body))
    blocks.extend(know_blocks)

    # ---- 预算：只降档，不删成员 ----
    total = sum(b.tokens for b in blocks)
    degraded: list[dict] = []
    dropped_know: list[Block] = []

    def _member_block(rel: str) -> Block | None:
        """按 label 前缀找回某成员当前的块。"""
        return next((x for x in blocks if x.label.startswith(rel + "  ")), None)

    if total > budget and args.degrade:
        # 阶梯降档：full→index→outline→(停)。每轮把「降了能省最多」的那个降一档，
        # 直到装得下或全部到底。按省得最多排序，而不是按顺序——
        # 否则会先把 57 tok 的小文件降成大纲（省 20 tok），大的还在占着位置。
        while total > budget:
            best = None
            for m in members:
                nxt = _route_degrade_role(m["role"])
                if nxt == m["role"]:
                    continue
                old = _member_block(m["path"])
                new = _route_member_block(base, m["path"], nxt)
                if old is None or new is None:
                    continue
                saved = old.tokens - est_tokens(new.text)
                if saved <= 0:
                    continue
                if best is None or saved > best[0]:
                    best = (saved, m, old, new, nxt)
            if best is None:
                break
            saved, m, old, new, nxt = best
            new.prio = ROUTE_ROLE_PRIO[nxt]
            blocks[blocks.index(old)] = new
            total -= saved
            prev, m["role"] = m["role"], nxt
            degraded.append({"path": m["path"], "from": prev, "to": nxt,
                             "saved": saved})

        # 还不够就先丢知识层：它比成员原文更可替代（成员清单仍然一个不少）
        if total > budget:
            for b in sorted(know_blocks, key=lambda x: -x.tokens):
                if total <= budget:
                    break
                if b in blocks:
                    blocks.remove(b)
                    total -= b.tokens
                    dropped_know.append(b)

        # 全部降到 outline 仍然超：这不是「再努力一下」能解决的，
        # 是预算比「最小可用的成员集」还小。必须报错——
        # 否则会输出一份超预算的包，而调用方以为 `--degrade` 已经保证了装得下。
        # 实测 800 tok 预算下 outline 档的三个成员仍要 1804 tok。
        if total > budget:
            _err(f"降档到底（全部 outline）仍超预算：{total} tok > {budget} tok")
            _err("")
            _err("每个成员的**最小**体积：")
            for m in members:
                b = next((x for x in blocks if x.label.startswith(m["path"] + "  ")), None)
                _err(f"  {b.tokens if b else 0:>7} tok  {m['role']:<8} {m['path']}")
            _err("")
            _err(f"预算至少要给到 {total} tok，或者用 --drop 明确去掉成员。")
            _err("这个包如果要给 agent 用，成员原文是它的全部价值——"
                 "塞不下就是任务太大了，该拆，而不是把答案换成大纲。")
            return 2

    if total > budget and not args.degrade:
        # 默认拒绝装订。悄悄降一档，答案就基于大纲而不是原文，
        # 而它长得像「装订成功」——这是最难被发现的一类失败。
        _err(f"路由装订超预算：{total} tok > {budget} tok（超 {total - budget}）")
        _err("")
        _err("成员明细：")
        for m in members:
            b = next((x for x in blocks if x.label.startswith(m["path"] + "  ")), None)
            _err(f"  {b.tokens if b else 0:>7} tok  {m['role']:<8} {m['path']}")
        if know_blocks:
            _err(f"  {sum(x.tokens for x in know_blocks):>7} tok  knowledge  "
                 f"{len(know_blocks)} 节")
        _err("")
        _err("三个选择（都是显式的，不会自动发生）：")
        _err(f"  --budget <更大的数>   当前 {budget}")
        _err("  --degrade            按 full→index→outline 自动降档，并在包顶写警告")
        _err("  --drop <path>        点名删掉某个成员（可重复）")
        return 2

    # 成员清单：**永不丢**，放最前。它同时回答「我手上有哪些原文」
    # 和「哪些只给了目录」——后者原先只在文末「有意省略」里，agent 得读到底。
    if args.json:
        print(json.dumps({
            "repo": repo, "entry": entry, "root": str(base),
            "budget": budget, "total": total,
            "members": [{"path": m["path"], "role": m["role"], "why": m["why"],
                         "tokens": (next((x.tokens for x in blocks
                                          if x.label.startswith(m["path"] + "  ")), 0))}
                        for m in members],
            "knowledge": [{"label": b.label, "tokens": b.tokens} for b in know_blocks],
            "degraded": degraded,
            "knowledge_dropped": [{"label": b.label, "tokens": b.tokens}
                                  for b in dropped_know],
            # leader 预设的问题必须出现在 JSON 里：MCP 层只转发 JSON，
            # 文本模式那段 questions 根本到不了 agent 眼里。
            # 这是「算出来不给，等于没算」的又一次：CLI 看着有，接口里没有。
            "questions": questions,
            "blocks": [{"prio": b.prio, "label": b.label, "tokens": b.tokens,
                        "text": b.text} for b in blocks],
        }, ensure_ascii=False, indent=2))
        return 0

    out = [f"# 路由包：{entry or repo}", ""]
    out.append(f"仓库 `{repo}` · 预算 {budget} · 实装 {total} tok · "
               f"{len(members)} 成员 / {len(know_blocks)} 知识节")
    if degraded:
        out.append("")
        out.append(f"> ⚠ **已降档 {len(degraded)} 个成员**（`--degrade`）："
                   "下面是降档后的形态，不是 leader 原本要的保真度。")
        for d in degraded:
            out.append(f"> - `{d['path']}`：{d['from']} → {d['to']}（省 {d['saved']} tok）")
    if dropped_know:
        out.append("")
        out.append(f"> ⚠ 知识层被挤掉 {len(dropped_know)} 节（"
                   f"{sum(b.tokens for b in dropped_know)} tok）。"
                   "「改了会静默出错」的约束可能就在里面。")

    # 成员索引：agent 的页表
    out.append("")
    out.append("## 成员索引")
    out.append("")
    out.append("| tok | 保真度 | 成员 | 说明 |")
    out.append("| --: | :-- | :-- | :-- |")
    for m in members:
        b = next((x for x in blocks if x.label.startswith(m["path"] + "  ")), None)
        tk = b.tokens if b else 0
        out.append(f"| {tk} | `{m['role']}` | `{m['path']}` | {m['why']} |")
    out.append("")
    out.append("> `full` = 原文已在下面；`index` = 只有函数级索引，正文用 "
               "`read_block(path, key)` 取；`outline` = 只有签名。")
    out.append("")

    for b in blocks:
        out.append(f"## {b.label}   〔{b.tokens} tok〕")
        out.append("")
        out.append(b.text)
        out.append("")

    # 问题清单：leader 预设的问题，一次装订后逐条问（每问都是全新调用，无历史）
    if questions:
        out.append("## 待回答的问题（leader 预设）")
        out.append("")
        for i, q in enumerate(questions, 1):
            out.append(f"{i}. {q}")
        out.append("")

    out.append("## 有意省略")
    out.append("")
    if degraded:
        for d in degraded:
            out.append(f"- 已降档：`{d['path']}` {d['from']} → {d['to']}")
    else:
        out.append("- 无降档：所有成员都按规格的保真度装入。")
    for b in dropped_know:
        out.append(f"- 知识层被挤掉：`{b.label}`（{b.tokens} tok）— `kb read` 取回")
    out.append("")
    out.append("**定位/计数类问题不要靠这份包回答**：实测模型在 155k 上下文里数不准"
               "（0/3），给 `grep` 原始命中仍只有 1/3。要用 `grep_count` / `find_line` "
               "这种「已经算好答案」的工具。")
    print("\n".join(out))
    return 0


def control_degrade(args) -> bool:
    return bool(getattr(args, "degrade", False))


def cmd_route_around(root: Path, args) -> int:
    """提议器：只提议、不装订。1-hop import 闭包 + 体量，帮 leader 点成员。

    --depth 默认 1 且只对 entry 展开：实测 Sidebar.tsx 1-hop 已经 19,166 tok
    （api.ts 一人占 64%），2-hop 会经由 api.ts 拉进整个 API 表面。
    更远处的东西由 leader 显式加成员——那是他的职责，不是解析器的推断。
    """
    scope = norm(args.around)
    roots = repo_roots(root)
    repo, base = scope_repo(roots, scope)
    if base is None:
        _err(f"{args.around} 定位不到磁盘根。已知：{', '.join(sorted(roots)) or '（无）'}")
        return 2
    rel = scope[len(repo) + 1:] if repo and scope.startswith(repo + "/") else scope
    entry = base / rel
    if not entry.is_file():
        _err(f"不是文件：{rel}（--around 只接受单个入口文件）")
        return 2

    seen: dict[str, Path] = {rel: entry}
    why: dict[str, str] = {rel: "entry"}
    frontier = [(rel, entry)]
    for _ in range(max(1, args.depth)):
        nxt = []
        for cur_rel, f in frontier:
            for spec in _imports_of(f):
                r = _resolve_import(spec, f, base)
                if r is None:
                    continue
                r_rel = r.relative_to(base).as_posix()
                if r_rel in seen:
                    continue
                seen[r_rel] = r
                why[r_rel] = cur_rel
                nxt.append((r_rel, r))
        frontier = nxt

    rows = []
    for r_rel, p in seen.items():
        try:
            text = _read_text_robust(p)
        except OSError:
            continue
        tk = est_tokens(text)
        rows.append({"path": r_rel, "tokens": tk,
                     "lines": len(text.splitlines()),
                     "imported_by": why.get(r_rel, ""),
                     "suggest": ("full" if tk <= 1500 else
                                 "index" if tk <= 6000 else "outline")})
    rows.sort(key=lambda x: -x["tokens"])

    if args.json:
        print(json.dumps({"repo": repo, "entry": rel, "depth": args.depth,
                          "members": rows,
                          "total_tokens": sum(x["tokens"] for x in rows)},
                         ensure_ascii=False, indent=2))
        return 0

    print(f"# 路由提议：{rel}（depth={args.depth}）")
    print()
    print(f"仓库 `{repo}` · {len(rows)} 个候选 · 合计 "
          f"{sum(x['tokens'] for x in rows)} tok（建 spec 时按此选 role）")
    print()
    print("| tok | 行 | 建议 role | 路径 | 被谁 import |")
    print("| --: | --: | :-- | :-- | :-- |")
    for x in rows:
        print(f"| {x['tokens']} | {x['lines']} | `{x['suggest']}` | "
              f"`{x['path']}` | `{x['imported_by']}` |")
    print()
    print("把上面想要的成员抄进路由规格的 members[]，role 可改。")
    print("**别全选 full**：把最大的那个改成 `index` 往往能省掉一半以上——")
    print("实测 api.ts 一个文件就占 Sidebar 闭包的 64%。")
    return 0


_IMPORT_FROM = re.compile(
    r"""^\s*(?:import|export)\b[^\n]*?from\s*['"]([^'"]+)['"]""", re.M)
_IMPORT_BARE = re.compile(r"""^\s*import\s*['"]([^'"]+)['"]""", re.M)
_PY_IMPORT = re.compile(r"^\s*from\s+([\w.]+)\s+import\b|^\s*import\s+([\w.]+)", re.M)


def _imports_of(path: Path) -> list[str]:
    """抽出一个文件的 import 说明符。

    TS 项目里 import 写 `.js` 而后缀实际是 `.ts`（ESM + Bundler 解析），
    所以要连后缀变体一起试——实测照 `.js` 直接拼路径永远找不到文件。
    """
    try:
        text = _read_text_robust(path)
    except OSError:
        return []
    if path.suffix in (".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs"):
        return _IMPORT_FROM.findall(text) + _IMPORT_BARE.findall(text)
    if path.suffix == ".py":
        out = []
        for a, b in _PY_IMPORT.findall(text):
            out.append(a or b)
        return out
    return []


def _resolve_import(spec: str, cur: Path, base: Path) -> Path | None:
    """解析相对 import。绝对包名（@atomkgraph/shared、react）一律跳过。"""
    if not spec.startswith("."):
        return None
    cands: list[Path] = []
    # 先试「原样使用 spec」。ESM 里 import 通常自带后缀（`./sqlite.mjs`），
    # 而下面的 with_suffix("") 会把 `.mjs` 一起剥掉——实测 webview 的
    # `import './sqlite.mjs'` 因此永远解析不到，`--around server.mjs`
    # 只报出它自己 1 个候选，看起来像「这个入口没有依赖」，其实是 bug。
    raw = cur.parent / spec
    cands.append(raw)
    stem = raw.with_suffix("")
    for suf in (".ts", ".tsx", ".mjs", ".cjs", ".js", ".jsx", ".json", ""):
        cands.append(Path(str(stem) + suf))
    # 目录 import → index.*
    for suf in (".ts", ".tsx", ".mjs", ".cjs", ".js", ".jsx"):
        cands.append(raw / f"index{suf}")
    for c in cands:
        try:
            c = c.resolve()
            c.relative_to(base.resolve())
        except (ValueError, OSError):
            continue
        if c.is_file():
            return c
    return None



# ------------------------------------------------------------------ 写入串行化
#
# 为什么需要：`_write_page` 原先是「整文件读-改-写」。两个会话同时 upsert
# 同一页的不同小节时，后写者会用自己读到的旧快照覆盖前者。
# 实测 20 个并发写 → 20 个 rc=0 全报成功，最终只剩 8 个小节，**静默丢 12 个**。
# 这不是格式问题（换成数据库不锁一样丢），是协议问题。
#
# 为什么用全库单锁而不是按页锁：知识写入的调用频率由人决定（一天几十次量级），
# 串行化的代价可以忽略；换来的好处是新建页与更新页共用一条临界区，
# 不需要为「页还不存在所以没有锁文件」这种情形设计第二套逻辑。

LOCK_DIR = ".kbwork/locks"
LOCK_TIMEOUT = 30.0          # 秒；超过就报错退出，而不是无限等待
LOCK_POLL = 0.02


def _err(msg: str) -> None:
    """往 stderr 打一行，遇到无法编码的终端就降级而不是崩。

    本机 pwsh 默认 GBK：直接 print 中文到 stderr 会得到乱码，或者抛
    UnicodeEncodeError。警告信息宁可写成带转义的形式，也不能因为
    编码问题而丢掉——那正好会把「有东西不对劲」这件事本身变成静默的。
    """
    try:
        print(msg, file=sys.stderr)
    except UnicodeEncodeError:
        enc = (getattr(sys.stderr, "encoding", None) or "ascii")
        print(msg.encode(enc, "backslashreplace").decode(enc, "replace"),
              file=sys.stderr)


def _lock_path(root: Path) -> Path:
    d = root / LOCK_DIR
    d.mkdir(parents=True, exist_ok=True)
    return d / "write.lock"


@contextlib.contextmanager
def write_lock(root: Path, timeout: float = LOCK_TIMEOUT):
    """独占写锁。跨平台，只用标准库。

    Windows 用 msvcrt.locking，POSIX 用 fcntl.flock。
    两者都是**建议锁**（advisory）：只有同样走这个函数的进程才受约束。
    这不是限制而是事实需要被记住的一点——绕过 kb.py 直接改 .md 文件
    不受此锁保护，所以写入必须始终保持单一入口。
    """
    path = _lock_path(root)
    fh = open(path, "a+b")
    deadline = time.monotonic() + timeout
    locked = False
    try:
        while True:
            try:
                if os.name == "nt":
                    import msvcrt
                    fh.seek(0)
                    msvcrt.locking(fh.fileno(), msvcrt.LK_NBLCK, 1)
                else:
                    import fcntl
                    fcntl.flock(fh.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                locked = True
                break
            except OSError:
                if time.monotonic() >= deadline:
                    print(f"等待写锁超时（{timeout:.0f}s）：{path}\n"
                          f"另一个 kb 写入进程可能卡住了。"
                          f"确认没有其它写入后可直接删掉该锁文件。",
                          file=sys.stderr)
                    raise SystemExit(2)
                time.sleep(LOCK_POLL)
        yield
    finally:
        if locked:
            try:
                if os.name == "nt":
                    import msvcrt
                    fh.seek(0)
                    msvcrt.locking(fh.fileno(), msvcrt.LK_UNLCK, 1)
                else:
                    import fcntl
                    fcntl.flock(fh.fileno(), fcntl.LOCK_UN)
            except OSError:
                pass
        fh.close()


def _read_bytes_retry(path: Path, tries: int = 8, delay: float = 0.01) -> bytes:
    """容忍 Windows 上短暂的共享冲突。

    实测：写入方 os.replace 的瞬间，并发读取会拿到 PermissionError
    （共享冲突）。这不是数据损坏，但如果直接把异常抛给读者，
    多会话下「A 在写、B 在读」就会变成 B 崩掉。退避重试即可。
    """
    for i in range(tries):
        try:
            return path.read_bytes()
        except PermissionError:
            if i == tries - 1:
                raise
            time.sleep(delay * (i + 1))
        except OSError:
            if i == tries - 1:
                raise
            time.sleep(delay * (i + 1))
    raise AssertionError("unreachable")


def _read_text_robust(path: Path, encoding: str = "utf-8-sig") -> str:
    """读文本：utf-8-sig 去 BOM，并在共享冲突时重试。"""
    raw = _read_bytes_retry(path)
    return raw.decode(encoding, errors="replace")


def _atomic_write(path: Path, data: bytes) -> None:
    """写临时文件再 os.replace。

    直接在目标文件上 write_bytes 有两个问题：
    1. 中途失败（磁盘满、进程被杀）会留下**半截页面**，而半截 Markdown
       往往仍能被解析，于是损坏会以"内容变少了"的形式静默传播。
    2. 读者可能读到写了一半的文件。
    os.replace 在同一文件系统内是原子的：读者要么看到旧文件，要么看到新文件。

    临时文件必须与目标同目录（同盘），否则 replace 会退化为复制+删除，不再原子。

    Windows 上 os.replace 会因「读者正持有目标文件句柄」而抛 PermissionError
    （共享冲突）。实测 25 次连续写入期间，并发读者会撞上 4 次（双向都会发生）。
    这里对 replace 退避重试——冲突是瞬时的，不是逻辑错误。
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), prefix=".kb-tmp-", suffix=".md")
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())      # 确保落盘后再 replace，防断电丢内容
        for i in range(10):
            try:
                os.replace(tmp, path)
                return
            except PermissionError:
                if i == 9:
                    raise
                time.sleep(0.01 * (i + 1))     # 等读者放开句柄
    except BaseException:
        with contextlib.suppress(OSError):
            os.unlink(tmp)
        raise


def _write_page(path: Path, title: str, body: str, covers: list[str],
                updated: str, parent: str = "", extra: dict | None = None) -> None:
    """写盘唯一出口：统一 LF、无 BOM、文件末尾恰好一个换行。

    这三个约束看起来琐碎，但跨平台下它们决定 diff 是否干净：
    CRLF 与 BOM 会让每次写入都产生全文件 diff，把真实改动淹掉。

    parent / extra 必须原样写回：早期版本只写 covers，导致任何一次 upsert
    都会把这两个字段**静默抹掉**——元数据在第一次编辑时就丢了，
    而丢得毫无提示。extra 承接不认识的键（tags 等），防止同类问题复发。

    并发安全由调用方持有的 write_lock() 保证；本函数自身只负责原子落盘。
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    body = body.replace("\r\n", "\n").replace("\r", "\n").strip("\n")
    fm: list[str] = []
    if parent:
        fm.append(f"parent: {parent}")
    if covers:
        fm.append("covers:")
        fm += [f"  - {c}" for c in covers]
    for k, v in (extra or {}).items():
        if k in ("parent", "covers", "updated"):
            continue
        if isinstance(v, list):
            if v:
                fm.append(f"{k}:")
                fm += [f"  - {x}" for x in v]
        elif v not in (None, ""):
            fm.append(f"{k}: {v}")
    if fm:
        fm.append(f"updated: {updated}")
        text = "\n".join(["---", *fm, "---"]) + "\n\n" + body + "\n"
    else:
        text = body + "\n"
    _atomic_write(path, text.encode("utf-8"))


def cmd_upsert(root: Path, args) -> int:
    """命中即更新、miss 即补充。

    - 命中：按 `--section` 替换该节，或 `--append` 追加到文末，或整页替换（显式 --replace）。
    - miss：新建页面。路径由 `--rel` 指定，或由 repo + 标题推导。

    整个「读→改→写」都在写锁内完成。
    只在 _write_page 里加锁是不够的：那时的 new_body 早已基于旧快照算好，
    锁只能保证写入不交错，不能保证写入基于最新内容。
    """
    with write_lock(root):
        return _upsert_locked(root, args)


def _upsert_locked(root: Path, args) -> int:
    today = date.today().isoformat()
    # 注意用 `is not None` 而不是 truthiness：--find 模式下空 body 表示「删除命中文本」，
    # 而 `args.body or ...` 会把 "" 当成「没给」而去读 --body-file。
    if args.body is not None:
        body = args.body
        body_given = True
    elif getattr(args, "body_file", None):
        # utf-8-sig：PowerShell 的 Out-File 会写 BOM，用 utf-8 读会把 BOM 当正文吞进去。
        body = Path(args.body_file).read_text(encoding="utf-8-sig")
        body_given = True
    else:
        body = ""
        body_given = False
    if not body_given and getattr(args, "find", None) is not None:
        # 「没传替换值」与「传了空串（要删除）」是两件事。
        # 前者多半是漏了参数，直接删掉命中文本会静默丢内容。
        print("--find 需要显式给替换值：传 --body '' 表示删除命中文本。",
              file=sys.stderr)
        return 2
    if not body.strip() and getattr(args, "find", None) is None:
        print("正文为空，取消写入。", file=sys.stderr)
        return 2
    if any("\ud800" <= ch <= "\udfff" for ch in body):
        body = body.encode("utf-8", "surrogateescape").decode("utf-8", "replace")

    covers = args.covers or []

    # 已存在的页：走更新
    existing_path, ambiguous = resolve_page(root, args.page) if args.page else (None, [])
    if ambiguous:
        print(f"“{args.page}” 指向多个页面，请写全路径：", file=sys.stderr)
        for a in ambiguous:
            print(f"  repo/{a}", file=sys.stderr)
        return 2

    # --find 是「只改已有页」的模式。页不存在时若不拦，它会落到新建分支，
    # 把「替换值」当正文写进一张新页——静默造出一张只含一个词的页。
    if args.find is not None and existing_path is None:
        print(f"页面不存在：{args.page or '(未给 page)'}；--find 只能改已有页。",
              file=sys.stderr)
        print("新建页面请省略 --find，用 --rel/--repo + --title + --body。", file=sys.stderr)
        return 2

    if existing_path is not None:
        page = load_page(root, existing_path)
        meta, old_body = split_frontmatter(
            _read_text_robust(existing_path).replace("\r\n", "\n").replace("\r", "\n")
        )
        merged_covers = list(dict.fromkeys([*page.covers, *covers]))

        if args.section:
            q = re.sub(r"\s+", "", args.section.lower())
            heads = list(iter_headings(old_body))
            src = old_body.splitlines()
            idx = next((i for i, (_, _, t) in enumerate(heads)
                        if q in re.sub(r"\s+", "", t.lower())), None)
            if idx is None:
                # 该节不存在：追加一个新节（这是 miss 的局部形态）
                # 若 body 自己已经以同名标题开头，不再重复加一层——否则会得到
                # `## X` 下面紧跟 `## X`，读起来是空节，这是实际踩过的坑。
                stripped = body.strip()
                first = stripped.splitlines()[0] if stripped else ""
                already = bool(_HEAD.match(first)) and \
                    re.sub(r"\s+", "", _HEAD.match(first).group(2).lower()) == q
                if already:
                    new_body = old_body.rstrip("\n") + "\n\n" + stripped + "\n"
                else:
                    new_body = old_body.rstrip("\n") + f"\n\n## {args.section}\n\n" + stripped + "\n"
                action = "section-appended"
            else:
                ln, level, _ = heads[idx]
                end = len(src)
                for ln2, level2, _ in heads[idx + 1:]:
                    if level2 <= level:
                        end = ln2
                        break
                heading = src[ln]
                rebuilt = src[:ln] + [heading, ""] + body.strip().splitlines()
                if end < len(src):
                    rebuilt += [""] + src[end:]
                new_body = "\n".join(rebuilt)
                action = "section-replaced"
        elif args.append:
            new_body = old_body.rstrip("\n") + "\n\n" + body.strip() + "\n"
            action = "appended"
        elif args.find is not None:
            # 细粒度替换：只换命中的字面文本，其余正文逐字节保留。
            # 命中数与预期不符就整体中止——「以为改了一处，实际改了七处」
            # 是这类编辑最危险的失败方式，而它不会报错。
            hits = old_body.count(args.find)
            expect = args.expect
            if hits == 0:
                print(f"没有找到要替换的文本：{args.find!r}", file=sys.stderr)
                print("（提示：这是字面匹配，不忽略空白；先用 kb_search 确认原文。）",
                      file=sys.stderr)
                return 2
            if expect is not None and hits != expect:
                print(f"命中 {hits} 处，与 --expect {expect} 不符，已中止（未写入）。",
                      file=sys.stderr)
                print("确认无误后把 --expect 改成实际命中数，或把 find 写得更具体。",
                      file=sys.stderr)
                return 2
            new_body = old_body.replace(args.find, body.strip() if body else "")
            action = f"replaced-text（{hits} 处）"
        elif args.replace:
            new_body = body.strip() + "\n"
            action = "replaced"
        else:
            print("目标页已存在：用 --section / --append / --replace 指明更新方式。",
                  file=sys.stderr)
            return 2

        title = page.title
        # 保留原页的 parent 与其它未知 frontmatter 键（tags 等）：
        # 编辑正文不该顺手删掉元数据。
        keep_parent = page.parent
        if getattr(args, "parent", None):
            keep_parent = norm(args.parent)
        extra = {k: v for k, v in meta.items()
                 if k not in ("covers", "parent", "updated")}
        _write_page(existing_path, title, new_body, merged_covers, today,
                    parent=keep_parent, extra=extra)
        out = {"action": action, "rel": page.rel, "path": str(existing_path),
               "covers": merged_covers, "tokens": est_tokens(new_body)}
        print(json.dumps(out, ensure_ascii=False, indent=2) if args.json
              else f"{action}: repo/{page.rel}.md（{out['tokens']} tok）")
        return 0

    # 不存在的页：新建
    # 路径优先级：--rel > page（当 page 已经是 repo 内相对路径时）> 由 repo+topic+title 推导
    rel = args.rel or (args.page if args.page else None)
    if not rel:
        if not args.repo:
            print("新建页面需要 --repo 或 --rel（也可以直接用位置参数给路径）。",
                  file=sys.stderr)
            return 2
        # 优先用英文标题生成文件名；中文标题回退到内容哈希，保证幂等
        name = slugify(args.title or "") or slugify(args.section or "")
        if not name:
            name = fallback_slug(args.title or args.section or body[:200])
            print(f"[kb] 标题没有 ASCII 部分，文件名回退为 {name}"
                  f"（要自定义请传 --rel）", file=sys.stderr)
        topic = slugify(args.topic) if args.topic else ""
        rel = f"{args.repo}/{topic + '/' if topic else ''}{name}"

    rel = norm(rel)
    if not rel.startswith(tuple(d.name for d in repo_dirs(root)) or ("__none__",)):
        rel = f"{args.repo}/{rel}" if args.repo and not rel.startswith(args.repo + "/") else rel
    path = repo_root(root) / (rel + ".md")
    if path.exists():
        print(f"页面已存在：repo/{rel}.md（改用 --section/--append 更新）", file=sys.stderr)
        return 2

    full = body.strip() + "\n"
    if not body.lstrip().startswith("#"):
        full = f"# {args.title or path.stem}\n\n" + full
    _write_page(path, args.title or path.stem, full, covers, today,
                parent=norm(args.parent) if getattr(args, "parent", None) else "")
    out = {"action": "created", "rel": rel, "path": str(path),
           "covers": covers, "tokens": est_tokens(full)}
    print(json.dumps(out, ensure_ascii=False, indent=2) if args.json
          else f"created: repo/{rel}.md（{out['tokens']} tok）")
    return 0


_BLK_ROW = re.compile(
    r"^\|\s*`?(?P<key>[A-Za-z0-9_.$]+)@(?P<line>\d+)`?\s*\|"
    r"\s*`?(?P<kind>[a-zA-Z]+)`?\s*\|"
    r"\s*L(?P<start>\d+)\s*-\s*(?P<end>\d+)\s*\|"
    r"(?P<rest>.*)$"
)

# 按「未转义的竖线」切分表格单元格：md 里字面竖线写作 \|
_SPLIT_CELLS = re.compile(r"(?<!\\)\|")


def cmd_reindex(root: Path, args) -> int:
    """从 Markdown 页表重建 sqlite 派生索引（md 仍是 source of truth）。

    只读 repo/**/*.md：pages/covers 来自 frontmatter 与正文，
    blocks 来自第4层符号索引 md 的表格。不解析源码，因此 kb.py 保持 stdlib-only。
    """
    db_path = index_db_path(root)
    conn = open_index(db_path)
    try:
        conn.execute("DELETE FROM blocks")
        conn.execute("DELETE FROM covers")
        conn.execute("DELETE FROM pages")
        conn.execute("DELETE FROM meta")

        pages = list(all_pages(root))
        n_pages = n_covers = n_blocks = 0
        for pg in pages:
            conn.execute(
                "INSERT OR REPLACE INTO pages(repo, rel, title, updated, path) VALUES (?,?,?,?,?)",
                (pg.repo, pg.rel, pg.title, pg.disk, pg.path.name),
            )
            n_pages += 1
            for c in pg.covers:
                cc = c.strip()
                conn.execute(
                    "INSERT OR REPLACE INTO covers(repo, page_rel, path, is_dir) VALUES (?,?,?,?)",
                    (pg.repo, pg.rel, cc, 1 if cc.endswith("/") else 0),
                )
                n_covers += 1

            # 只有符号索引页才抽 blocks（文件名在 symbols/ 下）
            if "/symbols/" not in pg.rel.replace("\\", "/"):
                continue
            text = _read_text_robust(pg.path).replace("\r\n", "\n")
            # covers[0] 就是该符号页对应的源码路径
            src = pg.covers[0] if pg.covers else ""
            for line in text.splitlines():
                m = _BLK_ROW.match(line.strip())
                if not m:
                    continue
                key = f"{m.group('key')}@{m.group('start')}"
                # 兼容两种列布局：
                #   旧 4 列：| key | kind | Lx-y | 签名 |
                #   新 5 列：| key | kind | Lx-y | 用途 | 签名 |
                # 注意：单元格里的竖线在 md 中是 `\|` 转义，必须按未转义的竖线切，
                # 否则 `def f(a: str \| None)` 这类签名会被切断，把签名误当成用途。
                cells = [c.strip() for c in _SPLIT_CELLS.split(m.group("rest"))]
                cells = [c.replace(r"\|", "|") for c in cells]
                # 去掉尾部空串（表格行以 | 结尾）
                while cells and cells[-1] == "":
                    cells.pop()
                if len(cells) >= 2:
                    purpose, sig = cells[0], cells[1]
                elif len(cells) == 1:
                    purpose, sig = "", cells[0]
                else:
                    purpose, sig = "", ""
                conn.execute(
                    "INSERT OR REPLACE INTO blocks(repo,file,key,name,kind,start,end,sig,scope,purpose,purpose_src) "
                    "VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                    (pg.repo, src, key, m.group("key"), m.group("kind"),
                     int(m.group("start")), int(m.group("end")), sig, "",
                     purpose, "md" if purpose else ""),
                )
                n_blocks += 1

        # 计数以表为准，不用累加器：INSERT OR REPLACE 遇到同 key 会覆盖，
        # 累加器会虚高（曾出现 meta.blocks=2334 而表内实际更少）。
        n_pages = conn.execute("SELECT COUNT(*) FROM pages").fetchone()[0]
        n_covers = conn.execute("SELECT COUNT(*) FROM covers").fetchone()[0]
        n_blocks = conn.execute("SELECT COUNT(*) FROM blocks").fetchone()[0]
        conn.executemany(
            "INSERT OR REPLACE INTO meta(key,value) VALUES (?,?)",
            [("schema_version", str(INDEX_SCHEMA_VERSION)),
             ("generated_at", __import__("datetime").datetime.now().isoformat()),
             ("pages", str(n_pages)), ("covers", str(n_covers)), ("blocks", str(n_blocks))],
        )
        conn.commit()
        print(f"reindex OK: {db_path}")
        print(f"  pages={n_pages} covers={n_covers} blocks={n_blocks}")
        return 0
    finally:
        conn.close()


def cmd_blocks(root: Path, args) -> int:
    """从 sqlite 索引查询语义块（需先运行 kb reindex）。"""
    db_path = index_db_path(root)
    if not db_path.exists():
        print("索引不存在，先运行: python -X utf8 kb.py reindex")
        return 1
    conn = sqlite3.connect(str(db_path))
    try:
        with_purpose = getattr(args, "purpose", False)
        cols = "repo,file,key,kind,start,end,sig,purpose"
        q = f"SELECT {cols} FROM blocks WHERE 1=1"
        p = []
        if args.file:
            q += " AND file LIKE ?"
            p.append("%" + args.file.strip("/") + "%")
        if args.name:
            q += " AND name LIKE ?"
            p.append("%" + args.name + "%")
        if with_purpose:
            q += " AND purpose <> ''"
        q += " ORDER BY repo,file,start LIMIT ?"
        p.append(getattr(args, "limit", 200))
        rows = conn.execute(q, p).fetchall()
        print(f"# 语义块查询：{len(rows)} 条（来源：{db_path}）\n")
        for repo, f, key, kind, s, e, sig, purpose in rows:
            print(f"  {repo}/{f:<44} {key:<30} {kind:<9} L{s}-{e}")
            if with_purpose:
                print(f"      用途: {purpose}")
            else:
                print(f"      {(sig or '')[:70]}")
        return 0
    finally:
        conn.close()


def cmd_covers_check(root: Path, args) -> int:
    """从 sqlite 索引做 covers 自检（stale/conflict/uncovered）。"""
    db_path = index_db_path(root)
    if not db_path.exists():
        print("索引不存在，先运行: python -X utf8 kb.py reindex")
        return 1
    conn = sqlite3.connect(str(db_path))
    try:
        rows = conn.execute(
            "SELECT c.repo, c.page_rel, c.path, c.is_dir, p.title "
            "FROM covers c LEFT JOIN pages p ON p.repo=c.repo AND p.rel=c.page_rel"
        ).fetchall()
        roots = repo_roots(root)
        # stale: 磁盘路径不存在
        stale = []
        for repo, pgrel, cpath, is_dir, title in rows:
            rel = cpath.rstrip("/")
            if repo and rel.startswith(repo + "/"):
                rel = rel[len(repo) + 1:]
            base = roots.get(repo)
            if not base:
                stale.append((repo, pgrel, cpath))
                continue
            if not (base / rel).exists() and "*" not in rel:
                stale.append((repo, pgrel, cpath))
        # conflict: 同 repo+path 被多个页 covers（排除导航/符号页）
        conflicts = {}
        for repo, pgrel, cpath, is_dir, title in rows:
            if "/00-" in pgrel or "/modules/" in pgrel or "/symbols/" in pgrel:
                continue
            conflicts.setdefault((repo, cpath), set()).add(pgrel)
        conflicts = {k: sorted(v) for k, v in conflicts.items() if len(v) > 1}

        print(f"# covers 自检（来源：{db_path}）")
        print(f"\n## stale（{len(stale)}）")
        for repo, pgrel, cpath in stale[:40]:
            print(f"  STALE {repo}/{pgrel} → {cpath}")
        print(f"\n## conflict（{len(conflicts)}）")
        for (repo, cpath), owners in list(conflicts.items())[:40]:
            print(f"  CONFLICT {repo}/{cpath} ← {', '.join(owners)}")
        # uncovered：核心源码未被任何 covers 声明（简化：用 blocks 表里的 file 反查）
        files = [r[0] for r in conn.execute("SELECT DISTINCT file FROM blocks").fetchall()]
        uncovered = []
        cover_paths = {r[0].rstrip("/") for r in conn.execute("SELECT path FROM covers").fetchall()}
        for f in files:
            if not any(f == c or c.endswith("/") and f.startswith(c) for c in cover_paths):
                uncovered.append(f)
        print(f"\n## uncovered（有语义块但无 covers 声明：{len(uncovered)}）")
        for f in uncovered[:40]:
            print(f"  UNCOVERED {f}")
        print(f"\n总计：{len(rows)} covers / {len(stale)} stale / {len(conflicts)} conflict / {len(uncovered)} uncovered")
        return 0
    finally:
        conn.close()


def cmd_init(root: Path, args) -> int:
    root.mkdir(parents=True, exist_ok=True)
    (root / ROOT_MARKER).write_text("", encoding="utf-8")
    (repo_root(root) / SHARED).mkdir(parents=True, exist_ok=True)
    print(f"已初始化知识库根：{root}")
    print(f"  {ROOT_MARKER}                 根标记")
    print(f"  {REPO_DIR}/{SHARED}/           跨仓库通用知识")
    print(f"  {REPO_DIR}/<repo-name>/       每个仓库一个英文名目录")
    return 0


# ------------------------------------------------------------------ 入口

def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(prog="kb", description="多仓库知识库基座")
    ap.add_argument("--root", help="知识库根目录（默认向上查找 .codeb）")
    ap.add_argument("--json", action="store_true", help="输出 JSON（MCP 层依赖）")
    sub = ap.add_subparsers(dest="cmd", required=True)

    t = sub.add_parser("tree")
    t.add_argument("--depth", type=int, default=3)
    t.add_argument("--repo")
    t.add_argument("--flat", action="store_true",
                   help="忽略 parent，按目录树显示（默认按 parent 折叠子页）")

    r = sub.add_parser("read")
    r.add_argument("page")
    r.add_argument("--section")

    h = sub.add_parser("heads")
    h.add_argument("page")

    s = sub.add_parser("search")
    s.add_argument("term")
    s.add_argument("--repo")
    s.add_argument("--limit", type=int, default=20)

    w = sub.add_parser("where")
    w.add_argument("path")
    w.add_argument("--repo")

    u = sub.add_parser("upsert", help="命中即更新、miss 即补充")
    u.add_argument("page", nargs="?", help="目标页（相对 repo/，可省 .md）")
    u.add_argument("--rel", help="新建时的相对路径（不含 .md）")
    u.add_argument("--repo", help="所属仓库目录名")
    u.add_argument("--topic", help="新建时折叠到的子目录（如 collector）")
    u.add_argument("--title")
    u.add_argument("--parent",
                   help="拆分来源页（相对 repo/，不含 .md）；子页将折叠显示在父页下")
    u.add_argument("--section", help="更新时：替换/新建该标题的节")
    u.add_argument("--append", action="store_true", help="更新时：追加到文末")
    u.add_argument("--replace", action="store_true", help="更新时：整页替换")
    u.add_argument("--find",
                   help="更新时：字面文本替换（细粒度）。配合 --body/--body-file 作替换值，"
                        "空值表示删除该文本。")
    u.add_argument("--expect", type=int,
                   help="与 --find 联用：命中数必须正好等于它，否则中止（防止误改多处）")
    u.add_argument("--covers", nargs="*", default=None)
    u.add_argument("--body", default=None)
    u.add_argument("--body-file", dest="body_file")

    g = sub.add_parser("graph",
                       help="把 covers 投影成页间图，看 hub / 孤立页 / 重复覆盖")
    g.add_argument("--repo")
    g.add_argument("--hub", type=int, default=5,
                   help="度数达到该值才算 hub（默认 5）")
    g.add_argument("--top", type=int, default=20,
                   help="重复覆盖最多列几条（默认 20）")

    p = sub.add_parser("plan",
                       help="列出散落在各页 ## 计划 小节的条目，状态按锚点现场算")
    p.add_argument("--repo")
    p.add_argument("--only", choices=["open", "partial", "manual", "stale", "dropped"],
                   help="只看某一桶")
    # 注意：不要在这里再声明 --json。顶层已有 --json，重复声明会让
    # 子命令用默认值 False 覆盖掉用户传的 True，导致 --json 静默失效。
    pc = p.add_subparsers(dest="plan_cmd")
    pcl = pc.add_parser("close", help="关闭一条计划：先写知识，再删条目")
    pcl.add_argument("id", metavar="P-ID")
    pcl.add_argument("--into", required=True,
                     help="知识落到哪一页（相对 repo/，不含 .md）")
    pcl.add_argument("--section", help="并进该页的哪一节（省略=追加到文末）")
    pcl.add_argument("--body-file", dest="body_file", required=True,
                     help="要并进正文的内容（背景 + 结论 + 放弃了什么）")

    pk = sub.add_parser("pack",
                        help="现场装订一份上下文：写范围 + 相关知识节 + 源码大纲，不落盘")
    pk.add_argument("scope", help="代码路径（文件或目录），相对仓库根")
    pk.add_argument("--budget", type=int, default=0,
                    help=f"token 预算（默认 {PACK_BUDGET}）；超了按可替代程度逐层丢，"
                         "并写进「有意省略」")
    pk.add_argument("--no-source", action="store_true",
                    help="只装知识层，不装源码。问「改这个有哪些坑」时用它："
                         "源码常常占总量的 70% 以上，而这个问题的答案不在源码里")
    pk.add_argument("--index", action="store_true",
                    help="源码只给函数级索引（函数名@行号），正文由 read_block 按需调入。"
                         "上下文=cache、索引=页表；省下的预算全留给知识层")

    ds = sub.add_parser("dispatch",
                        help="派发前检查：写范围互斥 / 共享知识 / 接口面 / 派生文件串行点")
    ds.add_argument("scopes", nargs="+", help="两批以上要并行的写范围")

    rt = sub.add_parser("route",
                        help="按路由规格装订：显式成员集 + 每成员保真度（full/index/outline）")
    rt.add_argument("--spec", help="路由规格 JSON 文件（{repo, entry, budget, members[], questions[]}）")
    rt.add_argument("--around", help="提议器：给一个入口文件，只提议成员、不装订")
    rt.add_argument("--depth", type=int, default=1, help="--around 的 import 深度（默认 1）")
    rt.add_argument("--budget", type=int, default=0,
                    help=f"token 预算（默认取规格里的 budget，否则 {PACK_BUDGET}）")
    rt.add_argument("--degrade", action="store_true",
                    help="超预算时按 full→index→outline 降档（默认拒绝装订并报明细）")
    rt.add_argument("--ask", action="store_true",
                    help="装订后逐条提问（每问都是全新会话，共享同一份包前缀）")
    rt.add_argument("--q", action="append", default=[],
                    help="覆盖规格里的 questions（可重复）")

    ag = sub.add_parser("agent",
                        help="在 codeb 里组装并运行子 agent（需要 openai-agents 环境）")
    ag.add_argument("scope", nargs="?", help="写范围（代码路径，相对仓库根）")
    ag.add_argument("--task", help="要做什么")
    ag.add_argument("--plan",
                    help="计划文件（JSON 任务数组）：带 depends_on 与并发上限，走 Scheduler")
    ag.add_argument("--concurrency", type=int, default=2,
                    help="并发上限（默认 2；同 key 并发过高会撞 429）")
    ag.add_argument("--persist", action="store_true",
                    help="把完整执行轨迹落盘（默认只把结论传给下游）")
    ag.add_argument("--repo", help="仓库名；省略则由 scope 推导")
    ag.add_argument("--allow", action="append", default=[],
                    help="可改文件白名单（相对仓库根），可多次；省略=只看不改")
    ag.add_argument("--deny", action="append", default=[], help="禁止改的文件，可多次")
    ag.add_argument("--budget", type=int, default=0,
                    help=f"装订预算（默认 {PACK_BUDGET}）")
    ag.add_argument("--no-source", action="store_true",
                    help="只装知识层不装源码（问「有哪些坑」时用）")
    ag.add_argument("--max-turns", type=int, default=None,
                    help="轮次上限；默认不限（任务应拆细，不要靠轮数掐断）")
    ag.add_argument("--no-cmd", action="store_true", help="不给 run_cmd 工具（只读任务）")
    ag.add_argument("--note", default="", help="追加的静态上下文（契约/警告等）")
    ag.add_argument("--route", default="",
                    help="路由规格 JSON：改走 kb route --spec（成员集 + 每成员保真度），"
                         "scope 仍用于 dispatch 与白名单推导")
    ag.add_argument("--route-degrade", action="store_true",
                    help="路由超预算时允许自动降档（默认拒绝并报明细）")
    ag.add_argument("--python", default="", help="跑 agent 的 python（默认 agvenv）")

    sub.add_parser("init")
    sub.add_parser("reindex",
                   help="从 Markdown 页表重建 sqlite 派生索引（_kbwork/codeb-index.db）")
    bk = sub.add_parser("blocks", help="从 sqlite 索引查询语义块")
    bk.add_argument("--file", help="按源码文件名/路径过滤")
    bk.add_argument("--name", help="按块名过滤")
    bk.add_argument("--limit", type=int, default=200, help="最多返回条数（默认 200）")
    bk.add_argument("--purpose", action="store_true",
                    help="只列有用途说明的块，并显示用途")
    sub.add_parser("covers-check", help="从 sqlite 索引做 covers 自检")
    return ap


HANDLERS = {
    "tree": cmd_tree, "read": cmd_read, "heads": cmd_heads,
    "search": cmd_search, "where": cmd_where, "graph": cmd_graph,
    "plan": cmd_plan, "upsert": cmd_upsert,
    "pack": cmd_pack, "dispatch": cmd_dispatch, "agent": cmd_agent,
    "route": cmd_route, "route-around": cmd_route_around,
    "reindex": cmd_reindex, "blocks": cmd_blocks, "covers-check": cmd_covers_check,
}


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stdin, "reconfigure"):
        try:
            sys.stdin.reconfigure(encoding="utf-8", errors="replace")
        except (OSError, ValueError):
            pass

    argv = list(sys.argv[1:] if argv is None else argv)
    # --json 允许写在子命令之后（MCP 层习惯自然语序，不该被参数位置绊倒）
    if "--json" in argv:
        argv = [a for a in argv if a != "--json"]
        argv.insert(0, "--json")

    args = build_parser().parse_args(argv)
    root = find_root(args.root)
    if args.cmd == "init":
        return cmd_init(root, args)
    if not repo_root(root).is_dir():
        print(f"{root} 不是知识库根（缺 {REPO_DIR}/）；先跑 kb init", file=sys.stderr)
        return 2
    # route 有两个互斥入口：--spec（装订）和 --around（提议）
    if args.cmd == "route":
        if bool(args.spec) == bool(args.around):
            _err("route 需要且只能给一个：--spec <file>（装订）或 --around <entry>（提议）")
            return 2
        if args.around:
            return cmd_route_around(root, args)
        if args.ask:
            # 提问走子进程：agvenv 里才有 openai 依赖，内核本身只用标准库。
            # 复用同一个 --spec，保证「装订出的包」与「提问用的包」是同一份。
            script = (Path(__file__).resolve().parent
                      / "distill" / "agent" / "route_ask.py")
            if not script.exists():
                _err(f"找不到 {script}（agent 层未安装）")
                return 2
            venv_py = (Path(__file__).resolve().parent
                       / "_kbwork" / "agvenv" / "Scripts" / "python.exe")
            py = str(venv_py) if venv_py.exists() else sys.executable
            argv = [py, "-X", "utf8", str(script), "--spec", args.spec]
            if args.budget:
                argv += ["--budget", str(args.budget)]
            for q in args.q:
                argv += ["--q", q]
            if args.json:
                argv.append("--json")
            # 子进程直接继承 stdout/stderr：提问是给人看的流式长任务，
            # 中间结果不该被父进程收走再统一打印（会等到全部结束才见到任何字）。
            return subprocess.call(argv, cwd=str(Path(__file__).resolve().parent))
        return cmd_route(root, args)
    return HANDLERS[args.cmd](root, args)


if __name__ == "__main__":
    raise SystemExit(main())
