---
covers:
  - src/lib/blank.ts
  - src/lib/data.ts
  - src/lib/list-sort.ts
  - src/lib/markdown.ts
  - src/lib/schemas.ts
  - src/lib/sensitive.ts
  - src/lib/server/card-store.ts
  - src/lib/server/reports.ts
  - src/lib/taxonomy/loader.ts
  - src/lib/taxonomy/tree-core.ts
  - src/lib/types.ts
title: Frontend Library Module (Layer 3)
updated: 2026-11-24
---

# 模块：前端库——部件细页表（第3层）

**项目**：infohub
**源码文件**：`src/lib/blank.ts`、`src/lib/data.ts`、`src/lib/list-sort.ts`、`src/lib/markdown.ts`、`src/lib/schemas.ts`、`src/lib/sensitive.ts`、`src/lib/server/card-store.ts`、`src/lib/server/reports.ts`、`src/lib/taxonomy/loader.ts`、`src/lib/taxonomy/tree-core.ts`、`src/lib/types.ts`
**第4层语义块索引**：
- `src-lib-blank.ts`: `../symbols/src-lib-blank.ts.md`
- `src-lib-data.ts`: `../symbols/src-lib-data.ts.md`
- `src-lib-list-sort.ts`: `../symbols/src-lib-list-sort.ts.md`
- `src-lib-markdown.ts`: `../symbols/src-lib-markdown.ts.md`
- `src-lib-schemas.ts`: `../symbols/src-lib-schemas.ts.md`
- `src-lib-sensitive.ts`: `../symbols/src-lib-sensitive.ts.md`
- `src-lib-server-card-store.ts`: `../symbols/src-lib-server-card-store.ts.md`
- `src-lib-server-reports.ts`: `../symbols/src-lib-server-reports.ts.md`
- `src-lib-taxonomy-loader.ts`: `../symbols/src-lib-taxonomy-loader.ts.md`
- `src-lib-taxonomy-tree-core.ts`: `../symbols/src-lib-taxonomy-tree-core.ts.md`
- `src-lib-types.ts`: `../symbols/src-lib-types.ts.md`
**写范围**：src/lib/**
**验证命令**：`powershell -NoProfile -ExecutionPolicy Bypass -File _kbwork/run_regression.ps1`

## 职责
SvelteKit 前端共享库：数据访问、Markdown 渲染、排序、schema、敏感词与分类树。

## 适用场景
- 需要定位或修改该模块内的源码部件时，先在此页选中部件，再下沉到第4层。
- 需要确认某个文件的语义块清单与行号时，打开对应 `symbols/` 页。

## 功能部件

| 部件 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| `isBlank@7` | function | L7-13 | 空值语义统一：缺失 / null / "" / [] / {} 一律视为「未填」。 | export function isBlank(v: unknown): boolean { |
| `getJson@3` | function | L3-9 |  | async function getJson<T>(url: string): Promise<T> { |
| `fetchIndex@12` | function | L12-14 | 领域索引：GET /data/index.json | export function fetchIndex(): Promise<DomainIndex> { |
| `fetchSummaries@17` | function | L17-19 | 某领域的全部卡片摘要：GET /data/{domain}-summaries.json | export function fetchSummaries(domain: string): Promise<Card… |
| `fetchCard@22` | function | L22-24 | 单卡完整详情（按需加载）：GET /data/cards/{domain}/{cardId}.json | export function fetchCard(domain: string, cardId: string): P… |
| `listSortKey@24` | function | L24-48 | 一行的排序键。空值返回 null，调用方据此把空值恒排最后（不随升降序翻转： | export function listSortKey(row: ListRow, col: string): stri… |
| `compareKeys@50` | function | L50-60 |  | function compareKeys(a: string \ |
| `listRowComparator@71` | function | L71-85 | 行比较器：format 取领域包声明的列格式（date 走 ISO 文本序，不走中文拼音序）。 | export function listRowComparator(col: string, dir: 'asc' \ |
| `escapeAttr@27` | arrow | L27-28 | - 知道原文地址 → 按原文地址解析成绝对链接（点出去才是该去的地方）； - 不知道 → 去掉 href 变成不可跳转的文本，原路径留在 t… | const escapeAttr = (text: string): string => |
| `isRelative@31` | arrow | L31-37 |  | const isRelative = (href: unknown): href is string => |
| `resolve@39` | function | L39-46 |  | function resolve(href: string, baseUrl: string \ |
| `renderMarkdown@93` | function | L93-95 | @param source 卡片正文（非字符串按空处理） @param baseUrl 原文的绝对地址（卡片的 source_ref 或 e… | export function renderMarkdown(source: unknown, baseUrl?: st… |
| `DeriveRule@23` | interface | L23-30 | 派生字段规则（见 src/core/derive.ts 的 applyDerives） | export interface DeriveRule { |
| `FieldSpec@32` | interface | L32-70 |  | export interface FieldSpec { |
| `buildShape@72` | function | L72-78 |  | function buildShape(fields: Record<string, FieldSpec>): Reco… |
| `buildZodFromSpec@81` | function | L81-109 | 递归地把 YAML 字段规格转换为 Zod 类型（不硬编码任何字段名） | export function buildZodFromSpec(spec: FieldSpec): z.ZodType… |
| `envRaw@28` | function | L28-31 | 客户端 bundle 里可能没有 process，所以取值要兜底 | function envRaw(): string \ |
| `localRuntime@38` | function | L38-40 | 确知是本地运行形态吗：dev 与 build:server 注入 false，静态发布注入 true。 | function localRuntime(): boolean { |
| `showSensitive@43` | function | L43-46 | 本次运行是否输出敏感字段：显式环境变量优先，否则按运行形态（本地显示 / 发布剥离） | export function showSensitive(env: string \ |
| `specOf@49` | function | L49-55 | 缓存到领域包 mtime 之外不需要——只在构建/请求路径上跑一次，成本可忽略 | function specOf(domain: string): DomainSpec \ |
| `domainDir@51` | function | L51-54 | domain 值 → 卡片目录（2026-11-05 三卡制迁移：目录改成三层 | function domainDir(domain: string): string { |
| `dirMtime@64` | function | L64-77 | 递归取目录下所有文件的最大 mtime。 | function dirMtime(dir: string): number { |
| `yamlMtime@79` | function | L79-85 |  | function yamlMtime(domain: string): number { |
| `cacheMtime@88` | function | L88-90 | 卡片或领域包任一变化都让缓存失效 | function cacheMtime(domain: string): number { |
| `ReportMeta@28` | interface | L28-42 |  | export interface ReportMeta { |
| `Report@44` | interface | L44-46 |  | export interface Report extends ReportMeta { |
| `parseFrontmatter@53` | function | L53-99 | 极简 frontmatter 解析：只认 key: "value" / key: N / key:\n - "item" 三种形态。 | function parseFrontmatter(raw: string): { meta: Record<strin… |
| `toMeta@101` | function | L101-116 |  | function toMeta(slug: string, meta: Record<string, any>, bod… |
| `Taxonomy@37` | interface | L37-41 |  | export interface Taxonomy { |
| `RawNode@44` | interface | L44-51 | YAML 一份文档里的 nodes 数组条目（宽松取值，逐字段归一化） | interface RawNode { |
| `readNodes@53` | function | L53-65 |  | function readNodes(file: string): TaxonomyNodeInput[] { |
| `loadTaxonomy@70` | function | L70-77 | 加载三份 YAML，构建索引并校验。结果缓存；返回 problems 而不抛错。 | export function loadTaxonomy(): Taxonomy { |
| `TagId@24` | interface | L24-30 |  | export interface TagId { |
| `TaxonomyNodeInput@36` | interface | L36-44 | YAML 里的一条节点。parent 用完整 ID，而不是相对名——跨 namespace 时相对名会撞。 | export interface TaxonomyNodeInput { |
| `TaxonomyTreeNode@46` | interface | L46-48 |  | export interface TaxonomyTreeNode extends TaxonomyNodeInput … |
| `TaxonomyTree@50` | interface | L50-55 |  | export interface TaxonomyTree { |
| `Card@8` | interface | L8-10 | 完整卡片 = 结构化字段 + Markdown 正文 | export interface Card extends CardFields { |
| `CardSummary@13` | interface | L13-22 | 汇总表用的轻量摘要 | export interface CardSummary { |
| `DomainIndexEntry@24` | interface | L24-28 |  | export interface DomainIndexEntry { |
| `DomainIndex@30` | interface | L30-32 |  | export interface DomainIndex { |

> 本模块共 **184** 个语义块，本页只列核心部件；完整清单见各 `symbols/` 页。

## 下沉指引
```
选中部件 → 打开第4层 symbols 文件 → read_block(path="src/lib/blank.ts", key="isBlank@7")
选中部件 → 打开第4层 symbols 文件 → read_block(path="src/lib/data.ts", key="getJson@3")
选中部件 → 打开第4层 symbols 文件 → read_block(path="src/lib/list-sort.ts", key="listSortKey@24")
```
