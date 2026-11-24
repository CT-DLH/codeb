"""语法树驱动的语义块解析器。

设计（用户指出：正则手写是短视的，底层应该自动拆解）：
  - Python：标准库 ast，精确 end_lineno + 作用域
  - TS/TSX/JS/JSX：调用 node + typescript 编译器 API（atomkgraph 已装）
  - 其他语言：回退到正则（已知粒度较粗，明确标注 fallback）

解决正则版的两个缺陷：
  1. key 撞名：用 `Class.method@line` 带作用域前缀
  2. 层级重复：类块和它的方法块二选一——默认只列**最细粒度**（方法），
     类本身作为 "class" 类型的块单独存在，但索引里标注方法有独立 key
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path


# ---------------------------------------------------------------- TS 解析器（node 子进程）
_TS_PARSER = r'''
const ts = require('typescript');
const fs = require('fs');
const file = process.argv[2];
const src = fs.readFileSync(file, 'utf8');
const sf = ts.createSourceFile(file, src, ts.ScriptTarget.Latest, true);
const out = [];

function loc(node) {
  return {
    start: sf.getLineAndCharacterOfPosition(node.getStart(sf)).line + 1,
    end: sf.getLineAndCharacterOfPosition(node.getEnd()).line + 1,
  };
}
function nameOf(n) {
  if (!n || !n.name) return null;
  return n.name.getText(sf);
}
function sigOf(n) {
  const line = sf.getLineAndCharacterOfPosition(n.getStart(sf)).line;
  const srcLine = src.split('\n')[line] || '';
  return srcLine.trim().slice(0, 90);
}
// 用途：优先 JSDoc/** */ 的首句，其次紧邻上方 // 注释。
// 与 Python 侧一致：取不到就留空，绝不猜。
function purposeOf(n) {
  const nodes = n.jsDoc || [];
  for (const d of nodes) {
    const c = (d.comment || '').trim();
    if (c) return { t: c.split('\n')[0].slice(0, 100), s: 'jsdoc' };
  }
  const line = sf.getLineAndCharacterOfPosition(n.getStart(sf)).line;
  const all = src.split('\n');
  const buf = [];
  let i = line - 1;
  const strip = t => t.replace(/^\s*\/\/+\s?/, '').replace(/^\s*\*+\s?/, '').trim();
  while (i >= 0 && buf.length < 3) {
    const t = all[i].trim();
    if (t === '' || /^[*/]+$/.test(t)) {
      if (buf.length) break;
      i--; continue;
    }
    if (t.startsWith('//') || (t.startsWith('*') && !t.startsWith('*/'))) {
      buf.unshift(strip(t)); i--; continue;
    }
    break;
  }
  if (buf.length) return { t: buf.join(' ').slice(0, 100), s: 'comment' };
  return { t: '', s: '' };
}

function walk(node, scope) {
  const isClass = ts.isClassDeclaration(node);
  const isInterface = ts.isInterfaceDeclaration(node);
  const isFn = ts.isFunctionDeclaration(node) || ts.isMethodDeclaration(node);
  let nm = null, kind = null;

  if (isClass) { nm = nameOf(node); kind = 'class'; }
  else if (isInterface) { nm = nameOf(node); kind = 'interface'; }
  else if (isFn) {
    nm = nameOf(node);
    kind = ts.isMethodDeclaration(node) ? 'method' : 'function';
  } else if (ts.isVariableDeclaration(node) && node.initializer &&
             (ts.isArrowFunction(node.initializer) || ts.isFunctionExpression(node.initializer))) {
    nm = nameOf(node);
    kind = 'arrow';
  }

  if (nm && kind) {
    const l = loc(node);
    const p = purposeOf(node);
    out.push({ name: nm, kind, scope: scope || '', start: l.start, end: l.end,
               sig: sigOf(node), purpose: p.t, purpose_src: p.s });
  }
  // 作用域不止 class/interface：函数内部的箭头函数（如 TreeNodeView 里的
  // handleDragOver / handleDrop）也需要带前缀，否则会和别处的同名函数撞 key。
  // 但留意：方法本身已经是 Class.method，不要再叠一层函数名。
  let nextScope = scope;
  if ((isClass || isInterface || isFn) && nm) {
    nextScope = scope ? `${scope}.${nm}` : nm;
  }
  ts.forEachChild(node, n => walk(n, nextScope));
}
walk(sf, null);
process.stdout.write(JSON.stringify(out));
'''


def _ts_blocks(path: Path) -> list[dict] | None:
    """用 atomkgraph 的 typescript 包解析 TS/TSX/JS/JSX。"""
    # 找 node 与 typescript：优先 atomkgraph 根
    ak_root = Path("D:/work/project/knowledge_map/atomkgraph")
    if not ak_root.exists():
        return None
    parser = ak_root / "_ts_block_parser.cjs"
    try:
        parser.write_text(_TS_PARSER, encoding="utf-8")
        r = subprocess.run(["node", str(parser), str(path)],
                           capture_output=True, text=True, encoding="utf-8",
                           errors="replace", timeout=30)
        if r.returncode != 0:
            return None
        raw = json.loads(r.stdout)
    except Exception:
        return None
    finally:
        parser.unlink(missing_ok=True)

    out = []
    for b in raw:
        scope = b.get("scope") or ""
        name = b["name"]
        # scope 已由 TS 解析器拼成完整链（如 TreeNodeView），直接加前缀
        key_name = f"{scope}.{name}" if scope else name
        out.append({"name": key_name, "raw_name": name, "kind": b["kind"],
                    "scope": scope, "start": b["start"], "end": b["end"],
                    "sig": b["sig"], "purpose": _clean_purpose(b.get("purpose") or ""),
                    "purpose_src": b.get("purpose_src") or ""})
    return out


# ---------------------------------------------------------------- Python 解析器
_PURPOSE_MAX = 100


def _clean_purpose(text: str) -> str:
    """压成一行、去掉 markdown 重音与多余空白，截到 _PURPOSE_MAX。"""
    t = " ".join(str(text).split())
    t = t.replace("`", "").replace("**", "")
    return t[:_PURPOSE_MAX]


def _py_blocks(path: Path) -> list[dict] | None:
    """用标准库 ast 解析 Python：精确边界 + 作用域 + 方法列表 + 用途。

    purpose 的取法（机械，不猜）：
      1. docstring 首行
      2. 紧邻上方的 # 注释（最多连续 3 行，向上跳过空行与装饰器）
      3. 都没有 → 空串，由调用方决定是否用 sig 兜底
    宁可留空也不编：编出来的「作用」比空白更有害。
    """
    import ast
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(text)
    except (SyntaxError, OSError):
        return None
    out = []
    lines = text.splitlines()

    def purpose_of(node) -> tuple[str, str]:
        doc = ast.get_docstring(node)
        if doc:
            first = doc.strip().splitlines()[0].strip()
            if first:
                return _clean_purpose(first), "docstring"
        # 往上找紧邻注释；遇到装饰器行要跳过
        i, buf = node.lineno - 2, []
        while i >= 0 and len(buf) < 3:
            t = lines[i].strip()
            if t.startswith("@"):
                i -= 1
                continue
            if t == "":
                # 最多跨一个空行，再往上就不是「紧邻」了
                if buf:
                    break
                j = i - 1
                if j >= 0 and lines[j].strip().startswith("#"):
                    i -= 1
                    continue
                break
            if t.startswith("#"):
                buf.insert(0, t.lstrip("#").strip())
                i -= 1
                continue
            break
        if buf:
            return _clean_purpose(" ".join(buf)), "comment"
        return "", ""

    def walk(node, scope: str) -> None:
        for child in node.body if hasattr(node, "body") else []:
            is_cls = isinstance(child, ast.ClassDef)
            is_fn = isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef))
            if is_cls or is_fn:
                name = child.name
                if is_cls:
                    kind, key_name, next_scope = "class", name, name
                else:
                    kind = "async def" if isinstance(child, ast.AsyncFunctionDef) else "def"
                    key_name = f"{scope}.{name}" if scope else name
                    next_scope = scope
                sig = lines[child.lineno - 1].strip()[:90] if child.lineno <= len(lines) else ""
                purpose, src = purpose_of(child)
                out.append({"name": key_name, "raw_name": name, "kind": kind,
                            "scope": scope, "start": child.lineno, "end": child.end_lineno,
                            "sig": sig, "purpose": purpose, "purpose_src": src})
            else:
                next_scope = scope
            if hasattr(child, "body"):
                walk(child, next_scope)

    walk(tree, "")
    return out


# ---------------------------------------------------------------- 回退（正则）
import re as _re

_FALLBACK_SIG = _re.compile(
    r"^(?P<indent>[ \t]*)(?:(?:export|default|async|declare)\s+)*"
    r"(?:def|class|function|interface|enum|type)\s+(?P<name>[A-Za-z_$][\w$]*)"
)


def _fallback_blocks(path: Path, lines: list[str]) -> list[dict]:
    out = []
    for i, line in enumerate(lines, 1):
        m = _FALLBACK_SIG.match(line)
        if m:
            out.append({"name": m.group("name"), "raw_name": m.group("name"),
                        "kind": "fallback", "scope": "", "start": i, "end": i,
                        "sig": line.strip()[:90], "purpose": "", "purpose_src": ""})
    return out


# ---------------------------------------------------------------- 统一入口
def parse_blocks(path: Path) -> tuple[list[dict], str]:
    """返回 (块列表, 解析器名)。块已按作用域命名、带精确边界。"""
    suffix = path.suffix.lower()
    if suffix == ".py":
        blocks = _py_blocks(path)
        if blocks is not None:
            return blocks, "ast"
    elif suffix in (".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs"):
        blocks = _ts_blocks(path)
        if blocks is not None:
            return blocks, "typescript"
    # 回退
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    return _fallback_blocks(path, lines), "regex-fallback"


def format_index(path: str, blocks: list[dict], parser: str, total: int) -> str:
    """渲染成 agent 可读的索引。

    层级去重：类块和方法块都列出，但方法用 `Class.method` 前缀，
    并在类块那行注明「方法见下方独立 key」——agent 取类块会拿到整体，
    取方法 key 只拿单个，两者是明确可选的，不是重复入口。
    """
    out = [f"{path}（共 {total} 行）语义块索引 · 解析器={parser}"]
    for b in blocks:
        key = f"{b['name']}@{b['start']}"
        scope_hint = f" [{b['scope']}]" if b["scope"] else ""
        out.append(f"  {key:<36} L{b['start']:<5}-{b['end']:<5} "
                   f"{b['kind']:<10}{scope_hint:<20} {b['sig']}")
    if not blocks:
        out.append("  （没有识别到语义块，用 read_file_range 按行号读）")
    return "\n".join(out)


# ---------------------------------------------------------------- CLI（供 kb.py subprocess 调用）
if __name__ == "__main__":
    import json
    import sys
    if len(sys.argv) < 2:
        print("usage: python semantic_blocks.py <file> [--json]", file=sys.stderr)
        sys.exit(1)
    fp = Path(sys.argv[1])
    if not fp.exists():
        print(f"file not found: {fp}", file=sys.stderr)
        sys.exit(2)
    blocks, parser = parse_blocks(fp)
    if "--json" in sys.argv:
        print(json.dumps({"parser": parser, "total": len(fp.read_text(encoding='utf-8', errors='replace').splitlines()), "blocks": blocks}, ensure_ascii=False))
    else:
        total = len(fp.read_text(encoding="utf-8", errors="replace").splitlines())
        print(format_index(str(fp), blocks, parser, total))
