---
covers:
  - package.json
updated: 2026-11-17
---

# npm scripts: what each one really runs

`package.json` 的 script 分三类，判据是「谁会重复跑它」：**日常动作**（改完就看）、**发布动作**（一次跑完整链路）、**一次性任务入口**（各自独立，跑完手动接下一步）。第三类占了绝大多数，它们不构成流水线，互相之间没有依赖。script 总数不在这里记——`package.json` 是唯一真源。

## 日常动作

| script | 展开后实际执行 | 说明 |
| :-- | :-- | :-- |
| `npm start` | `node scripts/serve-local.mjs` | 读 `build/index.js`（adapter-node 产物），带敏感字段值、只绑 127.0.0.1。**必须先有 `build:server` 产物**，否则脚本自己 `exit 1`。 |
| `npm run dev` | `vite dev` | SvelteKit dev server，每次请求实时读 `cards/`。改卡刷新即见。 |
| `npm run mcp` | `tsx src/mcp/server.ts` | stdio MCP server，供 MCP 客户端连接。工具清单以 `listTools()` 返回为准，不要背数量（`test:mcp` 的第一条断言就是工具名全排列，它才是真源）。 |

`start.bat` 是 `npm start` 的壳：它先跑 `scripts/needs-build.mjs` 判断是否要重建，必要时 `npm run build:server`，再杀掉占用端口的旧进程，最后 `node scripts/serve-local.mjs`。批处理里不写中文（OEM codepage 会截断字符）。

## 发布链路：export:static

```
npm run build   →  npm run export:static
                    ├── npm run validate          → tsx scripts/validate.ts
                    ├── npm run build:data        → tsx scripts/build-data.ts
                    ├── npm run build:site        → svelte-kit sync && BUILD_MODE=static vite build --mode static
                    ├── npm run build:search      → tsx scripts/build-search.ts（内部 npx pagefind）
                    └── npm run audit:publish     → tsx scripts/audit-publish.ts
```

**顺序不可重排**，每步都有强前置依赖：

1. `validate` 卡在第一步：frontmatter 不合法就不该进入任何产物。失败即整条链路停（非零退出码，`&&` 短路）。
2. `build:data` 必须在 `build:site` **之前**：它写的是 `static/data/` 分片，而 `vite build --mode static` 会把这些 `static/` 下的文件当静态资源拷进 `build/`。反过来跑，产物里的分片就是上一次的旧数据。
3. `build:site` 必须在 `build:search` **之前**：Pagefind 扫的是 `build/` 目录本身（`--site build`）。`build-search.ts` 第一件事就是 `existsSync(build)`，不存在直接 `exit 1` 并提示「请先执行 vite build」。
4. `audit:publish` 必须**最后**：它扫的是完整产物，包括 `build:search` 生成的索引之外的 HTML 与 JSON。放中间等于放行后两步可能引入的泄漏。

`build:site` 内部的 `BUILD_MODE=static` 是给 `svelte.config.js` 看的——它决定用 `adapter-static` 还是 `adapter-node`；`--mode static` 是给 `vite.config.ts` 看的——它把 `__BUILD_STATIC__` 注入成 `true`。两个信号缺一不可：`BUILD_MODE` 管产物形态，`__BUILD_STATIC__` 管敏感字段口径（`true` → 剥离）。

`build:data` 与 `build:search` 都要显式跑，`vite build` **不会**自动触发它们。这是最容易漏的一环：只跑 `build:site` 能出一个「看起来完整」的 `build/`，但里面没有 `data/` 分片、没有搜索索引，也没有门禁。

## 本地核对链路：export:static:local

```
npm run build:local  →  npm run export:static:local
                         ├── cross-env INFOHUB_SENSITIVE=1 npm run build:data
                         ├── cross-env INFOHUB_SENSITIVE=1 npm run build:site
                         ├── cross-env INFOHUB_SENSITIVE=1 npm run build:search
                         └── npm run audit:publish:local
                              └── cross-env INFOHUB_SENSITIVE=1 tsx scripts/audit-publish.ts
```

与部署链路的**三处实质差异**，不是简单的环境变量叠加：

