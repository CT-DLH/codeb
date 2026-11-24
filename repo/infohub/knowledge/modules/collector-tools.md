---
covers:
  - collector/tools/browser_login.py
  - collector/tools/capabilities.py
  - collector/tools/collect_site.py
  - collector/tools/crawl_course.py
  - collector/tools/crawl_long.py
  - collector/tools/enrich_batch.py
  - collector/tools/enrich_queue.py
  - collector/tools/fetch_fulltext.py
  - collector/tools/grab_cookie.py
  - collector/tools/idle_papers.py
  - collector/tools/ingest_curl.py
  - collector/tools/llm_compare.py
  - collector/tools/llm_projects.py
  - collector/tools/lookup_cnki.py
  - collector/tools/lookup_papers.py
  - collector/tools/paper_pipeline.py
  - collector/tools/paper_urls.py
  - collector/tools/papers_to_cards.py
  - collector/tools/run_keyword.py
  - collector/tools/run_nightly.py
  - collector/tools/run_refs.py
  - collector/tools/run_research.py
  - collector/tools/run_session.py
  - collector/tools/run_site.py
  - collector/tools/run_source.py
  - collector/tools/run_survey.py
  - collector/tools/run_target.py
  - collector/tools/selftest_academic.py
  - collector/tools/selftest_audience.py
  - collector/tools/selftest_bilibili.py
  - collector/tools/selftest_blob.py
  - collector/tools/selftest_browser.py
  - collector/tools/selftest_cnki.py
  - collector/tools/selftest_column.py
  - collector/tools/selftest_filename.py
  - collector/tools/selftest_fulltext.py
  - collector/tools/selftest_grab_cookie.py
  - collector/tools/selftest_kit.py
  - collector/tools/selftest_llm.py
  - collector/tools/selftest_paging.py
  - collector/tools/selftest_plugin.py
  - collector/tools/selftest_probe.py
  - collector/tools/selftest_query_guide.py
  - collector/tools/selftest_queue.py
  - collector/tools/selftest_refs.py
  - collector/tools/selftest_register.py
  - collector/tools/selftest_research.py
  - collector/tools/selftest_robots.py
  - collector/tools/selftest_session.py
  - collector/tools/selftest_site.py
  - collector/tools/selftest_throttle.py
  - collector/tools/selftest_two_stage.py
  - collector/tools/selftest_web.py
  - collector/tools/selftest_xhs.py
  - collector/tools/site_probe.py
  - collector/tools/summarize_platform.py
  - collector/tools/survey_cards.py
  - collector/tools/tag_cards.py
  - collector/tools/verify_zhihu_urls.py
title: Collector CLI Tools Module (Layer 3)
updated: 2026-11-24
---

# 模块：采集 CLI 工具——部件细页表（第3层）

