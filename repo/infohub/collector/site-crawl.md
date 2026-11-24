---
covers:
  - collector/site_crawl/
updated: 2026-11-21
---

# Collector: inside site_crawl

`site_crawl/` 动作层只写一份，站点差异全在 YAML。关键事实：
**这里只注册了一个 adapter**（`teacher_home`），列表型根本不走 adapter，走的是
`column.py` 的通用组合层。所以「加一个列表型站点 = 一份 YAML」是真的，
「加一个教师主页站点 = 一份 YAML」也是真的，只有**新形态**才要写 adapter。

## specs.py：_VALIDATORS 分派表与键白名单

```python
KNOWN_KINDS = {"teacher_home", "column_list", "announcement_list"}

_VALIDATORS = {
    "teacher_home":       _validate_teacher_home,
    "column_list":        _validate_column_list,
    "announcement_list":  _validate_announcement_list,
}
```

`load_spec()` 的执行顺序是四步，任一步失败都抛 `SpecError`（`ValueError` 子类）：

1. `yaml.safe_load` → 空文件当 `{}`
2. `_check_keys(data, TOP_KEYS, "顶层")` —— 未知键当场报错
3. `_validate_common(data)` —— 必填 `family/kind/site/base`、kind 必须在 `KNOWN_KINDS`、
   `base` 必须 http(s) 且**自动补尾斜杠**
4. `_VALIDATORS[kind](data)` —— 查不到校验器时再抛一次（兜住「`KNOWN_KINDS` 加了但忘了配校验器」）

六张键白名单是这一层的事实来源：

```python
TOP_KEYS     = {"family","kind","site","enabled","base","notes","http","apis",
                "selectors","output","seeds","paging","attach"}
HTTP_KEYS    = {"delay","timeout","retries","cookie","cookie_env","user_agent","verbose"}
API_KEYS     = {"body","name_search","dept_list","dept_teachers","dept_prefix","headers"}
SELECTOR_KEYS= {"profile","sections"}
PROFILE_KEYS = {"tid","name","describe","position","discipline","dept_link","photo",
                "contact_item","contact_label","contact_value","email","email_reverse"}
SECTION_KEYS = {"item","title","strip","paper_section","project_section",
                "paper_item","project_name_prefix","project_desc_prefix","aliases"}
OUTPUT_KEYS  = {"domain","object_type","source","fields","body_sections","clear_fields",
                "gaps_from","include_other_sections"}
SEED_KEYS    = {"url","label"}
PAGING_KEYS  = {"mode","pattern","start","probe_limit"}
ATTACH_KEYS  = {"mode","file_pattern","max_bytes"}
PAGING_MODES = {"auto","none","pattern"}
ATTACH_MODES = {"auto","none"}
```

三套必填的差别（`_validate_*` 各自的 `_require`）：

| kind | 必填 | 额外校验 |
| :-- | :-- | :-- |
| `teacher_home` | 顶层 `selectors` + `output`；`selectors` 内 `profile` + `sections`；`profile` 内 `tid` + `name`；`sections` 内 `item` + `title` | `aliases` 必须是 `{小节名: [别名...]}`；走 `_validate_output` |
| `column_list` | 只有 `_validate_common` 的四项 | `output` 可选；**写了 `selectors` 直接报错** |
| `announcement_list` | 加 `output` | 其余同列表型 |

列表型禁止 `selectors` 的那条报错话术值得记住：

```
{kind} 不用 selectors（正文靠 L1 密度抽取）；请删掉，或把 kind 改回 teacher_home
```

防的是「照 `teacher_home` 复制粘贴忘了删」——那种配置看起来很正常，实际一个键都不生效。

`_validate_output()` 的四条：`output.fields` 必须是非空映射、**必须含 `title`**、
`body_sections` 与 `clear_fields` 必须是列表。`fields` 的键是「卡片字段路径」
（`title` / `summary` / `ext.email` 这种带点号的形式），值是记录里的字段名。

`spec_summary(spec)` 产几行中文摘要，判据是 `spec["kind"] != "teacher_home"`
**而不是** `== "column_list"`——否则将来加第四个列表型 kind 会掉进
`teacher_home` 分支访问 `spec["selectors"]` 而 `KeyError`。

## store.py：teachers 表结构与 runs 只读

