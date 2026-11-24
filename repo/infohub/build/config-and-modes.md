---
covers:
  - svelte.config.js
  - vite.config.ts
  - src/hooks.server.ts
updated: 2026-11-17
---

# Build config: two modes from one codebase

同一个 `src/` 编出两种后端形态，靠的是两个环境变量（`BUILD_MODE`、`--mode static`）和两个 vite `define` 常量（`__BUILD_STATIC__`、`__PROJECT_ROOT__`）。搞错任何一个的表现都不是构建失败，而是「页面能开、数据是旧的」或「找不到 cards/」。

## Two variables, not one, and they are read at different times

| 变量 | 谁读 | 何时读 | 决定 |
| :-- | :-- | :-- | :-- |
| `BUILD_MODE` | `svelte.config.js` | **配置加载时**（构建开始前） | adapter 选 static 还是 node |
| `--mode static` | `vite.config.ts` 的 `mode` 参数 | 构建期 | `__BUILD_STATIC__` 的值 |

两条命令各自配对：

```jsonc
"build:site":   "svelte-kit sync && cross-env BUILD_MODE=static vite build --mode static"
"build:server": "cross-env BUILD_MODE=server vite build"        // 注意：没有 --mode
```

`dev` 两条都没设 —— `BUILD_MODE` 不是 `'server'`，所以 `isStatic` 为 true（adapter-static）；`mode` 是 `'development'`，所以 `__BUILD_STATIC__` 为 false。**dev 下 adapter 与常量是矛盾的**，但 `vite dev` 从不落 adapter 产物，所以这个矛盾永远不会暴露。

`npm run preview` 走 `vite preview`，它需要 `build:server` 的产物（`build/index.js`），不是静态产物。

## svelte.config.js: one ternary

```js
const isStatic = process.env.BUILD_MODE !== 'server';
```

**默认是 static**（`undefined`、空串、`'Static'`、拼错都归到 static）。理由：上线形态更安全，本地形态必须显式要。

```js
adapterStatic({ pages: 'build', assets: 'build', fallback: undefined, strict: true })
adapterNode({ out: 'build', precompress: false })
```

四个细节：

- `fallback: undefined` —— **没有 SPA 兜底**。任何没预渲染的路径就是真 404，这是 `strict: true` 的配套：构建期枚举不到的路由直接让构建失败，而不是上线后静默回落。
- `pages` 与 `assets` 都是 `build` —— 一个目录同时装 HTML 和 `_app/`。
- adapter-node 的 `precompress: false` 是**踩过坑的**：开着它会给 `build/client` 里上万个小文件各写 `.gz`/`.br`，在 Windows 上撞 `EMFILE`（注释点名 `student-*.json.gz`），构建时间还翻倍。本地服务是 node 直出，压缩交给浏览器/反向代理即可。
- 两种 adapter 的 `out` 都是 `build` —— 所以**切换模式必须先清目录或重新构建**，否则两种产物会混在一起（`serve-local.mjs` 只检查 `build/index.js` 存在，不检查它是不是 node 产物）。

## vite.config.ts: two defines, both mandatory

```ts
export default defineConfig(({ mode }) => ({
  plugins: [sveltekit()],
  define: {
    __BUILD_STATIC__: JSON.stringify(mode === 'static'),
    __PROJECT_ROOT__: JSON.stringify(process.cwd())
  }
}));
```

`__BUILD_STATIC__` —— `mode === 'static'` 严格相等。`dev`（`development`）、`build:server`（`production`）、`vite preview` 全是 false。

`__PROJECT_ROOT__` —— `process.cwd()`，**不是** `__dirname` 或 `import.meta.url`。理由是注释写的：打包后代码位置会变，基于 `import.meta.url` 的相对路径会指向 `build/` 内部而找不到 `cards/`。所以必须在构建时把绝对路径固化进去。

后果：**构建目录必须是项目根**。在子目录里跑 `vite build`（哪怕 `--config` 指对了）会把 `__PROJECT_ROOT__` 写成那个子目录，然后所有 `cards/` 读取静默返回空。三个消费方都是先试它、失败才回退 `import.meta.url`：

```ts
const ROOT = typeof __PROJECT_ROOT__ !== 'undefined' && __PROJECT_ROOT__
  ? __PROJECT_ROOT__
  : join(dirname(fileURLToPath(import.meta.url)), '..', '..', '..');
```

