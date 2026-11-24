---
covers:
  - src/mcp/lib/
updated: 2026-11-17
---

# MCP lib internals: storage, dedup, conflicts, LLM, collector

`src/mcp/lib/` 八个文件是工具的共用底座。这一页只记**实现级细节**：正则、权重、忽略键、降级顺序、探测逻辑。
不看源码也能照着改。

## storage.ts: where ROOT comes from

```ts
const LIB_DIR = dirname(fileURLToPath(import.meta.url));  // <root>/src/mcp/lib
export const ROOT = join(LIB_DIR, '..', '..', '..');       // 向上三级
```

**这是 MCP 侧的独立口径**，与 `src/lib/schemas.ts` 不同：后者优先用 vite 构建期注入的
`__PROJECT_ROOT__`（打包后 `import.meta.url` 会指向 `build/` 内部），退回 `join(HERE,'..','..')`。
MCP server 由 tsx 直接跑，不走构建，所以 storage 里没有那层兜底。
`INFOHUB_COLLECTOR_DIR` 只改 `COLLECTOR`，不改 `ROOT`。

`CARDS_DIR = ROOT/cards`，`.staging` / `.conflicts` / `.trash` 也都在 `ROOT` 下（不是 `cards/` 下）。

## The domainDir regex maps a one-segment domain onto a three-level tree

```ts
const m = /^(collect|info|report)_(.+)$/.exec(domain);
return m ? join(CARDS_DIR, m[1], m[2]) : join(CARDS_DIR, domain);
```

`info_student` → `cards/info/student/`；`collect_zhihu` → `cards/collect/zhihu/`；`mentor` → `cards/mentor/`。
`(.+)` 是贪婪的，所以 `info_a_b` → `cards/info/a_b/`（只切第一段，不递归分层）。
三个前缀是**硬编码**的，加第四种类别必须同时改这里与 `src/lib/server/card-store.ts` 的 `domainDir`——
两处不一致的症状是「卡片写进 A，读取找 B」，列表里 0 张。

## listCardFiles walks recursively and sorts

`walkMd()` 递归收集 `*.md`（连 `.trash` 也不排除，因为 base 是 `CARDS_DIR` 而非 `ROOT`），
最后 `out.sort()` 按完整路径字典序。不传 `domain` 时扫全仓库——`findCardFile()` 与
`card_search` / `card_list` / `card_find_similar` 都建立在这个全量扫描上，没有索引。

## readCardFile clones the frontmatter

`gray-matter` 会按**输入字符串**缓存解析结果（同一个 raw 返回同一个 `data` 对象引用）。
所以 `frontmatter` 是 `structuredClone(data)`——不克隆的话，任何调用方原地改 frontmatter 都会污染
下一次读同一份内容的结果。`revision = computeRevision(raw)` = `sha256(raw).slice(0,16)`。
解析失败返回 `null`（不是抛错），调用方一律 `if (!record) continue` 静默跳过。

## writeCardFile: the fingerprint that ignores two keys

```ts
const LIFECYCLE_KEYS = ['created_at', 'edited_at'] as const;
contentFingerprint(fm, body) = sha256(JSON.stringify(stableValue(fm 去掉两个键)) + '\0' + body)
```

`stableValue()` 递归按 key 排序，所以**键序无关**；这是它和 `computeRevision`（整份原文哈希，键序敏感）的核心区别。

三条规则：

- **内容没变 → `return existing.revision`，整张卡不写盘。** mtime、`edited_at`、`revision` 全都不动，
  重复导入同一份材料保持逐字节幂等。
- **老卡有 `created_at` → 沿用旧值**；老卡**没有** `created_at` → `delete frontmatter.created_at`，
  不拿「这次修改时间」冒充创建时间（留给 `npm run backfill:timestamps` 从 git 历史补）。
- **新卡**：`created_at = fm.created_at ?? now`，`edited_at = fm.edited_at ?? created_at`。

写盘前 `mkdirSync(dirname(file), { recursive: true })`，`matter.stringify(body, frontmatter)` 后
`writeFileSync`。返回新内容的 `computeRevision`。

## moveToTrash renames, it does not delete

```
dest = .trash/<cardId>/<ISO 时间戳把 : 和 . 换成 ->-<basename(file)>
```

