---
covers:
  - collector/docs/
  - collector/data/
  - collector/refs/
  - collector/llm/
updated: 2026-11-17
---

# Collector: selftests, data files, and the TS interface

这一页是三块「改代码之前必须先看」的现场事实：自检怎么跑、`data/` 里到底有什么、
以及采集产物怎么变成卡片。前两块没有文档，只有产物；第三块决定了字段名不能随便改。

## 自检怎么跑，以及哪一类红是真的

**判断某个自检现在是不是绿的，跑它。** 这页不记断言条数与通过数：
那些数字每次提交都漂移，写进来就是第二真源。这里只写「测什么」和「什么情况下会红」。

运行方式：`cd collector && python tools/selftest_xxx.py`。**没有统一入口**——
只有一个 TS 侧的薄壳 `scripts/python-selftest.ts`，它逐个子进程跑列出的脚本：

```
tsx scripts/python-selftest.ts selftest_research.py selftest_audience.py
```

`npm run test:research` 就是这么调的（只列了两个脚本，要跑别的自己加）。薄壳复用
`resolveCollectorPython('web')` 来选解释器（不写死路径），
给 `PYTHONIOENCODING=utf-8`、`cwd=collector`、600s 超时。
另一个入口 `scripts/collector-python-test.ts`（`npm run test:collector`）走的是
**行为契约**那一路，不是自检外壳。

不要把跨脚本的「通过条数」相加或对比——计数口径本身不一致（见本节末）。

| 脚本 | 测什么 |
| :-- | :-- |
| `selftest.py` | 端到端：免登录热榜跑通整条流水线，再跑一遍证明终态被跳过 |
| `selftest_kit.py` | 转发层与 `kit` 逐名 `is` 同一对象；`kit/store` 三条固定姿势与迁移幂等 |
| `selftest_blob.py` | 字节能否活着出来、类型嗅探、抽不出时点谁的名 |
| `selftest_paging.py` | 「200 不等于有下一页」；关掉 `FALLBACK_SHAPES` 让 `no_candidate` 可达 |
| `selftest_research.py` | 深度调研流水线（不调 LLM、不碰真实状态） |
| `selftest_web.py` | web 插件解析、身份、两条判据 |
| `selftest_query_guide.py` | `query_guide` 六字段契约与检索词语法 |
| `selftest_grab_cookie.py` | `grab_cookie.py`（不开浏览器、不碰真实 `.env`） |
| `selftest_academic.py` | 学术四源（真实结构的假响应） |
| `selftest_xhs.py` | 小红书插件（`BROWSER_SMOKE=1` 才跑真浏览器 DOM） |
| `selftest_cnki.py` | 知网：URL 身份、日期/计数、字段翻译、能力边界 |
| `selftest_llm.py` | LLM 抽取层（不烧 token） |
| `selftest_register.py` | 登记/缓存/队列（裁决 3 / 7 / P5） |
| `selftest_site.py` | `Document.extra` 与 `SiteSource` |
| `selftest_audience.py` | B 站评论/弹幕加工层 |
| `selftest_queue.py` | 状态机、获取队列、能力清单、摘要后端真值 |
| `selftest_bilibili.py` | B 站签名与字幕链路（配 cookie 时会抽查真实 AI 字幕） |
| `selftest_probe.py` | `site_probe` 的数字作用域、软 404 排除 |
| `selftest_browser.py` | 验证码判定、可选依赖、Cookie 解析、单例 |
| `selftest_robots.py` | robots 闸只有一份，且说清「被谁拒的」 |
| `selftest_session.py` | 限时会话器（预算/熔断/主题池） |
| `selftest_column.py` | P2c 端到端：一份 spec 组合 L1 的 blob + paging |
| `selftest_refs.py` | 引用文法六种写法 + 三类该被门禁挡掉的行 |
| `selftest_plugin.py` | 插件契约：接新平台只加一个文件 |
| `selftest_two_stage.py` | 两段式与总结段范围 |
| `selftest_filename.py` | 摘要文件名 `MAX_PATH` |
| `selftest_throttle.py` | 限速逐源接入的节奏等价（假时钟） |
| `selftest_fulltext.py` | 开放获取全文链路 |