`card-store.ts` / `schemas.ts` / `taxonomy/loader.ts` / `server/reports.ts` 四处各写一遍这段。前三处的回退层数不同（`'..','..','..'` vs `'..','..'`），因为它们在源码树里的深度不同 —— 这是重复代码的代价，`reports.ts` 的注释记着「早先只写两层 `..` 得到 `src/`，于是 `reports/` 找不到、列表页永远 0 份」。

TypeScript 侧靠 `src/app.d.ts` 的两条 `declare const` 认识这两个名字。注意它带 `export {}` 结尾，所以是**模块级声明**、没有暴露成全局：`taxonomy/loader.ts` 不得不在文件内自己再 `declare const __PROJECT_ROOT__: string;` 一次，注释写明这是为了让 `svelte-check` 不报 `Cannot find name`。

## hooks.server.ts: 15 lines, one decision

```ts
export async function init() {
  if (__BUILD_STATIC__) return;
  void warmListIndexes();
}
```

这是 SvelteKit 的 `init` 钩子（服务启动时跑一次，不是每请求）。三件事：

- **静态构建下直接返回** —— 预渲染走 `getDomainTable`，没有运行时，预热是纯浪费（而且 `warmListIndexes` 会真去建 13 个领域的索引，在构建期白烧几十秒）。
- **不 `await`** —— 首屏要的是「点进来就有热索引」，不是「启动慢两秒」。注释：「真赶上还在预热时，同域的请求会自动排到那次构建之后」——这句依赖 `card-store` 的 `listBuilds: Map<domain, Promise<ListIndex>>`。
- 没有 `handle` 钩子，**完全不做请求拦截**：没有 CSP、没有鉴权、没有日志、没有 `event.locals`。所以本地服务的安全性完全依赖 `HOST` 绑定（见 `infohub/reader/sensitive-and-publish`）。

## What actually forks in the code

`__BUILD_STATIC__` 在这 7 处被读，每处都是一个编译期分支：

| 位置 | 静态分支 | server 分支 |
| :-- | :-- | :-- |
| `routes/+layout.ts` | `prerender = true` | `prerender = false` |
| `routes/[domain]/+page.server.ts` | 不看 URL，`getDomainTable` 全表 | 解析 URL，`queryDomainList` 分页 |
| `routes/api/search/+server.ts` | 返回 `{query:'',results:[]}` 空壳 | 实时 `searchCards` |
| `routes/api/assistant/+server.ts` | 返回不可用壳 | 调 LLM |
| `routes/api/domains` / `api/cards/*` | `prerender` 跟随 | `prerender = false` |
| `routes/reports/*` | `prerender` 跟随 | 每次请求重扫目录 |
| `hooks.server.ts` | 跳过预热 | `warmListIndexes()` |

前端组件里另有两处 `$lib` 层的读（`[domain]/+page.svelte` 的 `AI_AVAILABLE`、`+page.svelte` 的搜索分支）——它们在客户端 bundle 里被折叠成常量，所以**静态产物里那段服务端检索代码是死代码，会被 tree-shake 掉**。

`sensitive.ts` 的 `showSensitive()` 也读它，但它多一层：显式 env 优先，且 `typeof` 探不到时返回 false。

## The prerender enumeration contract

静态构建时，每个动态路由**必须**能枚举出全部实例，否则 `strict: true` 让构建失败。三处 `entries()`：

```ts
// routes/[domain]/+page.server.ts —— 含抽象父包（/person 这类也是真实页面，漏了就 404）
listAllDomainIds().map(domain => ({ domain }))

// routes/[domain]/[card_id]/+page.server.ts
await listAllEntries()      // 遍历 13 个领域 × getSummaries

// routes/api/cards/[domain]/index.json
listDomainIds().map(domain => ({ domain }))
```

`[card_id]` 那条是**全站最贵的一次枚举**：`listAllEntries()` 把全库卡片扫一遍，然后为每张卡预渲染一个 HTML + 一个 `/api/cards/...` JSON（后者由 `api/cards/[domain]/[card_id]` 的 `entries()` 再枚举一次）。两次枚举各自独立，不能共享。

新增路由时漏写 `entries()` 或 `prerender`，构建会明确报错 —— 这是这个项目里少数**不会静默失败**的地方。

## Static data shards are a second, independent export

`scripts/build-data.ts` 与 SvelteKit 构建**没有关系**：它自己 glob `cards/**/*.md`，逐个 `loadDomainSchema` + `safeParse`，然后写 `static/data/`：

