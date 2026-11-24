---
covers:
  - src/mcp/tools/
updated: 2026-11-17
---

# MCP tools: full reference

工具全部在 `src/mcp/tools/*.ts`，每个文件导出 `registerXxx(server)`，`src/mcp/server.ts` 逐个调用。
本页只写**契约**：入参名、类型、默认值、返回键、错误条件。看代码前先读这页能省掉一轮试错。

## How a tool is registered

```ts
server.registerTool('card_read', {
  title: '读取信息卡',                 // 显示名，客户端 UI 用
  description: '...',                  // 给模型看的说明书，写清默认值与副作用
  inputSchema: { card_id: z.string().describe('卡片 ID') }  // 裸 zod shape，不是 z.object
}, async (args) => ({ content: [{ type: 'text', text }] }));
```

`inputSchema` 是**裸 shape**（`{ key: ZodType }`），SDK 负责 normalize 成 object schema。
工具有 `outputSchema` 的一个都没有，所以 `structuredContent` 从不出现——**所有返回值都是一个 `text` 块里的 JSON 字符串**，
调用方必须自己 `JSON.parse`。这是最容易踩的第一处。

## Two response dialects, and why it matters

返回体没有统一外壳，实测分三种：

| 方言 | 出现的工具 | 判别方式 |
| :-- | :-- | :-- |
| `{ok: true, ...}` | `card_create` / `card_import` / `card_batch` / `card_attach` / `card_derive` / `collect_run` / `collect_site` / `collect_guide` / `file_read` | 有 `ok` 键 |
| 裸对象（无 `ok`） | `card_read` / `card_search` / `card_list` / `card_list_domains` / `card_schema` / `card_find_similar` / `card_append` / `card_update` / `card_commit` / `card_conflicts` / `card_resolve` / `card_delete` / `domain_create` / `domain_update` | 没有 `ok` |
| 裸字符串（不是 JSON） | `llm_process` 成功时返回模型原文 | `JSON.parse` 会抛 |

**不要写「检查 ok 字段」的统一封装**：一半工具没有这个字段。判断成败用 `res.isError`（见 `infohub/mcp/error-taxonomy`）。

## Read-side tools

### card_read — one card, plus the version hash you need for updates

| 参数 | 类型 | 必填 | 默认 |
| :-- | :-- | :-- | :-- |
| `card_id` | string | ✓ | — |

返回 `{card_id, domain, frontmatter, body, _base_revision}`。
`_base_revision` = 整份文件（frontmatter + 正文）的 sha256 前 16 位，`card_update` 必须带它。
卡片不存在 → `isError: true`，text 是纯文本 `未找到卡片: <id>`（**不是 JSON**，别去 parse）。

`findCardFile()` 是全仓库线性扫描（`listCardFiles()` → 逐文件 `readCardFile` 比对 `card_id`），
没有索引。单次 `card_read` 要遍历全部文件——这就是 `card_list` 存在的原因。

### card_search — substring match over title / summary / body

| 参数 | 类型 | 必填 | 默认 |
| :-- | :-- | :-- | :-- |
| `query` | string | ✓ | — |
| `domain` | string | | 全部领域 |
| `confidence` | `'A'\|'B'\|'C'\|'D'` | | 不过滤 |

匹配是 `haystack.toLowerCase().includes(query.trim().toLowerCase())`，`haystack = title + summary + body`。
**不是分词、不是模糊**：中文里少一个字就查不到，且 `query` 为空串时 `if (q && ...)` 短路 → 返回全部卡片（无分页）。
返回 `{count, results[]}`，每条只有 `card_id/domain/title/summary/confidence/status`，**不带正文**。

### card_list — paged browse, optional body

| 参数 | 类型 | 必填 | 默认 | 边界 |
| :-- | :-- | :-- | :-- | :-- |
| `domain` | string | | 全部 | 非法领域 → isError |
| `status` | string | | 不过滤 | 精确相等，如 `冲突` |
| `confidence` | `'A'\|'B'\|'C'\|'D'` | | 不过滤 | |
| `limit` | int | | `50` | 1..200 |
| `offset` | int | | `0` | ≥0 |
| `filter` | record\<string,string\> | | — | 键是点号路径 `ext.mentors` |
| `with_body` | bool | | `false` | 不传时连分支都不进 |
| `body_limit` | int | | `6000` | 100..20000 |

`filter` 的语义是**宽松的精确**：数组字段用 `val.includes(v)`（成员相等），标量用 `String(val) === v`。
路径取不到（`undefined`/`null`）直接判不匹配，**不报错**。
排序：`last_verified` 倒序，同值按 `card_id` 升序；过滤后才排序、才切片，所以 `total` 是**过滤后**的总数。