两张表，`SCHEMA` 一次 `executescript` 建齐：

```sql
CREATE TABLE teachers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,  family TEXT NOT NULL,
    slug TEXT NOT NULL UNIQUE,             url TEXT,        tid TEXT,
    name TEXT,        name_en TEXT,        dept TEXT,       dept_id TEXT,
    dept_en TEXT,     discipline TEXT,     describe TEXT,   research TEXT,
    summary TEXT,     email TEXT,          email_roster TEXT, phone TEXT,
    address TEXT,     photo TEXT,          sections TEXT,   papers TEXT,
    projects TEXT,    browse TEXT,         update_time TEXT, roster_no INTEGER,
    flags TEXT,       sha1 TEXT,           first_seen TEXT, seen_at TEXT,
    updated_at TEXT
);
CREATE INDEX idx_teachers_family ON teachers(family);
CREATE INDEX idx_teachers_dept   ON teachers(dept);
CREATE INDEX idx_teachers_sha1   ON teachers(sha1);   -- 内容指纹比对用

CREATE TABLE runs (   -- 只读历史归档，代码不再写入
    id INTEGER PRIMARY KEY AUTOINCREMENT, started_at TEXT, finished_at TEXT,
    family TEXT, scope TEXT, created INTEGER DEFAULT 0, updated INTEGER DEFAULT 0,
    unchanged INTEGER DEFAULT 0, failed INTEGER DEFAULT 0, note TEXT
);
```

`TEACHER_FIELDS` 是参与哈希的字段全集，`JSON_FIELDS = ("sections","papers","projects","flags")`，
`HASH_EXCLUDE = {"browse","seen_at","updated_at","first_seen"}`。
`browse` 是实时浏览量，进哈希会让每次同步都判成内容变了。

`teacher_sha1(row)` 的算法是**位置敏感的字符串拼接**：

```python
parts = []
for key in TEACHER_FIELDS:
    if key in HASH_EXCLUDE: continue
    parts.append(_canonical(value) if key in JSON_FIELDS else str(value or ""))
return sha1("|".join(parts).encode("utf-8","ignore")).hexdigest()
```

`_canonical()` 对 JSON 字段做 `json.loads` 再 `json.dumps(sort_keys=True, ensure_ascii=False)`，
所以 `{"a":1,"b":2}` 与 `{"b":2,"a":1}` 同哈希；但 `TEACHER_FIELDS` 的**顺序改一下就全部指纹失效**。
`content_fingerprint(rec)` 就是 `teacher_sha1(_encode(rec))`，`cache_put` 与 L3 的
`--register` 拿它当 `pipeline.db.articles.content_hash`——两个库比的是同一个指纹。

`Store` 真正在用的公开方法：

| 方法 | 签名 | 行为 |
| :-- | :-- | :-- |
| `cache_cold` | `() -> bool` | `teachers` 表 count == 0 |
| `cache_get` | `(slug) -> str \| None` | 返回 sha1 |
| `cache_put` | `(slug, sha1, rec=None) -> bool` | `True` = 内容变了 |
| `get_teacher` | `(slug) -> dict \| None` | 反序列化 JSON 字段 |
| `teachers` | `() -> list[dict]` | 全量，`ORDER BY id` |
| `count_teachers` | `() -> int` | |

三个**保留壳**必须知道它们不干活：

- `start_run(scope, family) -> int` 只 `warnings.warn` 然后返回 `-1`，**不写库**
- `finish_run(run_id, counts, note)` 只 `warnings.warn`，不回写
- `upsert_teacher(rec) -> str` 把布尔翻回旧字符串 `created` / `updated` / `unchanged`，
  内部走 `cache_put`——只为让个别老调用点不炸

`cache_put` 的一个细节：`old == sha1` 时**只刷新 `seen_at`**，不动 `sha1` / `updated_at`、
不计数。`old is None` 时 INSERT 带 `sha1` / `first_seen` / `seen_at` / `updated_at` 四列，
其余列走 `UPDATE`。`row["family"]` 兜空串——`family` 是 `NOT NULL`，
缓存非教师内容时不该因为缺一个字段变成 `IntegrityError` 把整轮同步带走。