**三类「红」要分清，别把环境问题当回归**：

- **`ModuleNotFoundError: No module named 'zhihu_cli'`**——`selftest.py` /
  `selftest_session.py` / `selftest_throttle.py` 都 import 了
  `zhihu_pipe.fetch`，而它无条件
  `from zhihu_cli.content.handlers.requests import session`。
  `zhihu_cli` 不在 `requirements.txt` 里（它是可选的知乎凭据包），所以**任何 import
  到 `zhihu_pipe.fetch` 的模块在没有 zhihu-cli 的机器上都会失败**。这三个自检
  因此不是「不需要联网」，而是「需要 zhihu-cli 才能 import」。
- **缺 PDF 后端**——`selftest_blob.py` 的 PDF 段按本机 `_pdf_backends()` 的实际探测结果
  点名后端；机器上只有 `pdftotext`（或一个都没有）时，按「本机有 pypdf/pymupdf」写的
  那组断言会整批挂。这是**环境缺依赖**，不是回归。
- **真的代码/测试不一致**——`selftest_web.py` 挂在 `survey_cards.assign()` 的解包上
  （`ValueError: too many values to unpack (expected 3)`）：`assign()` 的返回形状变了
  而测试没跟着改。这类才是要修的，而且它只在**跑到那一段**才炸，前面全绿。

断言计数器有两套风格：多数脚本自己定义 `check(cond, msg)` / `ok(name, cond, detail)`
打在 `PASS` / `FAIL` 列表里并打印一句汇总；`selftest_academic` / `selftest_bilibili` /
`selftest_cnki` / `selftest_xhs` 等一批只打印中文结论句，没有逐条 `✓`；
`selftest.py` 完全不计数——它是演示脚本，靠人读输出。
所以「通过几条」在脚本之间**不可比**，跨脚本汇总总数没有意义。

## data/ 里有什么：四个 db 加一堆目录

```
collector/data/
├── pipeline.db          文章状态机（旧管道，zhihu_pipe.Store）
├── crawl.db             站点内容缓存（site_crawl.Store）
├── llm_cache.db         LLM 抽取缓存（llm/extract.py）
├── lookup.db            引用查找缓存（refs/cache.py LookupCache）
├── llm_ts_cache.json    旧 TS 侧的 LLM 缓存（历史遗留，Python 侧不读）
├── pipeline.db.bak-* / .pre-*-bak   改动库之前留的手工备份
├── raw/                 正文与摘要的原文，文件名 {kind}_{content_id}.md
├── out/                 报告与中间产物（json / jsonl / log / md / txt）
├── console/runs/        控制台运行日志 + index.jsonl
├── research/            调研主题定义
├── surveys/             调研中间状态
└── browser-profile/     持久化 Chrome profile（知网/小红书/知乎共用）
```

`raw/` 的 frontmatter 字段：`title` / `author` / `url` / `kind` / `content_id` /
`published_at` / `updated_at` / `voteup` / `comments` / `score` / `topic_match` /
`read_at`。文件名前缀就是 `kind`，所以 `ls raw/ | cut -d_ -f1 | sort | uniq -c`
能直接看出哪些源贡献了正文（`zhihu` / `crossref` / `web` / `github` / `arxiv` /
`openalex` / `bilibili` / `article` / `answer` / `paper` / `repo` / `page` / `video`）。

## pipeline.db 的三张表与它们的形状

`articles` 的 schema 与 `zhihu_pipe/store.py` 的 `_init_schema()` 逐字一致。
分布只记**形状**不记数值（scale 每次跑都在变，要看现值自己查库）：

```
status:   new ≫ summarized > fetched > skipped > failed
platform: zhihu > github > crossref > web > arxiv > openalex > cnki > bilibili
fidelity: metadata_only ≫ full > partial
kind:     article ≈ answer > paper ≈ repo > page > video
```