`with_body` 打开时每行额外带 `body`（超 `body_limit` 截断并附 `…（已截断，原 N 字）`）、`body_truncated`、`body_chars`。
这是「一次调用取回一整个主题的章节正文交给模型整合」的入口——8 张章节卡 1 次调用 11692 字，逐张 `card_read` 要 9 次。

### card_list_domains — discovery, no parameters

无入参。返回 `{count, domains[]}`，每个领域含 `id/name/object_types/summary_columns/dedup_key/identity/attachments/imports/ext_fields`。
`ext_fields` 每项只回 `label/type/required` + 可选的 `format/order/group/deprecated/sensitive`——
**比 `card_schema` 少**：这里没有 `enum`、没有嵌套 `item`/`fields`、没有 `derive`。要写卡就查 `card_schema`。

`listDomainIds()` 已排除 `_` 开头的包与 `abstract: true` 的父包，所以抽象包在这里看不到。

### card_schema — the full field contract

| 参数 | 类型 | 必填 |
| :-- | :-- | :-- |
| `domain` | string | ✓ |

返回 `describeDomainSchema()` 的结果：`domain/name/object_types/note/server_generated_fields/identity/dedup_key/attachments/imports/fields/summary_columns`。
`fields` 是 `{...baseFields, ext: {type:'object', fields:{...}}}`，每项由 `describe()` 递归展开，保留
`type/required/enum/label/format/order/group/placeholder/deprecated/server_generated/sensitive/derive/filterable/value_labels`，
`array` 带 `item`、`object` 带 `fields`。

两处容易误读：

- `required` 的判定是 `s.required !== false`——**没写 required 就算必填**。`_base` 里除 `title/domain/collected_at` 外都显式写了 `required: false`。
- `server_generated_fields` 固定包含 `card_id/domain/object_type`，再加上领域包里标 `server_generated: true` 的（`created_at`/`edited_at`）。这些**不该由调用方填**。
- `identity.warning` 只在标识位同时出现在 `summary_columns` 时出现（列表页会重复展示）。

### card_find_similar — deterministic dedup probe

| 参数 | 类型 | 必填 | 默认 |
| :-- | :-- | :-- | :-- |
| `domain` | string | | 全部领域（建议传，否则跨域命中） |
| `title` | string | | — |
| `aliases` | string[] | | — |
| `source_ref` | string | | — |
| `fields` | record\<string,any\> | | — |
| `limit` | int | | `5`，1..20 |

`title/aliases/source_ref/fields` 至少给一个，否则 `isError`。
返回 `{query, count, high_similarity, candidates[], suggestion}`；`candidates[]` 每项
`{card_id, domain, title, summary?, source_ref?, score, matched_by, matches[]}`，`score` 保留两位小数。
打分与阈值见 `infohub/mcp/lib-internals`。

## Write-side tools (detail lives in write-tool-relations)

### card_create — validate, dedup-warn, write

| 参数 | 类型 | 必填 | 默认 |
| :-- | :-- | :-- | :-- |
| `domain` | string | ✓ | — |
| `object_type` | string | | — |
| `fields` | record\<string,any\> | ✓ | — |
| `body` | string | | `''` |
| `body_file` | string | | — |
| `card_id` | string | | 由 identity 生成 |
| `dry_run` | bool | | `false` |

`fields.body`（如果调用方把它塞进 fields）会被**移出 frontmatter 当正文**，不是报错。
`body_file` 相对项目根或绝对路径，读失败 → `isError`；给了 `body_file` 就覆盖 `body`。
`prepareCard()` 补 `collected_at = 今天`、按 `identity.card_id_pattern` 生成 `card_id`，并跑一次 `findSimilarCards`。
返回 `{ok:true, card_id, file, _base_revision, duplicate_warning?}`；`dry_run` 时返回 `{ok:true, dry_run:true, valid:true, card_id, frontmatter, duplicate_warning?}`。

**校验失败 + `dry_run:true` 返回 `ok:true, valid:false`**（不是 isError）；不带 `dry_run` 才回 `isError`。

### card_append — add text to a section, never touch frontmatter

| 参数 | 类型 | 必填 | 默认 |
| :-- | :-- | :-- | :-- |
| `card_id` | string | ✓ | — |
| `section` | string | | 正文末尾 |
| `text` | string | ✓ | — |