`renameSync` 之后返回 `dest`。同一张卡删两次 → 两个不同时间戳的文件（第二次会先报 `未找到卡片`，因为原路径没了）。
`.staging/<cardId>/` 与 `.conflicts/<cardId>/` **不清理**，删卡后成为永久孤儿。

## dedup.ts: the exact scoring table

`findSimilarCards(query, limit = 5)` 里每个候选卡走得分为**取最大值**，不是累加：

| 命中 | 分数 | 附加条件 |
| :-- | :-- | :-- |
| `source_ref` 归一化后相等 | **1.0** | 两边都非空 |
| `title` 归一化后相等 | **1.0** | 两边都非空 |
| `title` 互相包含 | **0.85** | **较短一方长度 ≥ 6** |
| `alias` 精确相等（任意 pair） | **0.9** | 两边归一化后非空 |
| `alias` 互相包含 | **0.85** | 较短一方长度 ≥ 4 |
| `dedup_key` 组合键**全部**非空且归一化相等 | **1.0** | 覆盖前面所有分数 |

`DUPLICATE_THRESHOLD = 0.8`，`TITLE_CONTAINS_MIN = 6`，`ALIAS_CONTAINS_MIN = 4` 都是这个文件里的常量。

`aliasPairs()` 生成三组比较对：`queryAlias × candidateTitle`、`queryAlias × candidateAlias`（笛卡尔积）、
`queryTitle × candidateAlias`。**注意 `queryTitle × candidateTitle` 不在这组里**（那是 title 分支的事）。
`aliasExact` 与 `aliasContains` 分别累积——只要出现任意一次精确相等就取 0.9，否则有包含就取 0.85。

`matches[]` 是**所有**命中的去重数组（`[...new Set(matches)]`），`matched_by` 是**得分最高的那一个**。
`dedup_key` 命中时无条件把 `score` 顶到 1.0 并设为 `best`——它最后算，所以优先级最高。

### Normalization: two functions, two purposes