`new` 是最大的一档，说明大部分是**只登记没抓正文**的元数据行——这与
「`run_source.py` 只登记、`enrich_batch.py` 独吞获取腿」的分工一致。
`metadata_only` 多于 `full` 同理。

`query_ledger` 的 `state` 四态里 `done` 最多，`partial` 次之，
`empty_suspect` 与 `error` 都是个位数——`empty_suspect` 那几个就是被
`ledger_should_skip()` 拦下、**没有**判死的词。平台分布集中在
`web` / `bilibili` / `zhihu` / `github` 四个搜索型源上。

`runs` 是旧 `Pipeline.run()` 的流水，只增不改。

`crawl.db` 的 `teachers` 是历史导师数据；`runs` 表**全是归档**、代码已停止写入
（`site_crawl/store.py` 的 `start_run` / `finish_run` 只 `warnings.warn`，不落盘）。

`llm_cache.db` 的 `llm_cache` 有两个特征：`mode` 几乎全是 `json_schema`（降级到
`json_object` / `text` 的记录很少），而 `prompt_version` **跨多个版本共存**。
按 `name`（= schema 名）能看到调用方：

```
citations（最多） | research_evidence | projects | bili_audience
research_queries | research_outline | research_terms
```

**缓存里留着旧版本的行**是设计要求：`prompt_version` 进 key，所以新版不会命中旧缓存，
旧行只是占空间，不影响正确性。反过来说，`prompt_version` 的取值分布就是 prompt 的迭代史；
`citations` / `projects` / `bili-audience` 的版本号跨了好几代，`research-*` 还停在 v1。

`lookup.db` 的 `lookups` 绝大多数是 `hit`，`mismatch` 是少数——
`REUSABLE = ("hit", "mismatch")` 两种都算缓存可用。provider 以 `crossref` 为主、
`openalex` 为辅。

四个 db 都是**只读探测**拿到的（`sqlite3.connect("file:...?mode=ro", uri=True)`），
没有开过写事务。要查现值就照这个姿势读，别从文档抄数字：

```powershell
python -c "import sqlite3;c=sqlite3.connect('file:data/pipeline.db?mode=ro',uri=True);print(c.execute('select status,count(*) from articles group by 1 order by 2 desc').fetchall())"
```

## 采集产物 JSONL 的字段结构

`collector/` 自己**不产 JSONL**——它产 sqlite。JSONL 由 TS 侧的
`scripts/collect-export.ts`（`npm run collect:export`）从 `pipeline.db` 投影出来，
落到 `inbox/`。

两种模式：

| 模式 | 取哪些状态 | 输出 |
| :-- | :-- | :-- |
| `enrich`（默认） | `summarized` + `fetched` | `inbox/collect-articles.jsonl` |
| `index` | 不限状态（元数据一到就能建卡） | `inbox/collect-index.jsonl` |

`index` **不强制把 `fidelity` 改写成 `metadata_only`**——方案初稿这么写，
实测会把大批已有全文卡打回空壳状态。

每一行的字段（`collect-export.ts` 的 `JSON.stringify({...})` 逐项）：

```jsonc
{
  "title": "...",
  "object_type": "…",              // KIND_TO_TYPE[row.kind] ?? "其他"
  "ext.url": "https://…",          // 强标识，identity 判重只看它
  "ext.platform": "zhihu",         // 以 articles.platform 为准；历史行才用 platformOf() 兜底
  "ext.source": "…", "ext.kind": "article|answer|paper|repo|page|video",
  "ext.author": "…", "ext.author_id": "…", "ext.content_id": "…",
  "ext.collector_key": "article:123",   // = articles.canonical_key
  "ext.topic": "数学竞赛",
  "ext.score": 12.0,
  "ext.fidelity": "full|partial|metadata_only",
  "ext.voteup": 0, "ext.comments": 0, "ext.word_count": 2531,
  "ext.published_at": "2024-03-05", "ext.updated_at": "2024-06-01",
  "ext.fetched_at": "2024-06-02",  // 元数据卡写空串（它压根没采集过正文）
  "_body": "> 一句话结论：…\n\n## AI 摘要\n\n…",
  "_replace_sections": ["_lead","AI 摘要","原文位置","采集信息"],
  "_overwrite_fields": ["ext.fidelity","ext.word_count","ext.score", …],
  "_src": { "file": "collector/data/raw/article_123.md", "row": "1" }
}
```

