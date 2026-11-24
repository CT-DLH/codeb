---
covers:
  - packages/core/src/ingest/vision-clean.ts
title: Semantic block index: vision-clean.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：vision-clean.ts（第4层）

**源码文件**：`packages/core/src/ingest/vision-clean.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="packages/core/src/ingest/vision-clean.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| CleanPageResult@93 | interface | L93-97 |  | export interface CleanPageResult { |
| OutlineEntry@100 | interface | L100-107 | 大纲里的一条：章节号 + 标题 + 所在页码 | export interface OutlineEntry { |
| stripRunningHeaders@132 | function | L132-169 | 剥掉纯页码这类页眉页脚残渣（通用兜底）。 | export function stripRunningHeaders(markdown: string): string { |
| stripRunningHeaders.isBarePageNumber@144 | arrow | L144-154 | 注意：空行返回 false。上一版让它返回 true（想顺带跳过排版空行）， 循环一路吃进正文，把第 1 章首页从 3420 字符削到 771（丢 78%）。 | const isBarePageNumber = (raw: string): boolean => { |
| looksLikeTocPage@191 | function | L191-219 | 判断一页是不是目录页。 | export function looksLikeTocPage(markdown: string): boolean { |
| extractOutlineEntries@237 | function | L237-352 | 从一页的清洗正文里抽出大纲条目。 | export function extractOutlineEntries(markdown: string, page: number):… |
| RenderOverride@367 | interface | L367-371 |  | export interface RenderOverride { |
| CleanOptions@373 | interface | L373-460 |  | export interface CleanOptions { |
| CleanPageOut@462 | interface | L462-470 |  | export interface CleanPageOut { |
| CleanResult@472 | interface | L472-498 |  | export interface CleanResult { |
| stripSelfTalk@599 | function | L599-639 |  | export function stripSelfTalk(markdown: string): { text: string; remov… |
| dedupeParagraphs@665 | function | L665-737 | 去掉同一页里整段重复的内容。 | export function dedupeParagraphs(markdown: string): { text: string; re… |
| stripNestedDuplicates@759 | function | L759-848 | 去掉嵌套重复：一段的末尾（或开头）完整包含另一段。 | function stripNestedDuplicates(paras: string[]): { |
| assertPageCoverage@870 | function | L870-887 | 判断一页的清洗产物是否「明显不像这一页」，不合格就抛错。 | export function assertPageCoverage(markdown: string, page: number, nat… |
| collapseSymbolNoise@908 | function | L908-940 | 压掉「用符号硬画图表」产生的大段噪声。 | export function collapseSymbolNoise(markdown: string): { text: string;… |
| collapseSymbolNoise.isSymbolLine@914 | arrow | L914-915 |  | const isSymbolLine = (s: string): boolean => |
| collapseSymbolNoise.flushRun@917 | arrow | L917-925 |  | const flushRun = (): void => { |
| normalizeCleanOutput@942 | function | L942-963 |  | export function normalizeCleanOutput(raw: string): string { |
| assembleMarkdown@966 | function | L966-982 | 把逐页结果拼成一份可导入的 md。失败页留可见占位，绝不静默缺页。 | export function assembleMarkdown( |
| FigureBox@997 | interface | L997-1005 |  | export interface FigureBox { |
| parseFigureBoxes@1015 | function | L1015-1054 | 从清洗产物里抽出所有图的 bbox。 | export function parseFigureBoxes(markdown: string): { boxes: FigureBox… |
| insertFigureImages@1057 | function | L1057-1071 | 把 bbox 注释行换成 ![图注](url)；没裁到图的行原样保留（下游仍可自行裁）。 | export function insertFigureImages( |
| CroppedFigure@1073 | interface | L1073-1080 |  | interface CroppedFigure { |
| resolveCropScript@1083 | function | L1083-1095 | 定位裁图侧车（与 parse.ts / figures.ts 同一套「往上找仓库根」）。 | function resolveCropScript(): string \| null { |
| lastJsonLine@1098 | function | L1098-1110 | 侧车 stdout 可能被底层库的警告污染：从后往前找第一个能解析的 JSON 行。 | function lastJsonLine<T>(stdout: string): T \| null { |
| cropFigures@1113 | function | L1113-1169 | 按模型给的 bbox 从渲染 PNG 裁图，并把图片链接插回 Markdown。 | async function cropFigures( |
| defaultCleanPage@1171 | function | L1171-1275 |  | async function defaultCleanPage( |
| pageCachePath@1277 | function | L1277-1279 |  | function pageCachePath(cacheDir: string, page: number): string { |
| cleanPagesBatch@1295 | function | L1295-1399 | 一次调用转录多页，再把结果按 <!-- page N --> 标记拆回各页。 | async function cleanPagesBatch( |
| CleanCacheFile@1402 | interface | L1402-1410 |  | interface CleanCacheFile { |
| readCleanCache@1412 | function | L1412-1425 |  | async function readCleanCache( |
| cleanPdfToMarkdown@1433 | function | L1433-1762 | 主入口：逐页渲染 → 视觉清洗 → 页级缓存 → 拼成一份 md。 | export async function cleanPdfToMarkdown(filePath: string, opts: Clean… |
| cleanPdfToMarkdown.report@1462 | arrow | L1462-1465 |  | const report = (info: Parameters<NonNullable<CleanOptions['onProgress'… |
| cleanPdfToMarkdown.cleanOne@1515 | arrow | L1515-1543 |  | const cleanOne = async (item: { page: number; path: string; native?: s… |
| cleanPdfToMarkdown.run@1517 | arrow | L1517-1533 |  | const run = async (apiKey?: string): Promise<void> => { |
| cleanPdfToMarkdown.worker@1545 | arrow | L1545-1608 |  | const worker = async (): Promise<void> => { |
| cleanPdfToMarkdown.doBatch@1577 | arrow | L1577-1583 |  | const doBatch = (apiKey?: string) => |
| writeCleanMarkdown@1765 | function | L1765-1770 | 落盘：父目录不存在就建；返回绝对路径。写 md 用 UTF-8、LF。 | export async function writeCleanMarkdown(md: string, outPath: string):… |
| countCleanCache@1773 | function | L1773-1777 | 缓存目录里已有多少页（给 CLI 打印「可续跑」用）。 | export function countCleanCache(cacheDir: string): number { |
