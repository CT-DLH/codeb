---
covers:
  - src/mcp/lib/collector-runtime.ts
  - src/mcp/lib/conflict.ts
  - src/mcp/lib/dedup.ts
  - src/mcp/lib/llm-client.ts
  - src/mcp/lib/run-registry.ts
  - src/mcp/lib/schema-loader.ts
  - src/mcp/lib/storage.ts
  - src/mcp/tools/card_append.ts
  - src/mcp/tools/card_attach.ts
  - src/mcp/tools/card_batch.ts
  - src/mcp/tools/card_commit.ts
  - src/mcp/tools/card_conflicts.ts
  - src/mcp/tools/card_create.ts
  - src/mcp/tools/card_delete.ts
  - src/mcp/tools/card_derive.ts
  - src/mcp/tools/card_find_similar.ts
  - src/mcp/tools/card_import.ts
  - src/mcp/tools/card_list.ts
  - src/mcp/tools/card_list_domains.ts
  - src/mcp/tools/card_read.ts
  - src/mcp/tools/card_resolve.ts
  - src/mcp/tools/card_schema.ts
  - src/mcp/tools/card_search.ts
  - src/mcp/tools/card_update.ts
  - src/mcp/tools/collect_guide.ts
  - src/mcp/tools/collect_run.ts
  - src/mcp/tools/collect_site.ts
  - src/mcp/tools/domain_create.ts
  - src/mcp/tools/domain_update.ts
  - src/mcp/tools/file_read.ts
  - src/mcp/tools/llm_process.ts
title: MCP Server Module (Layer 3)
updated: 2026-11-24
---

# 模块：MCP 服务——部件细页表（第3层）

