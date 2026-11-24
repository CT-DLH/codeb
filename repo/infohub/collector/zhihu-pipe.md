---
covers:
  - collector/zhihu_pipe/
updated: 2026-11-17
---

# Collector: inside zhihu_pipe

`zhihu_pipe/` 下同时住着两套东西：`sources/` 里的插件文件（含 `__init__.py`）、
`fulltext.yaml` 配置，以及顶层的管道模块。
这里有两套东西：**旧知乎专用管道**（`fetch.py` / `pipeline.py` / `store.py` / `summarize.py`）
和**平台插件框架**（`source.py` + `sources/`）。前者是后者的第一个实现，不是废弃代码。

## store.py：articles 26 列与 7 状态

`articles` 表以 `url` 为 PRIMARY KEY，26 列（`_init_schema()` 里的建表语句原文顺序）：

```sql
url TEXT PRIMARY KEY,  canonical_key TEXT,  kind TEXT,  content_id TEXT,
author TEXT,  author_id TEXT,  title TEXT,
published_at INTEGER,  updated_at INTEGER,  voteup INTEGER,  comment_count INTEGER,
word_count INTEGER,  fidelity TEXT,  platform TEXT,  assets TEXT,
source TEXT,  topic_match TEXT,  raw_path TEXT,  content_hash TEXT,
status TEXT,  summary_path TEXT,  summary_backend TEXT,
summarized_at INTEGER,  fetched_at INTEGER,  seen_at INTEGER,  error TEXT
```

四个索引：

```sql
CREATE UNIQUE INDEX idx_articles_ckey ON articles(canonical_key) WHERE canonical_key != ''
CREATE INDEX idx_articles_status ON articles(status)
CREATE INDEX idx_articles_queue  ON articles(status, raw_path, platform)   -- queue() 专用
```

`idx_articles_ckey` 是**部分唯一索引**（`WHERE canonical_key != ''`）——
空串不算重复，所以只登记了 URL 没有 `content_id` 的行也能共存。

状态机的 7 个状态与 `TERMINAL_STATES = {"summarized", "skipped", "unfetchable"}`：

| 状态 | 含义 | 终态 | 重试语义 |
| :-- | :-- | :-- | :-- |
| `new` | 只登记了元数据，正文未读 | 否 | 正常入队 |
| `fetched` | 正文已抓取，等总结 | 否 | 待总结 |
| `summarized` | 已总结 | **是** | `--refresh` 且远端 `updated_at` 变新才重读 |
| `read` | 正文已读但当前主题不需要 | **否** | 跨主题复用，不再重读 |
| `skipped` | 内容级读不到（已删除 / 空正文） | **是** | 重试一万次也不会变 |
| `unfetchable` | 平台级取不到正文 | **是** | `--retry` 要能重开它 |
| `failed` | 抓取报错 | 否 | 下次重试 |

`skipped` 与 `unfetchable` 都是终态但**重试语义相反**，所以不能合并：
前者是内容级判决（作者删了），后者是平台级判决（源没声明 BODY 能力、缺身份键、
平台认不出来），插件补上能力或页面改版后应该能重开。

`read` **不是终态**是最反直觉的一条：旧逻辑把「主题不符」写成终态 `skipped`，
导致换主题后无法复用。现在 `_init_schema()` 里有两条**数据迁移 UPDATE** 每次启动都跑：

```sql
UPDATE articles SET status='read' WHERE status='skipped' AND error LIKE 'off-topic%' AND raw_path != ''
UPDATE articles SET status='new'  WHERE status='skipped' AND error LIKE 'off-topic%'
                                  AND (raw_path IS NULL OR raw_path='')
```

`seen_at` 的回填也是每次启动都跑：
`UPDATE articles SET seen_at = COALESCE(NULLIF(fetched_at,0), NULLIF(summarized_at,0), 0) WHERE seen_at IS NULL OR seen_at=0`
——只用真实的抓取/总结时间，**不拿发布时间冒充录入时间**。