返回 `{card_id, section, appended, _base_revision}`。`section` 省略时是 `body.trimEnd() + '\n\n' + text`，
不会加标题；给了 `section` 走 `appendToSection`（小节不存在则新建 `## section`）。
**不读 `_base_revision`、不检测漂移**——这是采集场景的「挂上去就行」，代价是并发追加会互相覆盖（后写的赢，无提示）。

### card_update — stage, never write

| 参数 | 类型 | 必填 |
| :-- | :-- | :-- |
| `card_id` | string | ✓ |
| `_base_revision` | string | ✓ |
| `changes` | record\<string,any\> | ✓ |

`changes` 先过 `expandDotPaths()`（`ext.a.b` → 嵌套），再过 `validatePartial()`（逐键校验，未声明即报错）。
返回 `{pending_id, staged:true, message}`。落盘在 `.staging/<card_id>/<pending_id>.json`，**不碰卡片文件**。
`_base_revision` 在这里只被**记录**，不比对——漂移检测发生在 commit。

### card_commit — compare revision, write or conflict

| 参数 | 类型 | 必填 |
| :-- | :-- | :-- |
| `pending_id` | string | ✓ |

一致 → 写盘，返回 `{committed:true, card_id, revision, draft_content}`（`draft_content` 是完整文件原文）。
不一致 → 建 `.conflicts/<card_id>/<conflict_id>.json`，返回 `{committed:false, conflict:true, conflict_id, message}`，
**源文件不动，且 `isError` 为 false**。两种路径都会删掉暂存记录。

### card_import — file-driven bulk load

| 参数 | 类型 | 必填 | 默认 | 说明 |
| :-- | :-- | :-- | :-- | :-- |
| `file_path` | string | ✓ | — | `.xlsx/.xls/.csv/.tsv/.jsonl/.md/.pdf` |
| `domain` | string | ✓ | — | |
| `object_type` | string | | — | 须在领域 `object_types` 内 |
| `sheet` | string | | 第一页 | |
| `header_row` | int | | `1` | 1 起 |
| `title_template` | string | | — | `{ext.name}` 取映射值，`{列名}` 取原始单元格 |
| `column_map` | record\<string, string\|string[]\> | | jsonl 按「键即路径」 | 保留目标 `_body/_src/_review/_ignore` |
| `defaults` | record | | — | 只补空字段 |
| `strategies` | object | | 见下 | `empty_title/on_duplicate/merge_rule/on_claim/on_invalid` |
| `row_overrides` | record\<行号, record\> | | — | 展示行号 → `{路径: 值}` |
| `max_updates` | int | | `20` | 只数「改动已有卡片」 |
| `limit` | int | | — | 只处理前 N 行 |
| `resume_from_row` | int | | — | 从该展示行号起 |
| `source_label` | string | | 文件名 | 进 `sources.file` |
| `dry_run` | bool | | `true` | **默认预演** |

`strategies` 默认值：`empty_title=placeholder`、`on_duplicate=keep_both`、`merge_rule=fill_empty`、
`on_claim=merge`、`on_invalid=quarantine`。优先级：显式参数 > 领域包 `imports.strategies` > 全局默认，
报告里的 `strategies` 字段显示**实际生效值**。

三个前置拒绝：领域不存在；`object_type` 不在白名单；**领域既无 `identity` 又无 `dedup_key`**（会不断新建重复卡）。
返回 `ImportReport` + `hints[]`，`ok` 为 false 时同时置 `isError`。

### card_attach — hang attachments onto existing cards

| 参数 | 类型 | 必填 | 默认 |
| :-- | :-- | :-- | :-- |
| `source_dir` | string | ✓ | — |
| `domain` | string | ✓ | — |
| `parser` | string | | 按候选顺序自动选 |
| `match_by` | string[] | | 领域 `attachments.match_by` → `identity.weak` |
| `on_missing` | `quarantine`\|`skip` | | `quarantine` |
| `on_ambiguous` | `review`\|`skip` | | `review` |
| `max_updates` | int | | `20` |
| `dry_run` | bool | | `true` |

领域没声明 `attachments` → 直接 `isError`。`source_dir` 必须是目录（单文件请用 `card_append`）。
`parser` 可选 `task-book / course-syllabus / pdf-text / generic-docx`；`SUPPORTED_EXT` 只有 `.docx` 和 `.pdf`。
返回 `AttachReport`：`scanned/parsed/matched/ambiguous/missing/duplicate/parse_error/unsupported/cards_to_write/attached/aborted/details/details_truncated/quarantine_file/hints`。
`report.aborted` 非空时置 `isError`（安全阀中止，一个文件都没写）。

### card_batch — multiples ops in one call

