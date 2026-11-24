---
covers:
  - src/lib/server/card-store.ts
updated: 2026-11-17
---

# Card store: the read hot path

`src/lib/server/card-store.ts` 是全仓最重的一个文件，也是唯一允许读 `cards/` 的地方，一次请求里同时承担「文件→卡片对象」「缓存失效」「分页索引」「敏感剥离」四件事。

## What one request actually touches

导出面按职责分四组，改任何一处都要先确认它在哪一组：

| 组 | 函数 | 成本 |
| :-- | :-- | :-- |
| 领域元 | `listAllDomainIds` / `listDomainIds` / `getDomainIndex` / `getDomainChain` / `countCardFiles` | 读 `domains/` 目录 + 每个包一次 YAML；`countCardFiles` 只数 `.md` 不解析 |
| 全表（静态） | `getDomainTable` / `getGroupTable` | 全量解析，paper 实测 1.88MB HTML |
| 分页（在线） | `queryDomainList` / `getListMeta` / `getListRow` / `hasCard` / `warmListIndexes` | ≈ 一页行数 |
| 单卡 / 搜索 | `getCard` / `searchCards` / `listAllEntries` | 单卡一次 `readFileSync`；搜索是全库扫 |

`ROOT` 的取法决定了打包后能不能找到 `cards/`：优先用 vite 注入的 `__PROJECT_ROOT__`，未注入（tsx 直跑）才回退 `join(dirname(import.meta.url), '..','..','..')`。`domainDir()` 是全文件最关键的一行：

```ts
/^(collect|info|report)_(.+)$/ → cards/<类别>/<子类型>/，否则 cards/<domain>/
```

这个映射**必须只有一份**。`src/mcp/lib/storage.ts`（写）与这里（读）各写一遍就会漂，症状是「卡片在磁盘上、列表里 0 张」，而且不报错。

## The mtime cache: three keys, not one

缓存不是一个 Map，是四层，失效条件各不相同：

- **`domainEpoch: Map<domain, number>`** —— watcher 每报一次写事件就 +1。这是「文件变了」的唯一权威信号。
- **`parsedCache: Map<domain, Map<file, {mtime, data}>>`** —— 逐文件 frontmatter，watcher 点名了哪个文件就只重解析那一个。
- **`dirtyFiles: Map<domain, Set<file>>`** —— 本轮待重读清单，`scanDomain` 开头 `delete` 掉整份（扫描期间新到的写事件进下一轮）。
- **`summaryCache` / `tableCache: Map<domain, {mtime, epoch, checkedAt, sensitive, ...}>`** —— 成品缓存，四个字段全是失效判据。

`cacheFresh()` 的判定顺序不能调：

1. `entry.sensitive !== showSensitive()` → 直接 false。**表内容取决于剥离口径**，本地口径的表不能拿去顶发布口径。
2. watcher 活着：`entry.epoch !== currentEpoch(domain)` → false；否则 `Date.now() - checkedAt < 60_000` → true（**不 stat**）。
3. 兜底：`cacheMtime(domain) = max(dirMtime(卡片目录), yamlMtime(domain))`，不等于 `entry.mtime` 才 false。此时顺手 `parsedCache.delete` + `dirtyFiles.delete` —— 漏了 watcher 事件，逐文件缓存已经不可信。

`dirMtime()` 是递归 `statSync` 取最大 mtime。注释里的实测数字是 Windows 上全站 12k 文件 ~690ms、paper 单域 ~240ms；每请求走一遍就是「点一下卡一下」的来源，所以 watcher 可用时完全不走它。

## Why the watcher has to translate filenames

`fs.watch(CARDS_DIR, {recursive:true})` 只给相对路径，而缓存键是 domain id。三卡制下是三层目录，转换规则写死在 `ensureWatcher()` 里：

- `collect/paper/xxx.md` → `domain = collect_paper`，`fileRel = xxx.md`（`parts.slice(2)`）
- 单层 `research/xxx.md` → `domain = research`，`fileRel = xxx.md`
- `parts[0]` 以 `.` 开头或拿不到 filename → `bumpAll()`

注释记了两条**实测踩过**的错：早先只取 `parts[0]` 得到 `collect`，与 `parsedCache` 的键 `collect_paper` 对不上，症状是「文件写了、索引看不见」；`fileRel` 若写成 `paper/xxx.md`，与 `scanDomain` 里 `readdirSync(dir)` 给的单层文件名前缀不匹配，`dirtyFiles` 的键永远命中不了，退化成每次整域重读。

两个 watcher 都 `.unref()`——不阻塞进程退出。`domains/` 的 watcher 只处理 `.yaml`，按文件名去掉后缀 bump 对应 domain。

