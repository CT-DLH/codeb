---
covers:
  - collector/zhihu_pipe/busy.py
  - collector/zhihu_pipe/cli.py
  - collector/zhihu_pipe/config.py
  - collector/zhihu_pipe/fetch.py
  - collector/zhihu_pipe/fulltext.py
  - collector/zhihu_pipe/html_text.py
  - collector/zhihu_pipe/matcher.py
  - collector/zhihu_pipe/pipeline.py
  - collector/zhihu_pipe/raw.py
  - collector/zhihu_pipe/runs.py
  - collector/zhihu_pipe/source.py
  - collector/zhihu_pipe/sources/__init__.py
  - collector/zhihu_pipe/sources/academic.py
  - collector/zhihu_pipe/sources/bilibili.py
  - collector/zhihu_pipe/sources/browser.py
  - collector/zhihu_pipe/sources/cnki.py
  - collector/zhihu_pipe/sources/crossref.py
  - collector/zhihu_pipe/sources/github.py
  - collector/zhihu_pipe/sources/site.py
  - collector/zhihu_pipe/sources/web.py
  - collector/zhihu_pipe/sources/xiaohongshu.py
  - collector/zhihu_pipe/sources/zhihu.py
  - collector/zhihu_pipe/store.py
  - collector/zhihu_pipe/summarize.py
title: Zhihu Pipeline Module (Layer 3)
updated: 2026-11-24
---

# 模块：知乎管道——部件细页表（第3层）