五个轻量迁移列（老库缺列时补）：`seen_at` / `fidelity` / `assets` / `platform` / `summary_backend`。
手法是 `PRAGMA table_info(articles)` 拿列名集合再逐个 `ALTER TABLE ADD COLUMN`。

另两张表 `runs`（9 列：`started_at`/`finished_at`/`source`/`topic`/`found`/`matched`/`fetched`/`duplicated`/`failed`）
与 `query_ledger`（13 列，UNIQUE(platform, query_norm, topic)），后者是检索词台账：

```sql
platform TEXT NOT NULL, query_norm TEXT NOT NULL, query TEXT NOT NULL,
topic TEXT DEFAULT '',  last_cursor TEXT,  pages_done INTEGER DEFAULT 0,
hits_total INTEGER DEFAULT 0,  new_total INTEGER DEFAULT 0,
exhausted INTEGER DEFAULT 0,  state TEXT DEFAULT '',  last_error TEXT DEFAULT '',
first_run_at INTEGER,  last_run_at INTEGER
CREATE INDEX idx_ledger_lookup ON query_ledger(platform, topic)
```

`state` 四态由 `ledger_record()` 按优先级判：`error` > `empty_suspect`（`hits==0 and not cursor`）
> `done`（exhausted）> `partial`。`empty_suspect` 单独一列存在的理由：
「0 条 + next_cursor=None」在协议上是合法返回，但在采集上几乎总是平台降级/风控的信号，
判成 exhausted 会**永久跳过这个词**（最贵的那种静默失败），所以
`ledger_should_skip()` 对它返回 `False, "上次 0 条疑似被降级，需要重试"`。
另外两种「看起来像捞干但不算」也挡住了：`last_error` 非空 → 重试；
`pages_done >= 10` 且 `exhausted=0` → 该从 `last_cursor` 续跑，不跳过。

`normalize_query()` 只做三件事（去首尾引号、折叠空白、小写），
**不做同义词/分词**——归一过头会让台账不再是事实记录。

## canonicalize_url：知乎专栏必须收敛到 zhuanlan

`KEEP_QUERY_PARAMS = ()` 表示知乎链接的 query 一律丢弃（历史库里的记录都是按这个口径生成的，
改动它等于让老记录全部查重失效）。非知乎源走**黑名单**而不是白名单：

```python
TRACKING_PARAMS = {"utm_source","utm_medium","utm_campaign","utm_term","utm_content",
    "spm_id_from","spm","vd_source","from_source","from_spmid","share_source",
    "share_medium","share_plat","share_session_id","share_tag","is_guided"}
```

白名单会误删语义参数（B 站 `?p=2` 是分 P 序号、小红书 `?xsec_token=` 是详情页访问凭证），
丢了就把不同内容并成一条。

知乎的分支是本文件最重要的一段：

```python
_ZHIHU_ARTICLE_PATH = re.compile(r"^/p/\d+$")
netloc = "zhuanlan.zhihu.com" if _is_zhihu_article_path(path) else "www.zhihu.com"
```

**专栏 `/p/<id>` 收敛到 `zhuanlan`，回答/问题收敛到 `www`**。原来的写法把所有知乎链接
都并到 `www.zhihu.com`，于是专栏变成 `www.zhihu.com/p/<id>`——那个 URL 是**软 404**：
HTTP 200，页面标题却是「404 - 知乎」。实测把手上所有专栏 id 都验了一遍，新旧两种 id
形态**全中**，而同一 id 的 `zhuanlan.zhihu.com/p/<id>` 正确定位。

危害是静默的：库里成批的专栏 URL 与卡片都是坏链接，而状态码 200 让任何
「按状态码判活」的检查都发现不了。抓正文不受影响（`fetch()` 用 `content_id` 走 API），
所以坏了很久没人察觉。

`platform_of(canonical_key, url, known=None)` 判这一行属于哪个插件：三段身份键
`<平台>:<类型>:<id>` 直接取前缀，**且前缀必须在注册表里**（否则 `article:3` 这种老身份键
会把类型名当平台）；老记录只有 `<类型>:<id>` 时按 URL 主机名匹配，
主机名按插件名**长度倒序**（否则通用源 `web` 会把别的域名抢走）；认不出来留空串。

