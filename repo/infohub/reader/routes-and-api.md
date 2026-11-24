---
covers:
  - src/routes/
  - src/hooks.server.ts
  - src/app.d.ts
updated: 2026-11-17
---

# Routes and API contracts

`src/routes/` 的每个路由都在 `__BUILD_STATIC__` 上有真实分叉——同一个 `load` 函数在两种模式下返回形状完全不同的数据。

## The prerender switch is one expression

每个路由自己声明，不是全局配置：

```ts
export const prerender = __BUILD_STATIC__;   // API 路由与页面路由都这么写
```

`src/routes/+layout.ts` 给整站兜底：`export const prerender = __BUILD_STATIC__`。静态构建时 SvelteKit 的 adapter-static 带 `strict: true`，任何一个没声明 `prerender` 的动态路由都会让构建失败——所以「加一个新 API 路由忘了写这一行」是立即报错，不是静默 404。

## Route inventory

| 路由 | 文件 | 形态 | 数据来源 |
| :-- | :-- | :-- | :-- |
| `/` | `+page.ts` + `+page.svelte` | SSR load + 客户端搜索 | `fetch('/api/domains')` |
| `/[domain]` | `+page.server.ts` + `+page.svelte` | 两态分化 | `queryDomainList` / `getDomainTable` / `getGroupTable` |
| `/[domain]/[card_id]` | `+page.server.ts` + `+page.svelte` | 预渲染 | `getCard` |
| `/search` | `+page.svelte` | 纯 CSR | Pagefind JS 动态加载 |
| `/reports` | `+page.server.ts` | 两态同形 | `listReports()` |
| `/reports/[slug]` | `+page.server.ts` | 两态同形 | `readReport()` |
| `/api/domains` | `+server.ts` | 两态 | `getDomainIndex()` |
| `/api/search` | `+server.ts` | 两态 | `searchCards()` |
| `/api/assistant` | `+server.ts` | 仅 server | `getListMeta()` + LLM |
| `/api/cards/[domain]/index.json` | `+server.ts` | 两态 | `getSummaries()` |
| `/api/cards/[domain]/[card_id]` | `+server.ts` | 两态 | `getCard()` |

## `/` — the only page that goes through HTTP

`+page.ts` 的 `load({ fetch })` 用 SvelteKit 提供的 `fetch` 请求 `/api/domains`，`!res.ok` 时回落 `{domains: []}`。这是全域唯一一处「页面 load 走 HTTP 而非直接 import 服务端函数」的地方，因为它要的是**同一份被缓存的 `/api/domains` 响应**，静态模式下就能落成 `build/api/domains.json` 一个文件。

首页本身不预取任何卡片摘要（注释：12k 行会让首屏变成 6MB HTML）。「全部卡片」是 `<details>` 展开时才发 13 个并发 `fetch('/api/cards/<id>/index.json')`，然后 `allRows.slice(0, 200)` 渲染——**加载全量但只显示前 200 张**。

## `/[domain]` — two completely different returns

`load({ params, url })` 有三条返回路径，前端靠三个布尔量区分：`groupView` / `paginated` / 以及 `__BUILD_STATIC__`。

**入口校验**：`isAbstractDomain(domain)` 为真则放行（抽象父包是真实页面），否则必须在 `listDomainIds()` 里，不然 `error(404)`。

**抽象父包分支**（`groupView: true`）：

```ts
{ domain, name, family, groupView: true, fieldMeta: {},
  paginated: false, card: null, domainChain, ...(await getGroupTable(domain)) }
```

`fieldMeta` 是空对象、`paginated: false` —— 聚合页一次下发最近 500 行，筛排切都在浏览器里，和静态模式同一条渲染路径。

**静态分支**（`paginated: false`）：`...(await getDomainTable(params.domain))`。注释点明原因：**预渲染的页面读不到 `query`，SvelteKit 直接抛错**，所以静态模式完全不看 URL，筛选/排序/深链状态由前端 `onMount` 从 `location.search` 还原。

**在线分支**（`paginated: true`）：解析 URL 后调 `queryDomainList`，返回 `rows` + `pager` 对象。

```ts
const RESERVED = new Set(['page','size','sort','dir','show_empty','card']);
```

`RESERVED` 之外的**每一个查询参数都当筛选分面**。这是个宽松设计：拼错一个参数名不会 404，只会被当成一个不存在的列，`queryDomainList` 里因为 `byCol` 不存在而被丢掉——**静默无效**。

`?card=` 深链由 `hasCard()` 校验（查索引，不读正文），坏 id 静默忽略成 `card: null`，不报错。

