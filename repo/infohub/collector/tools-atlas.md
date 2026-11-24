---
covers:
  - collector/tools/
updated: 2026-11-17
---

# Collector: the tool scripts

`collector/tools/` 的 py 文件分成两半：**干活的脚本 + 自检脚本**。全部以
`ROOT = Path(__file__).resolve().parent.parent` 然后 `sys.path.insert(0, str(ROOT))`
的方式拿到 `kit` / `site_crawl` / `zhihu_pipe` 三个包——所以它们必须从
`collector/` 目录下跑（`cd collector && python tools/xxx.py`），从仓库根跑会 import 失败。

## 入口脚本（编排，属 L3）

| 文件 | 职责 | 主要参数 |
| :-- | :-- | :-- |
| `collect_site.py` | MCP `collect_site` 的统一落点：按 spec 路径跑列表型（`crawl_column`）或教师主页型（`runner.run`），出 8 字段报告。`--register` 才写 pipeline.db，否则两个库都不碰 | `--config --max-pages --json --out --check --register --pipeline-db --cache-db --url --from-cards --only-card` |
| `run_site.py` | 站点采集入口：读 `sites/<family>/<kind>.yaml`，抓目标并写 crawl.db（`collect_site` 的前身，多了 `--show-pii`） | `--config --url --slug --from-cards --only-card --limit --db --check --dry-run --register --show-pii --json` |
| `run_source.py` | 通用源运行器：搜索 → 查重 → 主题打分 → **只登记元数据**（没有获取腿，补正文归 `enrich_batch`） | `source --query --urls --kind --topic --keywords --no-topic --max --min-heat --expand-authors --max-authors --authors --delay --cursor` |
| `run_keyword.py` | 一键关键词流水线：搜索 → 查重 → 筛选 → 抓正文 → 总结 → 报告（`run_nightly` 的薄壳） | `keyword --max --limit-fetch --keywords --backend --delay --no-summary` |
| `run_nightly.py` | 夜间深挖：主题搜索 → 顺着命中作者铺开 → 抓正文（读过的复用）→ LLM 总结 → 清单 | `keyword --keywords --max --max-authors --no-expand --limit-fetch --deep --refresh --backend --llm-interval --no-summary` |
| `run_target.py` | 单作者定点采集，默认作者 `haochizhang`、主题「数学竞赛」（历史遗留的演示入口） | `--author --topic --keywords --max --no-answers --deep --delay` |
| `run_session.py` | 限时会话：先跑指定任务，没到点就按权重随机补活（预算 / 熔断 / 主题池） | `--until --budget --topics --pace --max-new-bodies --max-llm --rescreen-limit --exclude-source` |
| `run_research.py` | **最大的一个**：给宽主题自动一轮轮搜下去 → 证据逐字校验 → 大纲 → 报告，直到能写出有据可查的东西 | `name topic --stage --rounds --per-round --docs-per-query --docs-total --evidence-per-doc --sources --follow` |
| `run_survey.py` | 通用调研：一份「实体清单」→ 每个实体查到官网 → 抓正文 → 复用已有平台源 → 出 md/jsonl 报告 | `name --stage --per-item --limit --only --force --list-file` |
| `run_refs.py` | 引用队列入口：卡片里的论文题录 → 文法/LLM 解析 → 可采集 URL → 交给现成流水线 | `--stage --slug --from-cards --section --papers --from-llm --db --limit --apply-limit --apply-source --providers --out --no-cache` |
| `crawl_long.py` | 长跑编排器：按主题优先级轮转**登记**，自带限流、退避与进度日志（`THROTTLE_HINTS` 命中即退避） | `--profile --hours --gap --max --offset --round-timeout --expand-every --max-authors --phase1-ratio --only --seed --log --run-id` |
| `crawl_course.py` | 课程主题驱动的学术长跑：按讲义主题去 arXiv / CNKI 取论文，跑固定时长 | `--minutes --sources --allow-login-sources --max-per-topic --batch --backend --dry-run --sleep` |
| `paper_pipeline.py` | 论文流水线：查找 → 取题录与摘要 → LLM 总结 → 落卡 | `--per-round --rounds --max-minutes --backend --delay --no-summarize --dry-run` |
| `idle_papers.py` | LLM 空闲时给论文正文补总结（「论文内容 → LLM 摘要 → paper 卡」的第一环），靠 `data/llm_busy.json` 避让 | `--batch --max-minutes --loop --poll --dry-run --redo-extract --llm-interval --redo-sample` |
| `summarize_platform.py` | 按平台总结（两段式的第二段独立入口，不走 `zhihu_pipe` 的摘要路径） | `platform --backend --limit --llm-interval --data-dir` |