1. **没有 `validate`**。本地核对的前提是「产物对不对」，不是「数据合不合法」——带上 `validate` 会让一次字段实验因为别处的历史脏卡而跑不起来。
2. `INFOHUB_SENSITIVE=1` 逐个前缀加在 `build:data` / `build:site` / `build:search` 上，而不是加在整条 chain 上。因为它是 npm script 的 `cross-env` 前缀，能压过的只有被它包住的那一条；写成 `cross-env INFOHUB_SENSITIVE=1 npm run export:static` 会因为内层 script 重新起进程而失效。
3. 门禁换成 `audit:publish:local`，判定方向**反过来**：不是「值必须找不到」，而是「值必须找得到」。目的防的是另一种事故——标记生效了但数据被弄丢，页面上少了一列而没人发现。

核对完必须复位：`npm run build:data`（**不带**环境变量）把 `static/data/` 重写成剥离版。这条没做，下一次 commit 就会把带值的分片带进版本库——`static/data/` 是 git 跟踪的。

## audit:publish 在链路里的位置与它是唯一门禁这件事

`audit:publish` 是整条链路唯一会因为「内容不对」而失败的一步。它的判定侧写在产物侧而非代码侧：拿 `cards/` 里**标记了 `sensitive: true` 的字段真值**当探针，逐个在 `build/` 里搜。

它**不检查**「有没有跑过 build:site」「分片是不是新的」——这些是顺序问题，脚本管不了。所以踩坑页记的那条「跳过门禁只跑 build:site」在机制上无法由脚本自证：一旦拆开跑，门禁根本不执行，退出码永远是 0。

`deploy.yml` 走的是 `npm run build`（即 `export:static`），所以 CI 上有门禁；但本地手动跑 `build:site` 时没有。

## 危险动作分级

| 级别 | script | 会动什么 | 可逆性 |
| :-- | :-- | :-- | :-- |
| 覆写 build/ | `build:site` / `build:server` / `build:static` | 整个 `build/` 目录被 vite 重建 | 可重建，非数据损失 |
| 覆写 static/data | `build:data` | 覆盖全部分片 JSON 与 `index.json`，并**删除孤儿分片**（上次生成、这次不存在的） | 可重建；但带 `INFOHUB_SENSITIVE=1` 跑过一次就在磁盘上留过明文，git 里也可能已有 |
| 写全站产物 | `export:static` / `export:static:local` | 上两项全部 | 同上 |
| 覆盖部署语义 | `export:static:local` | 让 `static/data` 与 `build` 都带敏感真值 | **必须手动复位**，否则下次 commit 污染版本库 |

`build:data` 的孤儿清理需要单独说：它不 `rmSync` 整个 `static/data`（那个目录的分片数量已到万级，整目录删除会触发 Windows 批量删除保护，也让增量构建变慢），而是先记下本次生成的文件集合 `generated`，最后遍历目录删掉不在集合里的 JSON。所以**手工放进 `static/data` 的文件会被删**。

## 一次性入口（按用途）