## scanDomain: 32 readers, 256-row yield

`scanDomain(domain, columns)` 是整个读取层的地基：

- `READ_CONCURRENCY = 32` 个 worker 抢一个自增下标，`readFile` + `stat` 用 `Promise.all` 并发；`YIELD_EVERY = 256` 行 `setImmediate` 让出一次事件循环，避免长扫描饿死同进程的其它请求。
- 串行 `readFileSync` 的实测是 3605 张 0.7~1.9 秒，并行读是它存在的原因。
- 行只带 `card_id` + `title` + 请求的 `columns`。`last_verified` 特殊：取 `d.last_verified ?? d.collected_at`。
- 单卡读/解析失败 `continue`，不影响其余卡；没有 `card_id` 的行直接丢掉。
- 结束时按 `card_id` 做 `localeCompare` 排序，并把 `store` 里已不存在的文件清掉（删掉的卡不能永远占内存）。

`getSummaries()` 用固定列 `['summary','confidence','status','last_verified','collected_at']`，产出 `CardSummary[]`（`last_verified` 回退 `collected_at`，`collected_at` 保留可选）。

## planDomain: 列规划只允许一份口径

`getDomainTable`（静态全表）、`queryDomainList`（在线分页）、`api/assistant`（`getListMeta`）共用 `planDomain(domain)`，否则两条路径会给出不同的列。它做五件事：

1. `summary_columns` 为空 → `DEFAULT_COLUMNS = ['title','summary','last_verified']`。
2. `visibleColumns()` 在剥离口径下**连表头一起**丢敏感列（留空列只会让人以为数据缺失）。
3. 没有 `title` 就补在最前——列表必须保留通往详情页的入口。
4. `filterableCols`：`object_type` 天然入选（不要求领域包声明），其余必须是字段声明了 `filterable: true` 的；敏感字段一律不进分面（否则筛选器就是泄露通道）。
5. `loadColumns = columns ∪ filterableCols ∪ title_zh`。`ext.title_zh` 只在领域包真的声明了它时才加载。
6. `signature` = 继承链上每个 `domains/*.yaml` 的 `${id}:${mtime}` 拼接 —— **改父包也要让列规划失效**。

`resolveFieldSpec()` 支持 `ext.foo.bar` 这种嵌套路径，逐层走 `node.fields?.[k] ?? node.item?.fields?.[k]`，所以数组 item 的子字段也能拿到 label。

## The paged index: build, persist, rebuild

索引 = `ListIndex`，六个结构：

| 字段 | 内容 | 用途 |
| :-- | :-- | :-- |
| `rows: Map<card_id, row>` | 投影后的列表行 | 出页面 |
| `idByFile` / `fileById` / `mtimeByFile` | 三向映射 | 增量更新与对账 |
| `inverted: Map<col, Map<value, Set<card_id>>>` | 可筛列倒排 | 分面计数 = `set.size`，O(1) |
| `emptyIds: Set<card_id>` | `ext.fidelity === 'metadata_only'` | 默认隐藏 |
| `orderCache: Map<'列\|方向', card_id[]>` | 排好的 id 序 | 翻页只切片 |
| `pending` / `stale` / `syncing` / `snapshotTimer` | 同步状态 | 见下 |

`LIST_VERSION = 2`，任何行结构或列规划口径变化都要 +1，旧快照自动作废。

**三张时间表**：`SNAPSHOT_DEBOUNCE_MS = 2000`（采集密集写入时不要每张卡重刷几 MB 快照）、`REVERIFY_MS = 60_000`（兜底对账间隔）、`PAGE_SIZES = [25,50,100]` + `DEFAULT_PAGE_SIZE = 50`。`FACET_MAX_OPTIONS = 40`：分面是「类别维度」不是搜索框，高基数字段不做分面，唯一例外是 `tags`（不设上限）。

**并发**：`listBuilds: Map<domain, Promise<ListIndex>>` 让「启动预热」与「第一个用户请求」共享同一次构建；没有这一层会白扫一遍，两份索引还可能给出不同总数。`runExclusive()` 把同一索引上的同步串成链（`index.syncing`），中途抛错也把链接下去。

**重建的四条路径**：

- 冷启动有快照 → `readSnapshot()`：校验 `version` / `sensitive` / `signature`，重建 `addCard`，把快照里的 `order` 直接灌进 `orderCache['|asc']` 与 `'|desc'`（省一次全量重排），并**强制 `stale = true`**——进程停过期间的改动 watch 看不见。
- 冷启动无快照 → `buildIndex()`：`loadListRows` 全量。
- `stale` → `verifyIndex()`：`readdirSync` + 并行 `statAll`（`READ_CONCURRENCY` 个 worker），只重读「mtime 变了 / 新增 / 文件已不存在」的那几张；`stale` 在扫描**开头**就置回 false，并发排队的第二次直接跳过。
- `pending` 非空 → `applyFiles(files)`：只重读被点名的文件。

