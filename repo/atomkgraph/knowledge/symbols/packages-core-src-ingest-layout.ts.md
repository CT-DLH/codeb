---
covers:
  - packages/core/src/ingest/layout.ts
title: Semantic block index: layout.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：layout.ts（第4层）

**源码文件**：`packages/core/src/ingest/layout.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="packages/core/src/ingest/layout.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| LayoutBlock@71 | interface | L71-81 |  | export interface LayoutBlock { |
| PageLayout@83 | interface | L83-92 |  | export interface PageLayout { |
| LayoutResult@94 | interface | L94-112 |  | export interface LayoutResult { |
| LayoutOptions@160 | interface | L160-187 |  | export interface LayoutOptions { |
| layoutCacheDir@190 | function | L190-192 | 分页缓存的目录：与 parse 的缓存放同一棵树，便于一起清理。 | export function layoutCacheDir(base = defaultCacheDir()): string { |
| shownLines@194 | function | L194-203 |  | function shownLines(text: string): Array<{ no: number; text: string }>… |
| buildUserPrompt@205 | function | L205-212 |  | function buildUserPrompt(pages: Array<{ page: number; text: string }>)… |
| normalizePageLayout@221 | function | L221-315 | 把模型的输出归一成块列表，并做代码侧纠错。 | export function normalizePageLayout( |
| layoutPages@324 | function | L324-382 | 一次调用分析一组页，返回 page → 结果。 | async function layoutPages( |
| parseLayoutPayload@385 | function | L385-411 | 版式结果可能是「多页」也可能是「单页」，两种都认（后者当模型漏了 pages 壳）。 | function parseLayoutPayload(content: string, truncated: boolean): Arra… |
| chunkPages@414 | function | L414-434 | 按「页数 / 字符数」把待分析的页分组：一组发一次调用。 | function chunkPages( |
| LayoutCacheFile@436 | interface | L436-441 |  | interface LayoutCacheFile { |
| layoutCacheKey@451 | function | L451-455 | 版式缓存的键：解析后的文本，不是文件字节的 hash。 | export function layoutCacheKey(doc: ParsedDocument): string { |
| cachePath@457 | function | L457-460 |  | function cachePath(dir: string, hash: string, model: string): string { |
| readCache@462 | function | L462-471 |  | async function readCache(path: string): Promise<LayoutCacheFile \| nul… |
| isEmptyLayout@474 | function | L474-476 | 只对「这一页没有任何块」的页返回 true——单页失败可以重跑，不必整份重来。 | function isEmptyLayout(p: PageLayout \| undefined): boolean { |
| coverageBad@488 | function | L488-493 | 一页「没盖住」的判据。 | function coverageBad(lay: PageLayout, text: string): boolean { |
| layoutDocument@501 | function | L501-674 | 逐页做版式分析。 | export async function layoutDocument( |
| layoutDocument.saveCache@532 | arrow | L532-548 |  | const saveCache = (): Promise<void> => { |
| layoutDocument.runChunk@556 | function | L556-606 | 跑一组。整组失败就二分重试——一组里坏一页不该让另外三页陪着作废， | async function runChunk(pages: Array<{ page: number; text: string }>, … |
| layoutDocument.worker@609 | function | L609-616 |  | async function worker(): Promise<void> { |
| LayoutFigure@680 | interface | L680-686 | --------------------------------------------------------------------------- 装配：块 → 题 --------------- | export interface LayoutFigure { |
| LayoutQuestion@688 | interface | L688-706 |  | export interface LayoutQuestion { |
| AssembleResult@708 | interface | L708-726 |  | export interface AssembleResult { |
| normalizeQuestionNo@745 | function | L745-783 | 题号归一。 | export function normalizeQuestionNo(raw: string): { seq: number \| nul… |
| questionNoKey@792 | function | L792-796 | 题号的对齐键（不是展示用的）。 | export function questionNoKey(raw: string): string { |
| Part@798 | interface | L798-802 |  | interface Part { |
| assembleQuestions@813 | function | L813-993 | 把一页页的块装配成题。 | export function assembleQuestions(doc: ParsedDocument, layouts: PageLa… |
| assembleQuestions.textOf@827 | arrow | L827-830 |  | const textOf = (page: number, from: number, to: number): string => { |
| assembleQuestions.newQuestion@832 | arrow | L832-850 |  | const newQuestion = (b: LayoutBlock, page: number): LayoutQuestion => … |
| composeQuestionText@1002 | function | L1002-1008 | 题干 + 选项 + 参考解答 → 一段正文。 | export function composeQuestionText(q: LayoutQuestion): string { |
| stripTrailingPageNo@1020 | function | L1020-1030 | 剥掉块尾粘着的页码。 | export function stripTrailingPageNo(text: string): string { |
| qualifySubNo@1047 | function | L1047-1053 | 给「只有小问标号」的题号补上大题号：(4) → 一(4)。 | export function qualifySubNo(raw: string, section?: string): string { |
| splitFillInBlankQuestions@1063 | function | L1063-1121 | 把「填空题 / 选择题」大题下的小问拆成独立题。 | export function splitFillInBlankQuestions(qs: LayoutQuestion[]): { |
| normalizeKey@1123 | function | L1123-1125 |  | function normalizeKey(no: string): string { |
| cleanTextByLayout@1136 | function | L1136-1157 | 按块重建「去掉页面装饰」的正文（答案册用）。 | export function cleanTextByLayout(doc: ParsedDocument, layouts: PageLa… |
| layoutToSegments@1165 | function | L1165-1181 | 装配结果 → Segment[]（一题一段）。 | export function layoutToSegments(questions: LayoutQuestion[]): Segment… |
