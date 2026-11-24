---
covers:
  - collector/kit/
updated: 2026-11-17
---

# Collector: kit API reference

`kit/` 的五件原语是 `http` / `html` / `blob` / `paging` / `store`。
`kit/__init__.py` 只做转发（`__all__` 就是这份公开面的清单，改完记得同步）。
要改采集行为，先在这张表里找到对应函数，不要去改调用点——L1 的每个常量值都是实测出来的。

## http.py 的常量与限速算法

```python
DEFAULT_UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
              "(KHTML, like Gecko) Chrome/120.0 Safari/537.36 EduInfoFetcher/0.1")
MAX_BYTES   = 8_000_000     # 单页上限，超过判 too_large
ROBOTS_TTL  = 3600.0        # robots 缓存秒数
RETRY_STATUS = (429, 500, 502, 503, 504)
```

`MAX_BYTES` 是**单页**上限，不是附件上限（附件另有 `blob.MAX_BLOB_BYTES = 20_000_000`）。
`RETRY_STATUS` 之外的状态码（400/401/403/404）**不重试**，直接返回 `http_<code>`。

`Throttle.wait()` 的实际算法（`kit/http.py` 的 `Throttle` 类末尾）：

```
interval = buckets.get(key, delay) if scope=="bucket" else delay
elapsed  = monotonic() - _last.get(key, 0.0)
wait     = interval - elapsed
if wait > 0:
    wait += random.uniform(0, jitter)   # jitter 默认 0.4
    sleep(wait)
_last[key] = monotonic()
```

注意 `_last.get(key, 0.0)` 的默认 0：**某个 key 的第一次请求永远不等待**（elapsed 是一个巨大值）。
`Http.__init__` 里 `self.delay = max(0.3, float(delay))`——构造期有 0.3s 地板，
但 `set_delay()` 没有地板（`max(0.0, ...)`），所以运行时 `--delay 0` 才能真正不限速。
`Http` 把自己的 `delay` 每次 `_throttle()` 时 `set_delay` 推给 Throttle，
这是为了保住「运行时直接改 `Http.delay` 立即生效」的旧语义。

四种 scope 的行为差异（`Throttle.__init__` 的 `scope` 参数）：

| scope | `_key()` 返回 | 谁在用 |
| :-- | :-- | :-- |
| `host` | URL 的 netloc（小写） | `Http` 默认、`site_crawl` 全站 |
| `global` | 固定 `"*"` | `zhihu_pipe/fetch.py`（单一域的 API 源，有意简化） |
| `bucket` | 桶名（`search` / `core`） | `bilibili.py`（两档配额不同） |
| `sliding` | 固定 `"window"` | `xiaohongshu.py`（滑动窗口 + 每分钟上限） |

`sliding` 有两个分支。通用分支（`max_per_minute>0`）先丢弃 60s 前的时戳，
满额则 `sleep(60 - (now - _times[0]) + 0.01)` 再重算一次；
`window_compat=True` 走 `_wait_window_compat()`，逐项复刻小红书原实现的节奏——
最小间隔相对**最近一次请求**、窗口满时 sleep 到最早请求过期后**重算**（`while True` 代替原递归）、
append 的是 **sleep 之后**的时钟值。两条分支的差别只在 `append` 时机，
`selftest_throttle.py` 用同一个假时钟证明迁移前后逐行等价。

## http.py 的编码嗅探顺序

`decode_body_ex(content, header_charset="") -> (text, reason)` 的候选编码顺序是**固定五段**：

1. `<meta charset=...>`（正则 `_CHARSET_RE`，只看前 4096 字节）
2. `<meta http-equiv=... content="...charset=...">`（`_HTTP_EQUIV_RE`）
3. 响应头 `Content-Type`（`_HEADER_CHARSET_RE`，取不到 charset 就把整个头当编码名试）
4. `utf-8`
5. `gb18030`

