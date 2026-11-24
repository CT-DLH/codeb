---
covers:
  - src/mcp/
updated: 2026-11-17
---

# MCP error taxonomy and the silent-success paths

失败有三种出口，只有第一种是「调用方一眼能看出来」的。第二类（`ok:false` 但不带 isError）和第三类
（完全无声）才是真正耗时的地方——它们都长得像成功。这一页把三类分清，再逐条列出「看起来成功但实际有问题」的路径。

## Three exits, and which one you actually get

| 出口 | 形态 | 触发条件 |
| :-- | :-- | :-- |
| `isError: true` | `content[0].text` 是 JSON 或纯文本 + 标志位 | 工具自己返回，或 SDK 兜住未捕获异常 |
| 纯 JSON-RPC error | `error` 对象，无 `content` | **只在工具调用之外**：未知 method、initialize 失败、传输层解析失败 |
| 静默 | 正常返回，`isError` 缺失/false | 报告里带 `ok:false`、`warning`、`hints`，或什么都没 |

**`tools/call` 这一层几乎没有纯 JSON-RPC error。** SDK 的 `setToolRequestHandlers` 把整段包在
`try { … } catch (error) { return this.createToolError(...) }` 里，所以：

- `Tool <name> not found` / `disabled` → 也是 `isError: true` 的 `CallToolResult`，`text` 是那句英文。
- **input schema 校验失败** → `isError: true`，`text` 是
  `Input validation error: Invalid arguments for tool <name>: <zod 消息>`。这是纯文本，不是 JSON。
- **handler 抛异常**（`writeFileSync` 失败、`readFileSync` ENOENT 之类没被工具自己 catch 的）→
  `isError: true`，`text` 是异常 message。同样是纯文本。

真正走 JSON-RPC error 的只剩协议层：未知 method（`MethodNotFound`）、`initialize` 契约不符、
以及 stdio 上出现非 JSON 行时 `ReadBuffer.readMessage()` → `JSONRPCMessageSchema.parse` 抛错，
客户端 `onerror` + `close()`，**连接整个断掉**（`llm-client.ts:113` 那句 `console.log` 就写向 stdout，
是这条路径的唯一现实风险）。

所以封装时的正确判据只有一个：`res.isError`。不要 parse text 找 `ok`，一半工具根本没这个字段。

## isError is used, but never for a conflict

冲突与「差一点」都不算错误：

| 情形 | 返回 |
| :-- | :-- |
| `card_commit` 检测到版本漂移 | `{committed:false, conflict:true, conflict_id, message}`，**isError 缺失** |
| `card_create` 命中相似卡 | `{ok:true, ..., duplicate_warning}`，**照常创建** |
| `card_create` dry_run 校验失败 | `{ok:true, dry_run:true, valid:false, errors, issues}`，**isError 缺失** |
| `card_import` 安全阀中止 | `{ok:false, aborted:'…'}` + `isError: true` |
| `card_attach` 安全阀中止 | `{ok:false, aborted:'…'}` + `isError: true` |
| `card_derive` 安全阀中止 | `{ok:false, aborted:true}` + `isError: true`（且 `report` 里的 `ok:true` 被显式改回 false） |
| `collect_run` dry_run 找不到解释器 | `{ok:false, python:{bin:null,…}, hints:[FIX_PYTHON]}`，**isError 缺失** |
| `collect_run` 真跑退出码非 0 | `{ok:false, exit_code:N, stdout, hints}`，**isError 缺失** |
| `collect_site` 报告缺契约字段 | `{ok:true, missing_report_fields:[…], hints}` |

`card_derive` 那处值得单独记：`fail([...], {...report, ok:false, aborted:true})` 里必须显式覆写 `ok`，
因为 `report` 展开在后面会把 `ok:true` 盖回去——注释里写着「中止必须真的是失败」。
同类写法以后照抄，否则安全阀会变成「看起来成功」。

## Every path where success is a lie