| 参数 | 类型 | 必填 | 默认 |
| :-- | :-- | :-- | :-- |
| `ops` | record[] | | — |
| `ops_file` | string | | — |
| `stop_on_error` | bool | | `true` |
| `response_mode` | `minimal`\|`full` | | `minimal` |
| `dry_run` | bool | | `false` |

`ops` 与 `ops_file` 二选一（同时给时 `ops_file` 优先）。每条 op 的可用键：
`op`（必填，`create/append/update/delete`）、`domain`、`object_type`、`fields`、`body`、`body_file`、
`text`、`text_file`、`section`、`changes`、`card_id`、`ref`、`as`、`note`。
语义细节见 `infohub/mcp/write-tool-relations`。

### card_delete — move to trash, never unlink

| 参数 | 类型 | 必填 |
| :-- | :-- | :-- |
| `card_id` | string | ✓ |

返回 `{deleted:true, card_id, trashed_to}`，目标 `.trash/<card_id>/<ISO 时间戳>-<文件名>`。
不做物理删除，也不清 `.staging`/`.conflicts` 里该卡的遗留记录（孤儿会一直留着）。

### card_conflicts — list pending conflicts

| 参数 | 类型 | 必填 |
| :-- | :-- | :-- |
| `card_id` | string | 否（不传列全部） |

返回 `{count, conflicts[]}`，每条含 `conflict_id/card_id/_base_revision/current_revision/current_content/draft_content/created_at`。
**两整份文件内容都回传**，一个字段都没省的合并判断交给你；损坏的 JSON 静默跳过。

### card_resolve — apply a decision

| 参数 | 类型 | 必填 | 默认 |
| :-- | :-- | :-- | :-- |
| `conflict_id` | string | ✓ | — |
| `resolution` | `'draft'\|'current'\|'merged'` | ✓ | — |
| `merged_content` | string | `merged` 时必填 | — |

`draft` → 写 `draft_content`；`merged` → 写 `merged_content`；`current` → **什么都不写**（`revision: null`），只删冲突记录。
返回 `{resolved:true, resolution, card_id, revision}`。不调用任何 LLM，不做三方合并。

### card_derive — replay domain derive rules over existing cards

| 参数 | 类型 | 必填 | 默认 |
| :-- | :-- | :-- | :-- |
| `domain` | string | ✓ | — |
| `fields` | string[] | | 领域包全部规则 |
| `mode` | `fill_empty`\|`overwrite` | | 规则自己的 `mode`，再退 `fill_empty` |
| `card_ids` | string[] | | 该领域全部卡片 |
| `max_updates` | int | | `20` |
| `dry_run` | bool | | `true` |

领域没有任何 `derive` 规则 → `isError`（提示用 `domain_update update_ext_fields` 加规则）。
`fields` 里出现没声明规则的路径 → `isError`，并列出本领域真正的派生字段。
返回逐规则统计 `rules[]`：`path/from/pattern/mode/sensitive/filled/no_source/no_match/kept_existing/samples[]`。
`sensitive` 字段的 `samples` 只给形状（`12…3（18 位）`），≤4 位给 `N 位`。
计划改动数 > `max_updates` 且 `dry_run:false` → `isError` + `aborted:true`，**一张都不写**。
`card_ids` 用文件名后缀 `endsWith('<id>.md')` 匹配，`card_id` 含同名后缀时会误中多张。

## Domain and file tools

### domain_create

| 参数 | 类型 | 必填 | 默认 |
| :-- | :-- | :-- | :-- |
| `domain_id` | string | ✓ | —（`/^[a-z0-9][a-z0-9_-]{0,63}$/`，不能是 `base`） |
| `name` | string | ✓ | — |
| `object_types` | string[] | | —（非 abstract 不能为空） |
| `ext_fields` | record\<string,any\> | ✓ | —（可为 `{}`） |
| `summary_columns` | string[] | | `['title','summary','last_verified']` |
| `dedup_key` | string[] | | — |
| `identity` | object | | — |
| `extends` | string | | `_base` |
| `overwrite` | bool | | `false` |
| `abstract` | bool | | `false` |

详见 `infohub/mcp/domain-pack-api`。

### domain_update — PATCH

12 个可选键，全不传时 `isError`（「没有要修改的内容」）：
`domain_id`(必填) + `extends/add_object_types/remove_object_types/add_ext_fields/update_ext_fields/remove_ext_fields/summary_columns/dedup_key/identity/attachments/imports`。

### file_read — preview tables, page text