```
static/data/index.json                              {domains: [{id,name,count}]}
static/data/<domain>-summaries.json                  CardSummary[]
static/data/cards/<domain>/<card_id>.json            完整卡 + ext_labels
```

实测 **13946 个文件**。四条实现约束：

- **不整目录 `rmSync`** —— 100+ 个分片整目录删除会触发批量删除保护、也让增量构建变慢。改成「覆盖写入 + 精准清理孤儿分片」：先记 `generated` 集合，结束时删掉不在集合里的 JSON。
- **`writeWithRetry`** —— Windows 上连续写几千个分片会偶发 `UNKNOWN`/`EBUSY`（杀毒、索引、同步进程短暂占用句柄），退避重试 5 次（`50ms × (attempt+1)`，用 `Atomics.wait` 而非 `setTimeout` 同步等待）。真正的权限/路径错误照抛，不吞错。
- **`structuredClone`** —— 注释：`card.ext` 与 `result.data.ext` 是同一个引用，就地删敏感字段会连本次校验用的对象一起改掉。
- **`collectUnknownFields` 只 `console.warn`**，未声明字段原样保留。

`src/lib/data.ts` 的 `fetchIndex` / `fetchSummaries` / `fetchCard` 是这套分片的客户端读取器 —— **但全仓无人调用**。页面实际走的是 `/api/cards/...`，所以 `static/data/` 目前只是「被生成的产物」，不是「被消费的产物」。这是一处明显的冗余：`export:static` 的耗时里有一大半花在写 13946 个它用不到的文件上（同时也进入 git 工作树）。

## Pagefind runs after the build, not inside it

```jsonc
"build:search": "tsx scripts/build-search.ts"
// → execSync('npx --no-install pagefind --site build --force-language zh')
```

三条约束：`--no-install`（不许网络安装，pagefind 在 devDependencies 里）、`--force-language zh`（中文分词，不设等于按英文切）、`--site build`（扫 SvelteKit 的产物目录，不扫 `static/`）。`build/` 不存在时脚本直接 `exit(1)`。

`audit:publish` 在它之后跑，且**不扫** `pagefind/` —— 索引是 brotli 压缩的，读不出明文；而它的输入只有 HTML，HTML 干净索引就干净。

## The export chain and its order

```jsonc
"export:static": "npm run validate && npm run build:data && npm run build:site && npm run build:search && npm run audit:publish"
```

五步的顺序是**语义顺序**，不能重排：

1. `validate` —— 卡片与领域包先过 Zod，坏数据在这里就停。
2. `build:data` —— 写 `static/data/` 分片（静态资源，必须先于 site）。
3. `build:site` —— `svelte-kit sync` + `vite build --mode static`，产出 `build/`。
4. `build:search` —— Pagefind 扫 `build/`。
5. `audit:publish` —— 扫 `build/`，命中敏感值就失败。

`"build": "npm run export:static"` 是别名，`"build:local": "npm run export:static:local"` 是带 `INFOHUB_SENSITIVE=1` 的版本（**三步都带**：build:data、build:site、build:search）。本地口径核对完必须跑一次 `npm run build:data` 复位，否则 `static/data/` 里留着带明文的分片。

`npm start` 完全不在这条链上：它只要求 `build/index.js` 存在，否则打印提示并 `exit(1)`。`start.bat` 会先跑 `scripts/needs-build.mjs` 判断要不要 `npm run build:server`，再 `set HOST=127.0.0.1` 后调 `serve-local.mjs`。

## Node version and one packaging trap

`start.bat` 里有一段 node 探测：先 `where node`，失败则回退硬编码的 `C:\Users\30520\.workbuddy\binaries\node\versions\22.22.2-6\node.exe`，再验证 `node -v`。这是单机脚本，不是可移植的启动器——换机器必须改那行路径。

`package.json` 里 `"type": "module"`，所以 `.js` 文件按 ESM 解析；`scripts/*.cjs` 是那个年代留下的 CommonJS（`_dep.cjs`、`_filter.cjs`、`_idstat.cjs`、`_scan.cjs`、`analyze-guidebooks.cjs` 等）。`tsx` 跑的 `.ts` 脚本走 ESM，可以直接 `import` 这些 `.cjs` 吗——不行，需要 `createRequire`；现有脚本没有这么用的。
