"""projtree：项目目录表。

一张表存结构，一张表存介绍。**扫描碰不到介绍，介绍改不了结构。**

    project_files   目录与文件清单   ← 扫描自动生成，程序唯一写者
    file_notes      每个文件的介绍   ← LLM 或 agent 写，扫描永不触碰

为什么拆两张表而不是一张：
  一张表里「覆盖结构」和「保留介绍」会打架——DELETE 重建就丢介绍，
  UPSERT 保留就删不掉已删文件。拆开后两个动作都干净：
  扫描可以整表重建，介绍一行不动；agent 改介绍时也只碰 file_notes。

为什么介绍不自动重新生成：
  源码一改就让 LLM 重写介绍，会把 agent（或人）刚精心改过的说明覆盖掉。
  所以只标记「过期」，由人和 agent 决定何时刷新。
  判定依据是 content_hash 与 note_hash 是否相等。

文件口径（选型唯一来源是 git，不读 .kbignore）：
  1. git ls-files --cached --others --exclude-standard   —— 有 .git 时最权威
     取「已跟踪 + 未跟踪但未忽略」，进了 git 的就是重要的。
  2. git 不可用时：扫整个项目（fs_files），仍跳过
     node_modules / dist / .git / _kbwork 等依赖与产物目录。
  3. SRC_SKIP 内置集合                                   —— 永远兜底

为什么不再有第二份规则文件：原先 repo/.kbignore 与 git 两份真值互相矛盾，
实测 webview/ 8 个文件都进了 git，却被 .kbignore 排除，导致 dispatch 报
「0 个代码文件」而 route --around 看得见它们。现在只认 git。
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sqlite3
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import kb  # noqa: E402  复用选型口径
from kb import repo_root  # noqa: E402  知识库的 repo/ 目录

# 入表的扩展名。含 .md：README.md / DESIGN.md / webview/README.md 是项目文档，
# 属于源码目录的一部分，不能一刀切掉。
# 但 repo/ 下的知识页是 kb 动态生成的输出，不是源码——由下面的 SKIP_TOP 单独排除。
# --all 时不看这个集合。
KEEP_EXTS = set(kb.CODE_EXT) | set(kb.CONF_EXT) | {
    ".md", ".ps1", ".sh", ".go", ".rs", ".java", ".kt", ".c", ".h",
    ".cpp", ".hpp", ".cc", ".cs", ".rb", ".php", ".swift", ".scala",
    ".txt", ".cfg", ".ini", ".toml", ".sql",
}

# 只按「顶层目录名」排除，不是任意层级——
# 否则项目里若有 src/repo/ 这类正常目录也会被误伤。
#   repo   知识库输出（727 个 md，动态生成，有专门的工具在看）
SKIP_TOP = {"repo"}

# 这些「任意层级」的目录即使未被 gitignore 也不入库：运行时会话、缓存、机器状态
EXTRA_SKIP = {".dsh-created-plugins", ".dsh", ".kbwork", ".mypy_cache",
              ".ruff_cache", ".pytest_cache", "__pycache__"}

DDL = """
CREATE TABLE IF NOT EXISTS project_files (
  repo         TEXT NOT NULL,
  path         TEXT NOT NULL,          -- 相对项目根，统一 / 分隔
  parent_path  TEXT,                   -- 父目录；'' = 项目根
  is_dir       INTEGER NOT NULL,       -- 1 目录 / 0 文件
  name         TEXT NOT NULL,
  ext          TEXT,                   -- 小写扩展名，目录为 NULL
  size         INTEGER,                -- 字节数，目录为 NULL
  mtime        REAL,                   -- 修改时间；与 size 一起决定能否复用 content_hash
  content_hash TEXT,                   -- 内容 sha256 前16位；判定介绍是否过期
  first_seen   TEXT NOT NULL,
  last_seen    TEXT NOT NULL,          -- 最近一次仍在的时间；用于清理已删文件
  PRIMARY KEY (repo, path)
);
CREATE INDEX IF NOT EXISTS idx_pf_parent ON project_files(repo, parent_path);
CREATE INDEX IF NOT EXISTS idx_pf_name   ON project_files(repo, name);

CREATE TABLE IF NOT EXISTS file_notes (
  repo        TEXT NOT NULL,
  path        TEXT NOT NULL,
  purpose     TEXT,                    -- 一句话介绍
  detail      TEXT,                    -- 可选补充
  note_hash   TEXT,                    -- 写介绍时的 content_hash
  source      TEXT NOT NULL,           -- llm / agent / human
  model       TEXT,
  updated_at  TEXT NOT NULL,
  PRIMARY KEY (repo, path)
);
CREATE INDEX IF NOT EXISTS idx_fn_source ON file_notes(repo, source);

CREATE TABLE IF NOT EXISTS scan_log (
  repo      TEXT NOT NULL,
  scan_id   TEXT NOT NULL,
  root      TEXT,
  method    TEXT,                      -- git / gitignore / fallback
  n_dirs    INTEGER,
  n_files   INTEGER,
  added     INTEGER,
  removed   INTEGER,
  elapsed_ms INTEGER,
  at        TEXT NOT NULL,
  PRIMARY KEY (repo, scan_id)
);

