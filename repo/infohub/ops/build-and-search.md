---
covers:
  - scripts/build-data.ts
  - scripts/build-search.ts
  - scripts/validate.ts
updated: 2026-11-17
---

# Build data and search: shards, then Pagefind

这一页讲发布链路的前三步：两个生成步（`build-data.ts` / `build-search.ts`）与唯一的入参校验步（`validate.ts`）。三者都只读 `cards/`，各自写一个不同目录，互不知道对方存在——顺序由 `export:static` 的 `&&` 串起来，脚本本身不检查前置条件（除了 `build-search` 会检查 `build/` 在不在）。

## build-data：真相 → 万级分片

输入是 `cards/**/*.md`（gray-matter 解析 frontmatter + 正文），输出在 `static/data/`：

```
static/data/
  index.json                     领域清单：id / name / count
  <domain>-summaries.json        每个领域一份列表页数据（CardSummary 数组）
  cards/<domain>/<card_id>.json  每张卡一份详情分片（完整 frontmatter + ext_labels + body）
```

`index.json` 只带 `{domains: [{id, name, count}]}`。`name` 走 `loadDomainMeta(domain).name`，取不到就退回 domain id——`safeMetaName` 用 try/catch 包住，因为领域包缺 `name` 不该让整次构建失败。

`<domain>-summaries.json` 的元素是 `CardSummary`：`card_id` / `title` / `summary` / `confidence` / `last_verified` / `status`。列表页只吃这一份，不读详情分片。

详情分片是 `{...publishable, ext_labels}`：卡片经过 `redactCard` 剥离后的完整对象，加上 `ext` 的中文 label 映射。`ext_labels` 的来源是 `loadDomainSpec(domain).extFields[key].label`，但**跳过 `hiddenExtKeys(domain)`**——敏感字段的中文名也不下发，产物里连「这一列存在」都不说。

`redactCard` 那一步有个必须的细节：`structuredClone`。`card.ext` 与 `result.data.ext` 是同一个引用，就地删敏感字段会连本次校验用的对象一起改掉，后面的逻辑看到的就是被改过的对象。

## 增量还是全量

**每张卡都全量重写，孤儿分片精准清理。** 这是两种极端做法之间的第三选择。

不做「整目录 `rmSync` 再重建」的原因写在注释里：`static/data` 下的分片已是万级，整目录删除会触发 Windows 的批量删除保护，也让增量构建变慢。所以流程改成：

1. 边写边把每个产出文件的相对路径记进 `generated: Set<string>`。
2. 全部写完后 `listJsonFiles(OUT_DIR)` 遍历目录，把不在 `generated` 里的 `.json` 逐个 `unlinkSync`，并计 `orphans`。

后果要说清楚：**手工放进 `static/data` 的 JSON 会被当成孤儿删掉**。这个目录是纯生成物，不要往里放东西。

写盘用 `writeWithRetry`：Windows 上连续写几千个分片会偶发 `UNKNOWN` / `EBUSY`（杀毒、索引、同步进程短暂占用句柄），这几个错误码退避重试（最多 5 次，间隔 50/100/150/200ms，用 `Atomics.wait` 而非 `sleep`），其他错误照抛——不吞错。

## 校验失败不中断

`build-data` 里 frontmatter 不合法、缺 `domain`、schema 校验不过的卡**不写分片、不报错退出**，只打 `[INVALID]` 并累加 `invalid`，最后一行汇总：

```
[build:data] valid=<N> invalid=<M> domains=<D> orphans=<K>
```

退出码恒为 0。所以 `build-data` 失败的唯一形态是抛异常（磁盘、权限）。「有卡没进产物」这件事只有 `validate` 能拦，而 `validate` 在链路里排在它前面——那是唯一的口子：`validate` 先跑，它失败就根本不会到 `build-data`。

另一个静默点：`[WARN] 未声明字段（原样保留）` 只警告不阻断。领域包是建议清单，Agent 可以随时加临时字段，所以未声明字段会**原样进分片**。

## build-search：就一行 pagefind

`build-search.ts` 短到几乎没有逻辑：

```js
if (!existsSync(join(ROOT, 'build'))) {
  console.error('[build-search] build/ 不存在 — 请先执行 vite build');
  process.exit(1);
}
execSync('npx --no-install pagefind --site build --force-language zh', { cwd: ROOT, stdio: 'inherit' });
```

三个点：