`normalizeText()` = 全角转半角 → 小写 → 删掉所有空白与标点（`，。；：、,.;:!?！？"'""''（）()【】[]《》<>·—-_/\`）。
所以「计算机 科学」与「计算机科学」等价，「A（已毕业）」与「A已毕业」等价。用于 title、alias、dedup_key。

`normalizeRef()` = 全角转半角 → 小写 → 空白折叠成一个空格。**保留 URL/DOI 内部结构**，只统一大小写与空白。
用于 `source_ref`。

`dedup_key` 的值读取用 `readPath()`，`nonEmpty()` 判空（`asText() !== ''`）——所以数值 `0` 会被
`asText(0) = '0'` 判为非空，但布尔 `false` 也是 `'false'` 非空。**空数组/空对象在 `asText` 下都不是空串**
（`String([]) = ''` 是空，`String({}) = '[object Object]'` 不是），这是 `nonEmpty` 的一个粗糙边界。

### Why no embeddings

三条原因，都在代码的选型里体现：① 判重结果必须**可复现**——`card_id` 由 `identity` 派生，
查重口径一变，3019 张学生卡与 1040 张文章卡的 id 一起漂移；② 每次 `card_create` 都要跑一遍全库，
embedding 需要预先算好全部卡片的向量并随写随更新，成本落在写入路径上；③ 相似度分数要能被人复核
（「为什么判成重复」），0.85 的含义是「标题互相包含」，而余弦 0.87 说不出任何东西。

### buildDuplicateWarning

```ts
{ matched_by, candidates: [{card_id, title, score, matched_by}], suggestion }
```

只收 `score ≥ 0.8` 的候选，取**前 3 条**，`matched_by` 来自 `hits[0]`（排序后的最高分）。
`suggestion` 按 `matched_by` 换措辞：`同一来源标识` / `相同领域去重键` / `相同别名/表述变体` / `相同或高度相似标题`，
后半句固定为「先 card_read 查看；补充信息用 card_append，字段变更用 card_update + card_commit，确认是不同实体再新建。」
一个候选都没到 0.8 → 返回 `undefined`（不是空对象）。

排序：`b.score - a.score || a.card_id.localeCompare(b.card_id)`，同分按 id 升序，所以结果稳定可断言。

`dedup_key` 的来源是**候选卡自己所属领域**的 `loadDomainSpec(domain).dedupKey`（`keyCache` 按领域缓存，
加载失败退化成 `[]`），不是查询方领域的——跨域查重时口径跟着被查的卡走。

## conflict.ts: dot-path expansion is a data-shape adapter

`expandDotPaths(changes, roots = ['ext'])` 只为一种输入存在：`scripts/batch_llm.ts` 产出的 ops 行用
**扁平路径**（`{"ext.curated_note": "..."}`，因为它是按 `target` 字段名直接当键），而
`validatePartial` / `applyChanges` 只认嵌套形状。

不展开的两种错**都不报错**：① `validatePartial` 报「ext.curated_note 未在领域包中声明」（键名对不上 ext 下的字段名）；
② 绕过校验后 `applyChanges` 把 `ext.curated_note` 当成**顶层键**写进 frontmatter，卡上多一个点号字段，
`ext` 里真正那个字段没变。

口径：**只展开首段在 `roots` 里的路径**。`title` 里带点不是路径，原样保留。
同一份 changes 里既有 `ext` 又有 `ext.a.b` 时，两边合并而不是互相覆盖（顶层对象先建，再往里写）。

`applyChanges`: `ext` 做**浅合并**（`{...next.ext, ...value}`，所以 `ext.a` 传对象会整个替换 `ext.a`，
不会深合并到 `ext.a.b`），其余键直接覆盖。
`buildDraftContent` = `matter.stringify(card.body, applyChanges(card.frontmatter, changes))`。
`detectRevisionDrift(card, base)` = `card.revision !== base`。

### Conflict records and migrate:conflicts

`card_commit` 产生冲突时写 `.conflicts/<card_id>/<conflict_id>.json`（`conflict_id = Date.now()-random6`），
内容 `{conflict_id, card_id, _base_revision, current_revision, current_content, draft_content, created_at}`。
`listConflictRecords()` 按 `created_at` 升序，损坏 JSON 静默跳过。

**`import_conflicts` 是另一套东西**：它是 frontmatter 里的字符串数组，由 `card_import` 合并时写入，
格式 `ext.x: 保留「A」，新值「B」（来源）`。`npm run migrate:conflicts` 收敛它：

| reason | 判定 | drop |
| :-- | :-- | :-- |
| `unparsed` | 路径前缀（`/^(\S+?): 保留「/`）或 `保留「…」，新值「…」` 解析不出 | ✗ 保留 |
| `path_missing` | 该路径在 frontmatter 上 `undefined`（`_clear` 撤回过） | ✓ 删 |
| `converged` | 现值归一化后 == 记录里的「新值」 | ✓ 删 |
| `kept_kept` | 现值 == 「保留」值 | ✗ 留给人看 |
| `open` | 第三种值 | ✗ 留给人看 |
| `superseded` | 同路径有多条记录，只留最后一条（最新导入） | ✓ 删（仅对未 drop 的） |

`norm()` 对 `undefined` 返回 `'\u0000missing'`（与空串区分）、`null` 返回 `''`、数组/对象走 `JSON.stringify`、
其余 `String().replace(/\s+/g,' ').trim()`。
解析两条口径：`line.replace(/（[^（）]*）$/, '')` 先剥尾部来源括注；`'」，新值「'` 必须在行内**只出现一次**。
`kept` 从 `body.indexOf('保留「') + 3` 取——找不到时 `indexOf` 返回 -1，`-1+3 = 2` 会**取错位置**，
但因为随后有 `if (!kept && !incoming) return null`，实际只在 `incoming` 也空时才兜住。

收敛后 `import_conflicts` 清空时 `status: 冲突` → `待核实`（**不自动变「有效」**：值对不对只能人确认）。
默认 dry-run，`--apply` 才写盘；`--json` 出结构化报告；第一个非 `--` 参数当领域名。幂等。

## schema-loader.ts vs field-spec.ts

两者的分工：`field-spec.ts` 管**「定义字段的字段」对不对**（元 Schema），`schema-loader.ts` 管**「卡片的字段值对不对」**（校验 + 自省）。

`fieldSpecSchema` 用 `z.lazy` 递归，`.strict()` 拒未知属性。`type` 必填且限定五值；
`item` / `fields` 递归；`derive` 是 `{from, pattern, mode?}` 且 `.strict()`，
`pattern` 用 `.refine(v => new RegExp(v))` 在**声明时**试编译。
`DOMAIN_ID_RE = /^[a-z0-9][a-z0-9_-]{0,63}$/`（下划线合法，为三卡制的 `info_student` 等前缀放开）。

字段规格十四个属性的解释：

| 属性 | 影响校验 | 影响渲染/工具 | 说明 |
| :-- | :-- | :-- | :-- |
| `type` | ✓ | ✓ | 五值之一，决定 Zod 类型 |
| `required` | ✓ | ✓ | `!== false` 即必填——**缺省算必填** |
| `enum` | ✓ | ✓ | 覆盖 `type`，变成 `z.enum` |
| `item` | ✓ | | array 元素类型，缺省 `{type:'string'}` |
| `fields` | ✓ | ✓ | object 子字段，递归 |
| `label` | ✗ | ✓ | 中文名，`card_schema`/`card_list_domains` 回传 |
| `format` | ✗ | ✓ | `date`/`url`/`markdown`/`badge`，前端渲染用 |
| `group` | ✗ | ✓ | 表单分组 |
| `order` | ✗ | ✓ | 字段排序 |
| `placeholder` | ✗ | ✓ | 输入提示 |
| `split` | ✗ | ✓ | `array` 专用；`false` 时整值当一项（课程名里有「、」） |
| `sensitive` | ✗ | ✓ | 发布产物剥离；`card_derive` 样值只给形状 |
| `derive` | ✗ | ✓ | 正则提取规则，`card_derive` 执行 |
| `value_labels` | ✗ | ✓ | 值 → 展示名（`zhihu` → `知乎`） |
| `filterable` | ✗ | ✓ | 列表页筛选分面 |
| `deprecated` | ✗ | ✓ | 标记废弃，不渲染但保留数据 |
| `server_generated` | ✗ | ✓ | 服务端生成，`card_schema` 汇总进 `server_generated_fields` |

`loadDomainSchema()` 的构建口径：顶层 = `base_fields`，外加 `ext`；`ext` 有字段时用
`z.object(extShape).catchall(z.unknown())`，没字段时 `z.record(z.string(), z.unknown())`；
**整个 schema 是 `.passthrough()`**——未声明字段保留、不阻断，只在构建期发警告。
「领域包是建议清单不是合同」就是这条。

`validatePartial(domain, changes)` 是 `card_update` 用的逐键校验，与全量校验有四处不同：
① `ext` 必须是对象（数组/null 报 `ext: 必须是对象`）；② ext 下未声明的键报 `ext.<k>: 未在领域包中声明`；
③ 顶层未声明的键报 `<k>: 未在领域包中声明`；④ **不检查必填**（只 `field.safeParse(ev)` 单字段），
所以能只改一个字段。`messageOf()` 把「输入是 undefined」的 issue 统一改写成 `Required（必填）`，
因为 Zod 默认的 `Required` 消息不说人话。

## llm-client.ts: one provider choice, five attempts, two timeouts that differ

配置全部来自环境变量（`collector/.env` 会被懒加载进 `process.env`，**不覆盖已存在的值**）：

| 变量 | 默认 | 作用 |
| :-- | :-- | :-- |
| `ZHIHU_LLM_API_KEY` | — | 缺失直接 `throw`，第一次调用才报 |
| `ZHIHU_LLM_BASE_URL` | `https://api.openai.com/v1` | 尾部 `/` 剥掉，拼 `/chat/completions` |
| `ZHIHU_LLM_MODEL` | `gpt-4o-mini` | |
| `LLM_EXTRA_BODY` | — | JSON，`Object.assign` 进请求体，**优先于** thinking 开关 |
| `LLM_DISABLE_THINKING` | — | `'1'` 时发 `chat_template_kwargs.enable_thinking=false` |