**项目**：infohub
**源码文件**：`collector/tools/browser_login.py`、`collector/tools/capabilities.py`、`collector/tools/collect_site.py`、`collector/tools/crawl_course.py`、`collector/tools/crawl_long.py`、`collector/tools/enrich_batch.py`、`collector/tools/enrich_queue.py`、`collector/tools/fetch_fulltext.py`、`collector/tools/grab_cookie.py`、`collector/tools/idle_papers.py`、`collector/tools/ingest_curl.py`、`collector/tools/llm_compare.py`、`collector/tools/llm_projects.py`、`collector/tools/lookup_cnki.py`、`collector/tools/lookup_papers.py`、`collector/tools/paper_pipeline.py`、`collector/tools/paper_urls.py`、`collector/tools/papers_to_cards.py`、`collector/tools/run_keyword.py`、`collector/tools/run_nightly.py`、`collector/tools/run_refs.py`、`collector/tools/run_research.py`、`collector/tools/run_session.py`、`collector/tools/run_site.py`、`collector/tools/run_source.py`、`collector/tools/run_survey.py`、`collector/tools/run_target.py`、`collector/tools/selftest_academic.py`、`collector/tools/selftest_audience.py`、`collector/tools/selftest_bilibili.py`、`collector/tools/selftest_blob.py`、`collector/tools/selftest_browser.py`、`collector/tools/selftest_cnki.py`、`collector/tools/selftest_column.py`、`collector/tools/selftest_filename.py`、`collector/tools/selftest_fulltext.py`、`collector/tools/selftest_grab_cookie.py`、`collector/tools/selftest_kit.py`、`collector/tools/selftest_llm.py`、`collector/tools/selftest_paging.py`、`collector/tools/selftest_plugin.py`、`collector/tools/selftest_probe.py`、`collector/tools/selftest_query_guide.py`、`collector/tools/selftest_queue.py`、`collector/tools/selftest_refs.py`、`collector/tools/selftest_register.py`、`collector/tools/selftest_research.py`、`collector/tools/selftest_robots.py`、`collector/tools/selftest_session.py`、`collector/tools/selftest_site.py`、`collector/tools/selftest_throttle.py`、`collector/tools/selftest_two_stage.py`、`collector/tools/selftest_web.py`、`collector/tools/selftest_xhs.py`、`collector/tools/site_probe.py`、`collector/tools/summarize_platform.py`、`collector/tools/survey_cards.py`、`collector/tools/tag_cards.py`、`collector/tools/verify_zhihu_urls.py`
**第4层语义块索引**：
- `collector-tools-browser_login.py`: `../symbols/collector-tools-browser_login.py.md`
- `collector-tools-capabilities.py`: `../symbols/collector-tools-capabilities.py.md`
- `collector-tools-collect_site.py`: `../symbols/collector-tools-collect_site.py.md`
- `collector-tools-crawl_course.py`: `../symbols/collector-tools-crawl_course.py.md`
- `collector-tools-crawl_long.py`: `../symbols/collector-tools-crawl_long.py.md`
- `collector-tools-enrich_batch.py`: `../symbols/collector-tools-enrich_batch.py.md`
- `collector-tools-enrich_queue.py`: `../symbols/collector-tools-enrich_queue.py.md`
- `collector-tools-fetch_fulltext.py`: `../symbols/collector-tools-fetch_fulltext.py.md`
- `collector-tools-grab_cookie.py`: `../symbols/collector-tools-grab_cookie.py.md`
- `collector-tools-idle_papers.py`: `../symbols/collector-tools-idle_papers.py.md`
- `collector-tools-ingest_curl.py`: `../symbols/collector-tools-ingest_curl.py.md`
- `collector-tools-llm_compare.py`: `../symbols/collector-tools-llm_compare.py.md`
- `collector-tools-llm_projects.py`: `../symbols/collector-tools-llm_projects.py.md`
- `collector-tools-lookup_cnki.py`: `../symbols/collector-tools-lookup_cnki.py.md`
- `collector-tools-lookup_papers.py`: `../symbols/collector-tools-lookup_papers.py.md`
- `collector-tools-paper_pipeline.py`: `../symbols/collector-tools-paper_pipeline.py.md`
- `collector-tools-paper_urls.py`: `../symbols/collector-tools-paper_urls.py.md`
- `collector-tools-papers_to_cards.py`: `../symbols/collector-tools-papers_to_cards.py.md`
- `collector-tools-run_keyword.py`: `../symbols/collector-tools-run_keyword.py.md`
- `collector-tools-run_nightly.py`: `../symbols/collector-tools-run_nightly.py.md`
- `collector-tools-run_refs.py`: `../symbols/collector-tools-run_refs.py.md`
- `collector-tools-run_research.py`: `../symbols/collector-tools-run_research.py.md`
- `collector-tools-run_session.py`: `../symbols/collector-tools-run_session.py.md`
- `collector-tools-run_site.py`: `../symbols/collector-tools-run_site.py.md`
- `collector-tools-run_source.py`: `../symbols/collector-tools-run_source.py.md`
- `collector-tools-run_survey.py`: `../symbols/collector-tools-run_survey.py.md`
- `collector-tools-run_target.py`: `../symbols/collector-tools-run_target.py.md`
- `collector-tools-selftest_academic.py`: `../symbols/collector-tools-selftest_academic.py.md`
- `collector-tools-selftest_audience.py`: `../symbols/collector-tools-selftest_audience.py.md`
- `collector-tools-selftest_bilibili.py`: `../symbols/collector-tools-selftest_bilibili.py.md`
- `collector-tools-selftest_blob.py`: `../symbols/collector-tools-selftest_blob.py.md`
- `collector-tools-selftest_browser.py`: `../symbols/collector-tools-selftest_browser.py.md`
- `collector-tools-selftest_cnki.py`: `../symbols/collector-tools-selftest_cnki.py.md`
- `collector-tools-selftest_column.py`: `../symbols/collector-tools-selftest_column.py.md`
- `collector-tools-selftest_filename.py`: `../symbols/collector-tools-selftest_filename.py.md`
- `collector-tools-selftest_fulltext.py`: `../symbols/collector-tools-selftest_fulltext.py.md`
- `collector-tools-selftest_grab_cookie.py`: `../symbols/collector-tools-selftest_grab_cookie.py.md`
- `collector-tools-selftest_kit.py`: `../symbols/collector-tools-selftest_kit.py.md`
- `collector-tools-selftest_llm.py`: `../symbols/collector-tools-selftest_llm.py.md`
- `collector-tools-selftest_paging.py`: `../symbols/collector-tools-selftest_paging.py.md`
- `collector-tools-selftest_plugin.py`: `../symbols/collector-tools-selftest_plugin.py.md`
- `collector-tools-selftest_probe.py`: `../symbols/collector-tools-selftest_probe.py.md`
- `collector-tools-selftest_query_guide.py`: `../symbols/collector-tools-selftest_query_guide.py.md`
- `collector-tools-selftest_queue.py`: `../symbols/collector-tools-selftest_queue.py.md`
- `collector-tools-selftest_refs.py`: `../symbols/collector-tools-selftest_refs.py.md`
- `collector-tools-selftest_register.py`: `../symbols/collector-tools-selftest_register.py.md`
- `collector-tools-selftest_research.py`: `../symbols/collector-tools-selftest_research.py.md`
- `collector-tools-selftest_robots.py`: `../symbols/collector-tools-selftest_robots.py.md`
- `collector-tools-selftest_session.py`: `../symbols/collector-tools-selftest_session.py.md`
- `collector-tools-selftest_site.py`: `../symbols/collector-tools-selftest_site.py.md`
- `collector-tools-selftest_throttle.py`: `../symbols/collector-tools-selftest_throttle.py.md`
- `collector-tools-selftest_two_stage.py`: `../symbols/collector-tools-selftest_two_stage.py.md`
- `collector-tools-selftest_web.py`: `../symbols/collector-tools-selftest_web.py.md`
- `collector-tools-selftest_xhs.py`: `../symbols/collector-tools-selftest_xhs.py.md`
- `collector-tools-site_probe.py`: `../symbols/collector-tools-site_probe.py.md`
- `collector-tools-summarize_platform.py`: `../symbols/collector-tools-summarize_platform.py.md`
- `collector-tools-survey_cards.py`: `../symbols/collector-tools-survey_cards.py.md`
- `collector-tools-tag_cards.py`: `../symbols/collector-tools-tag_cards.py.md`
- `collector-tools-verify_zhihu_urls.py`: `../symbols/collector-tools-verify_zhihu_urls.py.md`
**写范围**：collector/tools/**
**验证命令**：`powershell -NoProfile -ExecutionPolicy Bypass -File _kbwork/run_regression.ps1`

## 职责
采集流程的 CLI 入口集：按站点/课程/文献/关键词驱动的一键采集与维护脚本。

## 适用场景
- 需要定位或修改该模块内的源码部件时，先在此页选中部件，再下沉到第4层。
- 需要确认某个文件的语义块清单与行号时，打开对应 `symbols/` 页。

## 功能部件

| 部件 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| `main@41` | def | L41-130 |  | def main(argv: list[str] \ |
| `build@35` | def | L35-61 |  | def build() -> dict: |
| `main@64` | def | L64-95 |  | def main(argv: list[str] \ |
| `item_fingerprint@48` | def | L48-59 | 一条栏目内容的内容指纹：url + 标题 + 正文，稳定且可复现。 | def item_fingerprint(item: dict) -> str: |
| `build_register@62` | def | L62-101 | --register 回调工厂：把一条栏目内容登记进 pipeline.db（裁决 7）。 | def build_register(spec: dict, pipeline_store: "PipelineStor… |
| `main@274` | def | L274-341 |  | def main(argv: list[str] \ |
| `log@65` | def | L65-66 |  | def log(msg: str) -> None: |
| `run@69` | def | L69-73 |  | def run(cmd: list[str], cwd: Path, timeout: int = 3600) -> t… |
| `tail@76` | def | L76-78 |  | def tail(text: str, n: int = 4) -> str: |
| `login_state@81` | def | L81-88 | 探登录态：cnki 看 last_login 标记，小红书看 cookie。 | def login_state(source: str) -> bool: |
| `build_argv@330` | def | L330-345 |  | def build_argv(profile: str, spec: dict, query: str, args, r… |
| `run_one@348` | def | L348-361 |  | def run_one(argv: list, timeout: int) -> tuple: |
| `main@364` | def | L364-516 |  | def main() -> int: |
| `log@406` | def | L406-410 |  | def log(msg: str) -> None: |
| `main@153` | def | L153-412 |  | def main(argv: list[str] \ |
| `fetchable_platforms@42` | def | L42-51 | (可取正文的集合, 确认没有 body 能力的集合)。 | def fetchable_platforms(report: dict) -> tuple[set[str], set… |
| `explain@54` | def | L54-81 | 返回 (人类可读原因, 可判死的 reason code 或空串)。 | def explain(row: dict \ |
| `entry@84` | def | L84-101 | 队列行 → enrich_batch 吃的计划条目。字段全取自库，不在 TS 侧再解析一次日期。 | def entry(row: dict, card_id: str) -> dict: |
| `main@104` | def | L104-222 |  | def main(argv: list[str] \ |
| `candidates@42` | def | L42-52 |  | def candidates(store: Store, sources: list[str]) -> list[dic… |
| `body_of@55` | def | L55-57 |  | def body_of(path: Path) -> str: |
| `links_of@60` | def | L60-73 | 库里的 assets 优先；没有就用 OA 位置。顺序：PDF 在前，落地页在后。 | def links_of(row: dict, oa: dict) -> list[str]: |
| `main@111` | def | L111-195 |  | def main(argv: list[str] \ |
| `Platform@67` | class | L67-73 |  | class Platform: |
| `main@361` | def | L361-400 |  | def main(argv: list[str] \ |
| `is_paper@42` | def | L42-45 |  | def is_paper(row: dict) -> bool: |
| `summary_backend@48` | def | L48-55 | 这篇摘要是哪个后端产的——只读库里的 summary_backend 列。 | def summary_backend(row: dict) -> str: |
| `done_rows@58` | def | L58-66 | 已经用 llm 总结过的论文行——只给 --redo-sample 用（验证提示词改动，不动待办口径）。 | def done_rows(store: Store, data_dir: Path) -> list[dict]: |
| `pending_rows@69` | def | L69-81 |  | def pending_rows(store: Store, data_dir: Path, redo_extract:… |
| `parse_curl@27` | def | L27-50 | 返回 (headers_dict, cookie_string)。 | def parse_curl(text: str) -> tuple[dict[str, str], str]: |
| `main@53` | def | L53-80 |  | def main() -> int: |
| `resolve_name@35` | def | L35-49 | 卡片文件名是编号（mentor-001），slug 只存在于采集库：用它换出姓名再做匹配。 | def resolve_name(slug: str) -> str: |
| `card_title@52` | def | L52-57 |  | def card_title(path: Path) -> str: |
| `group_by_card@60` | def | L60-72 |  | def group_by_card( |
| `main@75` | def | L75-191 |  | def main() -> int: |
| `section_lines@34` | def | L34-48 | 取 ## 小节 下的非空行，去掉 markdown 前缀（### / - / *），保留原文供溯源。 | def section_lines(card_path: Path, section: str) -> list[str… |
| `main@51` | def | L51-143 |  | def main() -> int: |
| `read_frontmatter@45` | def | L45-48 | frontmatter.read_frontmatter 返回 (fm, body)，这里只要 fm（与 lookup_papers 同一写… | def read_frontmatter(path: Path) -> dict \ |
| `norm_title@51` | def | L51-57 | NFKC + 去空白 + 去书名号/引号 + 去尾标点 + 小写；只做归一化，不做同义改写。 | def norm_title(s: str) -> str: |
| `strip_tail_marks@60` | def | L60-66 | 剥掉「（网络首发）」这类版次后缀；只剥已知的这几个，别做通用去括号。 | def strip_tail_marks(s: str) -> str: |
| `title_matches@69` | def | L69-73 |  | def title_matches(card_title: str, result_title: str) -> boo… |
| `read_frontmatter@48` | def | L48-50 |  | def read_frontmatter(path: Path) -> dict \ |
| `build_citation@53` | def | L53-72 |  | def build_citation(fm: dict) -> Citation: |
| `main@75` | def | L75-170 |  | def main() -> int: |
| `run@41` | def | L41-59 | 跑一条命令，只留最后几行输出——3600 篇的日志全打出来没人看。 | def run(cmd: list[str], cwd: Path, label: str, tail: int = 6… |
| `mcp_import@62` | def | L62-72 | 走 MCP 落卡：判重、合并、来源登记都归导入内核，这里只负责触发。 | def mcp_import(config: str, dry: bool = False) -> tuple[int,… |
| `main@75` | def | L75-147 |  | def main() -> int: |
| `read_frontmatter@28` | def | L28-30 |  | def read_frontmatter(path: Path) -> dict \ |
| `main@33` | def | L33-74 |  | def main() -> int: |
| `main@24` | def | L24-80 |  | def main() -> int: |
| `main@27` | def | L27-74 |  | def main(argv: list[str] \ |
| `main@35` | def | L35-124 |  | def main(argv: list[str] \ |
| `main@72` | def | L72-192 |  | def main(argv: list[str] \ |
| `_Ledger@129` | class | L129-165 | 检索词台账的只读视图（写回由 run_source.py --ledger 负责）。 | class _Ledger: |
| `load_state@81` | def | L81-87 | ----------------------------------------------------------------------… | def load_state(path: Path) -> dict: |
| `save_state@90` | def | L90-92 |  | def save_state(path: Path, state: dict) -> None: |
| `new_state@95` | def | L95-109 |  | def new_state(name: str, topic: str, args) -> dict: |
| `Session@136` | class | L136-271 | ---------------------------------------------------------------- 四种补活动… | class Session: |
| `topic_pool@108` | def | L108-131 | 主题从哪来：内置注册表 + 历史跑过的主题 + 库里真实命中过的词。 | def topic_pool(store: Store, override: list[str]) -> list[st… |
| `Session.pick_topic@173` | def | L173-176 | 每个动作返回「做了多少件事」，0 表示这条路暂时没货（用于自动降权） | def pick_topic(self) -> str: |
| `Session.pick_unseen@178` | def | L178-187 | 本地动作挑没做过的主题：同一主题重筛第二遍不会产出新工作， | def pick_unseen(self) -> str \ |
| `build_site_register@49` | def | L49-82 | --register 回调：把一条教师记录登记进 pipeline.db（裁决 7）。 | def build_site_register(spec: dict, pipeline_store: "Pipelin… |
| `load_card_targets@119` | def | L119-164 | 从 cards/<domain> 读 ext.homepage，生成带「预期姓名」的批量目标。 | def load_card_targets(source: str, only: list[str]) -> tuple… |
| `main@167` | def | L167-254 |  | def main(argv: list[str] \ |
| `main@184` | def | L184-407 |  | def main(argv: list[str] \ |
| `write_json@218` | def | L218-239 |  | def write_json() -> None: |
| `load_list@57` | def | L57-72 | 解析名单文件。序号/名称必填，检索词缺省用名称，备注可空。 | def load_list(path: Path) -> list[dict]: |
| `load_state@75` | def | L75-81 |  | def load_state(path: Path) -> dict: |
| `save_state@84` | def | L84-86 |  | def save_state(path: Path, state: dict) -> None: |
| `run@89` | def | L89-102 | 跑一条命令，只留尾部输出——64 条实体的日志全打出来没人看。 | def run(cmd: list[str], label: str, tail: int = 4) -> tuple[… |
| `main@24` | def | L24-61 |  | def main() -> int: |
| `FakeArxiv@139` | class | L139-145 |  | class FakeArxiv(ArxivSource): |
| `FakeOpenAlex@148` | class | L148-162 |  | class FakeOpenAlex(OpenAlexSource): |
| `FakePubmed@165` | class | L165-174 |  | class FakePubmed(PubmedSource): |
| `FakeS2@177` | class | L177-185 |  | class FakeS2(S2Source): |
| `check@22` | def | L22-29 |  | def check(name: str, got, want) -> None: |
| `section@32` | def | L32-33 |  | def section(title: str) -> None: |
| `test_dm_protobuf@37` | def | L37-72 | ------------------------------------------------------------ 1. 弹幕 pro… | def test_dm_protobuf() -> None: |
| `varint@42` | def | L42-49 |  | def varint(v: int) -> bytes: |
| `check@26` | def | L26-31 |  | def check(name: str, got, want) -> None: |
| `make_view@34` | def | L34-41 |  | def make_view(bvid: str, pages: list[dict], desc: str = "一套竞… |
| `main@44` | def | L44-186 |  | def main() -> int: |
| `fake_call_signed@75` | def | L75-81 |  | def fake_call_signed(path, params=None, *, bucket="core", si… |
| `Res@165` | class | L165-175 | 模拟 http 层返回值（site_crawl.http.FetchResult 的字段面）。 | class Res: |
| `FakeHttp@178` | class | L178-189 |  | class FakeHttp: |
| `GetOnlyHttp@192` | class | L192-201 | 只有 get() 的实现（site_crawl.http.Http 两者都有，但 duck-typed 不能假设）。 | class GetOnlyHttp: |
| `NoFetch@268` | class | L268-269 |  | class NoFetch: |
| `_Page@46` | class | L46-54 |  | class _Page: |
| `DemoSource@106` | class | L106-108 |  | class DemoSource(br.BrowserSource): |
| `check@26` | def | L26-31 |  | def check(name: str, got, want) -> None: |
| `main@34` | def | L34-145 |  | def main() -> int: |
| `check@82` | def | L82-87 |  | def check(name: str, got, want) -> None: |
| `dom_smoke@105` | def | L105-152 | 把参考项目的 DOM 结构做成假页面，在真浏览器里跑我们的 JS。 | def dom_smoke(src: CnkiSource) -> None: |
| `main@155` | def | L155-314 |  | def main() -> int: |
| `FakeResult@45` | class | L45-56 |  | class FakeResult: |
| `FakeHttp@59` | class | L59-77 | 按 URL 返回预设页面或附件字节，并记下每一次 fetch。 | class FakeHttp: |
| `check@35` | def | L35-42 |  | def check(cond: bool, msg: str) -> None: |
| `FakeHttp.fetch@67` | def | L67-77 |  | def fetch(self, url: str, **kw): |
| `check@36` | def | L36-43 |  | def check(cond: bool, msg: str) -> None: |
| `summary_path@46` | def | L46-49 | 与 summarize.main_cli 第 475 行完全同形地拼出摘要路径。 | def summary_path(content_id: str, kind: str = "page") -> str… |
| `main@52` | def | L52-91 |  | def main() -> int: |
| `check@27` | def | L27-33 |  | def check(name: str, got, want) -> None: |
| `main@36` | def | L36-96 |  | def main() -> int: |
| `FakeSession@36` | class | L36-43 | 只实现 grab_cookie 用到的那一个方法（鸭子类型，不启浏览器）。 | class FakeSession: |
| `Page@156` | class | L156-161 |  | class Page: |
| `check@26` | def | L26-33 |  | def check(name: str, cond: bool, extra: str = "") -> None: |
| `FakeSession.cookies@42` | def | L42-43 |  | def cookies(self, domain: str = "") -> list[dict]: |
| `check@36` | def | L36-43 |  | def check(cond: bool, msg: str) -> None: |
| `main@46` | def | L46-211 |  | def main() -> int: |
| `Fake400@82` | class | L82-83 | ---------- response_format 回退判据 ---------- | class Fake400(Exception): |
| `FakeTimeout@85` | class | L85-86 |  | class FakeTimeout(Exception): |
| `ok@29` | def | L29-36 |  | def ok(cond: object, msg: str) -> None: |
| `main@39` | def | L39-191 |  | def main() -> int: |
| `Res@50` | class | L50-58 | 模拟 http 层返回值（两种现成 FetchResult 的字段并集）。 | class Res: |
| `FakeHttp@61` | class | L61-72 | 按 URL 查表返回页面的假 http。表里没有的一律 404——这正是最坏情况。 | class FakeHttp: |
| `GetOnlyFakeHttp@75` | class | L75-81 | 只有 get() 的实现，验证 duck-typing 不是只认 fetch。 | class GetOnlyFakeHttp(FakeHttp): |
| `OnlyId@269` | class | L269-270 |  | class OnlyId: |
| `FakeSource@37` | class | L37-106 | 一个「像 B 站」的假源：URL 的 query 有意义、正文有残片、没有 README 那套规矩。 | class FakeSource: |
| `EnSource@249` | class | L249-250 |  | class EnSource(FakeSource): |
| `ZhSource@252` | class | L252-253 |  | class ZhSource(FakeSource): |
| `FakeSource.parse_url@49` | def | L49-54 | 导入器钩子：从链接反查 Item（FakeSource 用它冒充「无搜索能力的源」）。 | def parse_url(self, url: str): |
| `FakeResult@41` | class | L41-51 |  | class FakeResult: |
| `FakeHttp@54` | class | L54-67 |  | class FakeHttp: |
| `check@31` | def | L31-38 |  | def check(cond: bool, msg: str) -> None: |
| `FakeHttp.fetch@60` | def | L60-67 |  | def fetch(self, url, **kw): |
| `check@31` | def | L31-38 |  | def check(cond: bool, msg: str) -> None: |
| `main@41` | def | L41-104 |  | def main() -> int: |
| `check@32` | def | L32-39 |  | def check(cond: bool, msg: str) -> None: |
| `row@42` | def | L42-56 |  | def row(n: int, **kw) -> ArticleRow: |
| `main@59` | def | L59-198 |  | def main() -> int: |
| `main@141` | def | L141-173 |  | def main() -> int: |
| `check@45` | def | L45-52 |  | def check(cond: bool, msg: str) -> None: |
| `teacher@63` | def | L63-71 |  | def teacher(slug: str, papers: list[str] \ |
| `json_tail@74` | def | L74-82 | collect_site --json 把人话行和 JSON 一起打到 stdout；取顶层那段 JSON。 | def json_tail(text: str) -> dict: |
| `main@85` | def | L85-356 |  | def main() -> int: |
| `check@23` | def | L23-30 |  | def check(name: str, got, want) -> None: |
| `section@33` | def | L33-34 |  | def section(title: str) -> None: |
| `test_relevance@38` | def | L38-91 | ---------------------------------------------------------------- 1. 跑题… | def test_relevance() -> None: |
| `ot@42` | def | L42-43 | 带桥接词的调用形式（off_topic 的第三参） | def ot(text, tt, bt=frozenset()): |
| `FakeResult@144` | class | L144-151 |  | class FakeResult: |
| `FakeHttp@153` | class | L153-155 |  | class FakeHttp: |
| `check@34` | def | L34-41 |  | def check(cond: bool, msg: str) -> None: |
| `deny_parser@44` | def | L44-47 |  | def deny_parser(): |
| `check@29` | def | L29-34 |  | def check(name: str, got, want) -> None: |
| `make_args@37` | def | L37-43 |  | def make_args(**kw) -> argparse.Namespace: |
| `make_session@46` | def | L46-48 |  | def make_session(store: Store, pool, **overrides) -> rs.Sess… |
| `seed_store@51` | def | L51-62 |  | def seed_store(tmp: Path) -> Store: |
| `FakeResult@53` | class | L53-63 |  | class FakeResult: |
| `FakeHttp@66` | class | L66-75 | 只回一页固定 HTML，并记下每一次 fetch（证明构造期零请求）。 | class FakeHttp: |
| `BombHttp@113` | class | L113-120 | 构造即炸：若 __init__ 里建 Http / 发请求就会被抓住。 | class BombHttp: |
| `BadHttp@190` | class | L190-198 |  | class BadHttp: |
| `Clock@61` | class | L61-79 |  | class Clock: |
| `BHttp@120` | class | L120-132 | kit/http.py Http._throttle 原实现（host + jitter）。 | class BHttp: |
| `BFetch@135` | class | L135-147 | zhihu_pipe/fetch.py _throttle 原实现（global，_MIN_INTERVAL 可 0）。 | class BFetch: |
| `BAcademic@150` | class | L150-161 | sources/academic.py _throttle 原实现（global）。 | class BAcademic: |
| `check@36` | def | L36-43 |  | def check(cond: bool, msg: str) -> None: |
| `make_row@46` | def | L46-55 |  | def make_row(data: Path, store: Store, platform: str, kind: … |
| `main@58` | def | L58-118 |  | def main() -> int: |
| `check@44` | def | L44-49 |  | def check(name: str, got, want) -> None: |
| `check_raises@52` | def | L52-62 |  | def check_raises(name: str, fn, exc) -> None: |
| `check_ok@65` | def | L65-72 |  | def check_ok(name: str, fn) -> None: |
| `test_unwrap@106` | def | L106-120 | ------------------------------------------------------------------ 1. … | def test_unwrap() -> None: |
| `check@54` | def | L54-59 |  | def check(name: str, got, want) -> None: |
| `image_note@62` | def | L62-73 |  | def image_note() -> dict: |
| `page@76` | def | L76-80 | 造一个含 JS 痕迹（undefined）与尾随脚本的页面，逼近真实 HTML。 | def page(state: dict) -> str: |
| `dom_smoke@83` | def | L83-102 | 在真浏览器里跑搜索页 JS：验选择器与字段翻译，不访问小红书。 | def dom_smoke(src: XhsSource) -> None: |
| `scoped_hits@50` | def | L50-70 | 选择器命中数，带作用域。 | def scoped_hits(html: str, selector: str, scope_selector: st… |
| `run_probe@134` | def | L134-197 | 抓一次主页 + 逐个翻页候选，返回诊断报告 dict。http 可注入（离线自检）。 | def run_probe(url: str, *, http=None, spec: dict \ |
| `main@228` | def | L228-271 |  | def main(argv: list[str] \ |
| `main@38` | def | L38-109 |  | def main() -> int: |
| `load_list@86` | def | L86-103 | 与 run_survey.load_list 同一口径，多记一个行号用于溯源。 | def load_list(path: Path) -> list[dict]: |
| `register_urls@106` | def | L106-136 | 序号 → 该实体历史上检索到过的 URL 清单。 | def register_urls(name: str) -> dict[str, list[str]]: |
| `db_rows@139` | def | L139-157 | 库里所有平台的已登记内容（含知乎等），归属靠 URL 清单匹配。 | def db_rows() -> list[tuple[str, str, str, float, str]]: |
| `assign@166` | def | L166-231 | 归属：优先按检索清单，其次按标题里的项目名兜底。 | def assign(url_map: dict[str, list[str]], rows: list[tuple], |
| `read_frontmatter@125` | def | L125-133 |  | def read_frontmatter(path: Path) -> dict \ |
| `brief_context@136` | def | L136-160 | 给模型的材料描述：短到能批量塞进一个请求，又足够判断方向。 | def brief_context(fm: dict) -> str: |
| `call_llm@163` | def | L163-180 | 一次请求给一批材料分类。返回每条的标签列表（与输入等长，失败则空列表）。 | def call_llm(batch: list[str]) -> list[list[str]]: |
| `parse_items@183` | def | L183-245 | 三层兜底：JSON → 抠 JSON 片段 → 放弃这一批（宁可空着也不乱写）。 | def parse_items(content: str, expected: int) -> list[list[st… |
| `check@32` | def | L32-39 |  | def check(name: str, cond: bool, detail: str = "") -> None: |

> 本模块共 **446** 个语义块，本页只列核心部件；完整清单见各 `symbols/` 页。

## 下沉指引
```
选中部件 → 打开第4层 symbols 文件 → read_block(path="collector/tools/browser_login.py", key="main@41")
选中部件 → 打开第4层 symbols 文件 → read_block(path="collector/tools/capabilities.py", key="build@35")
选中部件 → 打开第4层 symbols 文件 → read_block(path="collector/tools/collect_site.py", key="item_fingerprint@48")
```