按危害排序。前六条会让人做出错误决策。

### 1. `card_batch` 的 update 分支永远不会检测到漂移

```ts
const staged = stageUpdate(cardId, card.revision, changes);     // 基线 = 刚读到的版本
if (detectRevisionDrift(card, staged._base_revision)) { … }      // 和同一个值比 → 恒 false
const revision = writeCardFile(card.file, draft);
```

`stageUpdate` 收到的 base 与 `detectRevisionDrift` 收到的 `card.revision` 是同一个变量，
所以 `entry.error = 'conflict'` 这条路径**在生产上不可达**：批量 update 永远直接覆盖。
想真正防漂移只能走 `card_update` + `card_commit`（基线来自调用方，不是自己读的）。

### 2. `card_create` 的 dry_run 把失败伪装成 ok

`{ok:true, valid:false}`：只读 `ok` 的调用方会以为校验通过。这也是唯一一处 `ok:true` 与「有效」不一致的地方。
判据必须是 `valid`，不是 `ok`。

### 3. `card_append` 报告 `appended: N`，但可能一个字节都没写

`writeCardFile` 在**内容指纹不变**时直接 `return existing.revision`，不写盘。
追加同一段文本两次，两次都回 `appended: <长度>` 与一个 revision，第二次 `edited_at` 没变。
这不是 bug（幂等是有意的），但「appended > 0」不等于「正文变了」。

同样地，`card_commit` 的 `revision` 在内容没变时是**旧** revision，与写盘前一样。

### 4. `card_resolve` 的 `current` 分支什么都不写

`resolution: 'current'` 只 `deleteConflictRecord(conflict_id)`，返回 `{resolved:true, revision:null}`。
它的语义是「保留当前版本」——也就是「不做任何事」。`resolved:true` 很容易被读成「已处理完」，
而实际上被否掉的草稿就此消失（记录已删，`draft_content` 再也取不回来）。

### 5. `collect_run` 起的任务不进登记表

`run-registry` 的读侧探活很强（pid + 自清），但**`collect_run` 只读不写**：
`registerRun` 的调用者在 `console/jobs.ts` 与命令行 `crawl_long` 自己。
所以一个 `collect_run` 正在跑时再调一次，`readActiveRuns()` 看不到它，同源检查形同虚设，
只能靠 `pipeline.db` 的 `database is locked` 兜底。AGENTS 里「同一源已在跑直接拒」这条，
对手工 `collect_run` 来说只在对方是控制台/CLI 长跑时成立。

### 6. `domain_update` 的十二处「只警告」

这些都不阻断，写完即「成功」：

- `add_object_types.<t>: 已存在，忽略` / `remove_object_types.<t>: 不存在，忽略`
- `remove_object_types.<t>: 仍有 N 张卡片使用该类型（卡片不会删，但卡片校验会提示类型未声明）`
- `<t> 不是抽象包，继承一个可落卡的领域会让两张表共享同一套字段`
- `dedup_key: <path> 未在领域包中声明`（该键永远匹配不上）
- `summary_columns: <col> 未在领域包中声明，列表页该列将为空`
- `identity: <path> 未在领域包中声明`（**标识位永远取不到值**）
- `identity.card_id_pattern: {path} 未在领域包中声明或缺少来源，生成的 ID 会走哈希兜底`
- `identity 与 summary_columns 重叠：…`
- `attachments.match_by: <path> 未在领域包中声明` / `attachments.accept: <ext> 目前没有对应解析器`
- `attachments.body_section_map: 这些映射的键或值为空，已忽略`
- `attachments.match_by 为空且领域没有 identity.weak：card_attach 会因为没有关联键而报错`
- `enabled=false：card_attach 对该领域会直接报错而不是跳过`

`identity` 的路径警告最危险：标识位写错不会报错，而是**判重静默退化成「每次新建」**，
要等到发现重复卡才回溯得到这里。

### 7. `domain_create` 不校验 `card_id_pattern` 的 token

