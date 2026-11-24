---
covers:
  - src/lib/sensitive.ts
  - src/lib/markdown.ts
  - src/lib/list-sort.ts
  - src/lib/blank.ts
updated: 2026-11-17
---

# Sensitive boundary, rendering and sort rules

这一页记实现：`sensitive.ts` 的三处剥离怎么走，`INFOHUB_SENSITIVE` 三个取值各自压过什么，`markdown.ts` / `list-sort.ts` / `blank.ts` 的可执行规则。判据与理由见 `infohub/design-tradeoffs`，这里只写「跑起来是什么」。

## showSensitive resolves in two steps

```ts
const TRUTHY = new Set(['1','true','yes','on']);

export function showSensitive(env = envRaw()): boolean {
  if (env !== undefined) return TRUTHY.has(String(env).trim().toLowerCase());
  return localRuntime();
}

function localRuntime(): boolean {
  return typeof __BUILD_STATIC__ !== 'undefined' && __BUILD_STATIC__ === false;
}
```

| `INFOHUB_SENSITIVE` | 行为 | 典型用途 |
| :-- | :-- | :-- |
| 未设 | `localRuntime()`：dev / `build:server` → **显示**；`--mode static` → **剥离**；tsx 脚本探不到 `__BUILD_STATIC__` → **剥离** | 日常 |
| `=0`（或任何非 truthy 值） | **强制剥离**，压过本地形态 | `INFOHUB_SENSITIVE=0 npm start` 本地预演发布口径 |
| `=1` / `true` / `yes` / `on` | **强制显示**，压过静态形态 | `export:static:local` 核对「标记生效但数据没丢」 |

四个精确细节：

- `envRaw()` 走 `globalThis.process?.env` 而非裸 `process`：客户端 bundle 里可能没有 `process`。
- **显式值不退回形态默认**。设成 `2` / `false` / `off` 都是「关闭」，不是「未设」。
- `if (env !== undefined)` —— 空字符串 `INFOHUB_SENSITIVE=` 是显式值，判为关闭（`TRUTHY` 不含空串）。
- `showSensitive(env)` 接受参数是为了让测试注入；生产路径一律走默认参数。

`localRuntime()` 只认「**确知**是本地运行」这一个信号，`typeof` 探不到就返回 false —— fail-closed 的方向没变。构建后这段在 server bundle 里会被折叠成 `return true`，静态构建里折叠成 `return false`，运行时没有第二次判断。

## The three strip points, and what each one removes

| 出口 | 函数 | 剥什么 |
| :-- | :-- | :-- |
| 列表行（HTTP API + 预渲染列表） | `redactRows` / `redactRow` | 列值里的敏感子键，整列敏感则连列一起丢 |
| 单卡（详情页 + `/api/cards/...`） | `redactCard` | 字段 + 正文里出现的同名值 |
| `static/data` 分片 | `build-data.ts` 里 `redactCard(domain, structuredClone(card))` | 同上，外加 `ext_labels` 过滤 |
| 发布门禁 | `audit-publish.ts` | 不剥，**拿真值当探针去扫 `build/`** |

`sensitivePaths(domain)` 是四条路径的共同入口：递归 `spec.extFields`（前缀 `ext`）与 `spec.baseFields`（前缀空串），`field.fields` 往下走、`field.item.fields` 往下走并给路径加 `[]`。所以这三种都能标：

- `ext.id_card` —— 顶层，整列丢
- `ext.guardian.phone` —— object 子字段，只丢这一格
- `ext.family[].id_card` —— 数组每一项的子字段

返回 `[...new Set(out)].sort()` —— **排序是必须的**，`audit-publish` 与 `build-data` 的输出顺序依赖它稳定。

`hiddenExtKeys(domain)` 只藏**顶层**键：`parts.length === 2 && parts[0] === 'ext'` 才加进集合。注释写了为什么：`ext.family[].id_card` 敏感不该把 `family` 整列的中文名也抹掉。发布口径下返回这个集合，本地模式返回空集（前端要据此画「仅本地」红标）。

## redactPaths: order matters, and it is three phases

```ts
const REDACTED = '〔敏感信息已遮蔽〕';
export const MIN_REDACT_LEN = 4;
const UNTOUCHABLE_KEYS = new Set(['card_id','domain','sources','ext_labels']);
```

`redactPaths(card, paths)` 的三步顺序是硬约束：

1. **先取值**（`sensitiveValues`）——正文里那份同名内容要靠这些值才能找到，删完字段就取不到了。
2. **再删字段**（`prune`）——递归 `delete`，`removed` 记路径。`[]` 后缀表示「数组每一项」。
3. **最后按值抹正文**，`values.sort((a,b) => b.value.length - a.value.length)` **长的先抹**。

长的先抹的理由：`origin_region` 的值本来就出现在 `insurance_note` 那句话里，先抹短的会把整句拆碎，后面的整句替换就匹配不上。`done: Set` 再去重一次同值。