## upsert 的两个「0 不是空」

`upsert(row) -> (is_new, need_work)`。`need_work` 的判据：

```python
if hit is None:                    is_new, need_work = True, True
elif prev in TERMINAL_STATES and row.content_hash:
                                    need_work = hit["content_hash"] != row.content_hash
elif prev in TERMINAL_STATES:       need_work = False
else:                               need_work = True
```

更新分支里有两个**必须排除**的字段，都是实测踩出来的：

```python
upd = {k: d[k] for k in cols
       if d[k] not in (None, "")
       and not (k in ("seen_at","fetched_at","summarized_at") and not d[k])
       and not (k == "word_count" and not d[k])}
```

- `seen_at` 一旦被 0 覆盖，录入时间就永久丢了。典型触发：命中主题后补写
  `topic_match` 会再 `upsert` 一次，那一趟不该动任何时间列。
- `word_count=0` 表示「还没抓正文」，不是「正文 0 字」。不排除它，复跑一次就把已抓到的
  字数清零，且因为 `need_work=False` 再也不会补回来——实测默认库里**已经有一批中招**
  （`raw_path` 在、`word_count=0`，github / zhihu / crossref 都有），
  导出侧看到的就是「有正文但 0 字」。

另一个细节：`if hit["url"] != row.url: upd["url"] = row.url`。
身份是 `canonical_key`，URL 只是别名。小红书每次分享 `xsec_token` 都会变，
知乎专栏/短链也会给出不同 URL 指向同一条内容——此时不改写别名，那条 UPDATE 会命中 0 行，
条目卡在旧状态、每轮重抓、**且没有任何报错**。

## queue()：获取流水线的唯一候选查询

```python
SELECT *, percent_rank() OVER (PARTITION BY platform ORDER BY voteup DESC) AS heat_rank
FROM articles
WHERE COALESCE(raw_path,'') = '' AND COALESCE(content_id,'') != ''
  AND status IN (…)          -- retry=False 时 ('new','failed')，True 时加 'unfetchable'
  AND platform IN (…)        -- 只有传了 fetchable 才加
ORDER BY published_at DESC, voteup DESC [LIMIT n]
```

四个判据各挡一种错：

- 没正文：`raw_path = ''`——抓过就一定有路径，**不看 `fidelity`**（那是内容完整度）
- 还有救：`new`/`failed`；`retry=True` 加 `unfetchable`；`skipped` 永不入队
- 需要身份键：`content_id != ''`，否则构造不出 `ContentRef`
- 平台必须声明 BODY：`fetchable` 由调用方现算（`sources.body_capable_platforms()`），不写死名单

`heat_rank` 是 P5 热度归一分，用 `percent_rank() OVER (PARTITION BY platform ...)`。
**不改查询形状**：`WHERE` / `ORDER BY` / `LIMIT` 全不动，**也不按 platform 分组各取 N 条**
（会饿死小源）。只往 SELECT 追加一列，候选集合逐行不变——`enrich_queue.py` 用它对平「一条不差」。

## pipeline.py 的五步流程

`Pipeline(data_dir, store=None)` 的 `run(opts, fetch_bodies=True)`：

1. **`collect(opts)`** —— `--hot` 用免登录热榜；否则按作者列表拉文章+回答；
   有 `topic_name` 且无作者时走搜索。`expand_authors` 时把种子搜索结果里的作者
   前 `max_authors` 位继续铺开。最后按 `(kind, content_id)` 去重（接口分页重叠会让同一篇被处理两次）。
2. **`screen(pool, opts)`** —— 先硬过滤（`since` / `min_voteup`，纯内存不看库），
   然后**先查重登记再筛选**：`store.upsert(Hit(it,0,[]).row)`。
   顺序很关键——同一作者的文章列表每次都返回全部历史作品，先筛选再抓会让重复文章
   每次运行都被重新下载。`--refresh` 时对终态且远端 `updated_at` 变新的条目翻 `need_work=True`。
   未命中主题的**不写终态**（只登记后留在 `new`），换主题时还能本地重筛复用。