**项目**：infohub
**源码文件**：`src/mcp/lib/collector-runtime.ts`、`src/mcp/lib/conflict.ts`、`src/mcp/lib/dedup.ts`、`src/mcp/lib/llm-client.ts`、`src/mcp/lib/run-registry.ts`、`src/mcp/lib/schema-loader.ts`、`src/mcp/lib/storage.ts`、`src/mcp/tools/card_append.ts`、`src/mcp/tools/card_attach.ts`、`src/mcp/tools/card_batch.ts`、`src/mcp/tools/card_commit.ts`、`src/mcp/tools/card_conflicts.ts`、`src/mcp/tools/card_create.ts`、`src/mcp/tools/card_delete.ts`、`src/mcp/tools/card_derive.ts`、`src/mcp/tools/card_find_similar.ts`、`src/mcp/tools/card_import.ts`、`src/mcp/tools/card_list.ts`、`src/mcp/tools/card_list_domains.ts`、`src/mcp/tools/card_read.ts`、`src/mcp/tools/card_resolve.ts`、`src/mcp/tools/card_schema.ts`、`src/mcp/tools/card_search.ts`、`src/mcp/tools/card_update.ts`、`src/mcp/tools/collect_guide.ts`、`src/mcp/tools/collect_run.ts`、`src/mcp/tools/collect_site.ts`、`src/mcp/tools/domain_create.ts`、`src/mcp/tools/domain_update.ts`、`src/mcp/tools/file_read.ts`、`src/mcp/tools/llm_process.ts`
**第4层语义块索引**：
- `src-mcp-lib-collector-runtime.ts`: `../symbols/src-mcp-lib-collector-runtime.ts.md`
- `src-mcp-lib-conflict.ts`: `../symbols/src-mcp-lib-conflict.ts.md`
- `src-mcp-lib-dedup.ts`: `../symbols/src-mcp-lib-dedup.ts.md`
- `src-mcp-lib-llm-client.ts`: `../symbols/src-mcp-lib-llm-client.ts.md`
- `src-mcp-lib-run-registry.ts`: `../symbols/src-mcp-lib-run-registry.ts.md`
- `src-mcp-lib-schema-loader.ts`: `../symbols/src-mcp-lib-schema-loader.ts.md`
- `src-mcp-lib-storage.ts`: `../symbols/src-mcp-lib-storage.ts.md`
- `src-mcp-tools-card_append.ts`: `../symbols/src-mcp-tools-card_append.ts.md`
- `src-mcp-tools-card_attach.ts`: `../symbols/src-mcp-tools-card_attach.ts.md`
- `src-mcp-tools-card_batch.ts`: `../symbols/src-mcp-tools-card_batch.ts.md`
- `src-mcp-tools-card_commit.ts`: `../symbols/src-mcp-tools-card_commit.ts.md`
- `src-mcp-tools-card_conflicts.ts`: `../symbols/src-mcp-tools-card_conflicts.ts.md`
- `src-mcp-tools-card_create.ts`: `../symbols/src-mcp-tools-card_create.ts.md`
- `src-mcp-tools-card_delete.ts`: `../symbols/src-mcp-tools-card_delete.ts.md`
- `src-mcp-tools-card_derive.ts`: `../symbols/src-mcp-tools-card_derive.ts.md`
- `src-mcp-tools-card_find_similar.ts`: `../symbols/src-mcp-tools-card_find_similar.ts.md`
- `src-mcp-tools-card_import.ts`: `../symbols/src-mcp-tools-card_import.ts.md`
- `src-mcp-tools-card_list.ts`: `../symbols/src-mcp-tools-card_list.ts.md`
- `src-mcp-tools-card_list_domains.ts`: `../symbols/src-mcp-tools-card_list_domains.ts.md`
- `src-mcp-tools-card_read.ts`: `../symbols/src-mcp-tools-card_read.ts.md`
- `src-mcp-tools-card_resolve.ts`: `../symbols/src-mcp-tools-card_resolve.ts.md`
- `src-mcp-tools-card_schema.ts`: `../symbols/src-mcp-tools-card_schema.ts.md`
- `src-mcp-tools-card_search.ts`: `../symbols/src-mcp-tools-card_search.ts.md`
- `src-mcp-tools-card_update.ts`: `../symbols/src-mcp-tools-card_update.ts.md`
- `src-mcp-tools-collect_guide.ts`: `../symbols/src-mcp-tools-collect_guide.ts.md`
- `src-mcp-tools-collect_run.ts`: `../symbols/src-mcp-tools-collect_run.ts.md`
- `src-mcp-tools-collect_site.ts`: `../symbols/src-mcp-tools-collect_site.ts.md`
- `src-mcp-tools-domain_create.ts`: `../symbols/src-mcp-tools-domain_create.ts.md`
- `src-mcp-tools-domain_update.ts`: `../symbols/src-mcp-tools-domain_update.ts.md`
- `src-mcp-tools-file_read.ts`: `../symbols/src-mcp-tools-file_read.ts.md`
- `src-mcp-tools-llm_process.ts`: `../symbols/src-mcp-tools-llm_process.ts.md`
**写范围**：src/mcp/**
**验证命令**：`powershell -NoProfile -ExecutionPolicy Bypass -File _kbwork/run_regression.ps1`

## 职责
infohub 对外的 MCP 服务层：把卡片读写、搜索、领域包等能力暴露为 MCP 工具。

## 适用场景
- 需要定位或修改该模块内的源码部件时，先在此页选中部件，再下沉到第4层。
- 需要确认某个文件的语义块清单与行号时，打开对应 `symbols/` 页。

## 功能部件

| 部件 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| `readCapabilities@29` | function | L29-78 | 源清单的唯一真值是插件注册表导出的 collector/capabilities.json（platforms 的键）。 | function readCapabilities(): { all: string[]; search: string… |
| `pythonCandidates@104` | function | L104-125 | 候选解释器。「文件在不在」不够：本机 PATH 上的 python 启动得了，但装的是另一套依赖， | export function pythonCandidates(): Bin[] { |
| `pythonCandidates.push@106` | arrow | L106-109 |  | const push = (bin: string \ |
| `probeScript@128` | arrow | L128-128 |  | const probeScript = (source: string) => `from zhihu_pipe.sou… |
| `isPlainObject@4` | function | L4-6 |  | function isPlainObject(v: unknown): v is Record<string, any>… |
| `expandDotPaths@22` | function | L22-53 | 把「点号路径」的 changes 展开成嵌套结构。 | export function expandDotPaths( |
| `applyChanges@56` | function | L56-69 | 把 changes 应用到 frontmatter：ext 做浅合并，其余键覆盖 | export function applyChanges( |
| `buildDraftContent@72` | function | L72-74 | 生成“应用 changes 之后”的完整文件内容（草稿） | export function buildDraftContent(card: CardRecord, changes:… |
| `SimilarCard@7` | interface | L7-16 |  | export interface SimilarCard { |
| `SimilarQuery@18` | interface | L18-25 |  | export interface SimilarQuery { |
| `DuplicateWarning@27` | interface | L27-36 |  | export interface DuplicateWarning { |
| `aliasPairs@44` | function | L44-58 |  | function aliasPairs(query: SimilarQuery, candidate: Record<s… |
| `loadEnv@7` | function | L7-27 |  | function loadEnv() { |
| `saveCache@38` | function | L38-42 |  | function saveCache() { |
| `callLLM@44` | function | L44-131 |  | export async function callLLM(prompt: string, text: string, … |
| `ActiveRun@12` | interface | L12-22 | 长跑登记表的 TS 侧，契约与 collector/zhihu_pipe/runs.py 逐字一致： | export interface ActiveRun { |
| `pidAlive@26` | function | L26-36 |  | export function pidAlive(pid: unknown): boolean { |
| `runFile@39` | function | L39-42 | run_id 当文件名用（它来自命令行/请求体），消毒后不能越出 active/ | export function runFile(runId: string): string { |
| `registerRun@44` | function | L44-47 |  | export function registerRun(entry: ActiveRun): void { |
| `domainExists@12` | function | L12-14 |  | export function domainExists(domain: string): boolean { |
| `validateFull@17` | function | L17-19 | 全量校验（card_create 用） | export function validateFull(domain: string, fields: Record<… |
| `messageOf@21` | function | L21-24 |  | function messageOf(issue: { message: string; received?: stri… |
| `issueMessage@26` | function | L26-28 |  | function issueMessage(err: z.ZodError): string { |
| `domainDir@19` | function | L19-22 | domain 值 → 卡片目录（与 src/lib/server/card-store.ts 的 domainDir 同一口径）。 | export function domainDir(domain: string): string { |
| `computeRevision@28` | function | L28-30 | 内容哈希（替代 Git blob SHA，零依赖、跨平台） | export function computeRevision(content: string): string { |
| `stableValue@35` | function | L35-45 |  | function stableValue(value: unknown): unknown { |
| `contentFingerprint@51` | function | L51-59 | 内容指纹：frontmatter（忽略 created_at / edited_at，键序无关）+ 正文。 | export function contentFingerprint(frontmatter: Record<strin… |
| `registerCardAppend@6` | function | L6-57 |  | export function registerCardAppend(server: McpServer): void … |
| `fail@38` | function | L38-43 |  | function fail(errors: string[], extra: Record<string, unknow… |
| `registerCardAttach@45` | function | L45-106 |  | export function registerCardAttach(server: McpServer): void … |
| `BatchOp@45` | interface | L45-60 |  | interface BatchOp { |
| `fail@62` | function | L62-67 |  | function fail(errors: string[], extra: Record<string, unknow… |
| `readText@69` | function | L69-71 |  | function readText(path: string): string { |
| `parseOpsFile@73` | function | L73-96 |  | function parseOpsFile(path: string): BatchOp[] { |
| `registerCardCommit@6` | function | L6-78 |  | export function registerCardCommit(server: McpServer): void … |
| `registerCardConflicts@5` | function | L5-27 |  | export function registerCardConflicts(server: McpServer): vo… |
| `resolveInputPath@11` | function | L11-13 | 长文本一律走文件：桥接层对 content 参数里的长字符串转义不可靠 | export function resolveInputPath(filePath: string): string { |
| `errorPayload@15` | function | L15-20 |  | function errorPayload(extra: Record<string, unknown>) { |
| `okPayload@22` | function | L22-26 |  | function okPayload(payload: Record<string, unknown>) { |
| `registerCardCreate@28` | function | L28-101 |  | export function registerCardCreate(server: McpServer): void … |
| `registerCardDelete@5` | function | L5-35 |  | export function registerCardDelete(server: McpServer): void … |
| `fail@12` | function | L12-17 |  | function fail(errors: string[], extra: Record<string, unknow… |
| `shape@20` | function | L20-24 | 样值只给形状不给内容：派生出来的东西经常本身就是敏感信息 | function shape(value: unknown): string { |
| `RuleStat@26` | interface | L26-37 |  | interface RuleStat { |
| `registerCardDerive@39` | function | L39-212 |  | export function registerCardDerive(server: McpServer): void … |
| `registerCardFindSimilar@12` | function | L12-86 |  | export function registerCardFindSimilar(server: McpServer): … |
| `fail@83` | function | L83-88 |  | function fail(errors: string[], extra: Record<string, unknow… |
| `registerCardImport@90` | function | L90-219 |  | export function registerCardImport(server: McpServer): void … |
| `registerCardList@7` | function | L7-110 |  | export function registerCardList(server: McpServer): void { |
| `registerCardListDomains@4` | function | L4-57 |  | export function registerCardListDomains(server: McpServer): … |
| `registerCardRead@5` | function | L5-43 |  | export function registerCardRead(server: McpServer): void { |
| `registerCardResolve@5` | function | L5-60 |  | export function registerCardResolve(server: McpServer): void… |
| `registerCardSchema@6` | function | L6-29 |  | export function registerCardSchema(server: McpServer): void … |
| `registerCardSearch@7` | function | L7-51 |  | export function registerCardSearch(server: McpServer): void … |
| `registerCardUpdate@7` | function | L7-57 |  | export function registerCardUpdate(server: McpServer): void … |
| `QueryGuide@23` | interface | L23-30 |  | interface QueryGuide { |
| `PlatformInfo@32` | interface | L32-36 |  | interface PlatformInfo { |
| `loadCapabilities@38` | function | L38-49 |  | function loadCapabilities(): { platforms: Record<string, Pla… |
| `registerCollectGuide@51` | function | L51-173 |  | export function registerCollectGuide(server: McpServer): voi… |
| `fail@20` | function | L20-25 |  | function fail(errors: string[], extra: Record<string, unknow… |
| `runLabel@28` | function | L28-32 | 登记表里的一条正在跑的任务，写成给人看的一行 | function runLabel(run: ActiveRun): string { |
| `registerCollectRun@34` | function | L34-216 |  | export function registerCollectRun(server: McpServer): void … |
| `registerCollectRun.quote@98` | arrow | L98-98 |  | const quote = (a: string) => (/[\s"]/.test(a) ? `"${a}"` : a… |
| `fail@43` | function | L43-52 |  | function fail( |
| `shown@54` | arrow | L54-54 |  | const shown = (abs: string): string => relative(ROOT, abs).s… |
| `quote@55` | arrow | L55-55 |  | const quote = (arg: string): string => (/[\s"]/.test(arg) ? … |
| `tail@56` | arrow | L56-56 |  | const tail = (text: string, n = 4000): string => (text.lengt… |
| `registerDomainCreate@15` | function | L15-224 |  | export function registerDomainCreate(server: McpServer): voi… |
| `registerDomainCreate.list@127` | arrow | L127-128 |  | const list = (value?: string[]) => |
| `fail@19` | function | L19-21 |  | function fail(text: string) { |
| `formatIssues@23` | function | L23-27 |  | function formatIssues(err: z.ZodError): string { |
| `registerDomainUpdate@29` | function | L29-599 |  | export function registerDomainUpdate(server: McpServer): voi… |
| `registerDomainUpdate.isDeclaredPath@333` | arrow | L333-339 |  | const isDeclaredPath = (path: string) => { |
| `fail@13` | function | L13-18 |  | function fail(errors: string[], extra: Record<string, unknow… |
| `isNumericText@22` | function | L22-24 |  | function isNumericText(text: string): boolean { |
| `isDateText@26` | function | L26-28 |  | function isDateText(text: string): boolean { |
| `profileColumns@31` | function | L31-78 | 每列给一个轻量画像：填了多少、两个样例、类型与风险——映射判断只需要这些 | function profileColumns(columns: string[], rows: Record<stri… |
| `registerLlmProcess@5` | function | L5-31 |  | export function registerLlmProcess(server: McpServer): void … |

> 本模块共 **130** 个语义块，本页只列核心部件；完整清单见各 `symbols/` 页。

## 下沉指引
```
选中部件 → 打开第4层 symbols 文件 → read_block(path="src/mcp/lib/collector-runtime.ts", key="readCapabilities@29")
选中部件 → 打开第4层 symbols 文件 → read_block(path="src/mcp/lib/conflict.ts", key="isPlainObject@4")
选中部件 → 打开第4层 symbols 文件 → read_block(path="src/mcp/lib/dedup.ts", key="SimilarCard@7")
```
