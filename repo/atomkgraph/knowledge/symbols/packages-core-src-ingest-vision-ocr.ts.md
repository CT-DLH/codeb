---
covers:
  - packages/core/src/ingest/vision-ocr.ts
title: Semantic block index: vision-ocr.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：vision-ocr.ts（第4层）

**源码文件**：`packages/core/src/ingest/vision-ocr.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="packages/core/src/ingest/vision-ocr.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| PageTranscript@33 | interface | L33-46 | 单页结构化转写（R44）。 | export interface PageTranscript { |
| VisionOcrPage@48 | interface | L48-58 |  | export interface VisionOcrPage { |
| VisionOcrResult@60 | interface | L60-67 |  | export interface VisionOcrResult { |
| VisionOcrOptions@69 | interface | L69-95 |  | export interface VisionOcrOptions { |
| VisionError@102 | class | L102-110 |  | export class VisionError extends Error { |
| asBool@181 | function | L181-185 |  | function asBool(v: unknown): boolean { |
| asCount@187 | function | L187-190 |  | function asCount(v: unknown): number { |
| parseTranscript@201 | function | L201-232 | 解析单页的结构化转写。 | export function parseTranscript(raw: string): PageTranscript { |
| resolveRenderScript@243 | function | L243-258 | 渲染侧车脚本位置：env 覆盖 → cwd → 模块目录逐级向上（与 ocr.ts::resolveScript 同规矩） | export function resolveRenderScript(): string \| null { |
| probeRenderPython@268 | function | L268-275 | 探测 python 有没有 PyMuPDF。 | export async function probeRenderPython(python: string): Promise<{ ok:… |
| resolveRenderPython@278 | function | L278-289 | 依次尝试 env 指定 → python → python3 → py。全不可用返回 null。 | export async function resolveRenderPython(explicit?: string): Promise<… |
| parseStdoutJson@291 | function | L291-303 |  | function parseStdoutJson(stdout: string): Record<string, unknown> \| n… |
| RenderedPage@305 | interface | L305-309 |  | interface RenderedPage { |
| TodoPage@312 | interface | L312-315 | 待转录的页 = 渲染结果 + 文本层（原文与其指纹：指纹进缓存键，原文进提示词） | interface TodoPage extends RenderedPage { |
| renderPages@319 | function | L319-354 | 渲染指定页为 PNG。单页失败不抛，记 error 由调用方降级成 warning。 | export async function renderPages( |
| PageCacheFile@356 | interface | L356-366 |  | interface PageCacheFile { |
| nativeHash@369 | function | L369-372 | 文本层指纹：只留前 8 位，够区分「换没换」就行，不占缓存体积 | function nativeHash(s: string \| undefined): string { |
| pageCachePath@374 | function | L374-376 |  | function pageCachePath(cacheDir: string, page: number): string { |
| readPageCache@385 | function | L385-402 | 缓存必须同时匹配模型、dpi、协议版本、文本层指纹。 | async function readPageCache( |
| dataUrlOf@404 | function | L404-409 |  | export async function dataUrlOf(path: string): Promise<string> { |
| stripFence@412 | function | L412-416 | 去掉模型偶尔加上的 latex 包裹（它不影响内容，但会污染下游的题号识别） | function stripFence(text: string): string { |
| transcribeOne@471 | function | L471-531 | 单页转写（结构化）。 | async function transcribeOne( |
| visionStatus@534 | function | L534-554 | 视觉解析是否可用（给路由/CLI 提前提示，别让用户上传 76MB 之后才发现没配 key）。 | export async function visionStatus(): Promise<{ |
| visionOcr@562 | function | L562-682 | 对 PDF 指定页做视觉转写。 | export async function visionOcr(filePath: string, opts: VisionOcrOptio… |
| visionOcr.worker@624 | arrow | L624-670 |  | const worker = async (): Promise<void> => { |