四个 `_` 前缀的键是给内核的指令，不是卡片内容：

- `_replace_sections`：按小节覆盖。有正文时是 4 节，元数据卡只有
  `["原文位置","采集信息"]`——它本来就没有「一句话结论」和「AI 摘要」。
- `_overwrite_fields`：这一串 `ext.*` 是**采集库投影**，补到全文后
  `fidelity`/`word_count` 会跳变，默认的 fill_empty「已有值不动」会把旧读数永久钉在卡上
  （实测有卡片一直卡在 `metadata_only` 加几百字）。`title` 与 `ext.url` **不在**其中。
- `_src`：元数据卡指回 `collector/data/pipeline.db`（不编一个不存在的文件路径）。
- `_clear` **刻意不用**：内核对「带 `_clear` 却没匹配到卡」的行一律判进 review，
  而新建的元数据卡本来就没有卡可匹配——实测整批行全中、一张卡都建不出来。
  一次性撤残留走独立导入，不钉在投影里。

`word_count` 有个坑：库里常是 0（旧 run 没回填），导出侧用
`asNumber(row.word_count) || bodyText.length` 兜底，有正文才用实际长度。

「原文位置」那节的措辞分两种，取决于 `hasRaw`：

```
有正文： 本站只保留摘要与元数据，正文请回原平台阅读。
无正文： 尚未抓取正文，当前只有 metadata_only 元数据。
```

`ext.fetched_at` 在元数据卡上写**空串**的理由：登记时间不是采集时间。
把 `seen_at` 写进 `fetched_at` 会让「这张卡抓没抓过」失真——补正文的队列就是靠这个字段判的。
机器可读的那一列留在库里的 `seen_at`。

## 谁读这些产物

| 消费方 | 读什么 | 用途 |
| :-- | :-- | :-- |
| `scripts/import-jsonl.ts`（`npm run import:jsonl`） | `inbox/*.jsonl` | 预演 → 落卡，`card_import` 的唯一入口 |
| `src/core/ingest.ts` | 同上 | 卡片合并内核：identity 判重、`_replace_sections` / `_overwrite_fields` / `_clear` 的执行者 |
| `src/mcp/tools/card_import.ts` | 同上 | MCP 同步工具，**客户端默认 60s 超时**（LLM 因此绝不在写入路径上） |
| `scripts/collect-enrich.ts` | `pipeline.db` | 生成 `inbox/enrich-plan.json`（卡片队列），喂给 `enrich_batch.py --plan` |
| `scripts/crawl-export.ts` | `crawl.db` | 导师数据导出（`crawl:export`） |
| `src/mcp/lib/collector-runtime.ts` | `collector/capabilities.json` | 导出 `SOURCES` / `SEARCH_SOURCES` / `SITE_SOURCES` 三个常量 |
| `src/mcp/tools/collect_guide.ts` | 同上 | `collect_guide` 工具的全部数据来源 |

## capabilities.json 的生成与内容结构

生成：`cd collector && python tools/capabilities.py --write`。
校验：同文件 `--check`，与现算不一致时**退出码 1**。
`tsx scripts/collector-python-test.ts` 里有一条断言直接跑 `--check`，
所以**改了插件的 `capabilities` 却没重生成，CI 会红**。

顶层键（`SCHEMA_VERSION = 1`）：

```jsonc
{
  "schema": 1,
  "note": "由 collector/tools/capabilities.py --write 生成；能力由插件声明 Capability，不要手改。platforms=声明 SEARCH 的平台源（TS SOURCES/下拉来源），sites=仅 BODY 的站点源",
  "body_capable": ["arxiv","bilibili","cnki","crossref","github","openalex","pubmed","s2",
                   "site_hit_yzb_announcement_list","site_hitsz_grad_column_list",
                   "site_hitsz_teacher_home","web","xiaohongshu","zhihu"],
  "probe_failed": [],                     // 声明名 + 探测失败原因
  "body_capable_effective": [ …同 body_capable… ],   // = body_capable ∪ probe_failed
  "platforms": { "<name>": { "probe":"ok", "capabilities":["body","media","search"],
                             "query_guide": {…六字段…} } },
  "sites":     { "<name>": { "probe":"ok", "capabilities":["body"] } }
}
```

