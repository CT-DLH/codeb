---
covers:
  - src/core/ingest.ts
title: Semantic block index: ingest.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：ingest.ts（第4层）

**源码文件**：`src/core/ingest.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="src/core/ingest.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| Issue@52 | interface | L52-58 |  | export interface Issue { |
| toIssues@61 | function | L61-73 | Zod 错误 → 可直接 JSON 解析的 issues（替代文本拼接） | export function toIssues(err: ZodError): Issue[] { |
| ParsedFile@79 | interface | L79-87 |  | export interface ParsedFile { |
| detectFormat@89 | function | L89-99 |  | export function detectFormat(filePath: string): TableFormat \| null { |
| splitDelimited@101 | function | L101-137 |  | function splitDelimited(text: string, delimiter: string): string[][] { |
| headerize@139 | function | L139-147 |  | function headerize(firstRow: unknown[]): string[] { |
| matrixToRows@149 | function | L149-175 |  | function matrixToRows( |
| xlsxCell@177 | function | L177-184 |  | function xlsxCell(value: unknown): unknown { |
| xlsxCell.pad@179 | arrow | L179-179 |  | const pad = (n: number) => String(n).padStart(2, '0'); |
| parseXlsx@186 | function | L186-203 |  | function parseXlsx(filePath: string, sheet?: string, headerRow = 1): P… |
| parseDelimited@205 | function | L205-212 |  | function parseDelimited(filePath: string, format: 'csv' \| 'tsv', head… |
| parseJsonl@214 | function | L214-237 |  | function parseJsonl(filePath: string): ParsedFile { |
| parseMarkdownTable@239 | function | L239-261 |  | function parseMarkdownTable(filePath: string): ParsedFile { |
| TextToken@263 | interface | L263-267 |  | interface TextToken { |
| tokenizeLine@269 | function | L269-275 |  | function tokenizeLine(line: string): TextToken[] { |
| mergeClusters@281 | function | L281-296 | 列起点多于表头列数时，把间距最小的一对并成一列（一个单元格内含空格被拆成两个 token）。 | function mergeClusters(positions: number[], wanted: number): number[] … |
| alignClusters@305 | function | L305-339 | 把本页实际的列起点单调对齐到表头列（列只能从左到右，允许某些列在本页整列没有值）。 | function alignClusters(clusters: number[], headerStarts: number[]): nu… |
| nearestIndex@341 | function | L341-352 |  | function nearestIndex(positions: number[], value: number): number { |
| parsePdfTable@368 | function | L368-370 | PDF 表格 → 表格行（pdftotext -table，逐页定列）。 | function parsePdfTable(filePath: string, headerRow = 1): ParsedFile { |
| pdfTableFromPages@373 | function | L373-438 | 输入是 pdftotext -table 的按页文本（拆出来才能用固定样本测列对齐） | export function pdfTableFromPages(pages: string[], headerRow = 1): Par… |
| parseTableFile@440 | function | L440-454 |  | export function parseTableFile(filePath: string, sheet?: string, heade… |
| SourceRef@461 | interface | L461-465 |  | export interface SourceRef { |
| RowMapping@470 | interface | L470-492 |  | export interface RowMapping { |
| fieldSpecFor@494 | function | L494-503 |  | function fieldSpecFor(spec: DomainSpec, path: string): FieldSpec \| un… |
| coerceValue@510 | function | L510-561 | 表格里一切都是字符串，按领域包声明的类型做一次温和还原 | export function coerceValue(spec: DomainSpec, path: string, value: unk… |
| mapRow@563 | function | L563-648 |  | export function mapRow( |
| renderTitleTemplate@651 | function | L651-663 | 标题模板：{字段路径} 优先取映射后的值，{原始列名} 兜底；取不到的值留空 | function renderTitleTemplate( |
| IndexEntry@667 | interface | L667-673 |  | export interface IndexEntry { |
| DomainIndex@675 | interface | L675-678 |  | export interface DomainIndex { |
| loadDomainIndex@680 | function | L680-692 |  | export function loadDomainIndex(domain: string): DomainIndex { |
| identityKey@695 | function | L695-699 | identity 归一化：全角转半角 → 剥括号内容 → 去空白标点 → 小写 | function identityKey(value: unknown): string { |
| sameIdentityValue@701 | function | L701-705 |  | function sameIdentityValue(a: unknown, b: unknown): boolean { |
| IdentityMatch@707 | interface | L707-711 |  | export interface IdentityMatch { |
| matchIdentity@721 | function | L721-747 | 三步匹配，顺序不可颠倒： | export function matchIdentity( |
| findClaimableCards@750 | function | L750-765 | 找出「只有弱标识」的待认领卡：桥接材料出现时它们应当并入强标识卡 | export function findClaimableCards( |
| dedupMatch@768 | function | L768-785 | 没有声明 identity 的领域退回 dedup 口径（source_ref / title / alias / dedup_key） | function dedupMatch(domain: string, fields: Record<string, any>, index… |
| sanitizeSegment@789 | function | L789-793 |  | function sanitizeSegment(value: string): string { |
| hashIdentityValues@796 | function | L796-801 | 标识值 → 8 位内容哈希：同一实体得到同一 id，改名才换 id | function hashIdentityValues(values: string[]): string { |
| applyPattern@803 | function | L803-845 |  | function applyPattern( |
| buildCardId@847 | function | L847-875 |  | export function buildCardId( |
| uniqueCardId@877 | function | L877-888 |  | export function uniqueCardId(domain: string, baseId: string, taken?: S… |
| uniqueCardId.busy@879 | arrow | L879-879 |  | const busy = (id: string) => existsSync(join(dir, `${id}.md`)) \|\| ta… |
| flatten@892 | function | L892-903 |  | function flatten(target: Record<string, any>, prefix = ''): Record<str… |
| sameListItem@909 | function | L909-915 | 并集去重用「语义相同」判等：空白串与空数组都是空，其它走 identity 归一化 | function sameListItem(a: unknown, b: unknown): boolean { |
| unionListSources@921 | function | L921-938 | 追加溯源记录：同一份材料同一行的多次写入合并成一条（fields 取并集）， | function unionListSources(existing: unknown, incoming: SourceRef[]): R… |
| conflictFieldPath@947 | function | L947-950 | 冲突清单是「待办」不是流水账：按字段路径覆盖，没比过的字段原样保留。 | export function conflictFieldPath(line: unknown): string \| null { |
| MergeResult@952 | interface | L952-956 |  | export interface MergeResult { |
| deletePath@960 | function | L960-973 | 合并不静默覆盖：值不同就保留现状 + 记 import_conflicts + 标 status 冲突 | function deletePath(target: Record<string, any>, path: string): unknow… |
| isPlaceholderTitle@979 | function | L979-983 | 占位标题：卡片还没有真名时的兜底（内核生成的「…-待定题目」与模板拼出的「未命名…」）。 | function isPlaceholderTitle(value: unknown): boolean { |
| mergeFields@985 | function | L985-1080 |  | export function mergeFields( |
| PreparedCard@1084 | interface | L1084-1089 |  | export interface PreparedCard { |
| PrepareResult@1091 | interface | L1091-1096 |  | export interface PrepareResult { |
| prepareCard@1102 | function | L1102-1167 | 校验 + 生成 card_id + 查重，但不写盘。 | export function prepareCard(input: { |
| applySectionUpdates@1174 | function | L1174-1189 | 按声明的小节把上游正文覆盖进卡片正文。 | function applySectionUpdates(current: string, incoming: string, sectio… |
| commitCard@1191 | function | L1191-1193 |  | export function commitCard(prepared: PreparedCard, body: string, empty… |
| buildSourceBody@1196 | function | L1196-1211 | 从 sources 溯源生成最小正文：详情页至少能看到这张卡来自哪份材料的哪一行 | export function buildSourceBody(sources: unknown): string { |
| ImportStrategies@1215 | interface | L1215-1226 |  | export interface ImportStrategies { |
| ImportOptions@1228 | interface | L1228-1250 |  | export interface ImportOptions { |
| Anomaly@1262 | interface | L1262-1270 |  | export interface Anomaly { |
| PlannedRow@1272 | interface | L1272-1293 |  | interface PlannedRow { |
| ClearRecord@1295 | interface | L1295-1300 |  | export interface ClearRecord { |
| ImportRisk@1302 | interface | L1302-1308 |  | export interface ImportRisk { |
| ImportReport@1310 | interface | L1310-1366 |  | export interface ImportReport { |
| compactRow@1384 | function | L1384-1392 | 异常里的原始行只作定位用，长文本截断，避免整表内容灌进对话 | function compactRow(row: Record<string, unknown>): Record<string, unkn… |
| maskSensitivePaths@1401 | function | L1401-1407 |  | function maskSensitivePaths(spec: DomainSpec, row: Record<string, unkn… |
| sensitiveSourceColumns@1410 | function | L1410-1420 | 异常里的 raw 按「源列名」键，所以要用 column_map 反查哪些列落到了敏感字段 | function sensitiveSourceColumns( |
| maskSensitiveColumns@1422 | function | L1422-1429 |  | function maskSensitiveColumns(columns: Set<string>, row: unknown): unk… |
| placeholderTitle@1431 | function | L1431-1442 |  | function placeholderTitle(spec: DomainSpec, fields: Record<string, any… |
| assessMergeRisk@1461 | function | L1461-1512 | 弱标识命中并不等于同一实体：同一课题被拆成多个名额、同一活动有多份材料都会命中。 | function assessMergeRisk( |
| importTable@1514 | function | L1514-2231 |  | export function importTable(options: ImportOptions): ImportReport { |
| importTable.countOf@1954 | arrow | L1954-1954 |  | const countOf = (action: PlannedRow['action']) => plan.filter((item) =… |
| importTable.withDerives@2048 | arrow | L2048-2056 | 派生字段：值全部由领域包的 derive 规则从已有正文/字段里正则取出， 落在写盘前的最后一步，所以「先导入原始列、再补提取」与「一次性导完」结果一致。 | const withDerives = (frontmatter: Record<string, any>, body: string): … |
| importTable.absorbDonors@2062 | arrow | L2062-2098 | 把只有弱标识的「待认领卡」并进这张有强标识的卡： 合并字段（不覆盖已有值）、累加正文、donor 原文件移入 .trash/。 | const absorbDonors = ( |
