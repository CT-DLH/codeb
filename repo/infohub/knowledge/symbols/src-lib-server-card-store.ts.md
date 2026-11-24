---
covers:
  - src/lib/server/card-store.ts
title: Semantic block index: card-store.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：card-store.ts（第4层）

**源码文件**：`src/lib/server/card-store.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="src/lib/server/card-store.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| domainDir@51 | function | L51-54 | domain 值 → 卡片目录（2026-11-05 三卡制迁移：目录改成三层 | function domainDir(domain: string): string { |
| dirMtime@64 | function | L64-77 | 递归取目录下所有文件的最大 mtime。 | function dirMtime(dir: string): number { |
| yamlMtime@79 | function | L79-85 |  | function yamlMtime(domain: string): number { |
| cacheMtime@88 | function | L88-90 | 卡片或领域包任一变化都让缓存失效 | function cacheMtime(domain: string): number { |
| bumpDomain@109 | function | L109-118 |  | function bumpDomain(domain: string, file?: string): void { |
| resetDomain@121 | function | L121-126 | 不知道具体哪个文件变了（watch 没给文件名）：整域逐文件缓存作废 | function resetDomain(domain: string): void { |
| bumpAll@128 | function | L128-130 |  | function bumpAll(): void { |
| ensureWatcher@132 | function | L132-167 |  | function ensureWatcher(): void { |
| currentEpoch@169 | function | L169-171 |  | function currentEpoch(domain: string): number { |
| cacheFresh@174 | function | L174-193 | 缓存是否仍然新鲜（watcher 模式下不 stat；60 秒兜底或 watch 不可用时才比 mtime） | function cacheFresh( |
| pickByPath@196 | function | L196-198 | 按 ext.milestones 这类路径取嵌套值 | function pickByPath(obj: any, path: string): unknown { |
| CacheEntry@200 | interface | L200-206 |  | interface CacheEntry { |
| listDomainIds@214 | function | L214-216 | 可落卡的领域 ID（排除 _ 开头与 abstract 父包——父包只供继承，不进导航/API） | export function listDomainIds(): string[] { |
| listAllDomainIds@224 | function | L224-230 | 全部领域包 ID（含抽象父包），供首页组树用。 | export function listAllDomainIds(): string[] { |
| DomainIndexEntry@233 | interface | L233-242 | 领域索引：id + 中文名 + 卡片数（供首页与导航使用） | export interface DomainIndexEntry { |
| getDomainIndex@253 | function | L253-276 | 领域索引：扁平数组（含抽象父包），前端自己按 parent 组树。 | export function getDomainIndex(): DomainIndexEntry[] { |
| leafDescendants@283 | function | L283-298 | 某个领域包下的所有可落卡后代（不含自己）。 | function leafDescendants( |
| getDomainChain@307 | function | L307-327 | 继承链（叶 → 根），给详情页顶部那行面包屑用： | export function getDomainChain(domainId: string): Array<{ id: string; … |
| countCardFiles@329 | function | L329-335 |  | function countCardFiles(domain: string): number { |
| scanDomain@348 | function | L348-423 | 扫描领域内卡片。 | async function scanDomain( |
| scanDomain.worker@373 | arrow | L373-412 |  | const worker = async () => { |
| getSummaries@426 | function | L426-450 | 领域内全部卡片摘要（带 mtime 缓存） | export async function getSummaries(domain: string): Promise<CardSummar… |
| FilterFacet@454 | interface | L454-458 |  | export interface FilterFacet { |
| DomainTable@460 | interface | L460-469 |  | export interface DomainTable { |
| TableCacheEntry@471 | interface | L471-477 |  | interface TableCacheEntry { |
| resolveFieldSpec@485 | function | L485-494 | 按 ext.foo.bar 路径在领域包里找字段定义（含数组 item.fields） | function resolveFieldSpec(spec: DomainSpec, path: string): FieldSpec \… |
| DomainPlan@500 | interface | L500-509 | 列表页的「列规划」：加载哪些列、每列中文名/格式/值映射、哪些列可做分面。 | interface DomainPlan { |
| planDomain@511 | function | L511-550 |  | function planDomain(domain: string): DomainPlan { |
| facetValues@553 | function | L553-562 | 这一行的分面值：数组展开、对象（已解析的关联卡引用）不参与分面 | function facetValues(row: Record<string, any>, col: string): string[] … |
| resolveRefValue@568 | function | L568-591 | 关联卡片引用（mentor/mentor-001 → { label: '陈清财', link: '/mentor/mentor-001' }）。 | function resolveRefValue(val: any): any { |
| projectRow@594 | function | L594-608 | 一张卡的 frontmatter → 一条列表行（投影 + 敏感剥离 + 关联标题解析） | function projectRow(domain: string, plan: DomainPlan, data: Record<str… |
| loadListRows@611 | function | L611-625 | 领域内全部列表行（并行读 + 逐文件解析缓存） | async function loadListRows( |
| buildFacets@630 | function | L630-647 |  | function buildFacets(plan: DomainPlan, rows: Array<Record<string, any>… |
| getDomainTable@652 | function | L652-670 | 列表页全表：静态导出与 AI 助手用；在线列表走 queryDomainList 的分页索引。 | export async function getDomainTable(domain: string): Promise<DomainTa… |
| GroupTable@688 | interface | L688-694 |  | export interface GroupTable extends DomainTable { |
| getGroupTable@704 | function | L704-749 | 抽象父包的聚合表：把 extends 往下的所有可落卡域的卡混在一起。 | export async function getGroupTable(abstractId: string, limit = GROUP_… |
| getGroupTable.when@726 | arrow | L726-726 | 新的在前；旧卡没有 collected_at，退回 last_verified，两者都没有的排末尾 | const when = (row: Record<string, any>) => String(row.collected_at ?? … |
| ListIndex@769 | interface | L769-791 |  | interface ListIndex { |
| newListIndex@801 | function | L801-820 |  | function newListIndex(plan: DomainPlan): ListIndex { |
| markPending@822 | function | L822-825 |  | function markPending(domain: string, file: string): void { |
| markStale@827 | function | L827-832 |  | function markStale(domain: string): void { |
| dropCard@834 | function | L834-856 |  | function dropCard(index: ListIndex, id: string): void { |
| addCard@858 | function | L858-875 |  | function addCard(index: ListIndex, file: string, row: Record<string, a… |
| readRows@878 | function | L878-892 | 读一批卡 → 列表行；读不到（被删/解析坏）按删除处理 | async function readRows(domain: string, plan: DomainPlan, files: strin… |
| applyFiles@895 | function | L895-909 | 一次性落地：请求要么看到旧行、要么看到新行，不会读到「删了还没加回来」的中间态 | async function applyFiles(domain: string, index: ListIndex, files: Set… |
| statAll@912 | function | L912-929 | 并行 stat 一个领域的全部卡（对账只要 mtime，不重读内容） | async function statAll(dir: string, files: string[]): Promise<Map<stri… |
| statAll.worker@915 | arrow | L915-926 |  | const worker = async () => { |
| verifyIndex@932 | function | L932-956 | 与文件系统对账：变了/新增/被删的都重读那几张，其余原样保留 | async function verifyIndex(domain: string, index: ListIndex): Promise<… |
| buildIndex@958 | function | L958-970 |  | async function buildIndex(domain: string, plan: DomainPlan): Promise<L… |
| ListSnapshot@974 | interface | L974-982 |  | interface ListSnapshot { |
| snapshotPath@984 | function | L984-989 |  | function snapshotPath(domain: string): string { |
| readSnapshot@991 | function | L991-1015 |  | async function readSnapshot(domain: string, plan: DomainPlan): Promise… |
| writeSnapshot@1017 | function | L1017-1035 |  | async function writeSnapshot(domain: string, index: ListIndex): Promis… |
| scheduleSnapshot@1037 | function | L1037-1044 |  | function scheduleSnapshot(domain: string, index: ListIndex): void { |
| runExclusive@1049 | function | L1049-1057 | 同一份索引上的并发同步串成一条链，避免两个请求同时改索引 | function runExclusive(index: ListIndex, job: () => Promise<void>): Pro… |
| buildListIndex@1059 | function | L1059-1061 |  | async function buildListIndex(domain: string, plan: DomainPlan): Promi… |
| getListIndex@1063 | function | L1063-1112 |  | async function getListIndex(domain: string): Promise<ListIndex> { |
| orderedIds@1114 | function | L1114-1127 |  | function orderedIds(index: ListIndex, col: string \| null, dir: 'asc' … |
| idsForValues@1129 | function | L1129-1144 |  | function idsForValues(index: ListIndex, col: string, values: string[])… |
| ListQuery@1146 | interface | L1146-1155 |  | export interface ListQuery { |
| DomainListPage@1157 | interface | L1157-1177 |  | export interface DomainListPage { |
| queryDomainList@1183 | function | L1183-1255 | 列表页分页查询：筛选走倒排、排序走缓存好的 id 序、分面计数直接读集合大小。 | export async function queryDomainList(domain: string, query: ListQuery… |
| facetsFromIndex@1258 | function | L1258-1273 | 分面选项：值来自倒排、计数就是集合大小（不再遍历全表） | function facetsFromIndex(plan: DomainPlan, index: ListIndex): FilterFa… |
| hasCard@1276 | function | L1276-1278 | 卡片是否存在于该领域（分页列表里 ?card= 深链要校验，但不能为一张卡扫全目录） | export async function hasCard(domain: string, cardId: string): Promise… |
| getListRow@1281 | function | L1281-1285 | 索引里的一行（不读正文）：写入之后要能立刻确认「这一行变了没有」 | export async function getListRow(domain: string, cardId: string): Prom… |
| ListMeta@1291 | interface | L1291-1297 | 列表页的「口径」而非全表：列、中文名、分面取值与总数。 | export interface ListMeta { |
| getListMeta@1299 | function | L1299-1308 |  | export async function getListMeta(domain: string): Promise<ListMeta> { |
| warmListIndexes@1311 | function | L1311-1320 | 服务启动后在后台把各领域索引建好/对账好，用户点进来时已经是热的 | export async function warmListIndexes(): Promise<void> { |
| FieldMeta@1322 | interface | L1322-1333 |  | export interface FieldMeta { |
| getFieldMeta@1336 | function | L1336-1368 | 详情页领域的字段元信息：中文名、排序、渲染格式，全部来自领域包 | export function getFieldMeta(domain: string): Record<string, FieldMeta… |
| extLabels@1371 | function | L1371-1384 | ext 字段的中文 label 映射（来自领域包，前端渲染用） | function extLabels(domain: string): Record<string, string> { |
| getCard@1400 | function | L1400-1415 | 单张卡片详情。 | export function getCard(domain: string, cardId: string): Record<string… |
| refExtKeys@1418 | function | L1418-1427 | 领域包里声明了 format: 'ref' 的 ext 键（不需要硬编码字段名，别的领域也能用） | function refExtKeys(domain: string): string[] { |
| SearchHit@1431 | interface | L1431-1441 |  | export interface SearchHit { |
| snippetAround@1444 | function | L1444-1450 | 在 text 中找出首个命中位置，截取带上下文的片段 | function snippetAround(text: string, needle: string, radius = 40): str… |
| searchCards@1456 | function | L1456-1499 | 全文检索：匹配标题 / 摘要 / 别名 / 标签 / 正文。 | export function searchCards(query: string, limit = 20): SearchHit[] { |
| listAllEntries@1502 | function | L1502-1508 | 静态模式枚举用：全部 (domain, card_id) 组合 | export async function listAllEntries(): Promise<Array<{ domain: string… |