| script | 展开 | 危险度 |
| :-- | :-- | :-- |
| `validate` | `tsx scripts/validate.ts`，可加 `--verbose` | 只读 |
| `build:data` | `tsx scripts/build-data.ts` | 覆写 `static/data/` |
| `build:search` | `tsx scripts/build-search.ts` | 覆写 `build/pagefind/` |
| `audit:publish` / `audit:publish:local` | 同上 + `INFOHUB_SENSITIVE=1` | 只读，但失败会阻断 |
| `sync` | `svelte-kit sync` | 只写 `.svelte-kit/` |
| `preview` | `vite preview` | 只读，但起的是 vite 内置 server（不是 `scripts/preview-server.mjs`） |
| `migrate:ids` | `tsx scripts/migrate-card-ids.ts`，位置参数 = domain，`--apply` 落盘 | 默认 dry-run；`--apply` 会**重命名/删除卡文件** |
| `migrate:conflicts` | `tsx scripts/migrate-conflicts.ts`，位置参数 = domain（可省），`--apply` / `--json` | 默认 dry-run |
| `migrate:award` | `tsx scripts/migrate-award-to-student.ts`，`--apply` | 默认 dry-run；`--apply` 会把 award 卡**移入 `.trash/`** 并删目录 |
| `backfill:body` | `tsx scripts/backfill-source-body.ts`，位置参数 = domain，默认 `thesis`，`--apply` | 默认 dry-run |
| `backfill:timestamps` | `tsx scripts/backfill_timestamps.ts`，`--domain X`、`--apply` | 默认 dry-run |
| `collect:export` | `tsx scripts/collect-export.ts`，`--mode enrich\|index`、`--out`、`--urls-file` | 只写 `inbox/*.jsonl` |
| `collect:enrich` | `tsx scripts/collect-enrich.ts`，`--limit` / `--source` / `--backend` / `--delay` / `--retry` / `--dry-run` / `--max-updates` / `--domain` | **会写卡**（走 `importTable`，不经 `--write` 开关） |
| `collect:loop` | `tsx scripts/zhihu-enrich-loop.ts`，`--minutes` / `--gap-min` / `--batch` / `--drain-batch` / `--window-hours` / `--platform` / `--backend` | **会写卡**，且长跑 |
| `collect:site` | `tsx scripts/mcp-tool.ts collect_site` | **这条是坏的**（2026-11 实测）：`mcp-tool.ts` 要两个位置参数（toolName + args.json 路径），这里只给了一个，`exit 2` 打用法。真正调用要 `npx tsx scripts/mcp-tool.ts collect_site inbox/site-args.json` |
| `mentor:papers` | `tsx scripts/mentor-papers-summary.ts`，`--dry-run` / `--limit` / `--only` / `--force` / `--max-writes`（默认 20） | **直接写卡 frontmatter 与正文小节** |
| `paper:export` | `tsx scripts/paper-summary-export.ts` | 只写 `inbox/paper-summaries.jsonl` |
| `paper:cnki` | `tsx scripts/paper-cnki-summary.ts`，`--limit` / `--dry-run` / `--write` / `--backend` | 默认只预演，`--write` 才落卡 |
| `paper:title-fix` | `tsx scripts/paper-title-fix.ts`，`--apply` / `--only` | 默认 dry-run |
| `crawl:export` | `tsx scripts/crawl-export.ts`，`--config` / `--db` / `--out` | 只写 `inbox/crawl-*.jsonl` |
| （无 script） | `tsx scripts/apply-paper-summaries.ts` | 直接改卡，读 `inbox/paper-summaries.jsonl` 的 `op=update` 行 |
| `test:*` 系列 | 见测试矩阵页 | 除 `mcp-smoke-test` 外只读或自清理夹具 |
| `audit:profiles` | `tsx scripts/profile-audit.ts [dir]`，**默认 `cards/student` 已失效**（三卡制后是 `cards/info/student`），要么传参要么改默认 | 只读 |
| `scan:pii` | `tsx scripts/scan-collector-pii.ts` | 只读，扫 `collector/data/{raw,out}` |
| `attach:check` | `tsx scripts/attach-check.ts` | 只读，但依赖 `raw/综合毕设指导书` 语料 |
| `prepare:courses` | `tsx scripts/prepare-courses.ts [src] [out]`，默认 `raw/课程大纲` → `inbox/courses.jsonl` | 写 `inbox/`、调用 Word COM 转换 `.doc` |
| `import:jsonl` | `tsx scripts/import-jsonl.ts <jsonl> <domain> [--write] [--merge] [--max-updates N]` | 默认 dry-run，`--write` 才落卡 |
| `mcp:tool` | `tsx scripts/mcp-tool.ts <toolName> <args.json>` | 取决于被调工具 |
| `console` | `tsx console/server.ts` | 起采集控制台（HTTP） |

## 两个不成文约定

`npm run <script> -- <args>` 里的 `--` 必须留：npm 会把 `--` 之后的参数原样透传，不加就会被 npm 自己吃掉。`migrate:ids -- thesis --apply` 和 `migrate:ids thesis` 是两种不同结果。

`cross-env` 只用于 Windows 兼容。项目里所有需要设环境变量的地方都走它，`export:static:local` 与 `audit:publish:local` 是仅有的两处。