`platforms` 与 `sites` **分栏**的理由（注释原文）：`platforms` 是 TS 侧 `SOURCES` /
控制台「采集源」下拉的唯一来源；站点源只声明 BODY、不声明 SEARCH，混进 `platforms`
会让学校名出现在平台下拉里。

`body_capable` 的口径是 `probe == "ok" and "body" in capabilities`；
`body_capable_effective` 再加 `probe_failed`（不知道 ≠ 不能）。
`probe_failed` 为空说明**当前所有插件都能 import**——一旦某台机器缺 playwright，
`cnki` / `xiaohongshu` 会掉进这里而**不会**掉出 `body_capable_effective`。

清单**不带时间戳**是刻意设计：它必须逐字节稳定，`--check` 和「重生成后 git diff 干净」
这两条回归断言才有意义。

`collector-runtime.ts` 的三个派生常量：

```typescript
export const SOURCES        = PLATFORMS.all;      // platforms 全量 + sites
export const SEARCH_SOURCES = PLATFORMS.search;   // platforms 里声明 search 的
export const SITE_SOURCES   = PLATFORMS.site;     // sites 键 + 兼容旧格式的 site_ 前缀
```

`SOURCES` 保持**全量**不移除任何一项，因为 `collector-python-test.ts` 按它逐项比对——
在 TS 侧先过滤会让那条测试永远通过，等于把回归判据废掉。

## collect_guide 怎么消费

`src/mcp/tools/collect_guide.ts` 只做一件事：读 `collector/capabilities.json`，
把 `query_guide` 原样吐给调用方。**没有数据时给的是三条不同的回答**，不是一句「没有」：

| 情况 | 返回 |
| :-- | :-- |
| 文件不存在 | `isError: true` + 「先跑 `capabilities.py --write`（它由插件现算，不要手写）」 |
| 不传 `source` | 全部平台的概览（`lang` / `searchable` / `pattern` / `capacity`）+ `missing_query_guide` 列表 + `hint` |
| 传了未知 `source` | `isError: true` + `available` 列表 |
| 该源**没声明** `query_guide` | `ok: true` + `query_guide: null` + 「没有平台侧的检索词规则可给」 |
| 该源声明了 | `query_guide` 原样 + 若干条 `checklist` |

`missing_query_guide` 这个字段的存在理由是「不给 ≠ 默认规则」：
agent 必须能区分「这个源没说」和「这个源说可以这么写」。当前所有平台都声明了
`query_guide`，所以这个列表是空的——但**站点源（`sites`）不声明**，
`all = {...platforms, ...sites}` 里那些站点源查出来就是 `query_guide: null`。

`checklist` 的第一条会随 `searchable` 变：

```
searchable === false → "⚠ 该源没有可用搜索接口，只能走 --urls 导入"
否则                  → "✓ 可以按关键词检索"
```

当前 `searchable: false` 的只有 `xiaohongshu`（搜索要页面 JS 生成 `x-s` 签名，
没 playwright 时只能走 `--urls` 导入）。

## refs/：引用串解析，不新建状态机

`refs/` 的分工边界写在 `__init__.py` 里：只把卡片正文里的一行引用串解析成
`{作者, 标题, 年份, DOI}`，再用现成源插件解析成可采集 URL。**不入队、不写
`pipeline.db`、不新建状态机**——后续全部走 `run_source.py` / `collect:export` / `card_import`。