## 补正文与出链（获取腿）

| 文件 | 职责 | 主要参数 |
| :-- | :-- | :-- |
| `enrich_batch.py` | **M3 起唯一抓正文的实现**：把「只有元数据」变成「有正文」，可按源/URL 文件/plan 跑 | `--plan --source --urls --result --limit --backend --llm-interval --no-summary --two-stage --one-stage --summary-limit --no-fulltext --no-audience --delay` |
| `enrich_queue.py` | 获取流水线的**候选裁决**：这张卡还能不能再补正文只在这里判一次（`Store.queue()` 的唯一调用方） | `--candidates --db --limit --platform --retry --mark --json-out` |
| `fetch_fulltext.py` | 给只有摘要/题录的论文补抓**开放获取全文**（按 `fulltext.yaml` 白名单，幂等可分批） | `--db --data-dir --source --limit --offset --dry-run --no-oa --backend --json` |
| `dump_urls.py` | 把库里某个源已登记的链接导成 `urls.txt`（给 `enrich_batch` / `collect:export` 吃） | `source --all --out --db --status --full` |
| `paper_urls.py` | paper 卡 → 采集器能吃的链接清单 | `--domain --status --skip-summarized --limit --out` |
| `papers_to_cards.py` | LLM 题录 jsonl → paper 领域卡片的导入行（一行一实体，按标题去重） | `--inp --out --status` |

## 卡片与领域加工

| 文件 | 职责 | 主要参数 |
| :-- | :-- | :-- |
| `tag_cards.py` | 给卡片打内容标签（细粒度方向：目标检测 / 机器翻译 / 图神经网络…） | `--domain --limit --batch --retag --out --dry-run` |
| `survey_cards.py` | 名单 × 采集库 → 两份待落卡 jsonl（竞赛实体卡 + 带主题的采集卡），`assign()` 负责归属 | `name --list-file --articles --outdir` |
| `llm_projects.py` | 把卡片某一节的项目清单抽成结构化 jsonl（LLM，通用，不写文法） | `--domain --section --card --limit --out --no-cache --quiet --json` |
| `llm_compare.py` | 阶段 0：LLM 抽取层与现有文法的并排对照，只产 jsonl、不写任何卡 | `--domain --section --slug --card --limit --out --json --no-cache --show --quiet` |
| `lookup_papers.py` | paper 卡 → 查找（Crossref / arXiv）→ 回填 jsonl（带 `lookups` 缓存） | `--domain --status --limit --delay --providers --lookup-db --no-cache --out --dry-run --json` |
| `lookup_cnki.py` | 收尾 `ext.lookup_status=待知网` 的 paper 卡：知网搜同名论文，命中才回填链接与题录 | `--domain --status --limit --out --max-results --dry-run --no-resume --json` |

## 诊断与探测（发请求前先看清现场）

| 文件 | 职责 | 主要参数 |
| :-- | :-- | :-- |
| `site_probe.py` | 抓一次列表页，出「选择器命中 / 翻页候选 / 附件」诊断报告；`--check` 只校验 spec 不发请求 | `--url --config --check --json --max-candidates --delay` |
| `probe_cnki_state.py` | 采一条知网页面样本：正文长度、文案位置、验证控件的几何与可见性 | 无参数 |
| `probe_cookies.py` | 只读探测本机浏览器里是否存了知乎 cookie（**不解密、不输出值**） | 无参数 |
| `probe_public.py` | 免登录状态下哪些数据接口还能用 | 无参数 |
| `measure_grammar.py` | 逐条文法在真实采集数据上的覆盖度量（**不调网络**） | `--db --show --merge --limit` |
| `verify_zhihu_urls.py` | 知乎专栏 URL 修复的终验汇总（只读，不改任何东西） | 无参数 |
| `capabilities.py` | 导出/校验能力清单 `capabilities.json`：`--check` 与现算不一致退 1，`--write` 落盘 | `--out --write --check` |