「支持哪些 provider」= 任何 OpenAI 兼容的 `/chat/completions`。代码里**只有一个 baseUrl**，
换厂商靠改 `ZHIHU_LLM_BASE_URL`。`run-registry`/`collector-runtime` 与它无关，别混。

**重试与超时**：`for (attempt < 5)`，每次 `new AbortController()` + 30s `setTimeout`。
- `AbortError` → 立刻 `throw 'LLM API Request Timeout (30s)'`，**不重试**。
- `429` / `503` → `await 5s` 后 `continue`（最多 5 次，即最多等 25s）。
- 其他非 2xx → 立刻 `throw`。
- 五次都是 429/503 → 循环结束后 `throw lastErr`。
- `content` 为空 → `throw 'Empty response from LLM'`。

**这条 `console.log` 是 stdio 传输上的隐患**：`llm-client.ts:113` 在 429/503 时 `console.log`，
而 `StdioServerTransport` 用 `process.stdout` 写 JSON-RPC 帧。混进一行非 JSON 文本会让客户端的
`ReadBuffer.readMessage()` → `JSONRPCMessageSchema.parse(JSON.parse(line))` 抛错，进而 `close()`。
实际后果取决于客户端容错；服务端这里**没有把日志重定向到 stderr**（对比 `server.ts` 启动行用的是 `console.error`）。