| 文件 | 职责 |
| :-- | :-- |
| `grammar.py` | 六条文法 + 行角色分类，词表在 `lexicon.yaml`（**换站点改这里，不改代码**）；`refs/` 里最重的一个 |
| `llm_parse.py` | LLM 题录解析（`prompt_version = "citations-v2"`），与文法并排对照 |
| `resolver.py` | 题录 → 可采集 URL 的查找链（DOI 优先，标题兜底） |
| `cache.py` | `lookups` 表的读写（`lookup.db`） |
| `queue.py` | `Entry` 数据模型 + 三种入口 + 三个输出文件 |
| `oa.py` | OpenAlex 批量查开放获取（DOI → `{pdf_url, oa_url, is_oa}`） |
| `lexicon.yaml` | 词表：`gate` / `title_noise` / `venue_hints` / `name_like` / `title_min` / `providers` / `fragment` / `roles` / `thresholds` |

`grammar.py` 的常量：`RULES = (_rule_tagged, _rule_quoted, _rule_cnki_dotted, _rule_dblp,
_rule_comma_tail)`——**命中顺序即优先级**，`_rule_bare` 是兜底不进 RULES。
五种行角色：`ROLE_RECORD="record"` / `ROLE_TITLE="title"` / `ROLE_AUTHORS="authors"` /
`ROLE_VENUE="venue"` / `ROLE_OTHER="other"`。
五条识别正则原文：

```python
DOI_RE      = re.compile(r"\b(10\.\d{4,9}/[^\s,;)\]」》]+)")
URL_RE      = re.compile(r"https?://[^\s,;)\]」》]+")
ARXIV_RE    = re.compile(r"arXiv:?\s*(\d{4}\.\d{4,5}(?:v\d+)?)", re.I)
YEAR_PAREN_RE = re.compile(r"[（(]\s*((?:19|20)\d{2})\s*[)）]\s*[.。]?\s*$")   # 尾部年份
BRACKET_TYPE_RE = re.compile(r"\[(J|C|D|M|R)\]")                              # 文献类型标识
```

`lexicon.yaml` 的 `gate` 段决定「这行不是可采论文」，命中即终态 `not_paper`（不入库、
不重试、不进查找链）。三条最值得记的正则：

```yaml
- '^一种.{2,40}(方法|装置|系统|结构)$'          # 中文专利名
- '方法[、，].{0,8}(装置|设备|系统|介质)'        # 「…方法、装置及设备」= 专利
- '^(?:他|她|本人).{0,14}(?:发表|出版|主持|承担|获得)'   # 栏目开头的自述段
```

还有一条防误杀的注释：`(?:h-index|i10-index)\s*[:=为]?\s*\d`
——**带数字才算**，因为书计量学的论文标题真会含 `h-index`，光看词会误杀。

`resolver.py` 的 `CONTAINS_MIN = 30`（标题包含匹配的最短长度）、
`ARXIV_DOI_RE = re.compile(r"^10\.48550/arxiv\.(.+?)(?:v\d+)?$", re.I)`
（arXiv DOI 要还原成 abs 页，不是 `doi.org` 串）。
`Chain.resolve(cit)` 的两条路：`_by_doi` 优先、`_by_title`（`difflib` 相似度）兜底。

`cache.py` 的 `REUSABLE = ("hit", "mismatch")`——只有这两种状态算缓存可用。
`LookupCache.put()` 有一条保护：「缓存里的 DOI 一旦拿到就不被后来的 miss 覆盖」：
老状态是 `hit`/`mismatch` 而新状态不是时，只 `tries + 1`、不动其余字段。

`queue.py` 的 `write_outputs(entries, out_dir)` 一次产**三个文件**：

```
{name}.jsonl      每行一个 Entry.to_dict()：key / sources[{from,quote}] / Citation 字段 / resolved
{name}.urls.txt   可直接喂 run_source --urls 的 URL 清单
{name}.map.json   URL → [{from, quote}] 的溯源映射
```

出链时有一个统一纠正：`landing_url(r.doi, "")` 有值就用它覆盖 `resolved.canonical`——
`10.48550/arxiv.*` 的规范链接是 arXiv 的 abs 页，缓存里存的可能是旧值，这里统一纠一遍。