全部失败才 `content.decode("utf-8", "replace")`，此时若结果含 `\ufffd` 就返回 `reason="decode_failed"`。
空字节直接返回 `("", "empty_body")`。

`_CHARSET_ALIASES` 是把两份历史实现取并集的别名表，**关键的一条是
`iso-8859-1 → gb18030`**：中文站把「没设置编码」标成 iso-8859-1 是常态，
真拉丁页面用 gb18030 解不出来会继续走兜底，所以这个替换不会比原来更差。
其余：`gb2312` / `gbk` / `gb-2312` / `gb_2312` / `windows-936` / `cp936` 全部 → `gb18030`；
`big5` → `big5hkscs`；`utf8` → `utf-8`。

`normalize_charset()` 先 `.strip().lower().replace("_", "-")` 再查表，所以
`gb_2312` 会先变成 `gb-2312`——表里两条都留着只是为了阅读时不必心算转换。
别名 `_normalize_charset` 保留给老调用点。

## http.py 的 robots 判定

```python
robots_allowed(url, *, ua=DEFAULT_UA, timeout=10.0,
               loader=None, cache=None) -> tuple[bool, str]
```

判定链全部在 `_load_robots(root, timeout, ua)`：

| robots.txt 响应 | 返回 parser | 说明串 |
| :-- | :-- | :-- |
| 200 | 解析后的 `RobotFileParser` | `robots 已取到` |
| 401 / 403 | **一个手写的全站禁止 parser** | `robots 返回 403（视为禁止抓取）` |
| 其它 HTTP 错误（404 等） | `None`（= 允许） | `robots 返回 404（视为允许）` |
| 网络异常（任意 `Exception`） | `None`（= 允许） | `robots 取不到（TimeoutError，视为允许）` |

401/403 单独处理成「全站禁止」的理由写在注释里：拒绝访问 robots.txt 是「明确不想被抓」，
按主流口径置为禁止；如果返回 `None`（允许），就会出现「说明写了禁止、返回值却允许」的自相矛盾，
那是最难查的一类 bug。判定的**主语**（哪个状态码 / 哪条 Disallow）会拼进说明串，
一直传到 `FetchResult.robots_note` 和 `Blob.robots_note`——报告要能说出「被谁拒的」。

`robots.txt` 只读前 512_000 字节；`Http.robots()` 把 timeout 收窄到 `min(self.timeout, 10.0)`。
缓存键是 `scheme://netloc`（不是全 URL）——robots 是站点级的，按 URL 缓存会白取几百次。
`clear_robots_cache()` 清的是模块级 `_robots_cache_global`，`Http` 实例另有自己的 `_robots_cache`。

## http.py 的重试与失败码

`fetch()` **永远返回 `FetchResult`，不抛传输层异常**。重试循环 `for attempt in range(retries + 1)`：

- `HTTPError` 且 `status in RETRY_STATUS` → `sleep(2.0 * (attempt + 1))` 后重试（2s / 4s / 6s）
- `HTTPError` 其它状态 → 立即返回 `http_<code>`
- `URLError` / `TimeoutError` / 其它 `Exception` → `sleep(1.5 * (attempt + 1))` 后重试（1.5s / 3s / 4.5s）

状态码分支用 2.0 而网络分支用 1.5，不是笔误：服务端 5xx 是「它在忙」，退久一点；
网络错误多半是本机瞬时问题，退短一点。

`FetchResult.reason` 的取值集合：`bad_url` / `robots_disallow` / `http_<code>` /
`timeout` / `network_error` / `network_error: <异常类名>` / `too_large` / `empty_body` / `decode_failed`。
`decode_failed` 是**唯一一个既 `ok=False` 又带 `content` 字节**的码——为了不让好字节被丢掉，
`blob.fetch_blob()` 对它会翻成 `ok=True`。

`get(url, referer, allow_redirects=True)` 的 `allow_redirects` 是**兼容形参**：
urllib 默认跟随重定向，传 `False` 也会跟随。注释里明写了这一点，不要指望它拦重定向。