**结构化输出的「三级降级」不在这里。** `src/mcp/lib/llm-client.ts` 只有一级：
`schema` 存在时设 `response_format = {type:'json_object'}`，并把 Schema 的 JSON.stringify **拼进 system prompt**
（附一句「不要包含 markdown 标记」）。没有 `json_schema`、没有文本抠 JSON、没有本地校验。
真正实现三级降级的是 Python 侧 `collector/llm/extract.py`：
`json_schema` → `json_object` → `_extract_json(text)` 逐层本地校验，`mode` 字段记录用了哪一级。
`llm_process` 走的是 TS 这条单级路径——**它返回的「JSON」不保证合法，调用方必须自己 parse**。

**reasoning 模型**：这里只做 `enable_thinking=false`，且**只在 baseUrl 含 `nvidia.com` 且未设
`LLM_DISABLE_THINKING` 时自动生效**。没有「空 content + finish=length + 有 reasoning」的诊断
（那是 Python 侧的行为）。所以换到别的推理型端点而不设 `LLM_DISABLE_THINKING=1` 时，
症状是「content 为空 → Empty response」，看不出是思考把预算吃光了。

**缓存**：`sha256(model \0 prompt \0 text \0 JSON.stringify(schema||''))` → 内容，存
`collector/data/llm_ts_cache.json`（整个文件读写，非落盘追加）。**缓存没有 TTL、没有版本号**——
改提示词但文本与 schema 不变时命中旧缓存；反过来说，同一输入永远返回同一输出，这是它比温度 0 更可靠的地方。
文件读失败静默 `catch {}`（缓存作废），写失败也静默（丢缓存）。

## run-registry.ts: one JSON file per run, liveness by pid

`ACTIVE_RUNS_DIR = collector/data/console/runs/active`，**契约与 `collector/zhihu_pipe/runs.py` 逐字一致**：
一个任务一份 `<run_id>.json`，退出销案，读侧按 pid 探活。

- `runFile(runId)` 消毒：`/[^0-9A-Za-z._-]+/g → '-'`，再去首尾 `-.`，空则 `'x'`。**防 `../` 穿越**。
- `pidAlive(pid)`：`process.kill(pid, 0)`；抛错时 `code === 'EPERM'` 算活着（进程在、不归我），其余（`ESRCH`）算死。
- `readActiveRuns(prune = true)`：目录不存在返回 `[]`；逐个 parse，`pidAlive` 为真才收；
  死了（或 JSON 坏了）且 `prune` 时 `unlinkSync` 自己清掉——**读侧自清**，没有守护进程。
- `registerRun` 覆盖写（`writeFileSync`），`unregisterRun` 的失败被吞（「没登记过不是错误」）。

`ActiveRun` 的键除必需的 `run_id/kind/pid` 外都是 `[key: string]: unknown`，
collect_run 只用 `kind`（`'run'` / `'crawl_long'`）与 `source` 来判「同源是否已在跑」。

## collector-runtime.ts: shared by MCP and the console

`COLLECTOR = process.env.INFOHUB_COLLECTOR_DIR ?? ROOT/collector`，`RUNNER = COLLECTOR/tools/run_source.py`。
MCP 的 `collect_run` 与本地控制台都从这里取，**两边各抄一份的结果是「预演说能跑、真跑换了个解释器」**。

### Source lists come from capabilities.json, not hardcoded

`readCapabilities()` 读 `collector/capabilities.json`，分三个列表：

- `SOURCES` = `platforms` 的**全部键**（`collector-python-test.ts` 按它逐项比对，不能先过滤）
- `SEARCH_SOURCES` = 声明了 `capabilities` 含 `search` 的（**没有 `capabilities` 字段的旧条目也算**）→ `collect_run` 的 `z.enum`
- `SITE_SOURCES` = `sites` 键的全部 + `platforms` 里 `site_` 前缀且**没声明 search** 的（兼容旧格式）

