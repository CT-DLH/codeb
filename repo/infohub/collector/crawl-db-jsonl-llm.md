---
title: The mentor-card pipeline end to end: teacher page to crawl.db to JSONL to card to LLM
covers:
  - collector/sites/hitsz/teachers.yaml
  - collector/tools/collect_site.py
  - collector/site_crawl/runner.py
  - scripts/crawl-export.ts
  - scripts/import-jsonl.ts
  - pipelines/mentor-summary-unify.json
  - collector/data/crawl.db
updated: 2026-11-21
---

# 导师卡端到端链路

一页把「教师主页 → crawl.db → JSONL → 卡 → LLM 简介」串起来。各层的逐键细节在别处
（spec 键见 `collector/site-specs`，适配器与缓存见 `collector/site-crawl`，引擎与闸见 `ops/pipelines`），
**本页只讲这条链的接缝与跨层契约**——接缝写错不会报错，只会让数据悄悄错。

## 四段链路

```
collector/sites/hitsz/teachers.yaml          （spec：站点知识，纯 YAML）
        │
        ▼  python collector/tools/collect_site.py --config ... --register
collector/data/crawl.db  teachers 表          （内容缓存，sha1 指纹；与 pipeline.db 独立）
        │
        ▼  npm run crawl:export
inbox/crawl-hitsz-teachers.jsonl              （card_import 吃的行）
        │
        ▼  npm run import:jsonl <jsonl> info_mentor [--write]
cards/info_mentor/*.md                        （卡：frontmatter + 正文小节）
        │
        ▼  npx tsx scripts/batch_llm.ts --config pipelines/mentor-summary-unify.json
inbox/mentor-summary-unify.jsonl → card_import → summary 字段
```

注意最后一段：`mentor-summary-unify.json` **没有 `save_mode`**，引擎默认 `jsonl`，
所以它产出的是一份待导入的 JSONL，**落盘仍要过一遍 `card_import` 预演**，不是直接改卡。

## 第 1 段：抓（spec → crawl.db）

```bash
python collector/tools/collect_site.py --config collector/sites/hitsz/teachers.yaml --json
python collector/tools/collect_site.py --config ... --from-cards info_mentor --json
python collector/tools/collect_site.py --config ... --url <主页URL> --json
```

参数面（`collector/tools/collect_site.py`）：`--config`（必填）/ `--max-pages`（默认 5）/ `--json` /
`--out` / `--check` / `--register` / `--pipeline-db` / `--cache-db` / `--url`（可重复）/
`--from-cards <领域>` / `--only-card`（可重复）。

**`--register` 才写 pipeline.db，不给就是预演，两个库都不碰。** teacher_home 分支的
`run_site.build_site_register` 与列表型的 `build_register` 是两套指纹实现，别假设它们等价。

**teacher_home 不支持 `--out`**：脚本会明确打印「落卡走 `npm run crawl:export` → `card_import`」。
`--out` 导出的只是元数据清单，写成导入行会被误当成可落卡的内容。

无目标时返回 2 并提示：传 `--url` / `--from-cards <领域>`，或确认该领域卡片上有 `ext.homepage`。
`--from-cards` 不给时，`_default_teacher_targets()` 会退到 spec 的 `output.domain` 里所有带主页的卡。

L2 编排在 `collector/site_crawl/runner.py`：

- `run(spec_path, targets, *, dry_run=False, db_path, show_pii=False, register=None, report_dir=None)`
- **`dry_run` 时不构造 Store，完全不碰 crawl.db**（`store = None if dry_run else Store(path)`）
- `_same_person`：`a == b` 或 `long.startswith(short) and long[len(short):].isdigit()`；
  姓名对不上整条拒绝（卡片里的主页链接可能是别人的）
- `_brief`：敏感值默认只给 `has_email` / `has_phone` / `has_address` 布尔，`show_pii=True` 才带值
- 报告落 `collector/data/out/site_<family>_<kind>_last_run.json`，键为
  `scope / dry_run / started_at / finished_at / targets / cache_cold / would_update /
  registered / failed / teachers_total / items / errors`

## 第 2 段：导（crawl.db → JSONL）

```bash
npm run crawl:export                                        # 默认 spec + 默认库
npm run crawl:export -- --db path/to/crawl.db --out inbox/xxx.jsonl
```

`scripts/crawl-export.ts` 的 CLI 只有三个参数：`--config`（默认
`collector/sites/hitsz/teachers.yaml`）、`--db`（默认 `$INFOHUB_CRAWL_DB` 或
`collector/data/crawl.db`）、`--out`（默认 `inbox/crawl-<family>-teachers.jsonl`）。

**它不是纯投影器**，有四段实质逻辑，改行为要改这里而不是 spec：