`post_json()` 的请求头必须显式要 JSON：

```python
"Accept": "application/json, text/json; q=0.9, */*; q=0.8"
```

教师主页按 `Accept` 决定返回 JSON 字符串还是原始 HTML，默认的 `text/html` 会抢先命中。

## html.py 的函数清单

DOM 面（给适配器用的最小接口，选择器语法是 CSS，不是 XPath）：

| 函数 | 签名 | 要点 |
| :-- | :-- | :-- |
| `parse_html` | `(html) -> node \| None` | 固定按 `encoding="utf-8"` + `recover=True`；先 `document_fromstring`，失败退 `fromstring`，再失败返回 `None` |
| `select` | `(node, selector) -> list` | 选择器写错**抛 `ValueError`**，不静默返回 `[]`；缺 cssselect 抛 `RuntimeError` |
| `select_one` | `(node, selector) -> node \| None` | |
| `node_text` | `(node) -> str` | `" ".join(itertext())` 后 `clean_text` |
| `attr` | `(node, name, default="") -> str` | |
| `to_html` | `(node) -> str` | 不含 tail |
| `drop` | `(node) -> None` | `drop_tree()` 会把 tail 并回兄弟，这里保留 tail |

日期链（`_FULL_CN` / `_MD_CN` / `_ISO` / `_COMPACT` / `_YMD_SLASH` 五条正则）：

```python
DETAIL_DATE_SELECTORS = (".news-time", ".art-time", ".time", ".date", ".article-time",
                         ".f_time", ".info", ".xxtime", ".pubtime", ".publish-time")
```

`normalize_date(raw, default_year=0)` 的匹配顺序是 `_ISO` → `_YMD_SLASH` → `_FULL_CN`
→ `_COMPACT` → `_MD_CN`。`_COMPACT`（`YYYYMMDD`）额外要求 `1990 < 年 < 2100`；
`_MD_CN`（`9月3日`）只有给了 `default_year` 才出结果。
`join_digits()` 先反复折叠「数字 + 空格 + 数字」，因为学院站常把 `2026` 拆成
`<span>20</span><span>26</span>`，不折叠则日期正则全部失效。
`clean_title()` 用 `_TRAILING_DATE` 剥掉标题尾部的日期（发布日期另有字段）。
`detail_date()` 先走 `DETAIL_DATE_SELECTORS`，都落空才对正文前 400 字扫一遍。

正文抽取的两条路：

- `extract_content_ex(html, selectors) -> (text, reason)`：选择器链，命中要求
  `len(node_text(node)) > 40`；原因码 `""` / `selector_miss`（退回整页）/
  `empty_html` / `parse_failed` / `empty_text`。
- `density_extract(html, url="", *, max_chars=MAX_CHARS, min_chars=MIN_CHARS) -> Extraction`

## 密度打分的具体公式

```python
MAX_CHARS = 60_000   # 正文上限
MIN_CHARS = 400      # 低于此判「没抽到正文」
```

打分**不是**传统的「字数 × (1 − 链接占比)」，而是**直接拿 `_emit` 的产物长度当分数**：

```python
for el in doc.iter("body", "main", "article", "div", "section", "td"):
    if _content_len(el) < 200:        continue   # 门槛 1
    if _link_density(el) > 0.5:       continue   # 门槛 2：链接农场
    out = []; _emit(el, base, out, 0)
    n = len(_tidy("".join(out), MAX_CHARS))
    if n > best_len: best, best_len = el, n
if best is None: best = doc.find("body")
```

为什么改成这个口径：旧公式是 `_content_len(el) * (1 - link_density)`，但
`_content_len` 数的是 `p/li/td/dd/blockquote/h1-h6/pre` 的 `text_content` 总和，
而真正决定产出的是 `_emit` 的输出，`_emit` 只对其中**一部分**结构出文本。
口径不一致时的实测翻车（2026-11-04 复现 6/6）：