返回的 `pager` 形状：

```ts
{ page, pageSize, totalPages, totalCount, filteredCount,
  emptyCount, hideEmpty, sortCol, sortDir, filters }
```

前端 `+page.svelte` 用 `PAGINATED ? pager.* : local*` 一个三目统一两套状态源——这是 file 里最重要的一条约束（注释：「状态口径必须只有一个来源」）。

## `/[domain]/[card_id]` — entries() replaces crawling

```ts
export async function entries(): Promise<CardEntry[]> { return listAllEntries(); }
```

静态模式靠 `entries()` 枚举 `cards/` 源文件，**不依赖链接爬取**——漏一张就是上线 404。`listAllEntries()` 内部对每个领域 `await getSummaries(domain)`，所以它会把 13 个领域全量扫一遍（复用 `summaryCache`）。

`load` 同步、直接 `getCard`，`!card` 时 `error(404, 'Card not found')`。返回 `{ card, domain, fieldMeta, domainChain }`。

页面只有 18 行：`data.card?.ext?.fidelity === 'metadata_only'` 时给外层 `<div>` 加 `data-pagefind-ignore="all"` —— **只有元数据的卡不进搜索索引**，否则几千张空壳会和真内容抢排名。不带值的 `data-pagefind-ignore` 只忽略这一层，带 `="all"` 才连子元素一起。

## `/api/domains`

请求：无参数。响应：

```json
{ "domains": [ { "id": "info_student", "name": "学生名册",
                 "parent": "_info", "isAbstract": false, "count": 3019 } ] }
```

`count` 对抽象父包是**所有后代可落卡域的合计**（沿 `extends` 往下收），因为 `cards/person/` 这类目录本来就不存在。计数只数 `.md` 文件不解析——首页不需要为此把全库卡片解析一遍（那要 7~9 秒）。

## `/api/search`

请求：`GET /api/search?q=<关键词>&limit=<N>`（`limit` 默认 20，`Number.isFinite` 不成立时回落 20，**没有上限**）。响应：

```json
{ "query": "…",
  "results": [ { "card_id": "…", "domain": "info_mentor", "title": "…",
                 "summary": "…", "snippet": "…x…", "collected_at": "…",
                 "source_ref": "…", "score": 14 } ] }
```

静态模式返回固定空壳 `{query:'', results:[]}`（预渲染阶段不能碰 `url.searchParams`），前端在静态模式下根本不会请求它。

## `/api/assistant`

**唯一完全不可用于静态模式的路由**：`prerender = __BUILD_STATIC__`，但 GET 开头再判一次 `if (__BUILD_STATIC__) return json({ok:false, …, error:'静态站点不含 AI 助手…'})`，让它能在 `strict: true` 下被预渲染成一个「不可用壳」。

请求（GET，全部走查询参数）：

```
/api/assistant?domain=info_student&q=<自然语言>&state=<URL 编码的 JSON>
```

- `domain` 不在 `listDomainIds()` 里 → `error(404)`。
- `q` 为空 → `{ok:false, reply:'', actions:[], error:'请输入内容。'}`（**200，不是 4xx**）。
- `state` 是 `{filters?: Record<string,string[]>, sort?: {column?, direction?}}`，`JSON.parse` 失败直接忽略成 `{}`。

响应：

```json
{ "ok": true, "reply": "已筛出…",
  "actions": [ {"type":"clear"},
               {"type":"filter","column":"ext.collector","values":["zhihu"]},
               {"type":"sort","column":"ext.collected_at","direction":"desc"} ] }
```

四条实现约束值得单独记：

1. **prompt 素材来自 `getListMeta(domain)`，不来自全表**：`{columns, labels, formats, facets, totalCount}`。为了回答一句话去扫几千张卡是不可接受的。
2. **`facets` 已被 `card-store` 的可见列裁剪**，敏感字段不进上下文。
3. **`sanitize(parsed, table)` 是白名单守卫**，三个方向都校验：`facetByColumn.get(column)` 不存在就丢；值必须命中 `valid.has(text)`，否则试 `labelToValue`（`column\u0000label` → value，允许模型返回中文名）；排序列必须在 `table.columns` 里。模型说什么都不直接照做。
4. **LLM 客户端在 `src/mcp/lib/llm-client.ts`，不在 lib 里**：`temperature: 0`，`response_format: {type:'json_object'}`，30 秒超时，对 429/503 重试 5 次（每次等 5 秒），缓存键是 `sha256(model \0 prompt \0 text \0 schema)`，落 `collector/data/llm_ts_cache.json`。API key 从 `ZHIHU_LLM_API_KEY` 读，会先尝试加载 `collector/.env`。`baseUrl` 含 `nvidia.com` 时自动加 `chat_template_kwargs.enable_thinking=false`。