-- 项目注册表：哪个项目、源码在哪、从哪来。
--
-- 为什么必须是表而不是继续靠「frontmatter root: + 同名兄弟目录」两条约定：
-- 导入一个 D:\\work\\project\\foo 时两条都不成立（foo 不是 codeb 的兄弟目录，
-- 也没人给它写 frontmatter），kb.repo_roots() 就找不到源码根，
-- chat 装订目录树会直接空掉——界面看着像成功，上下文却是空的。
-- 所以这张表成为「认仓库」的第一真值，旧的两条规则退为兜底。
CREATE TABLE IF NOT EXISTS projects (
  name       TEXT PRIMARY KEY,          -- 与 repo/<name>/ 同名，英文小写
  disk_path  TEXT NOT NULL,             -- 源码磁盘根
  display    TEXT,                      -- 显示名；空则用 name
  source     TEXT NOT NULL,             -- discovered 自动发现 / imported 用户导入
  note       TEXT,
  created_at TEXT NOT NULL
);
"""


def db_path(root: Path) -> Path:
    """目录表的库固定放在本工具所在项目的 _kbwork 下。

    不能跟着 --root 走：扫 infohub 时若把库建在 infohub/_kbwork，
    等于往别人的项目里写了个 9MB 的派生文件（实测发生过一次）。
    库属于工具，不属于被扫的项目。
    """
    return Path(__file__).resolve().parent.parent / "_kbwork" / "codeb-index.db"


def open_db(root: Path) -> sqlite3.Connection:
    p = db_path(root)
    p.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(p))
    conn.executescript(DDL)
    # CREATE TABLE IF NOT EXISTS 不给旧表补列，必须显式迁移
    have = [r[1] for r in conn.execute("PRAGMA table_info(project_files)")]
    if have and "mtime" not in have:
        conn.execute("ALTER TABLE project_files ADD COLUMN mtime REAL")
    conn.commit()
    return conn


def h16(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", errors="replace")).hexdigest()[:16]


# --------------------------------------------------------------------- 枚举

def git_files(root: Path) -> tuple[list[str], str]:
    """git 口径：已跟踪 + 未跟踪但未被忽略的文件。返回 (相对路径, 方法名)。"""
    try:
        r = subprocess.run(
            ["git", "-C", str(root), "ls-files", "--cached", "--others",
             "--exclude-standard", "-z"],
            capture_output=True, timeout=180)
    except Exception:
        return [], "git-failed"
    if r.returncode != 0:
        return [], "git-failed"
    out = [x for x in r.stdout.decode("utf-8", "replace").split("\0") if x]
    return out, "git"


def fs_files(root: Path) -> tuple[list[str], str]:
    """git 不可用时：扫整个项目，只跳过依赖/产物目录。

    选型唯一来源是 git；git 拿不到时没有第二份规则文件可读
    （.kbignore 已停用），就退回字面意义的「整个项目」——
    但 node_modules / dist / .git / _kbwork 这类目录仍要挡掉。
    """
    out: list[str] = []
    for p in root.rglob("*"):
        rel = p.relative_to(root).as_posix()
        parts = rel.split("/")
        if any(seg in kb.SRC_SKIP or seg in EXTRA_SKIP for seg in parts):
            continue
        if parts[0] in SKIP_TOP:
            continue
        if p.is_file():
            out.append(rel)
    return out, "fallback"


def enumerate_project(root: Path, use_git: bool = True,
                      keep_all: bool = False) -> tuple[list[str], str]:
    """返回入表的相对路径列表（文件）与所用方法。"""
    files: list[str] = []
    method = ""
    if use_git:
        files, method = git_files(root)
    if not files:
        files, method = fs_files(root)
    # 目录节点由文件路径推导，这里只回文件；调用方补目录

    if keep_all:
        return files, method
    kept = [f for f in files
            if Path(f).suffix.lower() in KEEP_EXTS
            and f.split("/")[0] not in SKIP_TOP
            and not any(seg in EXTRA_SKIP for seg in f.split("/"))]
    return kept, method


def dirs_of(files: list[str]) -> set[str]:
    """从文件路径推导所有祖先目录。"""
    out: set[str] = set()
    for f in files:
        parts = f.split("/")[:-1]
        for i in range(1, len(parts) + 1):
            out.add("/".join(parts[:i]))
    return out


# --------------------------------------------------------------------- 扫描

def cmd_scan(root: Path, repo: str, use_git: bool, keep_all: bool,
             rehash: bool = False) -> int:
    t0 = time.time()
    files, method = enumerate_project(root, use_git, keep_all)
    if not files:
        print(f"没扫到任何文件（方法={method}）；检查路径或加 --all", file=sys.stderr)
        return 2

    scan_id = time.strftime("%Y%m%dT%H%M%S")
    now = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    conn = open_db(root)

    # 读旧记录：size + mtime 未变就不重算 hash（见下方快速路径）
    prev: dict[str, tuple] = {}
    for path, size, mtime, chash in conn.execute(
            "select path,size,mtime,content_hash from project_files "
            "where repo=? and is_dir=0", (repo,)):
        prev[path] = (size, mtime, chash)

    dirs = dirs_of(files)
    rows: list[tuple] = []

    for d in sorted(dirs):
        parts = d.split("/")
        parent = "/".join(parts[:-1])
        rows.append((repo, d, parent, 1, parts[-1], None, None, None, None,
                     now, now))

    for f in files:
        p = root / f
        parts = f.split("/")
        parent = "/".join(parts[:-1])
        try:
            st = p.stat()
        except OSError:
            continue
        size, mtime = st.st_size, st.st_mtime
        # 快速路径：size+mtime 与库里一致就复用旧的 content_hash，不读文件。
        # infohub 有 2.9 万个文件，逐个读全文算 sha256 要 536 秒；
        # 复用后降到几秒。mtime 精度足够——同一秒内改两次且大小不变才会漏判，
        # 而那种情况下 --rehash 可以强制重算。
        ch = None
        old = prev.get(f)
        if (old and not rehash and old[0] == size
                and abs((old[1] or 0) - mtime) < 1e-6 and old[2]):
            ch = old[2]
        elif size <= 2_000_000 and p.suffix.lower() in KEEP_EXTS:
            try:
                ch = h16(kb._read_text_robust(p))
            except Exception:
                ch = None
        rows.append((repo, f, parent, 0, parts[-1], p.suffix.lower(),
                     size, mtime, ch, now, now))

    # first_seen 只在首次出现时写入；last_seen 每次都刷新
    before = conn.execute("select count(*) from project_files where repo=?",
                          (repo,)).fetchone()[0]
    conn.executemany(
        """INSERT INTO project_files
             (repo,path,parent_path,is_dir,name,ext,size,mtime,content_hash,
              first_seen,last_seen)
           VALUES (?,?,?,?,?,?,?,?,?,?,?)
           ON CONFLICT(repo,path) DO UPDATE SET
             parent_path=excluded.parent_path,
             is_dir=excluded.is_dir,
             name=excluded.name,
             ext=excluded.ext,
             size=excluded.size,
             mtime=excluded.mtime,
             content_hash=excluded.content_hash,
             last_seen=excluded.last_seen""", rows)

    # 已删除的：这轮没被扫到 -> 从结构表移除。file_notes 保留（见文件头说明）
    cur = conn.execute(
        "DELETE FROM project_files WHERE repo=? AND last_seen<>?", (repo, now))
    removed = cur.rowcount
    after = conn.execute("select count(*) from project_files where repo=?",
                         (repo,)).fetchone()[0]
    added = max(0, after - before)

    ms = int((time.time() - t0) * 1000)
    nd = len(dirs)
    nf = len(rows) - nd
    conn.execute(
        """INSERT OR REPLACE INTO scan_log
           (repo,scan_id,root,method,n_dirs,n_files,added,removed,elapsed_ms,at)
           VALUES (?,?,?,?,?,?,?,?,?,?)""",
        (repo, scan_id, str(root), method, nd, nf, added, removed, ms, now))
    conn.commit()

    print(f"扫描 {repo}：目录 {nd}，文件 {nf}，新增 {added}，移除 {removed}，"
          f"方法 {method}，{ms}ms")
    stale = conn.execute(
        """select count(*) from project_files f
             join file_notes n on n.repo=f.repo and n.path=f.path
            where f.repo=? and f.is_dir=0
              and n.note_hash is not null and n.note_hash<>f.content_hash""",
        (repo,)).fetchone()[0]
    missing = conn.execute(
        """select count(*) from file_notes n
            left join project_files f on f.repo=n.repo and f.path=n.path
           where n.repo=? and f.path is null""", (repo,)).fetchone()[0]
    print(f"  介绍：过期 {stale}，孤儿 {missing}")
    return 0


def cmd_projects(root: Path, args) -> int:
    """projects list / add <path> / rm <name>。

    注意 --root 是**知识库根**（有 .codeb 的那个），而 add 的源码路径
    由位置参数给——两者是不同概念，别混用。
    """
    op = args.op or "list"

    if op == "list":
        rows = list_projects(root)
        if not rows:
            print("还没有项目。加一个：projtree projects add <源码路径>")
            return 0
        print(f"{'项目':<16}{'文件':>7}  {'来源':<11}{'状态':<8}磁盘路径")
        conn = open_db(root)
        try:
            for p in rows:
                n = conn.execute(
                    "select count(*) from project_files where repo=? and is_dir=0",
                    (p["name"],)).fetchone()[0]
                state = ("缺失" if not p["exists"] else
                         ("已登记" if p["registered"] else "未登记"))
                print(f"{p['name']:<16}{n:>7}  {p['source']:<11}{state:<8}"
                      f"{p['disk_path'] or '—'}")
        finally:
            conn.close()
        return 0

    if op == "add":
        src = args.target or ""
        if not src:
            print("用法：projtree projects add <源码路径> [--name x]", file=sys.stderr)
            return 2
        disk = Path(src).expanduser()
        if not disk.is_dir():
            print(f"路径不存在或不是目录：{disk}", file=sys.stderr)
            return 2
        name = (args.name or disk.resolve().name).strip().lower()
        try:
            p = register_project(root, name, str(disk.resolve()),
                                 display=args.display, source="imported",
                                 note=args.note)
        except ValueError as e:
            print(str(e), file=sys.stderr)
            return 2
        print(f"已登记项目 {p['name']} → {p['disk_path']}")
        # 顺手建 repo/<name>/knowledge/ 骨架，否则知识库里查不到这个项目
        d = repo_root(root) / name / "knowledge"
        d.mkdir(parents=True, exist_ok=True)
        print(f"知识页骨架：{d.relative_to(root)}")
        print(f"接着可跑：python -m distill.projtree --root {p['disk_path']} scan")
        return 0

    if op == "rm":
        name = (args.target or args.name or "").strip()
        if not name:
            print("用法：projtree projects rm <项目名>", file=sys.stderr)
            return 2
        if unregister_project(root, name):
            print(f"已注销 {name} 的登记（repo/ 与磁盘文件都保留）")
            return 0
        print(f"{name} 不在注册表里", file=sys.stderr)
        return 1

    return 2


# --------------------------------------------------------------- 项目注册表

def list_projects(root: Path) -> list[dict]:
    """列出所有项目：注册表里的 + 磁盘上发现但没登记的。

    两路合并，因为一个知识库的历史状态可能只有后者：
    老库（没跑过 projects add）四个项目全靠 frontmatter/兄弟目录约定，
    主页要把它们也显示出来，否则升级后主页是空的。

    返回顺序：先 registered，再 discovered，各自按名字排序。
    """
    conn = open_db(root)
    try:
        rows = conn.execute(
            "select name,disk_path,display,source,note,created_at "
            "from projects order by name").fetchall()
    finally:
        conn.close()

    out: dict[str, dict] = {}
    for name, disk, display, source, note, created in rows:
        out[name] = {
            "name": name, "disk_path": str(disk), "display": display or name,
            "source": source or "imported", "note": note or "",
            "created_at": created or "", "registered": True,
            "exists": Path(disk).is_dir(),
        }

    # 补充：知识库里已有目录、但没登记的（老库升级路径）
    for name in _known_repo_names(root):
        if name in out or name.startswith("_"):
            continue                      # _shared 这类不是可进入的项目
        disk = _guess_disk_root(root, name)
        out[name] = {
            "name": name, "disk_path": str(disk) if disk else "",
            "display": name, "source": "discovered", "note": "",
            "created_at": "", "registered": False,
            "exists": bool(disk and Path(disk).is_dir()),
        }

    def sortkey(p: dict):
        return (0 if p["registered"] else 1, p["name"])

    return sorted(out.values(), key=sortkey)


def _known_repo_names(root: Path) -> list[str]:
    """repo/ 下有一级子目录的仓库名（即知识库里真实存在的项目）。"""
    d = repo_root(root)
    try:
        return sorted(e.name for e in d.iterdir() if e.is_dir())
    except OSError:
        return []


def _guess_disk_root(root: Path, name: str) -> Path | None:
    """猜某个仓库的源码根：frontmatter root: → 兄弟目录。猜不到返回 None。

    与 kb.repo_roots 的判定顺序一致，只是限定在单个仓库上。
    """
    d = repo_root(root) / name
    try:
        for pg in sorted(d.rglob("*.md")):
            text = pg.read_text(encoding="utf-8", errors="replace")
            head = "\n".join(text.splitlines()[:24])
            m = re.search(r"^root:\s*(.+)$", head, re.M)
            if m:
                p = Path(m.group(1).strip().strip("\"'"))
                if p.is_dir():
                    return p
    except OSError:
        pass
    sib = Path(root).resolve().parent / name
    return sib if sib.is_dir() else None


def register_project(root: Path, name: str, disk_path: str,
                     display: str = "", source: str = "imported",
                     note: str = "") -> dict:
    """登记/更新一个项目。只写注册表，不碰 repo/ 与磁盘。"""
    name = (name or "").strip()
    if not name:
        raise ValueError("项目名不能为空")
    if not re.fullmatch(r"[a-z0-9][a-z0-9._-]*", name):
        raise ValueError(f"项目名必须是英文小写字母/数字/._-，得到：{name!r}")
    disk = Path(disk_path).expanduser()
    if not disk.is_absolute():
        disk = disk.resolve()
    t = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    conn = open_db(root)
    try:
        conn.execute(
            "INSERT INTO projects (name,disk_path,display,source,note,created_at) "
            "VALUES (?,?,?,?,?,?) "
            "ON CONFLICT(name) DO UPDATE SET disk_path=excluded.disk_path, "
            "display=excluded.display, source=excluded.source, note=excluded.note",
            (name, str(disk), display or name, source, note, t))
        conn.commit()
    finally:
        conn.close()
    return {"name": name, "disk_path": str(disk), "display": display or name,
            "source": source, "note": note, "exists": disk.is_dir()}


def unregister_project(root: Path, name: str) -> bool:
    """注销登记。**不删 repo/、不删磁盘、不删目录表数据**。

    删知识页是不可逆操作，必须走人工；这里只负责「主页不再显示它」。
    """
    conn = open_db(root)
    try:
        cur = conn.execute("DELETE FROM projects WHERE name=?", (name,))
        conn.commit()
        return cur.rowcount > 0
    finally:
        conn.close()


# --------------------------------------------------------------------- 查询

def _note_state(note_hash: str | None, content_hash: str | None,
                exists: bool) -> str:
    if not exists:
        return "孤儿"
    if note_hash is None:
        return "未写"
    if content_hash is None:
        return "无哈希"
    return "新鲜" if note_hash == content_hash else "过期"


def nest_items(items: list[dict], base: str) -> list[dict]:
    """把扁平 items 组装成嵌套树。

    每个节点：{name, path, type, children?, purpose?, state?, size?}
    目录行若被过滤掉，仍用文件路径中的段补出中间目录。
    """
    root: dict = {"children": {}}
    for it in items:
        rel = it["rel"].strip("/")
        parts = [p for p in rel.split("/") if p]
        cur = root
        for i, seg in enumerate(parts):
            is_last = i == len(parts) - 1
            leaf = cur["children"].get(seg)
            if leaf is None:
                p = it["path"] if is_last else "/".join(
                    ([base] if base else []) + parts[:i + 1])
                leaf = {"children": {}, "_n": {
                    "name": seg, "path": p, "type": "dir"}}
                cur["children"][seg] = leaf
            if is_last:
                n = leaf["_n"]
                n["type"] = "dir" if it["is_dir"] else "file"
                if it.get("purpose"):
                    n["purpose"] = it["purpose"]
                if it.get("state"):
                    n["state"] = it["state"]
                if it.get("size") is not None and not it["is_dir"]:
                    n["size"] = it["size"]
            cur = leaf

    def emit(node: dict) -> list[dict]:
        out = []
        for child in node["children"].values():
            n = dict(child["_n"])
            kids = emit(child)
            if kids:
                n["children"] = kids
            out.append(n)
        return out
    return emit(root)


def cmd_tree(root: Path, repo: str, sub: str, only: str, depth: int,
             as_json: bool, nested: bool = False) -> int:
    conn = open_db(root)
    base = sub.strip("/")
    like = f"{base}/%" if base else "%"
    # nested 输出由文件末尾统一处理，见 cmd_tree 的 as_json 分支
    rows = list(conn.execute(
        """select f.path,f.is_dir,f.size,f.content_hash,
                  n.purpose,n.note_hash,n.source
             from project_files f
             left join file_notes n on n.repo=f.repo and n.path=f.path
            where f.repo=? and (f.path like ? or f.path=?)
            order by f.path""", (repo, like, base or "\x00")))
    if not rows:
        print(f"没有 {repo} 的目录表；先跑 scan", file=sys.stderr)
        return 1

    items = []
    for path, is_dir, size, chash, purpose, nhash, src in rows:
        # 指定子树时，base 自身就是标题行，不能再当成子项打印
        if base and path == base:
            continue
        rel = path[len(base) + 1:] if base and path.startswith(base + "/") else path
        if not rel:
            continue
        if rel.count("/") > depth:
            continue
        state = _note_state(nhash, chash, True) if not is_dir else ""
        if only == "stale" and state != "过期":
            continue
        if only == "missing" and state != "未写":
            continue
        if only == "nodedoc" and (is_dir or purpose):
            continue
        items.append({"path": path, "rel": rel, "is_dir": bool(is_dir),
                      "size": size, "purpose": purpose, "state": state,
                      "source": src})

    if as_json:
        if nested:
            out = {
                "view": "source", "repo": repo, "base": base,
                "tree": nest_items(items, base),
                "count": len(items),
                "files": sum(1 for i in items if not i["is_dir"]),
            }
        else:
            out = items
        print(json.dumps(out, ensure_ascii=False, indent=2))
        return 0
    if not items:
        print(f"{repo}/{base or ''} 无匹配项（过滤条件 --only {only}）")
        return 0

    print(f"{repo}/{base}" if base else repo)
    # 指定子树时，rel 已剥掉 base 前缀，层级从 1 起算，
    # 否则子节点会与根节点同级（实测 `tree distill` 把 agent/ 画在了 distill/ 同层）。
    bump = 1 if base else 0
    for it in items:
        name = it["rel"].split("/")[-1]
        ind = "  " * (it["rel"].count("/") + bump)
        if it["is_dir"]:
            print(f"{ind}{name}/")
            continue
        tail = it["purpose"] or ""
        mark = {"过期": "  ⚠ 过期", "未写": "  · 未写", "孤儿": "  ⚠ 孤儿",
                "无哈希": ""}.get(it["state"], "")
        size = f"{it['size']}B" if it["size"] is not None else ""
        line = f"{ind}{name}"
        if size:
            line += f"  ({size})"
        if tail:
            line += f"  — {tail}"
        print(f"{line}{mark}")
    # 汇总
    n_stale = sum(1 for i in items if i["state"] == "过期")
    n_miss = sum(1 for i in items if i["state"] == "未写")
    print(f"\n共 {len(items)} 项（过期 {n_stale}，未写 {n_miss}）")
    return 0


def cmd_set_note(root: Path, repo: str, path: str, purpose: str,
                 detail: str | None, source: str, model: str | None) -> int:
    """写介绍。只碰 file_notes，note_hash 同步为当前 content_hash。"""
    conn = open_db(root)
    path = path.replace("\\", "/").lstrip("./")
    row = conn.execute(
        "select content_hash,is_dir from project_files where repo=? and path=?",
        (repo, path)).fetchone()
    if row is None:
        print(f"{path} 不在目录表里；先跑 scan（或检查路径）", file=sys.stderr)
        return 2
    chash, is_dir = row
    if is_dir:
        print(f"{path} 是目录，目录不写介绍", file=sys.stderr)
        return 2
    now = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    conn.execute(
        """INSERT INTO file_notes
             (repo,path,purpose,detail,note_hash,source,model,updated_at)
           VALUES (?,?,?,?,?,?,?,?)
           ON CONFLICT(repo,path) DO UPDATE SET
             purpose=excluded.purpose,
             detail=COALESCE(excluded.detail, file_notes.detail),
             note_hash=excluded.note_hash,
             source=excluded.source,
             model=excluded.model,
             updated_at=excluded.updated_at""",
        (repo, path, purpose, detail, chash, source, model, now))
    conn.commit()
    print(f"OK {path}  ← [{source}] {purpose}")
    return 0


def cmd_stats(root: Path, repo: str) -> int:
    conn = open_db(root)
    nd = conn.execute("select count(*) from project_files where repo=? and is_dir=1",
                      (repo,)).fetchone()[0]
    nf = conn.execute("select count(*) from project_files where repo=? and is_dir=0",
                      (repo,)).fetchone()[0]
    nn = conn.execute("select count(*) from file_notes where repo=?", (repo,)).fetchone()[0]
    stale = conn.execute(
        """select count(*) from project_files f
             join file_notes n on n.repo=f.repo and n.path=f.path
            where f.repo=? and f.is_dir=0
              and n.note_hash is not null and n.note_hash<>f.content_hash""",
        (repo,)).fetchone()[0]
    orphan = conn.execute(
        """select count(*) from file_notes n
            left join project_files f on f.repo=n.repo and f.path=n.path
           where n.repo=? and f.path is null""", (repo,)).fetchone()[0]
    nohash = conn.execute(
        "select count(*) from project_files where repo=? and is_dir=0 "
        "and content_hash is null", (repo,)).fetchone()[0]
    print(f"repo={repo}")
    print(f"  目录 {nd}   文件 {nf}")
    print(f"  介绍 {nn}   未写 {nf - nn + orphan}   过期 {stale}   孤儿 {orphan}")
    print(f"  无哈希（二进制/超大，不判过期）{nohash}")
    last = conn.execute(
        "select scan_id,method,n_dirs,n_files,elapsed_ms from scan_log "
        "where repo=? order by scan_id desc limit 1", (repo,)).fetchone()
    if last:
        print(f"  最近扫描 {last[0]}  方法 {last[1]}  "
              f"{last[2]} 目录 / {last[3]} 文件  {last[4]}ms")

    rows = list(conn.execute(
        """select f.ext, count(*) n,
                  sum(case when n2.path is not null then 1 else 0 end) noted
             from project_files f
             left join file_notes n2 on n2.repo=f.repo and n2.path=f.path
            where f.repo=? and f.is_dir=0
            group by f.ext order by n desc""", (repo,)))
    if rows:
        print(f"\n  {'扩展名':10s} {'文件':>6s} {'已写介绍':>8s}")
        for ext, n, noted in rows:
            print(f"  {ext or '(无)':10s} {n:6d} {int(noted or 0):8d}")
    return 0


def cmd_orphans(root: Path, repo: str) -> int:
    conn = open_db(root)
    rows = list(conn.execute(
        """select n.path,n.purpose,n.source,n.updated_at
             from file_notes n
             left join project_files f on f.repo=n.repo and f.path=n.path
            where n.repo=? and f.path is null order by n.path""", (repo,)))
    if not rows:
        print(f"{repo} 没有孤儿介绍")
        return 0
    print(f"{repo} 有 {len(rows)} 条孤儿介绍（文件已不在目录表中）：")
    for path, purpose, source, ts in rows:
        print(f"  {path}\n    [{source}] {purpose or '（空）'}  ({ts})")
    print("\n这些不自动删除：文件可能被 git 恢复，介绍还能复用。\n"
          "确认要清理用：projtree forget <repo> <path>")
    return 0


def cmd_forget(root: Path, repo: str, path: str) -> int:
    conn = open_db(root)
    cur = conn.execute("delete from file_notes where repo=? and path=?",
                       (repo, path.replace("\\", "/").lstrip("./")))
    conn.commit()
    if cur.rowcount == 0:
        print(f"{path} 没有介绍可删", file=sys.stderr)
        return 1
    print(f"已删除 {path} 的介绍")
    return 0


def cmd_clean(root: Path, repo: str, prefix: str | None, yes: bool) -> int:
    """批量删孤儿介绍。默认列出不删，--yes 才执行。

    孤儿通常是「文件被删」留下的，可能有价值（文件恢复后能复用），
    所以默认不删。但当扫描口径改变（如把 repo/ 移出目录表）时，
    会产生大批「本来就不该写」的介绍，此时用 --prefix repo/ 一次清掉。
    """
    conn = open_db(root)
    sql = """select n.path from file_notes n
               left join project_files f on f.repo=n.repo and f.path=n.path
              where n.repo=? and f.path is null"""
    args: list = [repo]
    if prefix:
        sql += " and n.path like ?"
        args.append(prefix.rstrip("/") + "/%")
    sql += " order by n.path"
    rows = [r[0] for r in conn.execute(sql, args)]
    if not rows:
        print("没有匹配的孤儿介绍")
        return 0
    print(f"匹配 {len(rows)} 条孤儿介绍")
    for p in rows[:8]:
        print(f"  {p}")
    if len(rows) > 8:
        print(f"  ... 其余 {len(rows) - 8} 条")
    if not yes:
        print("\n这是预览。确认删除请加 --yes")
        return 0
    conn.executemany("delete from file_notes where repo=? and path=?",
                     [(repo, p) for p in rows])
    conn.commit()
    print(f"已删除 {len(rows)} 条")
    return 0


NOTE_SCHEMA = {
    "type": "object",
    "properties": {
        "nodes": {
            "type": "array",
            "description": "为给定的每个文件各返回一条介绍",
            "items": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "文件路径，逐字照抄"},
                    "purpose": {"type": "string",
                                "description": "一句话说清它是什么、为什么存在，30 字以内"},
                },
                "required": ["path", "purpose"],
            },
        },
    },
    "required": ["nodes"],
}


def build_note_prompt(repo: str, items: list[dict]) -> str:
    listing = []
    for it in items:
        head = f"### {it['path']}  ({it['size']}B"
        head += f", {it['lines']} 行)" if it.get("lines") else ")"
        body = it.get("excerpt") or "（无内容/二进制）"
        listing.append(f"{head}\n{body}")
    return f"""下面是 {repo} 项目里若干文件的摘要。请为每个文件单独写一句介绍。