## 登录态与凭据

| 文件 | 职责 | 主要参数 |
| :-- | :-- | :-- |
| `browser_login.py` | 一次性浏览器引导：过滑块 / 扫码登录，把登录态留在持久化 profile 里 | `source --url --wait --keep-open` |
| `grab_cookie.py` | 开浏览器登录一次，把 Cookie **直接写回项目配置**（重跑即续期） | `platform --wait --keep-open --list` |
| `ingest_curl.py` | 把浏览器复制的 cURL 解析成 zhihu-cli 的 profile；`_SKIP_HEADERS` 剔掉 `x-zse-93`/`x-zse-96`/`x-zst-81` | 位置参数（文件路径或 `-` 读 stdin），无 argparse |

## 一次性回填与迁移（都可 `--apply` 预演）

| 文件 | 职责 | 主要参数 |
| :-- | :-- | :-- |
| `backfill_fidelity.py` | 回填 `articles.fidelity`，让「有没有正文」不再是空串 | `--data-dir --apply` |
| `backfill_platform.py` | 回填 `articles.platform`：把「这行属于哪个源插件」变成库里的一列 | `--db --apply --sample` |
| `backfill_summary_backend.py` | 回填 `articles.summary_backend`（llm / extract / unknown，**不猜**） | `--data-dir --apply --sample` |
| `migrate_zhihu_urls.py` | 把库里 `www.zhihu.com/p/<id>` 的软 404 专栏链接改写成 `zhuanlan.zhihu.com/p/<id>` | `--apply --cards` |
| `migrate_zhihu_card_urls.py` | 同上，但目标是卡片正文/frontmatter | `--apply` |
| `fix_zhihu_raw_urls.py` | 补迁：正文文件 frontmatter 里残留的专栏软 404 链接 | `--apply` |

三个 `migrate_*` / `fix_*` 必须**按顺序**跑（库 → raw → 卡片），否则终验
`verify_zhihu_urls.py` 会报残留——README 里那条三步命令就是为此。

## 自检（绝大多数离线）

`selftest.py` 是唯一的端到端例（热榜 → 查重 → 落盘 → 总结 → 再跑跳过），
它会真的打知乎；其余是单点分层自检，绝大多数不联网。
断言条数、退出码与「哪一类红是真的」见 `infohub/collector/selftests` 那一页，
这里只给「测什么」：