`oa.py` 的 `CHUNK = 50`、`API = "https://api.openalex.org/works"`，
`locations(dois, api_key, sleep=1.0, max_chunks=0)` 分批查；`401/429` 抛
`RuntimeError` 让人去查 key 或等额度，其余错误 `continue`（查不到的 DOI 不出现在结果里，不猜）。

## llm/：四个调用方共用一个 extract 底座

`llm/` 下 `extract.py` 是唯一的网络与缓存实现，其余模块只是 prompt + schema：

| 文件 | `name=` | `prompt_version` | 职责 |
| :-- | :-- | :-- | :-- |
| `extract.py` | 底座 | — | 提供 `llm_json` / `validate` / `cache_*` / `locate` / `check_fields` |
| `projects.py` | `projects` | `projects-v6` | 科研项目清单 → 结构化 |
| `audience.py` | `bili_audience` | `bili-audience-v4` | B 站评论/弹幕 → 观众反馈；`llm/` 里最重的一个 |
| `research.py` | `research_queries` / `research_terms` / `research_evidence` / `research_outline` | `-v1` 各自 | 深度调研四段，一个文件四个 `name` |

`llm_json()` 的完整签名与契约（在 `extract.py` 里，搜 `def llm_json` 就是）：

```python
llm_json(*, name, schema, system, user, prompt_version,
         model=None, max_tokens=None, temperature=0.0, retries=2, use_cache=True
) -> ExtractResult
```

**七个参数全部是 keyword-only**，没有位置参数可用。`model` 缺省读
`ZHIHU_LLM_MODEL`（默认 `"gpt-4o-mini"`）；`max_tokens` 缺省读
`LLM_EXTRACT_MAX_TOKENS`（默认 `"8192"`）——注意**不是** `.env` 里那个
`ZHIHU_LLM_MAX_TOKENS`，两者是不同的变量名。

`ExtractResult` 六个字段：`data` / `cached` / `mode`（`json_schema`/`json_object`/`text`）/
`model` / `prompt_version` / `stats` / `raw`。`stats` 是调用方回填的（如 `llm_parse` 塞进
`chunks` / `cached_chunks` / `failed_chunks` / `papers` / `doi_dropped`）。

缓存的三层实现位置：

| 环节 | 位置 | 细节 |
| :-- | :-- | :-- |
| 路径 | `_cache_path()` | `LLM_CACHE_DB` 环境变量 > `<root>/collector/data/llm_cache.db` |
| 建表 | `_cache_open()` | 列 `key/name/prompt_version/model/mode/output/created_at`；每次调用都 `CREATE TABLE IF NOT EXISTS` |
| key | `cache_key(pv, model, name, payload)` | `sha256(f"{pv}\x00{model}\x00{name}\x00{payload}")`，payload = `f"{system}\x00{user}"` |
| 命中 | `llm_json` 开头 | 命中直接返回 `ExtractResult(cached=True, mode=表里的 mode)`，**不建 client、不耗 token** |

`system` 也进 key 是刻意的：改 prompt 却忘了 bump `prompt_version` 时，
不会静默复用旧结果。代价是改一个字的 system 就让全部缓存失效——
所以 `prompt_version` 那列在 `llm_cache.db` 里能看到 `-v1` 到 `-v6` 的完整迭代史。

三级 `response_format` 降级与它的判据：

```python
formats = [("json_schema", {...strict: False}), ("json_object", {"type":"json_object"}), ("text", None)]
for attempt in range(retries + 1):
    for mode, response_format in formats:
        try: …
        except Exception as err:
            if _format_rejected(err): continue   # 换下一种格式
            break                                # 进下一次重试
```

`_format_rejected(err)` 只认「`status_code in (400,404,422)` 且错误文本含
`response_format` / `json_schema` / `unsupported`」。超时、网络、鉴权错误**换格式没用**，
所以走 `break` 进重试循环，`sleep(2 * (attempt + 1))`。