3. **`deep_screen(hits, topic)`** —— 粗筛未过时抓正文再筛一次；仍不中则
   `_save_raw` + `mark_read`（读过的正文一律落盘，下次不再重读）。
4. **`fetch_bodies(hits, limit)`** —— 已有 `raw_path` 且文件存在的**不联网**，
   直接 `set_status("fetched")` 复用。404 判 `mark_skipped("deleted")`，
   空正文判 `mark_skipped("empty-body")`。返回 `(docs, ok, fail, empty, reused)`。
5. `log_run(...)` + 写 `data/out/last_run.json`。

`_save_raw()` 写的 frontmatter 字段：`title` / `author` / `url` / `kind` /
`content_id` / `published_at` / `updated_at` / `voteup` / `comments` / `score` /
`topic_match` / `read_at`。文件名 `{kind}_{content_id}.md`。

`rescreen_topic(topic_name, keywords, limit, use_body=True)` 是**零联网**的本地重筛：
用新主题扫 `new/read/fetched/summarized` 四种状态的行，有正文的读前若干千字一起打分，
命中且状态是 `new`/`read` 的提升为 `fetched` 等总结。这是「不浪费」原则的落点。

`RunOptions` 的十几个字段里三个容易看错：`delay=-1.0` 表示用默认 0.8s（`0` 才是不限速）、
`limit_fetch=0` 表示不限、`deep_filter` 与 `refresh` 默认都关。

## sources/：插件文件数少于注册平台数

`_FACTORIES` 的完整映射（`sources/__init__.py`）：

```python
"zhihu":       (".zhihu",       "ZhihuSource")
"github":      (".github",      "GitHubSource")
"bilibili":    (".bilibili",    "BiliSource")
"xiaohongshu": (".xiaohongshu", "XhsSource")
"cnki":        (".cnki",        "CnkiSource")
"arxiv":       (".academic",    "ArxivSource")
"s2":          (".academic",    "S2Source")
"openalex":    (".academic",    "OpenAlexSource")
"pubmed":      (".academic",    "PubmedSource")
"crossref":    (".crossref",    "CrossrefSource")
"web":         (".web",         "WebSource")
```

**注册的平台数多于插件文件数**：`academic.py` 一个文件注册 4 个（arxiv / s2 / openalex / pubmed），
因为接口形状相同、只是端点/字段/限流不同，共用一个 `AcademicSource` 基类。
`browser.py` 与 `site.py` 是基础设施，**不注册成平台**：
`browser.py` 提供 `BrowserSession`（知网/小红书共用的持久化 Chrome）与 `BrowserSource` 基类；
`site.py` 的 `SiteSource` 由 `_register_site_sources()` **动态**注册。

站点源的注册是**扫描出来的**，不写死：

```python
for path in sorted(sites_dir.glob("*/*.yaml")):
    family = data.get("family") or path.parent.name
    kind   = data.get("kind")   or path.stem
    name   = f"site_{family}_{kind}"
    _FACTORIES[name] = (".site", "SiteSource"); _SITE_SPECS[name] = str(path)
```

`enabled: false` 的 spec 跳过；坏 spec 在 import 期**不抛**（交给 `capability_report()`
记 `probe=failed` 点名）。当前扫出的是 `site_hitsz_teacher_home` /
`site_hitsz_grad_column_list` / `site_hit_yzb_announcement_list`。

## 各平台的能力声明

`Capability` 是 `str` 枚举：`SEARCH="search"` / `AUTHOR="author"` / `BODY="body"` /
`MEDIA="media"` / `TRANSCRIPT="transcript"`。