```
站点 A 简介页   div#jzkow… score 542 → 出   62 字
                 body       score 456 → 出  913 字
站点 B 毕设栏目  body       score 376 → 出    0 字
                 div        score 336 → 出 2298 字
```

高分容器出不了字，而旁边能出正文的兄弟容器**根本没被试**。当时那一批里大部分都救回来了，
剩下的确实没有可抽的正文。

`_link_density(el) = min(1.0, 所有 <a> 的 text_content 去空白长度 / el 去空白总长度)`，
`total == 0` 时返回 1.0（空节点按「全是链接」处理，直接淘汰）。

两遍抽取：`for aggressive in (True, False)`。第一遍 `_prune` 按
`_BAD_ATTR`（nav/menu/footer/sidebar/comment/share/related/pagination 等一批词根）
和 `_BAD_ROLE`（navigation/banner/contentinfo/search/complementary）删容器，
但 **`main` / `article` 例外不删**；第二遍用未清理的树重来。原因是有的站把正文塞在
`id="header"` 这类容器里，一刀切会把它切掉。

`_DROP_TAGS` 里的每一个标签都必须从**这棵真正被用的树**上摘。曾经在 `doc` 上摘、
却用新解析的 `work` 去挑容器，等于这段清理是死代码（`<noscript>` 里的内容仍参与打分），
2026-11-04 实测确认。

`Extraction` 的字段：`title` / `text` / `lang` / `reason` / `assets` / `chars` / `selector`。
`lang` 判据：CJK 字数 `>= max(20, len(text) * 0.05)` 记 `zh`，否则 `en`。
`assets` 只收 `.pdf` 链接，有条数上限。`selector` 是「tag#id.class」的可读描述，给报告点名用。

## blob.py 四级降级的判据

`MAX_BLOB_BYTES = 20_000_000`。比 HTML 的 `MAX_BYTES` 放宽一档的理由写在注释里：
带插图的招生简章 PDF 常超过 8 MB，卡在 8 MB 会把真附件判成 `too_large`；
但也不能无上限——几百 MB 的镜像包里没有我们要的正文，下载它要付带宽和站点容忍度。

抽文降级链按 `sniff_kind()` 判出的 kind 分派，每条链的判据不同：

| kind | 后端顺序 | 全失败的 reason |
| :-- | :-- | :-- |
| `pdf` | `pypdf` → `pymupdf` → `pdftotext` → `pandoc` | `pdf_backend_missing` |
| `docx` | `builtin_docx`（zipfile + ElementTree） → `pandoc` | `doc_backend_missing` |
| `doc` | 只有 `word_com`（Word COM 经 PowerShell） | `doc_backend_missing` |
| `xlsx` | 只有 `builtin_xlsx`（sharedStrings + worksheet） | `unsupported_kind` 之外的失败 |
| `html` | 只有 `builtin_html`（纯 `re`） | — |
| `xls`/`ppt`/`pptx`/`zip`/`unknown` | **不抽** | `unsupported_kind` |

`_chain()` 把失败分两个桶，这是这一层最关键的区分：

```python
except Unparsed as exc:
    bucket = missing if exc.reason.endswith("_missing") else empty
```

全在 `missing` 桶 → 报 `*_backend_missing`（**环境问题**，装个后端就行）；
有任何一档跑过但出空 → 报 `empty_text`（**文档问题**）。报告上的话术完全不同。

`_pdf_backends()` / `_docx_backends()` 每次调用时重新取模块属性（而不是模块级常量），
自检替换 `_pdf_via_*` 就能整体关掉某一档——「本机缺这个后端时会落到下一个」这条行为
只能靠伪造缺失来证明。

`Unparsed.reason` 的完整取值：`pdf_backend_missing` / `doc_backend_missing` /
`encrypted` / `scan_only` / `empty_text` / `unsupported_kind`，另加一个非解析类的
`fetch_failed`（`fetch_and_text()` 里下载就没成）。

`pdftotext` 这一档的三个参数都是踩坑结果：走 **stdin**（Windows 下不拼中文临时文件名）、
传 `-layout`（保版面）、传 `-enc UTF-8`（中文不乱码的前提）。