`_extra_body()` 三个优先级：`LLM_EXTRA_BODY`（JSON 串）> `LLM_DISABLE_THINKING=0/1`
> 默认（`"nvidia.com" in ZHIHU_LLM_BASE_URL` 时才开 `enable_thinking=False`）。
「空输出 + `finish_reason=length` + 有 `reasoning_content`」时**直接抛 `LlmUnavailable`
让人去调**，不静默重试——重试只会再烧一次预算。

`_client()` 强制 `timeout=float(os.environ.get("LLM_TIMEOUT", "180"))` 且
`max_retries=0`：openai 客户端默认 600s 超时 + 内部重试，一家慢 provider 就能把整条
流水线挂死。`_throttle()` 是模块级 `_last_call` 的全局单值间隔，
`LLM_MIN_INTERVAL` 默认 `_DEFAULT_MIN_INTERVAL = 1.5`。

`validate(instance, schema, path="$")` 只支持本项目用得到的子集：
`type` / `properties` / `required` / `items` / `enum` / `nullable`。
一条容易忘的实现细节：`bool` 是 `int` 的子类，所以对 `integer` / `number`
额外排除 `isinstance(instance, bool)`，否则 `True` 会混进数字字段。

`_extract_json(text)` 的三步：先剥 ```` ```json ```` 围栏，再取第一个 `{` 到最后一个 `}`，
最后 `json.loads`。这三步都不成功就返回 `None`，由调用方记「响应里没有合法 JSON」。

`check_fields(items, source, verbatim)` 返回的是**计数字典**而不是修改后的数据：

```python
{f"not_verbatim_{name}": 0, "quote_missing": 0}
```

`locate(quote, source)` 的判据是 `_WS.sub(" ", quote).strip() in _WS.sub(" ", source)`
——**空白归一后的子串匹配**，不看行号。所以「逐字率」这个读数的口径是
「值能在原文里找到」，不是「值在第 N 行」。**它不校验位置，只校验存在**，
所以同一个值在原文出现两次也算通过。

`llm_parse.py` 在 `refs/` 而不是 `llm/`，因为它同时依赖两边：
`from llm.extract import ExtractResult, LlmUnavailable, check_fields, llm_json` +
`from refs.grammar import Citation, load_lexicon, norm_title, parse`。
它的四个公开函数：

| 函数 | 作用 |
| :-- | :-- |
| `build_user_prompt(lines, offset=0)` | 带整卡序号的 prompt（分块时 `offset` 保证 `line` 是全局行号） |
| `normalize_papers(papers, chunk, offset)` | 确定性清洗：剥 `12.` 前缀、丢空标题、`line` 加上 offset |
| `dedupe_papers(papers)` | 按 `norm_title` 去重 |
| `llm_parse_citations(lines, *, use_cache=True, chunk_lines=None, min_interval=None)` | 分块主入口 |
| `grammar_papers(lines)` | 纯文法路径（对照基准） |
| `diff_papers(llm, gram)` | 返回 `{"only_llm": [...], "only_grammar": [...]}` |

**分块实现在 `llm_parse_citations`，不在 `llm/extract.py`**——这是最容易找错的地方。
`size = chunk_lines or int(os.environ.get("LLM_CHUNK_LINES", "12"))`，
`chunks = [lines[i:i+size] for i in range(0, len(lines), size)] or [[]]`
（空输入也产一个空块，保证 `first` 不为 `None` 之外还有输出）。

单块失败的处置是本文件最重要的几行：

```python
except LlmUnavailable as e:
    stats["failed_chunks"] += 1
    last_error = e
    offset += len(chunk)      # ← offset 仍前进，后面的块行号不会错位
    continue
…
if first is None: raise last_error or LlmUnavailable("所有块都失败")
```

`offset` 在 `continue` 分支里也前进，所以第 3 块失败不会让第 4 块的行号整体前移。
`first.stats = stats` 把统计挂在**第一个成功的块**上返回——所以 `result.model` /
`result.prompt_version` 取自第一个成功块，而 `stats` 是全卡累计。

`min_interval` 参数是**写环境变量**的副作用实现（`os.environ["LLM_MIN_INTERVAL"] = str(...)`），
不是传参——因为 `_throttle()` 读的是环境变量。要改它的调用方必须知道这一点。