错误一律 `{ok:false, …, error}` + HTTP 200 —— 前端靠 `body.ok` 判断，不靠状态码。

## `/api/cards/[domain]/index.json`

路径为什么不是 `/api/cards/[domain]`：静态导出时前者会落成 `build/api/cards/academic` 这个**文件**，而卡片详情要落成 `build/api/cards/academic/xxx` 这个**目录** —— 同名冲突，Windows 下直接 EPERM。

请求：路径参数 `domain`，必须在 `listDomainIds()` 里，否则 `error(404)`。响应是**裸数组**（不是包装对象）：

```json
[ { "card_id":"…", "title":"…", "summary":"…", "confidence":"A",
    "last_verified":"2026-11-01", "status":"有效", "collected_at":"2026-11-01" } ]
```

`entries()` 枚举全部领域供预渲染。

## `/api/cards/[domain]/[card_id]`

请求：两个路径参数，**`domain` 不做校验**（`getCard` 找不到文件就返回 null → 404）。响应是完整卡片对象：`base fields + ext + body + ext_labels`，其中 `format: 'ref'` 的 ext 字段已解析成 `{label, link}`。

`entries()` 走 `listAllEntries()` —— 静态构建会给 14923 张卡各生成一个 JSON。

## `/reports` and `/reports/[slug]`

报告**不在卡片体系里**：`reports/*.md` 是独立文件，用一份 47 行的极简 frontmatter 解析器（`src/lib/server/reports.ts`），只认三种形态：

- `key: "value"` / `key: 42`（纯整数转 Number）
- `key:\n  - "item"`（列表项，靠 `currentKey` 记住归属）
- `key: []`（空列表）

不引 gray-matter 的理由写在注释里：报告是自己 `yaml_dump()` 产出的，形状完全可控；引一个通用解析器反而要处理它没见过的边界，而且 gray-matter 会按输入缓存。

`listReports()` 按 `updated_at` 倒序，`readReport(slug)` 用文件名主干查（中文文件名直接用，SvelteKit 负责 URL 解码），`body_chars = body.trim().length`。`hasReport()` 导出但**全仓无人调用**——详情页用 `readReport` + `error(404)`。

两个页面都 `prerender = __BUILD_STATIC__`，详情页另有 `entries()` 枚举全部报告（注释：比依赖链接爬取可靠，爬取遇到中文 URL 编码问题容易漏页）。

响应形状（列表页 load）：

```ts
{ reports: ReportMeta[], totalSources: number, totalEvidence: number }
```

## What hooks.server.ts does

15 行，只有一个 `init()`：

```ts
export async function init() {
  if (__BUILD_STATIC__) return;   // 静态导出没有运行时，预热是纯浪费
  void warmListIndexes();         // 不 await：首屏要「点进来就有热索引」，不是「启动慢两秒」
}
```

`warmListIndexes()` 串行遍历 `listDomainIds()`，每个 `await getListIndex(domain)` 之后 `setImmediate` 让一次。单个领域抛错被吞掉——其他领域仍会各自重试。

不 `await` 的代价由 `listBuilds` 那一层兜住：真赶上还在预热时，同域的请求会自动排到那次构建之后，拿到的是已对账的索引，不会读到半成品。

## CSR/SSR split per page

| 页面 | SSR | 客户端做什么 |
| :-- | :-- | :-- |
| `/` | 领域索引 | 搜索（防抖 200ms）、全部卡片展开、中译开关 |
| `/[domain]` | 当前页 + 分面 | 在线：所有交互 → `goto(url)`；静态：本地筛排切 |
| `/[domain]/[card_id]` | 整张卡 | 无 |
| `/search` | 空壳 | 全部（Pagefind UI） |
| `/reports/[slug]` | 整份报告 | 无（`renderMarkdown` 也在 SSR 侧跑） |

`app.html` 里有一段内联脚本在首屏前把 `localStorage.getItem('infohub:title-zh')` 读出来设成 `document.documentElement.dataset.titleZh` —— 避免「中译」行闪现后再隐藏。`+layout.svelte` 里 `onMount` 再 `sync()` 一次，两边共用 `STORAGE_KEY = 'infohub:title-zh'`。

`+layout.svelte` 的导航只有「首页 / 搜索」——注释说明原因是领域太多 topbar 放不下，顺带省掉了「每个预渲染页面一次 `/api/domains` 请求」。