`.doc` 走 Word COM 的 PowerShell 脚本是**纯 ASCII**，路径由 `-Src` / `-Dst` 从命令行传入：
PowerShell 5.1 读无 BOM 的 UTF-8 会按 ANSI 解释，脚本里一旦有中文路径就会拼出打不开的文件名。
`SaveAs2` 用第 12 个**位置**参数传 `65001`（UTF-8）而不是 `Encoding:=65001`：
后绑定 COM 的命名参数在部分 Word 版本上解析失败。
`fetch_blob(http, url, *, timeout=20.0, max_bytes=MAX_BLOB_BYTES, ua="")` 的
`timeout` 与 `ua` 是**保留形参、不透传**（超时和 UA 都在 http 层定），文档里明写了
「传了也不生效」。`_http_fetch()` 只 duck-type 认 `fetch(url)` / `get(url)`，
缺了抛 `ValueError` 而不是静默退回 urllib 直连——那样会绕开限速与 robots 闸。

`_payload_reason()` 把 http 层的细原因码收敛到 `REASON_CODES` 六个码，
但**收敛不等于丢弃**：原始串一定进 `Blob.note`，报告里照样能点名。
`robots_note` 单独存一列，`reason="robots_disallow"` 只是结论，还不知道「被哪一条 Disallow 拒的」。

## blob.py 的类型嗅探顺序

`sniff_kind(data, content_type="", url="")`：**内容优先，Content-Type 次之，扩展名最后**。

```
raw[:5] == b"%PDF-" 或 b"%PDF-" in raw[:1024]  → pdf
raw[:4] == b"PK\x03\x04"                       → _sniff_zip(raw)
raw[:8] == OLE2 b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1" → _sniff_ole2(ctype, url)
否则 _kind_from_ctype(ctype) → _kind_from_url(url) → "unknown"
```

`_sniff_zip` 先查三个精确条目 `word/document.xml` / `xl/workbook.xml` / `ppt/presentation.xml`，
再按前缀 `word/` / `xl/` / `ppt/` 认一次（少数生成器把主部件放子目录），
都不中是 `zip`。坏 zip 的 `BadZipFile` / `RuntimeError` / `OSError` / `ValueError` 全部吞掉——
调用方拿这个函数是为了**判类型**，不是为了处理压缩包错误。

`_sniff_ole2` 的顺序是 **ctype 优先于扩展名**：OLE2 字节里没有子类型信息，
而「.docx 扩展名装的其实是旧版 .doc」是常见坑，`Content-Type` 更接近
「服务器怎么理解这个文件」。两者矛盾（字节 OLE2、扩展名 OOXML）时返回 `unknown`，
宁可让调用方报未解析，也不假装知道。

为什么内容优先：`.doc 实为 HTML 下载页`是常态（附件链接被 302 到登录页/提示页），
按扩展名会派一个 doc 解析器去读 HTML，然后报「后端缺失」——
而真正该说的话是「这个链接给的是提示页」。`builtin_html` 这一档存在的理由就是这个：
报告上说「附件里写的是请先登录」比说「doc 后端缺失」有用得多。

## paging.py 的候选形状与原因码

```python
REASONS = {"no_candidate", "soft_404", "probe_limit",
           "fetch_failed", "parse_empty", "current_failed"}
_SHAPES_PER_FAMILY = 3
FALLBACK_SHAPES = True
PAGING_KEY = "\x00__paging_control__"
```

六个原因码各自的触发条件（`find_next_page` 与 `_find_next` 分工）：

| 码 | 触发点 |
| :-- | :-- |
| `current_failed` | `find_next_page` 里当前页取不回来 |
| `parse_empty` | 当前页解析出 0 条：**没有基准，任何「新增」都不可信，这时不能翻** |
| `probe_limit` | `probe_limit < 1`，调用方明确要求「不探测」 |
| `no_candidate` | 一个候选形状都发不出去（页面无显式下一页 + 关掉通用猜测） |
| `fetch_failed` | 候选全取不到（`fetched_ok == 0`） |
| `soft_404` | 至少一条候选拿到了内容，但没有一条带来新条目 |