**项目**：infohub
**源码文件**：`collector/zhihu_pipe/busy.py`、`collector/zhihu_pipe/cli.py`、`collector/zhihu_pipe/config.py`、`collector/zhihu_pipe/fetch.py`、`collector/zhihu_pipe/fulltext.py`、`collector/zhihu_pipe/html_text.py`、`collector/zhihu_pipe/matcher.py`、`collector/zhihu_pipe/pipeline.py`、`collector/zhihu_pipe/raw.py`、`collector/zhihu_pipe/runs.py`、`collector/zhihu_pipe/source.py`、`collector/zhihu_pipe/sources/__init__.py`、`collector/zhihu_pipe/sources/academic.py`、`collector/zhihu_pipe/sources/bilibili.py`、`collector/zhihu_pipe/sources/browser.py`、`collector/zhihu_pipe/sources/cnki.py`、`collector/zhihu_pipe/sources/crossref.py`、`collector/zhihu_pipe/sources/github.py`、`collector/zhihu_pipe/sources/site.py`、`collector/zhihu_pipe/sources/web.py`、`collector/zhihu_pipe/sources/xiaohongshu.py`、`collector/zhihu_pipe/sources/zhihu.py`、`collector/zhihu_pipe/store.py`、`collector/zhihu_pipe/summarize.py`
**第4层语义块索引**：
- `collector-zhihu_pipe-busy.py`: `../symbols/collector-zhihu_pipe-busy.py.md`
- `collector-zhihu_pipe-cli.py`: `../symbols/collector-zhihu_pipe-cli.py.md`
- `collector-zhihu_pipe-config.py`: `../symbols/collector-zhihu_pipe-config.py.md`
- `collector-zhihu_pipe-fetch.py`: `../symbols/collector-zhihu_pipe-fetch.py.md`
- `collector-zhihu_pipe-fulltext.py`: `../symbols/collector-zhihu_pipe-fulltext.py.md`
- `collector-zhihu_pipe-html_text.py`: `../symbols/collector-zhihu_pipe-html_text.py.md`
- `collector-zhihu_pipe-matcher.py`: `../symbols/collector-zhihu_pipe-matcher.py.md`
- `collector-zhihu_pipe-pipeline.py`: `../symbols/collector-zhihu_pipe-pipeline.py.md`
- `collector-zhihu_pipe-raw.py`: `../symbols/collector-zhihu_pipe-raw.py.md`
- `collector-zhihu_pipe-runs.py`: `../symbols/collector-zhihu_pipe-runs.py.md`
- `collector-zhihu_pipe-source.py`: `../symbols/collector-zhihu_pipe-source.py.md`
- `collector-zhihu_pipe-sources-__init__.py`: `../symbols/collector-zhihu_pipe-sources-__init__.py.md`
- `collector-zhihu_pipe-sources-academic.py`: `../symbols/collector-zhihu_pipe-sources-academic.py.md`
- `collector-zhihu_pipe-sources-bilibili.py`: `../symbols/collector-zhihu_pipe-sources-bilibili.py.md`
- `collector-zhihu_pipe-sources-browser.py`: `../symbols/collector-zhihu_pipe-sources-browser.py.md`
- `collector-zhihu_pipe-sources-cnki.py`: `../symbols/collector-zhihu_pipe-sources-cnki.py.md`
- `collector-zhihu_pipe-sources-crossref.py`: `../symbols/collector-zhihu_pipe-sources-crossref.py.md`
- `collector-zhihu_pipe-sources-github.py`: `../symbols/collector-zhihu_pipe-sources-github.py.md`
- `collector-zhihu_pipe-sources-site.py`: `../symbols/collector-zhihu_pipe-sources-site.py.md`
- `collector-zhihu_pipe-sources-web.py`: `../symbols/collector-zhihu_pipe-sources-web.py.md`
- `collector-zhihu_pipe-sources-xiaohongshu.py`: `../symbols/collector-zhihu_pipe-sources-xiaohongshu.py.md`
- `collector-zhihu_pipe-sources-zhihu.py`: `../symbols/collector-zhihu_pipe-sources-zhihu.py.md`
- `collector-zhihu_pipe-store.py`: `../symbols/collector-zhihu_pipe-store.py.md`
- `collector-zhihu_pipe-summarize.py`: `../symbols/collector-zhihu_pipe-summarize.py.md`
**写范围**：collector/zhihu_pipe/**
**验证命令**：`powershell -NoProfile -ExecutionPolicy Bypass -File _kbwork/run_regression.ps1`

## 职责
知乎内容采集管道：从热榜/搜索/作者主页抓取内容，粗筛与深筛，落库与再筛。

## 适用场景
- 需要定位或修改该模块内的源码部件时，先在此页选中部件，再下沉到第4层。
- 需要确认某个文件的语义块清单与行号时，打开对应 `symbols/` 页。

## 功能部件

| 部件 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| `busy_file@24` | def | L24-25 |  | def busy_file() -> Path: |
| `touch@28` | def | L28-37 | 登记「现在有人在用 LLM」。写临时文件再 rename，避免半个 JSON 被读到。 | def touch(kind: str, note: str = "") -> None: |
| `current@40` | def | L40-52 | 当前持有者；没有文件或心跳过期都算空闲。 | def current() -> dict \ |
| `busy@55` | def | L55-62 | 除 exclude_kind（自己）之外还有人在用 LLM 就返回那条记录。 | def busy(exclude_kind: str = "") -> dict \ |
| `main@97` | def | L97-247 |  | def main(argv: list[str] \ |
| `load_dotenv@16` | def | L16-35 |  | def load_dotenv() -> None: |
| `get_env@38` | def | L38-40 |  | def get_env(key: str, default: str = "") -> str: |
| `github_token@43` | def | L43-45 | GitHub PAT。不填也能跑，但配额从 5000/h 降到 60/h、搜索从 30/min 降到 10/min。 | def github_token() -> str: |
| `bili_cookie@48` | def | L48-54 | B 站浏览器 Cookie（整串，形如 SESSDATA=xxx; bili_jct=yyy; ...）。 | def bili_cookie() -> str: |
| `set_min_interval@59` | def | L59-63 | 设置两次请求之间的最小间隔（秒）；0 = 不限速。 | def set_min_interval(seconds: float) -> None: |
| `list_author_articles@152` | def | L152-176 | ---------------------------------------------------------------- 列表 | def list_author_articles(url_token: str, max_items: int = 50… |
| `list_author_answers@179` | def | L179-202 |  | def list_author_answers(url_token: str, max_items: int = 50)… |
| `fetch_article_doc@207` | def | L207-221 | 取单篇文章的完整内容（HTML → Markdown）。 | def fetch_article_doc(content_id: str) -> dict[str, Any]: |
| `load_cfg@38` | def | L38-45 |  | def load_cfg() -> dict: |
| `host_of@59` | def | L59-60 |  | def host_of(url: str) -> str: |
| `allowed@63` | def | L63-72 | 域名后缀匹配：arxiv.org 也放行 export.arxiv.org。 | def allowed(url: str, cfg: dict \ |
| `download@116` | def | L116-156 | 带大小上限的下载；不是 PDF 就直接拒绝（不顺手去爬 HTML 正文页）。 | def download(url: str, cfg: dict \ |
| `FetchResult@62` | class | L62-70 | ----------------------------------------------------------------------… | class FetchResult: |
| `download@73` | def | L73-121 | 取一个页面。robots 闸在这一层，不在调用方。 | def download(url: str, *, timeout: float = 20.0, ua: str = U… |
| `Topic@44` | class | L44-79 |  | class Topic: |
| `Topic.score@63` | def | L63-79 |  | def score(self, title: str, excerpt: str = "", body: str = "… |
| `resolve_topic@115` | def | L115-129 |  | def resolve_topic(name: str \ |
| `strip_html@132` | def | L132-133 |  | def strip_html(s: str) -> str: |
| `RunOptions@37` | class | L37-54 |  | class RunOptions: |
| `Hit@58` | class | L58-81 |  | class Hit: |
| `Pipeline@84` | class | L84-414 |  | class Pipeline: |
| `Hit.row@64` | def | L64-81 |  | def row(self) -> ArticleRow: |
| `safe_name@25` | def | L25-32 | content_id 可能含 /（GitHub 的 owner/repo），做文件名前必须消毒。 | def safe_name(value: object) -> str: |
| `save_raw@35` | def | L35-60 |  | def save_raw(data_dir: Path, source: str, item, body: str, s… |
| `run_file@27` | def | L27-33 | run_id 会当文件名用（它来自命令行参数），消毒后必须仍落在 active/ 里。 | def run_file(run_id: str) -> Path: |
| `pid_alive@36` | def | L36-67 |  | def pid_alive(pid: object) -> bool: |
| `register@70` | def | L70-91 | 登记一条正在跑的任务。 | def register(run_id: str, kind: str, *, source: str = "", pr… |
| `unregister@94` | def | L94-98 |  | def unregister(run_id: str) -> None: |
| `QuotaExceeded@26` | class | L26-30 | 本源配额/限流耗尽，属于「临时不可用」，不应判为内容抓取失败。 | class QuotaExceeded(RuntimeError): |
| `NoSearch@33` | class | L33-38 | 这个源根本没有可用的搜索接口（小红书搜索要 x-s 签名，只有浏览器能产生）。 | class NoSearch(RuntimeError): |
| `Capability@41` | class | L41-46 |  | class Capability(str, Enum): |
| `Fidelity@49` | class | L49-52 |  | class Fidelity(str, Enum): |
| `available@71` | def | L71-72 |  | def available() -> list[str]: |
| `site_source_names@75` | def | L75-77 | 已注册的站点源名（供 capabilities.py 把平台源与站点源分栏）。 | def site_source_names() -> tuple[str, ...]: |
| `is_site_source@80` | def | L80-81 |  | def is_site_source(name: str) -> bool: |
| `get_source@84` | def | L84-95 |  | def get_source(name: str) -> Source: |
| `AcademicSource@96` | class | L96-230 | 学术源的公共骨架。子类只需要填 name 和四个端点实现。 | class AcademicSource: |
| `ArxivSource@235` | class | L235-378 | ======================================================================… | class ArxivSource(AcademicSource): |
| `S2Source@383` | class | L383-475 | ========================================================== Semantic Sc… | class S2Source(AcademicSource): |
| `OpenAlexSource@480` | class | L480-592 | ==================================================================== O… | class OpenAlexSource(AcademicSource): |
| `RiskControl@70` | class | L70-74 | -352 / 412 / 429：B 站风控，属于「本源临时不可用」，不是某篇内容抓取失败。 | class RiskControl(QuotaExceeded): |
| `BiliSource@215` | class | L215-691 |  | class BiliSource: |
| `BiliSource.set_min_interval@265` | def | L265-272 | CLI 的 --delay：两档一起覆盖（0 = 不限速，风控环境下不建议）。 | def set_min_interval(self, seconds: float) -> None: |
| `BiliSource.search@405` | def | L405-420 | 关键词搜视频。kind 除 video 外本插件没有别的可给（不做专栏/用户搜索）。 | def search(self, query: str, *, limit: int = 30, cursor: str… |
| `BrowserUnavailable@90` | class | L90-91 | 没装 playwright / 机器上没有可用的 Chrome。属于环境问题，不是站点问题。 | class BrowserUnavailable(RuntimeError): |
| `NeedManualAction@94` | class | L94-99 | 需要人工过滑块/扫码登录。 | class NeedManualAction(QuotaExceeded): |
| `BrowserBlocked@102` | class | L102-107 | 站点直接返回 4xx/5xx（反爬），且没落到能识别的验证页。 | class BrowserBlocked(QuotaExceeded): |
| `BrowserConfig@203` | class | L203-220 |  | class BrowserConfig: |
| `NoSearchAvailable@141` | class | L141-142 |  | class NoSearchAvailable(NoSearch): |
| `CnkiSource@208` | class | L208-485 |  | class CnkiSource(BrowserSource): |
| `CnkiSource.capabilities@245` | def | L245-254 |  | def capabilities(self) -> frozenset[Capability]: |
| `CnkiSource.search@289` | def | L289-312 |  | def search(self, query: str, *, limit: int = 20, cursor: str… |
| `CrossrefSource@43` | class | L43-147 |  | class CrossrefSource(AcademicSource): |
| `CrossrefSource.canonicalize@135` | def | L135-138 | DOI 不区分大小写，统一成小写 doi.org 链接——这是跨源合并的主键。 | def canonicalize(self, url: str) -> str: |
| `CrossrefSource.health@140` | def | L140-147 |  | def health(self) -> Health: |
| `RateLimited@50` | class | L50-51 | 配额耗尽。调用方应把它当作「本源的临时不可用」，而不是内容错误。 | class RateLimited(QuotaExceeded): |
| `GitHubSource@63` | class | L63-328 |  | class GitHubSource: |
| `GitHubSource.set_min_interval@101` | def | L101-108 | 统一覆盖两档间隔（CLI 的 --delay）。 | def set_min_interval(self, seconds: float) -> None: |
| `GitHubSource.search@208` | def | L208-234 | 检索仓库（默认）或 issue/PR。 | def search(self, query: str, *, limit: int = 30, cursor: str… |
| `SiteSource@56` | class | L56-267 | 一份站点 spec → 一个 Source 实例。构造期绝不联网。 | class SiteSource: |
| `SiteSource.search@124` | def | L124-132 | 没有 SEARCH 能力：返回空页，但明确说明为什么是空的（不是静默空列表）。 | def search(self, query: str, *, limit: int, cursor: str \ |
| `SiteSource.list_author@134` | def | L134-139 | 站点源没有作者维度。沿用现有各源「不硬猜就返回空」的口径，但点名原因。 | def list_author(self, author_id: str, *, kinds: Iterable[str… |
| `SiteSource.fetch@141` | def | L141-150 | 取一条站点内容：正文进 body_md，结构化字段进 extra，fidelity 按实际抽取设置。 | def fetch(self, ref: ContentRef) -> Document: |
| `WebSource@230` | class | L230-645 | 通用网页搜索 + 正文抓取。正文走 zhihu_pipe/html_text.py，三条闸见模块 docstring。 | class WebSource: |
| `WebSource.set_min_interval@275` | def | L275-279 | ------------------------------------------------------------------ 传输 | def set_min_interval(self, seconds: float) -> None: |
| `WebSource.search@303` | def | L303-323 | kind 是内核概念，本插件没有多种内容类型，忽略。 | def search(self, query: str, *, limit: int, cursor: str \ |
| `WebSource.canonicalize@540` | def | L540-552 | 去追踪参数 + fragment + 尾斜杠，scheme 统一成 https。必须幂等。 | def canonicalize(self, url: str) -> str: |
| `NeedsLogin@132` | class | L132-137 | 页面回来了但没有笔记本体——登录态缺失或已过期。 | class NeedsLogin(QuotaExceeded): |
| `NoSearchAvailable@140` | class | L140-141 |  | class NoSearchAvailable(NoSearch): |
| `XhsSource@294` | class | L294-647 |  | class XhsSource(BrowserSource): |
| `initial_state@248` | def | L248-263 |  | def initial_state(html: str) -> dict \ |
| `ZhihuSource@21` | class | L21-116 |  | class ZhihuSource: |
| `ZhihuSource.search@72` | def | L72-79 |  | def search(self, query: str, *, limit: int = 30, cursor: str… |
| `ZhihuSource.list_author@81` | def | L81-91 |  | def list_author(self, author_id: str, *, kinds: Iterable[str… |
| `ZhihuSource.fetch@93` | def | L93-103 |  | def fetch(self, ref: ContentRef) -> Document: |
| `ArticleRow@158` | class | L158-187 |  | class ArticleRow: |
| `Store@190` | class | L190-733 |  | class Store: |
| `platform_of@42` | def | L42-62 | 这行属于哪个源插件——取正文资格的判定基础，口径与历史身份键兼容。 | def platform_of(canonical_key: str, url: str, known: tuple[s… |
| `canonicalize_url@96` | def | L96-146 | 把同一篇文章的各种 URL 形态收敛成一个形态（内核的默认规范化）。 | def canonicalize_url(url: str) -> str: |
| `SummaryResult@106` | class | L106-113 |  | class SummaryResult: |
| `Summarizer@390` | class | L390-433 |  | class Summarizer: |
| `set_llm_min_interval@91` | def | L91-93 |  | def set_llm_min_interval(seconds: float) -> None: |
| `extract_summary@192` | def | L192-235 |  | def extract_summary(title: str, markdown: str, word_count: i… |

> 本模块共 **409** 个语义块，本页只列核心部件；完整清单见各 `symbols/` 页。

## 下沉指引
```
选中部件 → 打开第4层 symbols 文件 → read_block(path="collector/zhihu_pipe/busy.py", key="busy_file@24")
选中部件 → 打开第4层 symbols 文件 → read_block(path="collector/zhihu_pipe/cli.py", key="_fmt_ts@19")
选中部件 → 打开第4层 symbols 文件 → read_block(path="collector/zhihu_pipe/config.py", key="load_dotenv@16")
```