`replaceIn(node, needle, seen)` 有两个必须这么写的点：

- **`seen` 每轮各给一份新 Set**。注释：它是环路保护，不是「这个对象扫过了」的全局记账，跨值复用会让第二个以后的敏感值一个都替换不到。这是修过的真实 bug。
- **`UNTOUCHABLE_KEYS` 整个跳过**。把溯源里的号码抹掉，卡就找不回材料了。

`MIN_REDACT_LEN = 4`：短于 4 位的值不进正文替换。「重庆」「138」这类串在页面里到处都是，拿它去替换会把无关文字一起抹掉。注意这与门禁的 `MIN_NEEDLE_LEN = 6` **不是一回事**：4 位是「在产物里抹正文」，6 位是「拿真值扫 build/」。

## redactRow: rows are flat, sensitive paths are nested

列表行是**按列路径平铺**的（`row['ext.family'] = 整个数组`），而敏感路径可能落在子键上。`redactRowPaths` 对每一列做前缀匹配：

```ts
if (path === column) dropWhole = true;                                  // 整列丢
if (path.startsWith(`${column}[].`)) inner.push(['[]', ...rest]);       // 数组项的子字段
else if (path.startsWith(`${column}.`)) inner.push(rest);               // 对象的子字段
```

然后 `structuredClone(value)` **再剪**。这句 clone 不是防御性编程：gray-matter 按输入字符串缓存解析结果，列值和它指向的是同一个对象，就地剪会把「剪过的值」留给同进程的后续读取，真值再也拿不回来。

`redactRows` 存在的唯一理由是性能：**批量行只解析一次领域包**。注释：3602 行逐行调 `sensitivePaths` 会把列表拖到十几秒。

## Gating: what the publish gate actually proves

`scripts/audit-publish.ts` 不检查「代码里剥过没有」，而是从 `cards/` 里按领域包标记读出全部敏感值，合成**一条正则**去扫 `build/` 每个内容文件：

- `MIN_NEEDLE_LEN = 6`，太短的值列出来但不扫。
- 等长数字串合并成 alternation，比逐个 `includes` 快一个量级。
- 扫 `build/` 的 HTML、分片 JSON、预渲染 `/api` 响应；**不扫** `pagefind/`（brotli 压缩读不出明文，而它的输入只有 HTML）与 `_app/`（框架 JS，不是卡片内容）。
- 三个自证机制：**阳性对照**（每条探针必须能在自己卡片源文件里读到）、**读取失败计数**（读不到就阻断构建）、**本地口径反向断言**（`audit:publish:local` 要求真值全都在产物里）。

实测覆盖 **13953 个内容文件**，命中 0；本地口径 180 条真值全部在产物里。文档记录门禁抓到过的真实问题：mentor 领域 114 张卡的电话、115 张卡的住址此前一直公开。

## HOST default: loopback, not 0.0.0.0

adapter-node 自己的默认是 `HOST=0.0.0.0`，而本地运行口径**带敏感字段值** —— 绑全网卡等于把身份证手机号送到局域网。两道防线：

```js
// scripts/serve-local.mjs
process.env.HOST ??= '127.0.0.1';
```

```bat
rem start.bat
if not defined HOST set "HOST=127.0.0.1"
```

`??=` 与 `not defined` 都是「**显式设了就尊重**」：`HOST=localhost npm start` 会绑到 `[::1]`，`HOST=0.0.0.0` 会真的对外 —— 要对外 serving 得自己先定口径。`start.bat` 另有一段 `if "%OPEN_HOST%"=="0.0.0.0" set "OPEN_HOST=127.0.0.1"` 只为自动打开的浏览器窗口用，不改绑定。

`npm start` 启动时打印 `serving http://<HOST>:<PORT>（本地口径：敏感字段带值）`；`PORT` 默认 3000。

## markdown.ts: four rendering rules

一个 `MarkdownIt` 实例，配置 `{html: false, linkify: true, breaks: true}` —— **不许 HTML 透传**是安全前提。

**规则一：正文标题降一级**。`md.core.ruler.push('shift_body_headings', …)` 把 `h1→h2 … h5→h6`，`Math.min(level + 1, 6)`。页面已有 h1、面板已有 h2，正文从 h2/h3 起才符合层级。

**规则二：页内锚点不动**。`href.startsWith('#')` 直接走默认渲染，不加 `target`。给 `#小节` 挂 `_blank` 会新开一个整页，滚动位置全丢。

**规则三：相对链接两分**。`isRelative()` 排除有 scheme 的、`//host/x` 的、`#` 开头的。剩下的：

- 有 `baseUrl` → `new URL(href, baseUrl).href` 转绝对地址；
- 没有 → **去掉 `href`**，加 `class="md-inert-link"` 和 `title="原文相对链接，本站没有可解析的出处：<href>"`。