| 参数 | 类型 | 必填 | 默认 | 边界 |
| :-- | :-- | :-- | :-- | :-- |
| `file_path` | string | ✓ | — | 相对项目根或绝对 |
| `mode` | `auto`\|`preview`\|`text` | | `auto` | |
| `sheet` | string | | 第一页 | |
| `header_row` | int | | `1` | |
| `rows` | int | | `5` | ≤50 |
| `start_line` | int | | `1` | text 模式 |
| `lines` | int | | `80` | ≤500 |
| `max_cell` | int | | `60` | |

`mode=auto` 时按 `detectFormat()` 分流：认得表格格式走 preview，否则走 text。`mode=preview` 但格式不认 → 走 `parseTableFile` 抛错，`isError` 并提示改用 `mode=text`。
preview 返回 `total_rows/columns/header_row/column_profile[]/first_row_line/rows/truncated/hint`，
`column_profile` 每列 `{column, filled, of, type, samples[≤2], risk?}`；
`type` 取值 `empty/integer/number/string-number/date/enum/mixed/text`，
`string-number` 专指前导零或 ≥16 位数字（按数字处理会丢零/丢精度）。
text 返回 `total_lines/bytes/start_line/end_line/truncated/lines[]`（`lines` 是原始行数组，不是 JSON 对象）。

## LLM and collector tools

### llm_process — one-shot model call

| 参数 | 类型 | 必填 |
| :-- | :-- | :-- |
| `prompt` | string | ✓（作为 system message） |
| `text` | string | ✓（作为 user message） |
| `schema` | any | 否 |

成功时**直接返回模型原文**，不包 JSON、不校验结构。失败 → `isError: true`，text 是 `LLM 调用失败: ...`。
客户端实现在 `src/mcp/lib/llm-client.ts`，与 Python 侧的 `collector/llm/extract.py` **不是同一套**（那边才做三层降级）。

### collect_run — register a collection run (metadata only)

| 参数 | 类型 | 必填 | 默认 | 说明 |
| :-- | :-- | :-- | :-- | :-- |
| `source` | string | ✓ | — | `z.enum(SEARCH_SOURCES)`，来自 `collector/capabilities.json` |
| `topic` | string | | — | 与 `query` 二选一 |
| `query` | string | | — | 原样搜索，追加 `--no-topic` |
| `max` | int | | 采集器自定 | ≤200 |
| `urls_file` | string | | — | 相对项目根，`--urls` |
| `expand_authors` | bool | | `false` | `--expand-authors` |
| `timeout_ms` | int | | `300000` | ≤1800000 |
| `dry_run` | bool | | `true` | |

`topic`、`query`、`urls_file` 全空 → `isError`（不给条件会按采集器内置默认主题跑，白烧配额）。`topic` 与 `query` 同给 → `isError`。
**只登记元数据**：不抓正文、不调 LLM。返回 dry-run 报告（`python/command/candidates_rejected/missing_env/notes/active_runs/hints`）
或真跑结果（`exit_code/seconds/stdout/stderr?`）。

### collect_site — run a site spec

| 参数 | 类型 | 必填 | 默认 |
| :-- | :-- | :-- | :-- |
| `config` | string | ✓ | —（相对项目根或绝对） |
| `max_pages` | int | | 采集器决定，≤100 |
| `register` | bool | | `false` |
| `check` | bool | | `false` |

`check=true` 是纯本地体检：**不起 Python、不联网、不写盘**，返回 `spawned:false` 与命令形态。
`check=false` 且 `register=false` 仍然**真跑采集**（联网抓页面），只是不带 `--register` 不写 `pipeline.db`。
失败按 `reason` 点名：`spec_not_found / spec_validation_failed / runner_missing / python_launch_failed / python_nonzero_exit / report_parse_failed / timeout`。
返回只含报告摘要（`pages/items/attachments/unparsed/failures` 的**计数**），整批条目不进返回值。

### collect_guide — how to write a query for a platform

| 参数 | 类型 | 必填 |
| :-- | :-- | :-- |
| `source` | string | 否（不传返回全部平台总览） |

不传 `source` → `{ok, platforms[], missing_query_guide[], hint, usage}`，`platforms` 只列 `platforms`（不含 `sites`）。
传 `source` → 该平台的 `probe/capabilities/query_guide/checklist[]`；平台没声明 `query_guide` 时 `ok:true` 但 `query_guide:null` + 一段 `note`（不是错误）。
`capabilities.json` 缺失 → `isError`，提示先跑 `python tools/capabilities.py --write`。
未知源 → `isError` + `available[]`。

`all = {...platforms, ...sites}`，所以站点源也能查，但总览里不出现。