| 文件 | 测什么 |
| :-- | :-- |
| `selftest.py` | 端到端：免登录热榜跑通整条流水线，再跑一遍证明终态被跳过 |
| `selftest_kit.py` | P1 纯搬家等价：转发层与 `kit` 必须拿到**同一个对象**（逐名 `is` 比较） |
| `selftest_blob.py` | 字节能不能活着出来、类型怎么判、抽不出时点谁的名 |
| `selftest_paging.py` | 用假站点证明「200 不等于有下一页」 |
| `selftest_robots.py` | robots 闸只有一份，且被拒时必须说清「被谁拒的」 |
| `selftest_throttle.py` | P1 遗留 8 处限速「逐源接入」的节奏等价（假时钟） |
| `selftest_store` 无此文件 | `kit/store.py` 的三条固定姿势与迁移幂等性由 `selftest_kit.py` 的第 3 段覆盖 |
| `selftest_column.py` | P2c 端到端：只写一份 spec，L1 的 blob / paging 真被组合起来 |
| `selftest_site.py` | 站点源侧：`Document.extra` 与 `SiteSource` 两条裁决 |
| `selftest_probe.py` | `site_probe` 报告里的数字在正确作用域里数、软 404 被排除 |
| `selftest_register.py` | 登记/缓存/队列侧：crawl.db 降级为内容缓存、pipeline.db 登记、P5 热度归一分 |
| `selftest_queue.py` | 状态机、获取队列、能力清单、摘要后端真值（M1 判据收口） |
| `selftest_plugin.py` | 插件契约：用一个假源证明「接新平台只是加一个文件」 |
| `selftest_query_guide.py` | `query_guide` 六字段契约与检索词语法 |
| `selftest_llm.py` | LLM 抽取层（不联网、不烧 token） |
| `selftest_refs.py` | 引用文法：真实主页的六种写法 + 三类该被门禁挡掉的行 |
| `selftest_two_stage.py` | 两段式与总结段的范围 |
| `selftest_filename.py` | 摘要文件名 `MAX_PATH`（`FILENAME_BUDGET = 120`） |
| `selftest_fulltext.py` | 开放获取全文链路：白名单、文本清洗、出链规范、摘要取材口径 |
| `selftest_session.py` | 限时会话器：预算解析与跨天顺延、主题池、见底报 0、文件名确定性 |
| `selftest_research.py` | 深度调研流水线（不联网、不调 LLM、不碰真实状态） |
| `selftest_audience.py` | B 站评论/弹幕加工层（不联网、不调 LLM） |
| `selftest_academic.py` | 学术源：真实结构的假响应验证解析 |
| `selftest_bilibili.py` | B 站插件：搬过来的签名与字幕链路（配 cookie 时会抽查真实字幕） |
| `selftest_xhs.py` | 小红书插件：假页面验证解析（`BROWSER_SMOKE=1` 才跑真浏览器 DOM） |
| `selftest_cnki.py` | 知网：URL 身份、日期/计数解析、字段翻译、完整度口径、能力边界 |
| `selftest_browser.py` | 共享浏览器层：验证码判定、可选依赖、Cookie 解析、单例 |
| `selftest_web.py` | web 插件：假页面验证解析、身份与两条判据 |
| `selftest_grab_cookie.py` | `grab_cookie.py`（不开浏览器、不联网、不碰真实 `.env`） |

## 改动一个工具前先看的三条

1. **`run_source.py` 没有获取腿**。它只登记元数据；所有抓正文都走 `enrich_batch.py`。
   `collector-python-test.ts` 有一条断言专门查这个：`build_argv('zhihu', ...)` 拼出的
   命令行里**不许出现** `--stage` / `--limit-fetch` / `--backend`。
2. **`collect_site.py` 的 `platform` 必须写注册名** `site_<family>_<kind>`，
   不能写 spec 的 `output.source`（如 `hitsz_column`）。`Store.queue()` 的
   `fetchable` 过滤按 `capability_report()` 的注册名取集合，写错会把站点行判死、
   永远补不到正文。
3. **一次性脚本都要 `--apply` 才写**。没有 `--apply` 时全部只打印将要改多少行；
   写库/写文件的脚本（`migrate_*` / `backfill_*` / `fix_*`）都遵守这条，
   所以试跑是默认安全的。

## 工具之间的隐式契约

- **`capabilities.py` 的输出必须逐字节稳定**：它不带时间戳，`--check` 和
  「重生成后 git diff 干净」这条回归断言才有意义。动态声明能力的插件
  （cnki 看登录态、bilibili 看接口可用性）按默认实例化路径取值，
  所以 `probe=ok` 只代表「这次问到了」，不代表运行时永远如此。
- **`enrich_queue.py --mark` 是唯一允许改状态的补正文入口**，其他脚本要改状态
  必须走它或 `Store.mark_*`，否则队列判据会分叉。
- **`run_session.py` 通过子进程调 `run_source.py`**（`_run` 返回退出码，
  `1 = 本源暂时不可用`），所以本源熔断是**跨进程**的：它靠退出码而不是异常传播。
- `crawl_long.py` 的 `THROTTLE_HINTS = ("暂时不可用", "配额", "限流", "风控", "403", "429", "database is locked")`
  是**字符串匹配**子进程输出后决定退避——改子进程的失败话术会直接让退避失效。