`domain_update` 会逐个校验 `{…}` token（`year`/`domain`/`hash:weak`/`hash:strong`/`slug(路径)`），
`domain_create` **完全跳过这一步**——它只校验 `identity.strong/weak/disambiguator` 引用的路径。
所以新建领域时写错 `card_id_pattern: student-{ext.studen_id}` 会被接受，之后所有卡都走哈希兜底，
`card_id` 变成 `student-<8位哈希>` 而不是「按学号」。

### 8. `card_derive` 的正则失效只体现在 hint 里

规则 `pattern` 非法时，`applyDerives` 返回 `reason: 'invalid_pattern'`，
`card_derive` 把它推进 `invalid[]`（`stat` 的四个计数**一个都不加**），dry_run 报告仍是 `ok:true`。
症状是「这条规则在所有卡上都是 0，也不在 no_match 里」。
更常见的静默失效是 `no_match`：规则合法但一条都没命中，报告里就是 `no_match: N`，
没有任何「可能是 pattern 写错了」的提示。判据是 `filled` 与 `no_match` 的比例，不是 `ok`。

`card_derive` 的 `card_ids` 用 `f.endsWith('<id>.md')` 匹配文件名，`card_id` 互为后缀时会误中多张。

### 9. `card_attach` 的重复检测依赖 cwd

`alreadyAttached()` 比对的是 `sources[].file` 与 `relative(process.cwd(), file)`。
MCP server 由 tsx 从项目根起，所以正常口径是 `inbox/xxx.docx`；但**从别的 cwd 起 server 时，
同一份附件会被判成新的、再追加一遍正文**。判重键是相对的路径字符串，不是内容哈希。
同一份附件里若有两个不同实体（如一份合同两份附件同名），第二个会因 `alreadyAttached` 命中而被跳过。

### 10. `readCardFile` 解析失败返回 null，全链路静默跳过

`card_search` / `card_list` / `findSimilarCards` / `card_derive` / `card_import` 都是 `if (!rec) continue`。
一张 frontmatter 坏掉的卡（罕见但可能：手工编辑、YAML 缩进错）会从**所有**列表与查重里消失，
而 `card_read` 对它报的只是 `未找到卡片`。查重漏掉它是更严重的后果——那张卡会被当成「不存在」而重复创建。

### 11. `findSimilarCards` 在领域包加载失败时退化成「无 dedup_key」

`loadDomainSpec(domain)` 抛错时 `catch { dedupKeys = [] }`，该领域的 `dedup_key` 匹配整条分支不执行。
查重仍然跑（source_ref/title/alias 还在），但**领域级组合键静默失效**。
写卡路径不受影响（`prepareCard` 里 `loadDomainSpec` 抛错会直接失败），只有查重被削弱。

### 12. `card_search` 的空 query 返回全部卡片

`if (q && !haystack.includes(q)) continue` —— `q` 为空串时条件短路，**每一张卡都通过**。
没有分页，全量返回。`query: ' '`（空格）也会被 `trim()` 成空串走进这条路。

### 13. `card_list` 的 filter 命中不了时不报错

`filter: {'ext.mentors': 'mentor/x'}` 若路径拼错或值为空，只是**不匹配**，`total` 变成 0。
没有「未知路径」提示。配合 `confidence`/`status` 的精确相等，很容易得到「这个领域没有卡」的错误结论。

### 14. `llm_process` 不校验输出结构

`schema` 只被 `JSON.stringify` 拼进 system prompt + 设 `response_format: {type:'json_object'}`。
没有 `json_schema`、没有文本抠 JSON、没有本地 schema 校验，所以返回值**可能是带 markdown 围栏的文本、
可能是空、可能是另一个形状**。`content` 为空时 `callLLM` 抛 `Empty response from LLM`（这条会走 isError），
但「有内容且不合法」完全无声。

### 15. `llm-client` 的缓存让「改提示词」不生效