1. **正文拼装 `buildBody()`**：`## 数据来源`（`- [官方] <source> <url> —— 快照抓取于 <日期>`，
   有则追加「主页更新」「主页浏览量」）→ 按 `output.body_sections` 顺序放各节
   （`科研论文` 渲染成列表、`科研项目` 渲染成 `### 项目名` 块）→ `include_other_sections: true` 时
   把**没点名的小节接在后面**。两个跳过条件：已按正文小标题拆过段的（`split_into` 非空且已有
   结构化清单）、名字里同时含「论文/paper/publication」与「项目/project」的合并小节。
   **`body_sections` 是排序不是白名单**。
2. **字段映射 `buildRecord()`**：按 `output.fields` 的 15 项逐键取，跳过 null / 空串 / 空数组；
   `browse` 转 Number；`flags` 直接透传。
3. **`summary` 兜底**：`record.research || record.describe || '研究方向未在主页披露'`。
   这是**采集期的占位**，后面 LLM 清洗才有真简介。
4. **`_clear` 的精细撤销**（这是最容易被误改的一段）：`clear_fields` 是「允许撤回的字段」清单，
   但**新值为空时不撤**——`browse <= 0` 不撤 `ext.browse_count`、`update_time` 空不撤
   `ext.homepage_updated`、`research/dept/discipline/email/name_en` 任一为空则不撤对应路径。
   理由写在注释里：浏览量为 0 / 主页这次没给，不代表「旧值错了」。
   另外 `summary` 为空或等于 `研究方向未在主页披露` 时，`delete fields.summary` 且
   `clear.delete('summary')`——不拿占位句覆盖卡里已有的真简介。

两个安全阀：`sections` 为空的整条**跳过不导出**（宁可保留旧卡）；正文 < 40 字记 `problems`
并置 `exitCode = 1`（仍是退出码失败，不静默）。

产出行形如：`_src: {file: 'collector/data/crawl.db', row: 'teachers/<slug>'}`、
`_body`、`_replace_sections`（`数据来源` + 实际替换的小节名）、`_clear`（过滤后的数组）。

## 第 3 段：落卡

```bash
npm run import:jsonl inbox/crawl-hitsz-teachers.jsonl info_mentor          # 默认 dry-run
npm run import:jsonl inbox/crawl-hitsz-teachers.jsonl info_mentor --write  # 落盘
```

`scripts/import-jsonl.ts` 是 `card_import` 的命令行 runner（MCP 工具没有命令行入口，
这里起 StdioClientTransport 打 `src/mcp/server.ts`）。参数：
`<jsonl> <domain> [--write] [--merge] [--max-updates N]`。

- 默认 `dry_run: true`，**只有显式 `--write` 才落盘**
- `--merge` → `strategies.on_duplicate: 'merge'`（强标识命中即合并）
- `--max-updates N` → 安全阀
- 报告打印时刻意剥掉 `sample / anomalies / risks / columns / clears` 的明细，只给
  `clears` 计数、`anomalies` 按 `type` 聚合（附首个非 duplicate 样例）、`risks` 前 6 条
  ——数据不进对话上下文是这条通道的设计前提
- 长导入用 `MCP_TIMEOUT_MS=<ms>` 抬高客户端超时

## 第 4 段：LLM 清洗简介

```bash
npx tsx scripts/batch_llm.ts --config pipelines/mentor-summary-unify.json --dry-run   # 抽样
npx tsx scripts/batch_llm.ts --config pipelines/mentor-summary-unify.json --limit 20
npx tsx scripts/batch_llm.ts --config pipelines/mentor-summary-unify.json --only mentor/xxx
```

CLI 只有 `--config` / `--limit N` / `--only id1,id2` / `--dry-run`。
`saveMode = dryRun ? 'jsonl' : config.save_mode ?? 'jsonl'`。

### 当前配置的真实内容（`pipelines/mentor-summary-unify.json`，23 行）

| 键 | 值 |
|---|---|
| domain / target | `info_mentor` / `summary` |
| source_sections | `["个人简介", "研究方向"]` —— **只取两节小品** |
| source_min_chars | 30（材料不足则不请求模型） |
| min_output_chars | 20 |
| allow_superset | true（重写型：新简介包含旧摘要属正常） |
| grounding.corpus_fields | `["ext.dept"]` |
| grounding.terms | 12 项：教授/副教授/助理教授/讲师/博士生导师/硕士生导师/国家级/省部级/院士/特聘/长江学者/杰青/优青 |
| grounding.min_cjk_coverage | 0.45 |
| out | `inbox/mentor-summary-unify.jsonl` |

**它没有** `save_mode` / `max_output_chars` / `require_cjk` / `strip_leading_title` /
`concurrency` / `filter`。所以：产出进 `inbox/` 后再 `card_import`；长度上限只由提示词的
「20~120 字」约束，没有写盘前的硬闸。

### 为什么是这两节