`applyFiles` 刻意分两步——**先把所有旧行摘掉，再统一加回来**，这样请求要么看到旧行要么看到新行，不会读到「删了还没加回来」的中间态。任何写入都会 `orderCache.clear()`。

**请求路径的优先级**：`needsSync && stale` → **必须 await 对账完才回数据**（否则重启后第一屏拿着旧快照把删掉的卡照常显示）；`needsSync && pending` → await 增量；兜底复查 `verifiedAt > 60s` → `void` 后台跑，这一轮请求仍用现有索引。

**快照落盘**：`.cache/list-index/<domain>.json`，本地口径加 `.local` 后缀（`snapshotPath()`）。两种口径行内容不同，共用一个文件会互相顶掉、每次换模式退回全量扫描，而且 `.local` 含敏感明文，单独文件名更容易看清该不该删。写入是 `<target>.<pid>.tmp` + `rename`，失败静默——快照只是加速器。

实测快照体积：`collect_paper` 2.79MB、`collect_zhihu` 1.92MB、`info_student` 1.50MB、`collect_github` 607KB。全部 13 个领域一次建满约 12MB 磁盘。

## queryDomainList: 参数口径的三个坑

```ts
export interface ListQuery {
  page?: number; size?: number;
  sortCol?: string | null; sortDir?: 'asc' | 'desc';
  filters?: Record<string, string[]>;   // 列内 OR、列间 AND
  showEmpty?: boolean;
}
```

- **`size` 白名单**：`PAGE_SIZES.includes(Number(query.size))` 才认，否则回落 50。`page` 先 `Math.trunc` 再夹在 `[1, totalPages]`。
- **`sortCol` 必须在 `plan.columns` 里**，否则静默变成默认序（按 `card_id`）。注意 `sort` 用**原始列名**（`?sort=ext.year`），分面参数才去 `ext.` 前缀。
- **短名撞名**：`tags`（`_base`）与 `ext.tags`（`_collect`）剥前缀后都叫 `tags`。`paramCols` 建「短名 → 候选列数组」，只保留「这一列真有这些取值」的那些，逐列 AND。若只认第一个候选，空列会把有值的那列吃掉——实测 `?tags=机器学习` 筛出 0 张而 chip 上写着 378。
- `hideEmpty = !showEmpty && emptyIds.size > 0`：只有在领域里真的存在「仅元数据」卡时才启用，别的领域不受影响。

`facetsFromIndex()` 的选项排序是 `count` 降序 + `label` 的 `zh-Hans-CN` 比较；过滤条件是 `options.length > 1 && (column === 'tags' || options.length <= 40)`——只有一个取值的维度不是分面。

## Aggregate table: why 500 rows and generic columns

`getGroupTable(abstractId, limit = GROUP_ROW_LIMIT = 500)` 把 `leafDescendants` 的所有可落卡域的 `getDomainTable` 结果混在一起，按 `collected_at ?? last_verified` 降序，`slice(0, limit)`，`totalRows` / `truncated` 照实报。

列是**通用列** `['title','domain','object_type','collected_at']`，不是子域的 `summary_columns`：mentor 声明研究方向/职称、student 声明学号/导师，硬拼会得到一堆空列。行里 `domain` 存中文名（展示）、`domain_id` 存 id（跳转）——一个列要同时承担展示和跳转就只能拆两个键。分面只保留 `domain`。

代价写在注释里：`/person` 首次 15.0s（3134 行）、`/content` 首次 31.1s（11437 行），缓存后 0.65s / 0.16s。慢的原因是全局按时间排序没法只读前 N 个文件（文件名不代表时间），而聚合页只用内存 `tableCache`，没有磁盘快照，进程重启就重付一次。

## getCard: clone, redact, then resolve

顺序是硬约束，注释里写了原因：

1. `matter(readFileSync(...))`，然后 **`structuredClone(parsed.data)`** —— gray-matter 按输入字符串缓存解析结果，不克隆就污染后续读取。
2. `redactCard(domain, card)` 剥敏感字段 + 按值抹正文。
3. **剥完再解析引用**：`refExtKeys(domain)` 取所有 `format: 'ref'` 的 ext 键，`resolveRefValue()` 把 `mentor/mentor-001` 换成 `{label:'陈清财', link:'/mentor/mentor-001'}`。顺序反了的话 ref 串会先被换成 `〔敏感信息已遮蔽〕`，形状匹配不上。

