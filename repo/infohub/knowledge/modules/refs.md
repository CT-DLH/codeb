---
covers:
  - collector/refs/cache.py
  - collector/refs/grammar.py
  - collector/refs/llm_parse.py
  - collector/refs/oa.py
  - collector/refs/queue.py
  - collector/refs/resolver.py
title: References Resolution Module (Layer 3)
updated: 2026-11-24
---

# 模块：引用解析——部件细页表（第3层）

**项目**：infohub
**源码文件**：`collector/refs/cache.py`、`collector/refs/grammar.py`、`collector/refs/llm_parse.py`、`collector/refs/oa.py`、`collector/refs/queue.py`、`collector/refs/resolver.py`
**第4层语义块索引**：
- `collector-refs-cache.py`: `../symbols/collector-refs-cache.py.md`
- `collector-refs-grammar.py`: `../symbols/collector-refs-grammar.py.md`
- `collector-refs-llm_parse.py`: `../symbols/collector-refs-llm_parse.py.md`
- `collector-refs-oa.py`: `../symbols/collector-refs-oa.py.md`
- `collector-refs-queue.py`: `../symbols/collector-refs-queue.py.md`
- `collector-refs-resolver.py`: `../symbols/collector-refs-resolver.py.md`
**写范围**：collector/refs/**
**验证命令**：`powershell -NoProfile -ExecutionPolicy Bypass -File _kbwork/run_regression.ps1`

## 职责
参考文献与引用链的解析、规范化与队列调度：把散落的引用变成可解析的结构化条目。

## 适用场景
- 需要定位或修改该模块内的源码部件时，先在此页选中部件，再下沉到第4层。
- 需要确认某个文件的语义块清单与行号时，打开对应 `symbols/` 页。

## 功能部件

| 部件 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| `LookupCache@33` | class | L33-110 |  | class LookupCache: |
| `default_path@27` | def | L27-30 |  | def default_path() -> Path: |
| `LookupCache.conn@42` | def | L42-50 |  | def conn(self) -> Iterator[sqlite3.Connection]: |
| `LookupCache.get@67` | def | L67-78 |  | def get(self, key: str) -> Resolved \ |
| `Citation@41` | class | L41-62 |  | class Citation: |
| `Citation.to_dict@54` | def | L54-55 |  | def to_dict(self) -> dict: |
| `Citation.merge_key@58` | def | L58-62 | 跨老师合并的键：DOI 优先，其次「规范标题+年份」。 | def merge_key(self) -> str: |
| `load_lexicon@66` | def | L66-68 |  | def load_lexicon(path: str \ |
| `build_user_prompt@70` | def | L70-76 |  | def build_user_prompt(lines: list[str], offset: int = 0) -> … |
| `normalize_papers@102` | def | L102-142 | 模型输出 → 可用题录。纯函数，离线可测。 | def normalize_papers( |
| `dedupe_papers@145` | def | L145-154 |  | def dedupe_papers(papers: list[dict[str, Any]]) -> list[dict… |
| `llm_parse_citations@157` | def | L157-217 | 一张卡（一组行）→ 题录列表。 | def llm_parse_citations( |
| `doi_of@20` | def | L20-26 |  | def doi_of(url: str) -> str: |
| `locations@37` | def | L37-67 | DOI → {"pdf_url","oa_url","is_oa"}。查不到的 DOI 不出现在结果里（不猜）。 | def locations(dois: list[str], api_key: str = "", sleep: flo… |
| `d_ok@70` | def | L70-71 |  | def d_ok(value: str) -> bool: |
| `links_for@74` | def | L74-77 | 单篇（少量条目用）；批量请走 locations()。 | def links_for(url: str, api_key: str = "") -> dict: |
| `Entry@27` | class | L27-41 |  | class Entry: |
| `Entry.add_source@33` | def | L33-36 |  | def add_source(self, from_ref: str, raw: str) -> None: |
| `Entry.to_dict@38` | def | L38-41 |  | def to_dict(self) -> dict: |
| `default_db@44` | def | L44-47 |  | def default_db() -> Path: |
| `Resolved@41` | class | L41-58 |  | class Resolved: |
| `Chain@90` | class | L90-268 | 按 lexicon 的 provider 顺序尝试；每个 provider 复用同一个插件实例（共享节流）。 | class Chain: |
| `landing_url@30` | def | L30-37 |  | def landing_url(doi: str, fallback: str = "") -> str: |
| `Resolved.to_dict@57` | def | L57-58 |  | def to_dict(self) -> dict: |

> 本模块共 **70** 个语义块，本页只列核心部件；完整清单见各 `symbols/` 页。

## 下沉指引
```
选中部件 → 打开第4层 symbols 文件 → read_block(path="collector/refs/cache.py", key="default_path@27")
选中部件 → 打开第4层 symbols 文件 → read_block(path="collector/refs/grammar.py", key="Citation@41")
选中部件 → 打开第4层 symbols 文件 → read_block(path="collector/refs/llm_parse.py", key="build_user_prompt@70")
```