`fetch_failed` 与 `soft_404` 必须分开：前者是「取不到」，后者是「取到了但是同一页」，
两种失败的处置完全不同。

候选生成顺序（`_candidates`，越可能真是下一页的越靠前）：

1. 页面里显式的「下一页」锚点（`rel="next"` 排在最前，其次锚文本命中）
2. `?page=N`，N = 2, 3, 4（`_with_page_query` 先删掉已有的 `page` 参数，避免 `page=1&page=2`）
3. `list{N}.htm`，N = 2, 3, 4（`_sibling` 替换同目录文件名）
4. `index_{N}.html`，N = 2, 3, 4

猜测之间把 query 形状排最前的理由：`list2.htm` 这种「写死页码的文件名」
在实测里恰好是软 404 的高发形状（同样内容被复制到多个文件名上）。

锚文本的匹配正则原文：

```python
NEXT_TEXTS = frozenset({"下一页","下页","后一页","下一頁","Next","next","NEXT","Next >","›","»",">","≫"})
_NEXT_SUFFIX_RE = re.compile(r"^(?:下一页|下页|后一页|下一頁|next)\s*[（(]?\s*\d*\s*[)）]?\s*(?:[›»>≫]+)?$", re.I)
```

**不用「包含」匹配**：否则正文里的行内链接「下一页的说明」会被误抓成翻页控件。
锚文本在比较前先 `_WS_RE.sub("", _INNER_TAG_RE.sub(" ", inner))`——去标签、去空白、再精确比对。

`item_key(item)` 的取值优先级：`dict` 依次试 `url` / `href` / `link` / `id` / `title`，
对象依次试 `url` / `id` / `title`，`str` 单独先处理（`"http://a/x".title` 是 str 的方法，
不拦下来会把 key 变成一个 bound method 的 repr）。`_key_str()` 会**去掉 `#fragment`**——
列表页里同一条常同时出现 `.../x` 与 `.../x#top`，不归一就会算成「新增 1 条」，
软 404 被误判成真翻页。判据对了但 key 写错，等于没判。

`PAGING_LABELS`（下一页/下页/后一页/上一页/上页/前一页/首页/末页/尾页/
第一页/最后一页/next/prev/previous/first/last/›/»/‹/«/>）由 `is_paging_label()`
判定（去空白 + 小写，纯数字或空文本也算），全部塌缩到哨兵 key `PAGING_KEY`。
理由：软 404 页常常多/少一个「下一页」锚点，于是「同一页」被算成新增 1 条，铁律直接失效。
这是 P2c 离线自检抓到的真实缺陷，不是理论风险。

`iter_pages()` 的防御：`max_pages` 硬上限（默认 10）、`visited` 集合拦环形翻页（A→B→A
在软 404 站上很常见）、每页只取一次（判定下一城用本页已取到的 html/条目）。

`store.py` 只有三个真正的 API：`connect(path, *, timeout=5.0)`（一次做齐 `Row` 工厂 /
`busy_timeout=5000` / `journal_mode=WAL` / `foreign_keys=ON` / `synchronous=NORMAL`）、
`migrate(conn, migrations)`（`PRAGMA user_version` 当版本号，**不做 downgrade**，
SQL 必须可重入因为 `executescript` 会隐式 COMMIT 导致做不到一条迁移一个事务）、
`ensure_columns(conn, table, columns)`（只加不删、不改类型，列名必须过
`[A-Za-z_][A-Za-z0-9_]*` 白名单才拼进 DDL）。

`connect()` 里同时留了 Python 侧的 `timeout=5.0` 和 SQLite 侧的 `busy_timeout=5000`
不是冗余：前者管连接建立阶段，后者管每次语句执行阶段。