`resolveRefValue` 有个容易被忽略的细节：**先查 `refTitleCache` 再 `existsSync`**。3600 行逐行 stat 文件系统也要几百毫秒；缓存键是**被引用卡的文件绝对路径**，`epoch` 用被引用领域的版本号（不是请求领域）。

`getFieldMeta()` / `extLabels()` 都按 `hiddenExtKeys()` 过滤：发布口径下连「身份证号」这四个字都不出现在产物里。

## searchCards: linear, synchronous, no index

```ts
export function searchCards(query: string, limit = 20): SearchHit[]
```

同步函数，遍历 `listDomainIds()`，对每个 `.md` 做 `readFileSync` + `matter`，**没有任何缓存**。打分权重：

| 命中位置 | 分 |
| :-- | --: |
| `title` | 10 |
| `aliases[]` | 8 |
| `summary` | 4 |
| `tags[]` | 3 |
| 正文 `body` | 1 |

`score === 0` 丢弃，最后 `sort((a,b) => b.score - a.score).slice(0, limit)`。`snippet` 由 `snippetAround(text, needle, radius = 40)` 生成：命中位置前后各 40 字符，前后被截断处补 `…`，空白折叠成单空格；正文没命中就退回 `summary`。注意**同分不保证稳定序**——没有第二排序键。

## Where the two search paths fork

分叉点只有一处，而且是编译期常量：

- `src/routes/api/search/+server.ts` 里 `export const prerender = __BUILD_STATIC__`；静态模式 `GET` 直接返回 `{query:'', results:[]}` 空壳（预渲染阶段不能访问 `url.searchParams`）。
- `src/routes/+page.svelte` 的 `runSearch()`：`if (!__BUILD_STATIC__)` 走 `fetch('/api/search?q=…')`；否则动态 `import('/pagefind/pagefind.js')`，`search(q)` 取前 20 条，`excerpt` 去 HTML 标签，`d.url` 按 `/` 切开取 `parts[0]=domain`、`parts[1]=card_id`。
- `/search` 独立页是第三套：只加载 `PagefindUI`，静态、纯客户端，dev 下索引不存在会显示「需先 npm run build」。

所以「服务端检索」与「Pagefind」不是运行时开关，而是**同一份代码的两次编译**。

## Why you must not traverse cards/ yourself

四条都是硬理由，不是洁癖：

1. **绕过 epoch 失效**。`domainEpoch` 只在 watcher 回调里 +1，外部代码读文件不改变它；缓存于是不会失效，「改完卡刷新即见」这个性质就没了。反过来说，如果你必须自己读，就得自己实现 watcher + 60 秒兜底 + 逐文件增量，等于重写这个文件。
2. **绕过敏感边界**。`projectRow()` / `getCard()` 里各过一次 `redactRow` / `redactCard`。自己读 frontmatter 拿到的是**带明文敏感字段**的对象，一路带进 HTML 或 JSON 就是泄露。
3. **复制 `domainDir()` 映射**。三卡制的目录映射是全文件唯一一处正则，复制一份必然漂（`pitfalls` 里的「卡片写在 A、读取找 B」）。
4. **失去索引**。`inverted` / `orderCache` / `snapshot` 都建立在「这是一份被管理的行集」上；旁路读取拿不到它们，只能全表排序，一页的成本从 55ms 变成秒级。

## Measured numbers

- 卡片总数：现查（`python sizes.py` 不数 cards/，用 `ls cards/info` 与文件计数）。2026-11-16 当日为 14923，仅作量级参考。
- 热索引打开一页 **55~60ms**（含 SSR），翻页/筛选/排序同量级。
- 重启后带快照首请求 **0.3~0.6s**；无快照首次建索引 **1.2~2s**（每领域一次性）。
- 对账并行 stat 全部卡片文件约 0.4s。
- 中文比较器不复用的代价：7214 行排序把自检从 4.1s 拖到 32s（详见 `infohub/reader/sensitive-and-publish`）。

## Known rough edges

- `getSummaries()` 与 `getDomainTable()` 是两套独立缓存：同一领域被首页「全部卡片」和列表页同时打开时会各扫一遍。
- `searchCards` 无缓存、无索引，每次全库读；`limit` 只截断结果不截断扫描。
- 快照只在 `applyFiles` / `buildIndex` 后 2 秒去抖写盘，进程被强杀会丢最后一次。
- `hasReport` / `REPORTS_ROOT` 导出但全仓无人调用（报告页改用 `readReport` + `error(404)`）。
- `listDomainIds` 排除 `_` 开头与 `abstract: true`；`listAllDomainIds` 只排除 `_base`。两处各写一遍必漂，注释里记了「首页 parent 全 null」的旧 bug。