| 平台 | capabilities | heat_metric | min_interval | 备注 |
| :-- | :-- | :-- | --: | :-- |
| `zhihu` | SEARCH, AUTHOR, BODY, MEDIA | `voteup` | 0.8 | 未公开限流，按风控保守处理 |
| `github` | SEARCH, AUTHOR, BODY | `stars` | 0.5 | core 5000/h；search 30/min（独立配额） |
| `bilibili` | SEARCH, BODY, MEDIA, TRANSCRIPT（**+AUTHOR 仅当有 BILI_COOKIE**） | `view` | 1.5 | 两档：search 3.0 / core 1.5 |
| `xiaohongshu` | AUTHOR, BODY, MEDIA（**+SEARCH 仅当有浏览器且有 cookie/登录记录**） | `like` | 3.0 | 每分钟上限 10 |
| `cnki` | **属性**，运行时算：`browser_available()` 才有 BODY，`last_login()` 再加 SEARCH | `cite` | 6.0 | 无 playwright → `frozenset()` |
| `arxiv` | SEARCH, BODY, MEDIA | `""` | 3.0 | 官方要求 3s/次；不提供引用数 |
| `s2` | SEARCH, BODY（继承基类） | `citations` | 1.2 | 匿名共享池实测长期 429 |
| `openalex` | SEARCH, AUTHOR, BODY（+MEDIA） | `citations` | 1.0 | |
| `pubmed` | SEARCH, BODY | `""` | 0.4 | 无 key 3 次/秒；配 KEY 到 10 次/秒 |
| `crossref` | SEARCH, BODY | `citations` | 1.0 | 匿名 1 次/秒（实测响应头 `x-rate-limit-interval: 1s`） |
| `web` | SEARCH, BODY | `heat` | 1.2 | 唯一不绑定平台的源；已接入平台域名被 `_OWNED` 拦掉 |
| `site_*` | 只有 BODY | `""` | 取 spec 的 `http.delay` | 站点内容没有热度键 |

三个动态能力的理由值得记住，它们都是「宁可少声明」：

- `bilibili` 的 AUTHOR：按 UP 铺开（space 接口）匿名一律 -352/412，补 `dm_*` 风控参数也没用
  （只签 HTTP 412、签了 `dm` 参数 code=-352）。所以**没有登录态就不声明 AUTHOR**，
  别让调度器以为可以铺开。
- `xiaohongshu` 的 SEARCH：搜索要页面 JS 生成 `x-s` 签名；没装 playwright 时什么都不声明，
  调度器就不会白挑它。进随机采集池的条件是「有浏览器，且要么有 `XHS_COOKIE`、
  要么人工登录过一次」。
- `cnki` 的 SEARCH：没有 playwright → 搜索和详情都做不了，返回 `frozenset()`；
  有浏览器但没人过滑块 → 也不声明 SEARCH，否则夜间会话会白白弹一只 Chrome 窗口。

`capability_report()` 逐插件 `try`，一个插件坏了不能把整份清单带走：

```python
# probe=failed 的那一项
{"probe": "failed", "reason": f"{type(err).__name__}: {err}", "capabilities": []}
# probe=ok 的那一项
{"probe": "ok", "capabilities": sorted(...), "query_guide": {...}?}
```

`query_guide` **只有插件声明了才出现这个键**——不给 ≠ 默认规则，agent 必须能区分
「这个源没说」和「这个源说可以这么写」。

`body_capable_platforms() -> (set, dict)` 的口径：集合 = 声明 BODY 的 ∪ **探测失败的**
（不知道 ≠ 不能），逐插件说明里三种话术：`声明 body` / `探测失败（…），按可取正文处理` /
`未声明 body（能力：…）`。只有**确认没声明** BODY 的平台才允许被写成 `unfetchable`——
否则一次 import 失败就会把几百行静默判死。

## x-zse-93/96 签名：完全不自己算

`fetch.py` 的模块 docstring 第一句就说清了：

```python
from zhihu_cli.content.handlers.requests import session
from zhihu_cli.content.utils.html2markdown import converter
```

**签名由 `zhihu-cli` 的 `ZhihuSession` 用 `d_c0` 自动生成**，本项目一行签名代码都没有。
`fetch.py` 只做两件事：请求自己发（用 `session`）、字段自己解析
（`zhihu-cli` 的 handler 会把时间戳格式化成字符串，流水线需要原始 unix 时间戳才能排序
和判断「内容是否更新过」）。