读不出来时三个都空、`SOURCES_NOTE` 给可执行提示，**不让 MCP 启动直接崩**。
`collect_run` 见到 `SEARCH_SOURCES` 为空会拒跑并提示 `cd collector && python tools/capabilities.py`。

### Interpreter probing must actually load the source

`pythonCandidates()` 顺序：`INFOHUB_COLLECTOR_PYTHON` → `collector/.venv/Scripts/python.exe` 或 `.venv/bin/python`
→ `collector/python.txt` 里第一条非注释行 → `PATH` 上的 `python`、`python3`（去重）。

探测**不能只 `--help`**（插件的第三方依赖全是延迟导入，`--help` 探不出来）：
脚本是 `from zhihu_pipe.source import get_source; get_source("<source>")`，
先跑一次 `import sys; print(sys.version)` 确认解释器起得来。**按源分别探测并缓存**
（`probes: Map<'bin|source', {ok, reason}>`），所以学术源与知乎的探测结果不共享。
`failureReason()` 挑第一条含 `Error:` 的行——Python 的 `ModuleNotFoundError` 在中间几行，
末行常常只是解释器版本号，照着末行报就查不下去。

同步版 `resolveCollectorPython` 用 `spawnSync`（30s 超时），异步版 `resolveCollectorPythonAsync` 给控制台用——
`spawnSync` 会把整个 HTTP 服务卡住，探测一个装错依赖的解释器最多等 30 秒。

### prerequisites() reports key names, never values

只看文件、不联网：扫 `collector/.env` 的 `KEY=非空值` 行收集键名集合。
`ZHIHU_LLM_API_KEY` 缺失进 `missing`（硬阻断提示），`BILI_COOKIE` / `XHS_COOKIE` / `GITHUB_TOKEN` /
`S2_API_KEY` 缺失进 `notes`（软提示）。`.env` 不存在时给一条总说明（知乎登录态在 profile 里，与 `.env` 无关）。
**报告里只出现键名**，值一个字节都不回显。

## How a long run is registered and polled

`collect_run` **只登记元数据**（M3 起抓正文与摘要移到 `collect:enrich`）。
真跑流程：`readActiveRuns()` 取外部任务 → 过滤 `kind ∈ {crawl_long, run}` → 同源命中即拒（两个进程抢写
`pipeline.db` 只会撞 `database is locked`）→ `spawnSync(chosen.bin, argv, {cwd: COLLECTOR, timeout: timeout_ms ?? 300000,
env: {...process.env, PYTHONIOENCODING: 'utf-8'}, shell: false})`。

**登记表不由 `collect_run` 写**：它只读 `readActiveRuns()` 判冲突，真正 `registerRun` 的是
`console/jobs.ts`（控制台起的任务）与命令行 `crawl_long` 自己。
`collect_run` 起的子进程**不进登记表**——所以一个 `collect_run` 正在跑时，另一次 `collect_run` 看不到它，
只能靠 `pipeline.db` 的锁兜。这是当前实现的一个真实缺口。

超时与并发：

- `timeout_ms` 默认 `300000`，上限 `1800000`。**它只管子进程**，MCP 客户端默认 60s 就断。
  `slowHint` 会在 `budget > (MCP_TIMEOUT_MS || 60000)` 时明确提示加 `MCP_TIMEOUT_MS`，
  否则「连接先断、采集器还在写库，报告一个字都拿不到」。
- `stdout` / `stderr` 各截尾 4000 / 1500 字符回传（`tail()`），不解析、不改写。
- 退出码非 0 **不算失败**（`ok: result.status === 0` 但只有 `result.error` 才走 `isError`），
  所以 `ok:false` 的返回是**成功响应**，要读 `exit_code` 与 `hints`。
- 不同源可以同跑（登记腿写入极短，WAL + `busy_timeout=5000` 兜住）。

`collect_site` 的 spawn 与它平行但**不复用源探测**：站点采集脚本只依赖本地 `site_crawl` 包，
任何能启动的解释器都能跑，所以 `choosePython()` 只判文件存在，不 import 探测。
子进程超时压到 `Math.max(5000, (MCP_TIMEOUT_MS || 60000) - 3000)`——**让子进程死在客户端之前**，
这样至少能拿到 `timeout` 的命名失败而不是连接被掐断。