注释里的理由是硬的：预渲染器会把 `<a href>` 当站内路径去爬，一个 `404 /article/README.zh-CN.md` 就能把整场构建炸掉。宁可少一个链接，也不留假链接，也不靠关闭构建绕过。

**规则四：相对图片同理**。解析不出就渲染成 `<span class="md-inert-img" title="…">[图片：…]</span>`，`escapeAttr` 转义 `& < > "`。

所有非锚点链接（含已转绝对的）统一加 `target="_blank" rel="noopener noreferrer"`。

`baseUrl` 的来处是 `CardDetail.svelte`：`card.source_ref ?? card.ext?.url ?? null`。报告页显式传 `null`（报告是本地产物，没有原文地址）。

出口只有一个：`renderMarkdown(source, baseUrl)`，`String(source ?? '')` 兜底非字符串。

## list-sort.ts: one comparator, two runtimes

服务端分页索引与静态模式的浏览器排序**共用这一份**。注释：两边各写一遍必漂，同一个「按年份排序」在两种形态给出不同顺序是最难发现的 bug。

**排序键 `listSortKey(row, col)`**：

| 值 | 键 |
| :-- | :-- |
| `null` / `undefined` / `''` | `null`（排序时恒最后） |
| `[]` | `null` |
| `string` 且 `trim() === ''` | `null` |
| 全部 `{name: string}` 的对象数组 | `names.join(' / ')` |
| 全部 `{label: string}` 的对象数组 | `labels.join(' / ')`（用于已解析的 ref） |
| 全部 string 的数组 | `join(' · ')` |
| 其他数组 | `value.length` |
| 单个对象带 `label` | `value.label` |
| 单个其他对象 | `null` |
| 数字 / 布尔 / 其他标量 | 原值 |

**比较 `compareKeys(a, b, format)`** 的五级：

1. 两边都是 number → `a - b`。
2. 两边都是 `PURE_NUMBER` 形态且**都不以 0 开头** → 按数值比。带前导零的走文本，否则 `00123` 会被当成 `123` 错排。
3. `format === 'date'` → 纯字符串比较（ISO 文本序）。
4. 其余 → `ZH_COLLATOR.compare`，其中 `ZH_COLLATOR = new Intl.Collator('zh-Hans-CN')` 模块级建一次。

第 4 条是性能关键：`String.prototype.localeCompare(b, 'zh-Hans-CN')` 每次调用都按 locale 现建一个 collator。注释里的实测：7214 行排序把自检从 4.1s 拖到 32s。

**空值位置**是这份文件最刻意的一处：

```ts
if (ka === null || kb === null) {
  if (ka !== kb) return ka === null ? 1 : -1;   // 空值恒排最后，不随升降序翻转
}
```

`sign` 只乘在 `compareKeys` 的非空分支上。所以**升序降序空值都在最后** —— 一列里没填的行不应该在降序时冲到最前面。

**第二排序键**是 `card_id` 的 `localeCompare`。注释记了一次真实回归：`course-ACCT3005` 与 `course-ACCT3006` 标题完全相同，比较器返回 0 时相对顺序取决于底层排序算法的稳定性，索引与全表两条路径于是给出不同顺序，`test:list` 红了 5 条。

`listRowComparator(col, dir, format)` 只做闭包捕获 `sign`，三行有效逻辑。

## blank.ts: five empties, one predicate

```ts
export function isBlank(v: unknown): boolean {
  if (v === null || v === undefined) return true;
  if (typeof v === 'string') return v.trim() === '';
  if (Array.isArray(v)) return v.length === 0;
  if (typeof v === 'object') return Object.keys(v).length === 0;
  return false;
}
```

`null` / `undefined` / `""` / `"   "` / `[]` / `{}` 全部为真。注意 `0` 与 `false` **不算空**（走最后的 `return false`），这是刻意的：`voteup: 0` 是一条真实数据，不是缺失。

三个消费点：

- `CardDetail.svelte` 的 `extEntries` 过滤 —— 空值字段不产生空行。
- `CardDetail.svelte` 的 `metaEntries` —— 对象类型 / 采集时间 / 来源类型 / 标签 / 别名 / 备注 六项只显示有值的。
- `+page.svelte` 的检索结果 —— `r.collected_at` 与 `r.snippet` 为空时不渲染。

它与 `listSortKey` 的边界不完全重合：`listSortKey` 对 `0` 返回 `0`（参与排序），`isBlank` 对 `0` 返回 false（参与渲染）—— 两者一致。但 `listSortKey` 对「数组长度」这种退化键返回数字，`isBlank` 不会，因为那条路径只在排序里出现。

## Where the mode fork is decided, once

七个文件里出现 `__BUILD_STATIC__`，全部是读，没有一处写入。它在 `vite.config.ts` 里 `JSON.stringify(mode === 'static')` 注入，此后每个模块拿到的都是编译期常量，打包时被折叠。所以「这次运行是不是发布口径」不是一个运行时判断，而是**这份 bundle 是用哪条命令构建的**。