`tools/ingest_curl.py` 配合这一点：

```python
_SKIP_HEADERS = {"x-zse-93", "x-zse-96", "x-zst-81", "accept-encoding", "content-length"}
```

从 cURL 里解析 `-H` 头与 `-b` Cookie，但**主动剔除手写的签名头**——避免用过期的签名值导致 403。
之所以要自己写这个脚本：`zhihu auth paste` 只解析 `-H` 头，**抓不到 `-b` 里的 Cookie**。

`fetch.py` 的限速是 `Throttle(delay=_MIN_INTERVAL, scope="global", jitter=0.0)`：
`scope="global"` 是**有意的简化**（单一域的 API 源，不需要按 host 分键），
`jitter=0` 是因为知乎的风控模型更怕不可预测的节奏吗——不是，是原实现就没有 jitter，
`selftest_throttle.py` 要能逐项证明迁移前后等价。默认 0.8s ≈ 75 次/分钟。

三个 `include` 参数是踩坑结果：`_ANSWER_DETAIL_INCLUDE` 必须显式要 `content,excerpt,...`，
不带 include 时 `/api/v4/answers/{id}` **默认不返回正文**，导致历史上所有回答正文为空、
全部被判成 `empty-body`。

## summarize.py 与摘要后端

`Summarizer(backend="extract")`，两个后端：`extract`（确定性抽取，离线可用）与 `llm`。
`SummaryResult` 带 `backend` 字段，落进 `articles.summary_backend` 列——
这一列存在之前，`idle_papers.py` 只能去 grep 摘要文件里的「摘要方式：llm」，
同一件事有了库状态和文件文本两个真值，文件被重算或丢失时两边会分叉。

`FILENAME_BUDGET = 120` 是摘要文件名的长度预算（`MAX_PATH` 相关，`selftest_filename.py` 专测）。
`_CONCLUSION_RE`（`因此|所以|综上|总之|一句话|结论|答案是|本质上|换言之|简言之|归根结底`）
用来找「一句话结论」那句。

## fulltext.yaml：开放获取白名单与四个实测数字

```yaml
hosts: [arxiv.org, aclanthology.org, openaccess.thecvf.com, proceedings.mlr.press,
        www.pmlr.org, proceedings.neurips.cc, papers.nips.cc, papers.jmlr.org, jmlr.org,
        openreview.net, ojs.aaai.org, pmc.ncbi.nlm.nih.gov, www.ebi.ac.uk,
        copernicus.org, doaj.org, frontiersin.org]
limits:
  max_bytes: 60000000      # 60MB，不是 20MB
  timeout: 90              # 单次 socket 操作
  wall_timeout: 400        # 整次下载的墙钟上限
  min_chars: 1500          # 抽出来的正文至少这么多字
  max_chars: 150000        # 进正文的上限
  interval: 5.0            # 两次请求间隔
```

每个数字都带实测理由，四个最反直觉的：

- `max_bytes` 60MB 而不是 20MB：视频生成/世界模型类论文塞了大量高清帧图，
  PDF 会到 20MB 以上，按 20MB 卡会把整个方向的全文全挡掉，而那个方向恰恰最需要读全文。
- `wall_timeout` 400 而不是 180：实测 arXiv 的 PDF 单篇就要十几到三十几秒
  （单文件不到 1MB），按 180s 卡会把大量正常下载误判成超时（一批里多数中招）。
- `interval` 5.0 而不是 1.0：arXiv 对连续 PDF 请求会限速，间隔过短时后面的请求集体拖到超时。
- `mdpi.com` 从白名单**移出**了：对我们的 UA 直接 403，换 UA 属于绕访问控制，不做。

付费墙后面的正文页（IEEE / Elsevier / Springer / Wiley / ACS…）**一律不在白名单**，
也禁止用任何方式绕——这类条目停在摘要+题录是**有意的**结果。
`DEAD_AFTER = 5`：连不通的域名连续失败 5 次就暂时跳过（等冷却）。
