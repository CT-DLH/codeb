---
covers:
  - collector/kit/
  - collector/zhihu_pipe/html_text.py
  - collector/site_crawl/http.py
  - collector/site_crawl/text.py
---

# Collector: L1 primitives

五个原语，每个都对应一个**真实踩过的坑**。这里的规则之所以写得这么细，是因为违反它们的写法更自然。

## Paging: judge by new-item count only

**铁律**：候选页的条目集合相对当前页的**新增条目数 > 0** 才算翻页成功。
返回 200、条目数相同、甚至条目数变多但全是旧条目——**都不算**。

实测（哈工大研究生院通知栏目）：第 1 页 20 条，`list2.htm` 也返回 20 条且**全部重合**，
`?page=2` 同样。这就是**软 404**：返回 200，内容其实是同一页。

**违反的后果不是崩溃，而是静默的低效**：程序会一页页翻下去，每页都是同样 20 条，
不报错不超时，报告写「翻页 12 页、共 240 条」。去重在下游发生，所以**卡片数是对的**，
但没有任何一处能解释「为什么这个站耗时是别的站的 12 倍」。

问题被藏进了性能数字里——这是最难发现的一类 bug。

**候选从哪来**（L1 通用猜测，不含任何站点知识）：
`<a rel="next">` → 锚文本 `下一页|下页|后一页|Next|›|»|>` → `?page=N` → `list{N}.htm` → `index_{N}.html`。

锚文本用**精确匹配加页码后缀**，不用「包含」——否则正文里的行内链接「下一页的说明」会被误抓成翻页控件。

原因码设计（第二个返回值）：`soft_404` / `no_candidate` / `probe_limit` / `fetch_failed` /
`parse_empty` / `current_failed`。空串表示找到了。区分这些码是为了让报告能说清「为什么没翻下去」。

## HTTP: throttle per host, not per site

`kit/http.py` 负责限速、重试、编码嗅探、UA、cookie（从 env 读）、robots 硬闸。

关键设计：**限速按 host 而不是按站点名**。同一个站点有多个域名、多个站点共用一个 host 时，
按站点名限速会漏。

`robots` 是**硬闸**，不是建议——它在 L1，所以任何 L2 站点都无法绕过。

## Body extraction: density scoring, not selectors

`kit/html.py` 的 `density_extract` 用文本密度打分抽正文，对所有站点同构。

**为什么不用选择器**：栏目通知页的正文版式各异且会改版，选择器一改就全废。
密度打分不依赖版式，代价是偶尔抽不干净（这时才需要站点 adapter）。

`kit/blob.py` 处理非 HTML 字节：下载、类型嗅探、**四级降级抽文**（pdf → docx → 纯文本 → 失败）。
`MAX_BLOB_BYTES` 是硬上限，防止一个超大附件吃满内存。

## store: a single sqlite base

`kit/store.py` 只有 68 行，但定了三件事：

- **WAL 模式**：读写不互相阻塞，采集与导出可以同时进行。
- `busy_timeout = 5000`：并发写时等待而不是立刻报 `database is locked`。
- `user_version` 做轻量迁移：版本号存在 sqlite 自己的元数据里，不用额外的迁移表。

**红线：`collector/` 不许出现第二套状态库。** 出现即说明这条约束没守住。

## Why these comments repeat the failure mode

`paging.py` 的注释里有这么一句逻辑：**「200 就算成功」是最自然也最错的写法，
下一个人接手时一定会那样写。他可能不读文档，但会读函数的第一个注释块。**

所以关键约束写在**函数的第一个注释块**里，而不是散在 `docs/`。
文档会被跳过，紧挨着代码的注释不会。

## Self-tests per primitive

每个原语都有对应的 `selftest_*.py`（`selftest_kit` / `selftest_blob` / `selftest_paging` /
`selftest_robots` / `selftest_throttle`），共 30+ 个，全部**不联网**。

`selftest_paging` 里有个刻意的设计：关掉通用形状兜底后，`no_candidate` 分支才可达。
否则 `?page=2` 总能拼出来，那个分支**永远跑不到，也就永远没人验证过它**。