- `--no-install` 是关键。没有它，`npx` 在 pagefind 没装时会去联网装一个，构建就变成了有网络依赖的动作。装了才跑，没装直接报错。
- `--force-language zh` 强制中文分词。Pagefind 对 zh 不做 stemming（运行时会打 `Note: Pagefind doesn't support stemming for the language zh`），但语言标记仍然决定分词与高亮方式。
- 没有 `pagefind.yml`。全部行为走命令行参数与 Pagefind 自己的默认值（扫 `build/` 下所有 HTML，输出到 `build/pagefind/`）。

索引产物落在 `build/pagefind/`，里面有 `.pf_meta` / `.pf_fragment` / `.pf_index` 这类分片，以及 wasm。这些扩展名不是标准 MIME——`preview-server.mjs` 专门为 `.pf_*` 前缀做了 `application/json` 映射，否则浏览器拒绝加载。

`execSync` 用 `stdio: 'inherit'`，所以 pagefind 自己的进度与统计直接进终端。它会报 `Indexed N pages` / `Indexed M words` / `Indexed 0 filters` / `Indexed 0 sorts`。**filters 与 sorts 恒为 0**——项目没有在 HTML 里埋 `data-pagefind-filter` / `data-pagefind-sort`，领域筛选走的是列表页自己的 URL 参数，不依赖 Pagefind。

`Did not find a data-pagefind-body element on the site.` 这条警告是常态：没有标记 body 时 Pagefind 索引整页（含导航与页脚），噪声大一些但不会漏内容。

## 耗时参考（2026-11 实测）

来自一次完整的 `export:static` 日志，机器与当时的卡量见 `.tmp-build2.log`：

| 阶段 | 耗时 | 说明 |
| :-- | :-- | :-- |
| `validate` | 秒级 | 纯读 + zod 校验 |
| `build:data` | 数十秒量级 | 主要花在逐分片写盘；Windows 上写句柄争用会明显变慢 |
| `build:site` | **分钟级，是整条链路的大头** | SvelteKit 预渲染每张卡一个页面；`adapter-static` 的 `strict: true` 要求所有路由可预渲染 |
| `build:search` | 十几秒 | Pagefind 扫全部预渲染 HTML |
| `audit:publish` | 十几秒 | 数万探针拼成一条正则扫数万个文件 |

`build:site` 慢的根因是页面数与卡数同阶。所以「改一张卡就想看效果」应该走 `npm start` / `npm run dev`（实时读卡、零构建），而不是跑构建——这是踩坑页第一条的机制解释。

`adapter-node` 侧有个对应优化：`svelte.config.js` 里 `precompress: false`。开着它会为 `build/client` 下每个文件各写 `.gz`/`.br`，在 Windows 上撞 `EMFILE`（实测 `student-*.json.gz`），同时把构建时间拉长一倍。静态导出走 `adapter-static`，那边的预压缩不受影响。

## validate.ts：入参校验与继承链检查

`validate.ts` 做两件事：逐卡 schema 校验，加全领域继承链深度检查。

逐卡部分与 `build-data` 的前半段几乎同构（都读 frontmatter、都 `loadDomainSchema`、都 `safeParse`），但判定口径不同：

| 情况 | validate | build-data |
| :-- | :-- | :-- |
| frontmatter 解析失败 | `[INVALID]` + 计数 | `[INVALID]` + 计数，跳过 |
| 缺 `domain` | `[INVALID]` + 计数 | `[INVALID]` + 计数，跳过 |
| 领域包加载失败 | `[INVALID]` + 计数 | `[INVALID]` + 计数，跳过 |
| schema 校验不过 | `[INVALID]` + **`flatten()` 结构** | 同左，但 `JSON.stringify(..., null, 2)` |
| 未声明字段 | `[WARN]` + `warned++` | `[WARN]`，**不计数** |
| 退出码 | `invalid > 0 ? 1 : 0` | 恒 0 |

`--verbose` 让每张合法卡打一行 `[OK] <rel>`；不加时只打汇总。

继承链部分：对「卡片里出现过的 domain」与 `listAllDomainIds()` 的并集，逐个跑 `domainInheritanceIds(id)`，算 `hops = chain.length - 1`。`hops >= MAX_CHAIN_WARN`（常量 5）时打 `[WARN] <id> 继承链 N 层：a → b → c`，`deepChains++`，但**不失败**——注释写明「再深多半是设计问题，但拆层本身是正常演进」。继承链抛异常也只 `console.warn` 并计入 `deepChains`。

汇总行：

```
[validate] <N> cards, <M> invalid, <K> warned[, <D> deep chains]（需要逐卡结果加 --verbose）
```

退出码 1 时整条 `export:static` 因 `&&` 短路停下。这是发布链路唯一「因为数据本身不合法而拒绝出产物」的地方。
