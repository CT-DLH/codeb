---
covers:
  - packages/core/src/ingest/parse.ts
title: Semantic block index: parse.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：parse.ts（第4层）

**源码文件**：`packages/core/src/ingest/parse.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="packages/core/src/ingest/parse.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| defaultCacheDir@29 | function | L29-38 | 解析缓存的默认目录（按仓库根算，不按 cwd）。 | export function defaultCacheDir(): string { |
| ParsedPage@49 | interface | L49-60 |  | export interface ParsedPage { |
| ParsedDocument@62 | interface | L62-99 |  | export interface ParsedDocument { |
| ocrEngineKind@114 | function | L114-116 | 从 engine 字符串判断是哪一类引擎（缓存命中时要靠它拒绝「换了引擎却读旧缓存」）。 | export function ocrEngineKind(engine: string): OcrEngine { |
| ParseOptions@118 | interface | L118-151 |  | export interface ParseOptions { |
| ParseError@153 | class | L153-163 |  | export class ParseError extends Error { |
| cachePathOf@165 | function | L165-167 |  | function cachePathOf(cacheDir: string, hash: string): string { |
| isPlainPath@176 | function | L176-179 | 是不是走 parsePlain 的那几种扩展名（缓存判据要按这个分支对待）。 | function isPlainPath(filePath: string): boolean { |
| cacheUsable@182 | function | L182-198 | 解析缓存命中后仍可用的判据（OCR 相关，见下方注释）。 | function cacheUsable(doc: ParsedDocument, opts: ParseOptions): boolean… |
| readCache@200 | function | L200-208 |  | async function readCache(path: string): Promise<ParsedDocument \| null… |
| resolveNativeTextScript@213 | function | L213-225 | 定位原生文本兜底侧车（与 figures.ts 的 resolveFigureScript 同一套「往上找仓库根」的写法）。 | function resolveNativeTextScript(): string \| null { |
| NativeTextOut@227 | interface | L227-231 |  | export interface NativeTextOut { |
| parseNativeTextStdout@241 | function | L241-253 | 从侧车 stdout 里找出那一行 JSON。 | export function parseNativeTextStdout(stdout: string): NativeTextOut \… |
| nativeTextFallback@261 | function | L261-288 | pdfjs 读不出中文 CID 字体时，用 PyMuPDF 把文本层取回来。 | async function nativeTextFallback( |
| PdfParseResult@290 | interface | L290-294 |  | interface PdfParseResult { |
| parsePdf@297 | function | L297-374 | 解析 PDF：逐页取文本层，并按 operator 统计图片数以识别扫描页。 | async function parsePdf(buf: Uint8Array, filePath: string): Promise<Pd… |
| splitMarkdownPages@385 | function | L385-397 | 按 <!-- page N --> 把 Markdown 拆成页。 | export function splitMarkdownPages(text: string): Array<{ page: number… |
| parsePlain@399 | function | L399-419 |  | async function parsePlain(buf: Uint8Array): Promise<ParsedPage[]> { |
| buildMarkdown@421 | function | L421-426 |  | function buildMarkdown(pages: ParsedPage[]): string { |
| collectWarnings@428 | function | L428-465 |  | function collectWarnings(pages: ParsedPage[], ocr?: ParsedDocument['oc… |
| pageCacheFile@468 | function | L468-470 | 侧车的页级缓存文件名（与 scripts/ocr/ocr_pdf.py 的 pNNNN.json 必须一致）。 | function pageCacheFile(cacheDir: string, page: number): string { |
| applyOcr@480 | function | L480-557 | 对需要 OCR 的页跑侧车，并把结果合并回 pages。 | async function applyOcr( |
| applyVision@568 | function | L568-637 | 视觉解析：把页面渲染成图，交给视觉模型逐字转写后替换该页文本。 | async function applyVision( |
| loadParsed@646 | function | L646-653 | 按 token（= content_hash）读回已解析的文档。 | export async function loadParsed(token: string, cacheDir?: string): Pr… |
| parseFile@656 | function | L656-736 | 解析一个文件（按扩展名分派）。未支持的类型明确报错，绝不返回空文档假装成功。 | export async function parseFile(filePath: string, opts: ParseOptions =… |