`content_cache_cold(path)` 是**独立于 `Store` 的只读函数**，给 `collect_site.py --dry-run` 用：
库不存在 → `True`；`sqlite3.connect(f"file:{p}?mode=ro", uri=True)` 打开；
`sqlite3.Error`（没有 teachers 表）→ `True`。它既不建文件也不开 WAL。

`default_db_path()` 读环境变量 `INFOHUB_CRAWL_DB`，默认 `<collector>/data/crawl.db`——
和 `pipeline.db` **同目录但独立文件**，两套状态机互不影响。

## adapters/：只有一个

```python
ADAPTERS = {"teacher_home": TeacherHomeAdapter}
```

`get_adapter(kind)` 查不到抛 `KeyError`（不是静默返回 `None`）。
`TeacherHomeAdapter` 的这批模块级函数就是站点知识的具体位置：

| 函数 | 作用 |
| :-- | :-- |
| `slug_of(value, host="homepage.hit.edu.cn")` | 从 URL 抠出 `slug`；不是该 host 返回空串 |
| `split_title(title) -> (zh, en)` | 中英标题拆分 |
| `first_sentence(text, limit=180)` | 取首句当 `summary` |
| `canonical_section(title, aliases)` | 栏目名归并到稳定小节名 |
| `title_matches(title, names)` | 包含匹配、大小写不敏感 |
| `merge_sections(sections)` | 同名小节合并 |
| `subhead_segments(text, aliases)` | 正文里的子标题切段 |
| `_extract_papers(node, item_sel)` / `_papers_from_lines(lines)` | 论文两级抽取 |
| `_extract_projects(node)` / `_projects_from_lines(lines)` | 项目两级抽取 |

`collect(target)` 的五步：`slug_of` → `_profile`（首屏 HTML）→ `_sections`（POST 接口）
→ `_record` → `_enrich` → `_finish`。

`_profile()` 的关键点是**邮箱反转**：`email_reverse: true` 时 `value[::-1]`
（主页写的是 `nc.ude.tih@…`）。`_sections()` 的接口调用是
`post_json(urljoin(base, apis.body), {"id": tid, "versionId": ""}, referer=url)`——
`versionId` 传空串是站点要求的。

`collect()` 的三种拒绝都是**点名式**的：无 `tid` 抛
`页面没有 teacher-body/tid，可能不是教师主页或站点改版`；
`_sections` 接口返回空正文抛 `empty_body_payload`；
选择器 `item` 一个都没命中抛 `selector_miss` + 「可能站点改版」。
这三句话术是给报告用的，不是给人猜的。

## http.py 与 text.py 的 re-export 关系

两个文件**都只是转发、不放实现**，且都用同一手法把私有件也搬过去：

```python
from kit import http as _impl
from kit.http import (DEFAULT_UA, MAX_BYTES, RETRY_STATUS, ROBOTS_TTL, FetchError,
                      FetchResult, Http, RobotsLoader, clear_robots_cache, decode_body,
                      decode_body_ex, decode_html, json_loads_ignore, normalize_charset,
                      robots_allowed)
globals().update({k: v for k, v in vars(_impl).items() if not k.startswith("__")})
```

`globals().update(...)` 这一行是**给 monkeypatch 用的**：离线自检会替换
`_robots_for` / `_load_robots` 这类内部函数，少转一个就会「看起来跑通了、
其实测的是另一份实现」。`selftest_kit.py` 用 `is` 逐个名字比对，不是在测行为等价。

保留这层转发层的理由写在 docstring 里：P1 的判据是「同一批 URL 重放，
`pipeline.db` 逐行不变」。把调用点一起改掉，就无法区分「搬家搬坏了」和「调用点改错了」。

`text.py` 额外把适配器用到的名字逐个显式转发（`parse_html` / `select` / `select_one` /
`node_text` / `attr` / `to_html` / `drop` / `html_to_text` / `extract_content` /
`extract_content_ex` / `extract_links` / `looks_like_file` / `normalize_date` /
`clean_title` / `detail_date` / `dedupe` / `BLOCK_TAGS` / `card_of` / `join_digits` /
`now_stamp` / `parse_publish` / `to_iso` / `clean_text`），
因为 `adapters/teacher_home.py` 的 `from ..text import parse_html, select, ...` 一行不想改。

## column.py：列表型的通用组合层

`crawl_column(spec, *, http=None, max_pages=10) -> ColumnReport`，报告字段：

