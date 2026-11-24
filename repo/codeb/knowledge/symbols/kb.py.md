---
covers:
  - kb.py
title: Semantic block index: kb.py (layer 4)
updated: 2026-11-24
---

# 语义块索引：kb.py（第4层）

**源码文件**：`kb.py`  
**解析器**：`ast`  
**第5层完整正文**：`read_block(path="kb.py", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| index_db_path@94 | def | L94-96 | 派生索引路径：_kbwork/codeb-index.db。 | def index_db_path(root: Path) -> Path: |
| open_index@99 | def | L99-114 | 打开（必要时建表）sqlite 索引，返回 connection。 | def open_index(db_path: Path): |
| IgnoreRules@121 | class | L121-263 | gitignore 语法的选型规则（.kbignore）。 | class IgnoreRules: |
| IgnoreRules.__init__@134 | def | L134-135 |  | def __init__(self, rules: list[tuple[bool, bool, "re.Pattern[str]"]]): |
| IgnoreRules.__len__@137 | def | L137-138 |  | def __len__(self) -> int: |
| IgnoreRules.load@141 | def | L141-145 |  | def load(cls, root: Path) -> "IgnoreRules": |
| IgnoreRules.parse@148 | def | L148-169 |  | def parse(cls, text: str) -> "IgnoreRules": |
| IgnoreRules._compile@172 | def | L172-197 | glob → 正则。锚定模式只匹配路径开头，否则任意层都能命中。 | def _compile(pattern: str, anchored: bool) -> "re.Pattern[str]": |
| IgnoreRules.ignored@199 | def | L199-206 | rel 是相对知识库根的 posix 路径。后规则覆盖前规则。 | def ignored(self, rel: str) -> bool: |
| IgnoreRules.excluded@208 | def | L208-210 | 语义糖：ignored 且不是被 ! 反向豁免回来的。 | def excluded(self, rel: str) -> bool: |
| IgnoreRules.prune_dir@212 | def | L212-230 | 这个目录能否整个跳过（不再向下遍历）。 | def prune_dir(self, rel: str) -> bool: |
| IgnoreRules.walk@232 | def | L232-263 | 按 .kbignore 遍历，返回相对 base 的源码路径。 | def walk(self, base: Path, exts: set[str], repo: str = "") -> list[str… |
| est_tokens@266 | def | L266-269 | 粗估 token：CJK 1 字符 1 tok，其余 3.5 字符 1 tok（偏保守，安全方向）。 | def est_tokens(text: str) -> int: |
| slugify@272 | def | L272-275 | 英文 slug。中文标题会退化成空串，交给调用方回退。 | def slugify(text: str) -> str: |
| fallback_slug@278 | def | L278-284 | 中文标题的稳定文件名：取内容哈希前 10 位。 | def fallback_slug(text: str) -> str: |
| find_root@289 | def | L289-296 | --------------------------------------------------------------------- 路径 | def find_root(explicit: str \| None) -> Path: |
| repo_root@299 | def | L299-300 |  | def repo_root(root: Path) -> Path: |
| skipped@303 | def | L303-304 |  | def skipped(name: str) -> bool: |
| norm@307 | def | L307-311 |  | def norm(p: str) -> str: |
| iter_headings@319 | def | L319-335 | 产出 (行号, 级别, 标题)。跳过代码围栏内的伪标题。 | def iter_headings(body: str): |
| split_frontmatter@338 | def | L338-371 | 极简 frontmatter：只支持 key: value、行内数组与 - item 列表。 | def split_frontmatter(text: str) -> tuple[dict, str]: |
| Page@375 | class | L375-414 |  | class Page: |
| Page.repo@385 | def | L385-386 |  | def repo(self) -> str: |
| Page.topic_dir@389 | def | L389-391 |  | def topic_dir(self) -> str: |
| Page.hint@393 | def | L393-414 | 取正文首段的普通句子，用于在英文标题旁给一行中文提示。 | def hint(self, limit: int = 44) -> str: |
| load_page@417 | def | L417-453 |  | def load_page(root: Path, path: Path) -> Page: |
| repo_dirs@456 | def | L456-467 | repo/ 下的一级目录。_shared 是保留目录，要显式放行。 | def repo_dirs(root: Path) -> list[Path]: |
| all_pages@470 | def | L470-478 |  | def all_pages(root: Path): |
| resolve_page@481 | def | L481-503 | 返回 (命中页, 歧义候选)。歧义时不猜——静默选错页比报错更糟。 | def resolve_page(root: Path, target: str) -> tuple[Path \| None, list[… |
| pick_page@506 | def | L506-535 |  | def pick_page(root: Path, target: str) -> Path \| None: |
| cover_match@540 | def | L540-546 | ------------------------------------------------------------------ 匹配 | def cover_match(cover: str, target: str) -> bool: |
| check_repo@551 | def | L551-590 | 校验 --repo 是一级仓库名。返回错误文本，None 表示合法。 | def check_repo(root: Path, name: str) -> str \| None: |
| cmd_tree@593 | def | L593-712 |  | def cmd_tree(root: Path, args) -> int: |
| walk@597 | def | L597-615 |  | def walk(d: Path, depth: int) -> None: |
| sort_key@670 | def | L670-674 |  | def sort_key(x: dict) -> tuple[int, str]: |
| emit_page@676 | def | L676-687 |  | def emit_page(it: dict, indent: str, depth: int) -> None: |
| emit@689 | def | L689-696 |  | def emit(d: str, depth: int) -> None: |
| cmd_read@715 | def | L715-753 |  | def cmd_read(root: Path, args) -> int: |
| cmd_heads@756 | def | L756-771 |  | def cmd_heads(root: Path, args) -> int: |
| cmd_search@774 | def | L774-803 |  | def cmd_search(root: Path, args) -> int: |
| cmd_graph@806 | def | L806-895 | 把 covers 的二部图投影成页间图，输出三类结构性信号。 | def cmd_graph(root: Path, args) -> int: |
| parse_plan_item@919 | def | L919-937 | 解析一行计划条目，返回 (item, 错误说明)。 | def parse_plan_item(line: str) -> tuple[dict \| None, str]: |
| plan_section_body@940 | def | L940-951 | 取出页面里 ## 计划 小节正文（到下一个同级或更高级标题为止）。 | def plan_section_body(body: str) -> str: |
| anchor_status@954 | def | L954-999 | 按锚点现场核对代码，返回 (状态, 证据)。 | def anchor_status(root: Path, anchor: str) -> tuple[str, list[str]]: |
| collect_plan@1002 | def | L1002-1028 | 扫描所有页面的 ## 计划 小节，返回 (条目列表, 格式错误列表)。 | def collect_plan(root: Path, repo: str \| None = None) -> tuple[list[d… |
| cmd_plan@1031 | def | L1031-1111 | 列出计划条目，按「现场算出来的」状态分桶。 | def cmd_plan(root: Path, args) -> int: |
| cmd_plan_close@1114 | def | L1114-1190 | 关闭一条计划：先落知识，再删条目。 | def cmd_plan_close(root: Path, args) -> int: |
| _drop_plan_line@1193 | def | L1193-1214 | 从页面删掉指定 ID 的条目行。返回错误说明，空串表示成功。 | def _drop_plan_line(root: Path, page_rel: str, pid: str) -> str: |
| pathlib_name@1267 | def | L1267-1268 |  | def pathlib_name(rel: str) -> str: |
| Block@1276 | class | L1276-1284 | 装订的一个块。prio 越大越先被丢。 | class Block: |
| Block.__post_init__@1283 | def | L1283-1284 |  | def __post_init__(self): |
| repo_roots@1287 | def | L1287-1305 | 仓库名 → 磁盘根。 | def repo_roots(root: Path) -> dict[str, Path]: |
| scope_repo@1308 | def | L1308-1316 | 把 scope 解析成 (仓库名, 磁盘根)。允许写 infohub/collector/kit/ 或 collector/kit/。 | def scope_repo(roots: dict[str, Path], scope: str) -> tuple[str \| Non… |
| src_files@1319 | def | L1319-1343 | 目录下的源码与配置，返回相对仓库根的路径。 | def src_files(base: Path, rel: str, root: Path \| None = None) -> list… |
| file_outline@1346 | def | L1346-1357 | 只取签名行，带行号——行号让 agent 能直接跳到目标位置，不用整文件读。 | def file_outline(path: Path) -> tuple[str, int]: |
| _source_index_block@1367 | def | L1367-1407 | 源码的语义块索引块：每块一行 Class.method@行号 L起-止 kind 签名。 | def _source_index_block(path: Path, rel: str) -> Block \| None: |
| render_source@1410 | def | L1410-1438 | 一个源码/配置文件的装订形态。 | def render_source(path: Path, rel: str, prio_full: int, prio_out: int, |
| page_sections@1441 | def | L1441-1453 | (级别, 标题, 该节正文)。与 kb read --section 同一套切片规则。 | def page_sections(pg: Page) -> list[tuple[int, str, str]]: |
| claiming_pages@1456 | def | L1456-1492 | 哪些页认领了这个范围，以及精度（exact = 精确到这条路径，dir = 只到目录）。 | def claiming_pages(pages: list[Page], scope: str, target: str \| None … |
| shallow_files@1495 | def | L1495-1515 | 只列一层（不递归）。用于找聚合型产物，不能用来找源码—— | def shallow_files(base: Path, rel: str, include_skip: bool = False) ->… |
| derived_note@1518 | def | L1518-1538 | 读文件头部找「本文件由某脚本生成」的标记。命中就是串行点。 | def derived_note(path: Path, head: int = 4000) -> str: |
| cmd_pack@1541 | def | L1541-1725 |  | def cmd_pack(root: Path, args) -> int: |
| cmd_agent@1728 | def | L1728-1796 | 在 codeb 里组装并运行子 agent（单任务或按计划多任务）。 | def cmd_agent(root: Path, args) -> int: |
| _run_agent_proc@1799 | def | L1799-1853 | 起子进程跑 agent，解析 JSON 并输出。 | def _run_agent_proc(argv: list[str], as_json: bool, multi: bool) -> in… |
| _print_agent_result@1856 | def | L1856-1867 |  | def _print_agent_result(res: dict) -> None: |
| _run_agent_proc@1870 | def | L1870-1925 | 起子进程跑 agent，解析 JSON 并输出。 | def _run_agent_proc(argv: list[str], as_json: bool, multi: bool) -> in… |
| cmd_dispatch@1928 | def | L1928-2084 | 派发前的地面检查：写范围互斥、共享知识、接口面、派生文件。 | def cmd_dispatch(root: Path, args) -> int: |
| cmd_where@2087 | def | L2087-2111 |  | def cmd_where(root: Path, args) -> int: |
| _err@2130 | def | L2130-2142 | 往 stderr 打一行，遇到无法编码的终端就降级而不是崩。 | def _err(msg: str) -> None: |
| _lock_path@2145 | def | L2145-2148 |  | def _lock_path(root: Path) -> Path: |
| write_lock@2152 | def | L2152-2197 | 独占写锁。跨平台，只用标准库。 | def write_lock(root: Path, timeout: float = LOCK_TIMEOUT): |
| _read_bytes_retry@2200 | def | L2200-2218 | 容忍 Windows 上短暂的共享冲突。 | def _read_bytes_retry(path: Path, tries: int = 8, delay: float = 0.01)… |
| _read_text_robust@2221 | def | L2221-2224 | 读文本：utf-8-sig 去 BOM，并在共享冲突时重试。 | def _read_text_robust(path: Path, encoding: str = "utf-8-sig") -> str: |
| _atomic_write@2227 | def | L2227-2260 | 写临时文件再 os.replace。 | def _atomic_write(path: Path, data: bytes) -> None: |
| _write_page@2263 | def | L2263-2298 | 写盘唯一出口：统一 LF、无 BOM、文件末尾恰好一个换行。 | def _write_page(path: Path, title: str, body: str, covers: list[str], |
| cmd_upsert@2301 | def | L2301-2312 | 命中即更新、miss 即补充。 | def cmd_upsert(root: Path, args) -> int: |
| _upsert_locked@2315 | def | L2315-2478 |  | def _upsert_locked(root: Path, args) -> int: |
| cmd_reindex@2492 | def | L2492-2569 | 从 Markdown 页表重建 sqlite 派生索引（md 仍是 source of truth）。 | def cmd_reindex(root: Path, args) -> int: |
| cmd_blocks@2572 | def | L2572-2596 | 从 sqlite 索引查询语义块（需先运行 kb reindex）。 | def cmd_blocks(root: Path, args) -> int: |
| cmd_covers_check@2599 | def | L2599-2652 | 从 sqlite 索引做 covers 自检（stale/conflict/uncovered）。 | def cmd_covers_check(root: Path, args) -> int: |
| cmd_init@2655 | def | L2655-2663 |  | def cmd_init(root: Path, args) -> int: |
| build_parser@2668 | def | L2668-2789 | ------------------------------------------------------------------ 入口 | def build_parser() -> argparse.ArgumentParser: |
| main@2801 | def | L2801-2823 |  | def main(argv: list[str] \| None = None) -> int: |