`source: "body"` 会把「科研论文」小节一起塞进去（中位数 2.8 万字），既超预算，又让模型拿
论文列表编简介。小节名不存在时跳过并计数，不把空输入当材料（`readSections()`）。
字数只算小节正文，不算拼上去的 `### 小节名` 标题行（`readSectionsWithSize()`）——
带着标题行判断会把英文材料误判成中文材料（实测误伤 002）。

### 提示词的四条硬约束

1. 只依据材料，**不凭印象补**职称、头衔、年份、学校、项目
2. 保留姓名、院系、研究方向，删掉完整论文书目与项目清单
3. 2~3 句中文，20~120 字，不要「简介：」前缀、引号、代码块、换行
4. 材料 < 30 字或纯占位（「主页未提供个人简介栏目」）→ **返回空字符串**，不强行生成漂亮话

### 写盘前的闸（`scripts/batch_llm.ts` 的 `applyResult`）

所有闸串在同一个函数里，单卡与批量两条路径共用。实测顺序：

```
null/空 保护 → strip_leading_title → 与原值逐字相同 → normalizeSkeleton（只差标点/大小写）
→ join.reject（形状不可能） → join.reject_name_list（像作者名单）
→ max_output_chars → allow_superset（返回里套着原值）
→ allow_language_change（中英文互换） → require_cjk → min_output_chars
→ join.verbatim（须逐字命中关联原文） → grounding.terms → grounding.min_cjk_coverage
```

两个顺序细节：

- **`strip_leading_title` 必须排在「与原值比较」之前**。落盘后卡里存的是去掉姓名的版本，
  后比较的话每次重跑都判成「有改动」，统计与幂等一起失真。
- **`grounding.terms` 只在材料正文是中文时生效**。材料是英文时模型会把
  `Associate Professor` 译成「副教授」，按中文词表核对必然误伤；判定前先剥掉
  `### 小节名` 标题行（`material.replace(/^#{1,6}\s.*$/gm, '')`）。

闸只负责「不写坏」，不负责「写得对」——够长了仍然要人审。

## 跨层契约（写错不报错，只会让数据悄悄错）

| 契约 | 错写后果 |
|---|---|
| `output.domain` 必须 `info_mentor`，不能是旧名 `mentor` | `crawl:export` 照常成功，`import:jsonl` 报「未知领域: mentor」；`--check` 查不出这一层 |
| `output.source`（`哈工大教师主页系统`）是中文显示名，≠ 注册名 `site_hitsz_teacher_home` | 注册进 `pipeline.db.articles.platform` 的必须是注册名，写显示名会让 `queue()` 的 fetchable 过滤把站点行判死 |
| `body_sections` 是**排序**，不是白名单 | 当成白名单读会以为获奖/专利/招生信息丢了，实际由 `include_other_sections` 接在后面 |
| `clear_fields` 是「允许撤回」清单，但新值为空时逐路径例外不撤 | 少一个字段 → 「主页已补上、卡片还是占位」；改掉那段例外逻辑 → 用 0 浏览量和空日期覆盖真值 |
| `crawl.db` 与 `pipeline.db` **两个库** | 混用会让 `cache_cold` 判据失准；`crawl.db` 已降级为内容缓存，`runs` 表只读归档不再写 |
| `email_reverse: true`（主页邮箱倒写 `nc.ude.tih@…`） | 删掉不报错，所有邮箱变成乱序字符串 |

## 三条实测坑

- **`npm run collect:site` 这条 script 是坏的**：`package.json` 里是
  `tsx scripts/mcp-tool.ts collect_site`，而 `mcp-tool.ts` 要两个位置参数。真调用是
  `npx tsx scripts/mcp-tool.ts collect_site inbox/site-args.json`，或直接用
  `python collector/tools/collect_site.py`。
- **`crawl-export.ts` 报错文案指向 `collector/tools/run_site.py`**（第 203 行），
  而 MCP 侧入口是 `collect_site.py`。两个入口并存，别把报错里的名字当成唯一入口。
- **`ext.research` 会混进论文标题连写残片**（甚至拼错成 `Videso`）。模型会忠实抄、
  `grounding` 也放行——因为每个字确实在材料里。遇到「输出荒谬但过闸」，去看上游字段，
  不要调阈值。

## 重跑与幂等

- `crawl:export` 与 `import:jsonl` 都是幂等的：`_src` 相同、字段相同 → 逐字节不变
- `runner.py` 用内容 sha1 判变化（`HASH_EXCLUDE` 排除 browse/seen_at/updated_at/first_seen），
  报 `would_update` 而不是 created/updated/unchanged 三个计数
- `mentor-summary-unify` 重跑要过「与原值相同」闸；改过提示词会让 `batch_llm` 的
  `llm_ts_cache.json` 缓存全失效（键是 `sha256(model \0 prompt \0 text \0 schema)`）