```python
pages: list[str]          # 真正走过的页 URL
items: list[dict]         # 正文：{url, title, chars, backend, text, entries}
attachments: list[dict]   # 附件：{url, kind, bytes, chars, backend, robots_note, text}
unparsed: list[dict]      # 未解析：{url, kind, reason, backend}
failures: list[dict]      # 取页/取件失败，点名到原因
stop_reason: str
```

三个「不猜」的设计：

1. `_CachedHttp` 包一层按 URL 缓存——`kit.paging.iter_pages` 为了判新增条目数会自己取每一页，
   而 L2 还要用同一份 HTML 抽正文和找附件。包一层保证**一个页面只发一次请求**，
   且不改 L1 的任何接口。
2. `paging.mode == "pattern"` 时报告 `pattern_mode_pending` 并**直接返回**，不静默按 auto 跑。
   原话：「写进报告里说 pattern 生效了，那是说谎」。
3. `pages` 为空时**再探一次**把具体原因带出来（`ok=` / `reason=` / `robots_note=` /
   `html_chars=` / `内容条目=`）——「网络断了」和「被 robots 拒了」在报告里不能长得一样。

`stop_reason` 三选一：`paging_none` / `soft_404_or_limit` / `no_pages`。

`_parse_items(html, url) -> list[dict]` 是翻页判据的基准：条目 = **内容链接**，
过滤掉 `rel=next/prev`、`#/javascript:/mailto:/tel:` 开头、附件（`looks_like_file`）、
分页控件文本（`_PAGING_LABELS`、纯数字、空文本），按绝对 URL（去 fragment）去重。
用绝对 URL 当身份键——软 404 返回同一页时 20 条会全重合，新增 0，铁律才拦得住。

`_PAGING_LABELS = KPaging.PAGING_LABELS` 是转发名，不是本地定义：
「分页控件不是内容」这条知识已经下沉进 L1，这里保留名字让既有 `_parse_items` 零改动。

`announcement_list` 与 `column_list` **走同一个 `crawl_column`**——两者的区别只在
spec 的 `output`，代码里没有任何分支。这是「两种 kind 同族」的具体实现方式。

## runner.py：teacher_home 的编排与三条拒绝

`run(spec_path, targets, *, dry_run=False, db_path=None, show_pii=False, register=None,
report_dir=None) -> dict`。`register` 是 L3 注入的回调 `(record, sha1) -> bool`，
不给就是预演，runner **完全不碰 pipeline.db**。

三条容易忽略的行为：

- `_same_person(expected, actual)` 只容忍「陈斌」vs「陈斌2020」这种数字后缀。
  卡片里的主页链接可能是错的，姓名对不上就整条拒绝——**绝不把别人的资料写进这张卡**。
  归一化用 `_name_key()`：去掉括号内容、去空白与 `·.,，、`、小写。
- `_brief()` 是给报告用的摘要，敏感值（email/phone/address）默认只留布尔
  （`has_email` / `has_phone` / `has_address`），`show_pii=True` 才带值。
- 进度文件路径固定为 `data/out/site_<family>_<kind>_last_run.json`，
  `report_dir` 参数只给离线自检写临时目录用。

报告的字段面：`scope` / `dry_run` / `started_at` / `finished_at` / `targets` /
`cache_cold` / `would_update`（内容指纹变化的条数）/ `registered` / `failed` /
`teachers_total` / `items` / `errors`。`would_update` 取代了旧的
created/updated/unchanged 三计数——那套计数会和 `pipeline.db.articles`、
`runs/active/*.json` 各说一套，形成第三套状态机。

`_http_from_spec(spec)` 的凭据优先级：`http.cookie_env` 指向的环境变量 >
`http.cookie` 字面值 > 空。`user_agent` 只在非空时才传给 `Http`（否则用 `DEFAULT_UA`）。

## 另见：端到端链路

本页讲的是动作层（spec 加载、适配器、缓存指纹）。把 `teachers.yaml → collect_site.py →
crawl.db → crawl:export → import:jsonl → batch_llm` 这条链的**接缝与跨层契约**串起来的那一页是
`infohub/collector/crawl-db-jsonl-llm`——`domain` 必须写 `info_mentor`、`source` 是中文显示名
≠ 注册名、`body_sections` 是排序不是白名单、`clear_fields` 的空值例外，这些都记在那页。
