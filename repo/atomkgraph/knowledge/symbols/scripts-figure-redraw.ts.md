---
covers:
  - scripts/figure-redraw.ts
title: Semantic block index: figure-redraw.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：figure-redraw.ts（第4层）

**源码文件**：`scripts/figure-redraw.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="scripts/figure-redraw.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| SvgAudit@94 | interface | L94-101 | 特别强调：不允许把参考图嵌入 SVG。这是「重画」，不是「截图转存」——要的是矢量线框与文字。 | export interface SvgAudit { |
| svgAudit@110 | function | L110-134 | 静态 SVG 的硬校验。 | export function svgAudit(svg: string): SvgAudit { |
| svgTexts@137 | function | L137-147 | 抽出 SVG 里的可见文字（<text> 内可能还有 <tspan> 与实体）。 | export function svgTexts(svg: string): string[] { |
| decodeEntities@149 | function | L149-159 |  | function decodeEntities(s: string): string { |
| LabelRecall@161 | interface | L161-165 |  | export interface LabelRecall { |
| labelRecall@176 | function | L176-180 | 标签召回：给一批「必须出现的文字」，看 SVG 里逐字出现了没有。 | export function labelRecall(labels: string[], texts: string[]): LabelR… |
| containsAcrossTexts@183 | function | L183-193 | 目标串是否出现在「某个 text 本身」或「若干个相邻 text 的拼接」里。 | function containsAcrossTexts(target: string, texts: string[]): boolean… |
| pngSize@196 | function | L196-200 | 读 PNG 的宽高（IHDR 固定在第 16..24 字节，大端）。项目里没有图像库，够用就行。 | export function pngSize(buf: Buffer): { width: number; height: number … |
| renderSvgToPng@203 | function | L203-234 | 把 SVG 渲染成 PNG（走真实浏览器，与网页 iframe 同一套主题 CSS）。 | export async function renderSvgToPng( |
| RedrawOptions@236 | interface | L236-263 |  | export interface RedrawOptions { |
| RedrawResult@265 | interface | L265-276 |  | export interface RedrawResult { |
| defaultRedrawCacheDir@279 | function | L279-288 | 默认缓存目录：跟着仓库根走（不随 cwd 漂移，与解析缓存同口径）。 | export function defaultRedrawCacheDir(): string { |
| redrawFigure@298 | function | L298-485 | 主流程：读图 → （缓存未命中则）调模型 → 硬校验 → 渲染两套主题。 | export async function redrawFigure(opts: RedrawOptions): Promise<Redra… |
| extractSvg@488 | function | L488-495 | 从模型输出里截出 <svg …>…</svg>：围栏、前言、后记一律丢掉。 | export function extractSvg(raw: string): string { |
| CliArgs@501 | interface | L501-511 | ─────────────────────────────────────────────────────────────────────────── CLI ──────────────────── | interface CliArgs { |
| parseArgs@513 | function | L513-533 |  | function parseArgs(argv: string[]): CliArgs { |
| parseArgs.get@514 | arrow | L514-517 |  | const get = (n: string): string \| undefined => { |