`cacheKey = sha256(model \0 prompt \0 text \0 JSON.stringify(schema||''))`——prompt 变了 key 就变，
所以改提示词本身没问题。真正会咬人的是：**同一个 (prompt, text, schema) 永远返回第一次的输出**，
包括当初那次失败重试后得到的次优结果。缓存文件是整个 `collector/data/llm_ts_cache.json` 读写，
没有 TTL、没有失效接口；读失败时静默清空（`catch {}`），写失败静默丢弃。

### 16. `prerequisites()` 分不清「键写成空」与「没有这一行」

TS 侧用 `/^\s*([A-Z_0-9]+)\s*=\s*(\S+)/` 收键名，**值为空时不入集合**，于是
`GITHUB_TOKEN=` 与「根本没有这一行」给出完全相同的 `notes`。
Python 侧的控制台预检区分这两种（`GITHUB_TOKEN=空` 会照旧报匿名配额），
所以「MCP 预演说没配 / 控制台说能用」的差异不是矛盾，是两套实现。

### 17. `collect_site` 的 `check` 与「预演」不是一回事

`check:true` → 纯本地，返回 `spawned:false`。
`check:false` + `register:false` → **仍然 spawn 采集进程、仍然联网抓页面**，只是不带 `--register` 不写库。
把「默认不写库」读成「默认不跑」是这条路径最常见的误判。真正的失败会被点名 `reason`
（七个枚举值之一），不会返回空对象冒充成功——这是 `collect_site` 做得最好的一处。

### 18. `collect_run` 的 `urls_file` 不接受绝对路径

`const abs = join(ROOT, urls_file)`——传 `D:\x\y.txt` 会拼成 `<root>\D:\x\y.txt` 然后 `不存在`。
`collect_site` 的 `config` 用了 `isAbsolute()` 判断，`collect_run` 没用。两条路径不一致。

### 19. `writeCardFile` 的指纹忽略两个键，但**不忽略**键序之外的任何东西

`contentFingerprint` 用 `stableValue()` 把对象键排序后再哈希，所以「重排 frontmatter」不算内容变化。
但它对**数组顺序敏感**：`aliases: [a,b]` 与 `[b,a]` 是两个不同指纹，会触发一次写盘与 `edited_at` 刷新。
`tags` 一类由合并逻辑取并集的字段不受影响（并集会保持原顺序），手工重排才会。

### 20. `card_delete` 留下孤儿记录

`.staging/<card_id>/` 与 `.conflicts/<card_id>/` 不清理，`card_id` 目录保留。
删卡后重建同名 `card_id`（identity 派生，很可能同名）会**读到旧的冲突记录**，因为
`listConflictRecords()` 只按目录名找。

## Where each failure actually surfaces

排查时按这张表找，比逐个工具读代码快：

| 症状 | 先看哪里 |
| :-- | :-- |
| 卡片写进去了但列表没有 | `domainDir` 两侧口径（`src/mcp/lib/storage.ts` 与 `src/lib/server/card-store.ts`） |
| 导入说成功但字段没变 | `report.would_update` 与 `strategies.merge_rule`；`fill_empty` 不覆盖非空值 |
| 同一实体建了两张卡 | `identity` 的路径是否真的取得到值（`domain_update` 的 warning） |
| 冲突越积越多 | 是不是投影字段没进 `_overwrite_fields`；跑 `npm run migrate:conflicts` 预演看 `by_reason` |
| `card_update` 成功但 `card_commit` 报冲突 | `.conflicts/` 里那份 `draft_content` 已经套用了别人的改动，不是基线版本 |
| 采集预演说能跑、真跑报错 | `collect_run` 的 `ok:false` 不是 isError，读 `exit_code` 与 `hints` |
| 模型返回的 JSON 解析不了 | `llm_process` 只有 `json_object` 一级，没有抠 JSON 与本地校验 |
| 客户端连接莫名断开 | stdout 上被写入了非 JSON 行（`console.log`） |