要求：
- purpose 一句话，30 字以内，说清**这个文件本身是什么**。
  主语必须是这个文件，不要描述整个项目。
  反例（错）：README.md 写成「知识库 CLI 基座」——那是 kb.py 的定位。
  正例（对）：README.md 写成「项目说明：目标、目录结构、四条强制规则」。
- **每个文件的介绍必须不一样**。如果几个文件都是文档、都同属一层，
  要写出它们各自的内容差异，不要用同一句话套。
- 依据给出的摘要判断。摘要里的标题、首行、注释就是最直接的线索。
  看不出来就写「用途不明」，不要编造项目里没有的东西。
- path 必须与给出的路径逐字一致，不许改名。
- 目录结构、文件是否存在都由扫描确定，不需要你判断。

{chr(10).join(listing)}

返回 JSON：nodes 数组，每项含 path 和 purpose。"""


def _excerpt(p: Path, limit_lines: int = 60, limit_chars: int = 3000) -> dict:
    """取文件摘要给模型看：行数 + 头部若干行。"""
    try:
        text = kb._read_text_robust(p)
    except Exception:
        return {"excerpt": None, "lines": None}
    lines = text.count("\n") + 1
    body = "\n".join(text.splitlines()[:limit_lines])
    if len(body) > limit_chars:
        body = body[:limit_chars] + "\n..."
    elif lines > limit_lines:
        body += f"\n... （共 {lines} 行）"
    return {"excerpt": body, "lines": lines}


def cmd_fill(root: Path, repo: str, mode: str, limit: int, only: str,
             force: bool, verbose: bool, model: str | None = None) -> int:
    """用 LLM 给缺少介绍的文件补上。只写 file_notes。"""
    conn = open_db(root)
    sql = """select f.path,f.size from project_files f
               left join file_notes n on n.repo=f.repo and n.path=f.path
              where f.repo=? and f.is_dir=0"""
    args: list = [repo]
    if only == "missing" and not force:
        sql += " and (n.path is null or n.purpose is null or trim(n.purpose)='')"
    elif only == "stale":
        sql += " and n.path is not null and n.note_hash is not null"
        sql += " and n.note_hash<>f.content_hash"
    elif not force:
        sql += " and n.path is null"
    sql += " order by f.path"
    if limit:
        sql += f" limit {int(limit)}"

    rows = list(conn.execute(sql, args))
    if only == "stale":
        # 过期模式只要真正过期的
        rows = [r for r in rows if _is_stale_row(conn, repo, r[0])]
    if not rows:
        print("没有需要填写的文件", file=sys.stderr)
        return 0

    print(f"待填介绍 {len(rows)} 个文件（mode={mode}）", file=sys.stderr)
    try:
        sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
        from distill import distill as _d
    except Exception as e:
        print(f"无法导入 LLM 后端: {e}", file=sys.stderr)
        return 2

    # 分批：一次让模型说太多文件，它会把介绍写串
    BATCH = 12
    ok = fail = 0
    for i in range(0, len(rows), BATCH):
        chunk = rows[i:i + BATCH]
        items = []
        for path, size in chunk:
            p = root / path
            info = _excerpt(p)
            items.append({"path": path, "size": size, **info})
        t0 = time.time()
        res = _d.call_llm(build_note_prompt(repo, items), mode,
                          verbose=verbose, schema=NOTE_SCHEMA, model=model)
        ms = int((time.time() - t0) * 1000)
        if not res or not res.get("nodes"):
            fail += len(chunk)
            print(f"[{i // BATCH + 1}] FAIL 本批 {len(chunk)} 个（模型返回空）")
            continue
        byp = {str(n.get("path", "")).strip(): str(n.get("purpose", "") or "").strip()
               for n in res["nodes"] if isinstance(n, dict)}
        for path, _size in chunk:
            purpose = byp.get(path, "")
            if not purpose:
                # 模型常把 path 写成 ./x 或少一层前缀，宽松匹配一次
                for k, v in byp.items():
                    if k.lstrip("./") == path or k.endswith("/" + path) or path.endswith("/" + k):
                        purpose = v
                        break
            if not purpose:
                fail += 1
                print(f"  MISS {path}（模型未给这一条）")
                continue
            chash = conn.execute(
                "select content_hash from project_files where repo=? and path=?",
                (repo, path)).fetchone()
            now = time.strftime("%Y-%m-%dT%H:%M:%S%z")
            conn.execute(
                """INSERT INTO file_notes
                     (repo,path,purpose,detail,note_hash,source,model,updated_at)
                   VALUES (?,?,?,?,?,?,?,?)
                   ON CONFLICT(repo,path) DO UPDATE SET
                     purpose=excluded.purpose, note_hash=excluded.note_hash,
                     source=excluded.source, model=excluded.model,
                     updated_at=excluded.updated_at""",
                (repo, path, purpose, None, chash[0] if chash else None,
                 "llm", None, now))
            ok += 1
        conn.commit()
        print(f"[{i // BATCH + 1}/{(len(rows) + BATCH - 1) // BATCH}] "
              f"{len(chunk)} 个，累计成功 {ok} ({ms}ms)")
    print(f"\n完成：成功 {ok}，失败 {fail}", file=sys.stderr)
    return 0 if fail == 0 else 1


def _is_stale_row(conn: sqlite3.Connection, repo: str, path: str) -> bool:
    r = conn.execute(
        """select n.note_hash,f.content_hash from project_files f
             join file_notes n on n.repo=f.repo and n.path=f.path
            where f.repo=? and f.path=?""", (repo, path)).fetchone()
    if not r:
        return False
    nh, ch = r
    return nh is not None and ch is not None and nh != ch


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(
        prog="python -m distill.projtree",
        description="项目目录表：结构自动扫描，介绍由 LLM/agent 填写")
    ap.add_argument("--root", default=".",
                    help="项目根目录（默认当前目录）")
    ap.add_argument("--repo", default="",
                    help="项目名（默认取根目录名）")
    sub = ap.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("scan", help="扫描并重建目录结构（不碰介绍）")
    s.add_argument("--no-git", action="store_true", help="强制走 .gitignore 解析")
    s.add_argument("--all", action="store_true", help="不按扩展名过滤，全部入库")
    s.add_argument("--rehash", action="store_true",
                   help="强制重算所有 content_hash（忽略 mtime 快速路径）")

    t = sub.add_parser("tree", help="展示目录树")
    t.add_argument("sub", nargs="?", default="", help="子树路径")
    t.add_argument("--depth", type=int, default=99)
    t.add_argument("--only", choices=["stale", "missing", "nodedoc"], default="",
                   help="stale=只看过期；missing=只看未写；nodedoc=只看没介绍的")
    t.add_argument("--json", dest="as_json", action="store_true")
    t.add_argument("--nested", action="store_true",
                   help="JSON 时输出嵌套树（供 MCP tree 工具用），默认扁平列表")

    n = sub.add_parser("note", help="写/改某个文件的介绍")
    n.add_argument("path")
    n.add_argument("--purpose", required=True)
    n.add_argument("--detail", default=None)
    n.add_argument("--source", default="agent", choices=["agent", "llm", "human"])
    n.add_argument("--model", default=None)

    sub.add_parser("stats", help="统计")
    sub.add_parser("orphans", help="列出孤儿介绍")

    # 项目注册表：主页与 repo_roots 的数据源
    pj = sub.add_parser("projects", help="项目注册表（list / add / rm）")
    pj.add_argument("op", choices=["list", "add", "rm"], nargs="?", default="list")
    pj.add_argument("target", nargs="?", default="",
                    help="add 时是源码路径；rm 时是项目名")
    pj.add_argument("--name", default="", help="项目名（默认取目录名）")
    pj.add_argument("--display", default="", help="显示名")
    pj.add_argument("--note", default="", help="备注")
    fl = sub.add_parser("fill", help="用 LLM 补介绍")
    fl.add_argument("--mode", default="openai", choices=["openai", "cmd", "none"])
    fl.add_argument("--only", default="missing",
                    choices=["missing", "stale", "all"])
    fl.add_argument("--limit", type=int, default=0)
    fl.add_argument("--force", action="store_true", help="连已有的也重写")
    fl.add_argument("--model", default=None,
                    help="覆盖 ZHIHU_LLM_MODEL（infohub 的 .env 写死了旧模型）")
    fl.add_argument("-v", "--verbose", action="store_true")
    f = sub.add_parser("forget", help="删除某条介绍")
    f.add_argument("path")
    cl = sub.add_parser("clean", help="批量删除孤儿介绍")
    cl.add_argument("--prefix", default=None,
                    help="只删这个前缀下的，如 repo/；默认删全部孤儿")
    cl.add_argument("--yes", action="store_true", help="确认执行（默认只预览）")

    args = ap.parse_args(argv)
    root = Path(args.root).resolve()
    repo = args.repo or root.name

    if args.cmd == "scan":
        return cmd_scan(root, repo, not args.no_git, args.all, args.rehash)
    if args.cmd == "tree":
        return cmd_tree(root, repo, args.sub, args.only, args.depth,
                        args.as_json, args.nested)
    if args.cmd == "note":
        return cmd_set_note(root, repo, args.path, args.purpose,
                            args.detail, args.source, args.model)
    if args.cmd == "stats":
        return cmd_stats(root, repo)
    if args.cmd == "orphans":
        return cmd_orphans(root, repo)
    if args.cmd == "fill":
        return cmd_fill(root, repo, args.mode, args.limit, args.only,
                        args.force, args.verbose, args.model)
    if args.cmd == "clean":
        return cmd_clean(root, repo, args.prefix, args.yes)
    if args.cmd == "projects":
        return cmd_projects(root, args)
    return cmd_forget(root, repo, args.path)


if __name__ == "__main__":
    raise SystemExit(main())
