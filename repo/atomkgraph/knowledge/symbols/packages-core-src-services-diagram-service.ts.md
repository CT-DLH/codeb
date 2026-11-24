---
covers:
  - packages/core/src/services/diagram-service.ts
title: Semantic block index: diagram-service.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：diagram-service.ts（第4层）

**源码文件**：`packages/core/src/services/diagram-service.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="packages/core/src/services/diagram-service.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| DiagramRenderResult@43 | interface | L43-50 |  | export interface DiagramRenderResult { |
| DiagramServiceOptions@52 | interface | L52-59 |  | export interface DiagramServiceOptions { |
| defaultDiagramCacheDir@62 | function | L62-71 | 默认缓存目录：往上找 pnpm-workspace.yaml 当根（与解析缓存同口径，不随 cwd 漂移）。 | export function defaultDiagramCacheDir(): string { |
| tikzDocument@77 | function | L77-92 | standalone 文档前导：矢量图 + 中文（xeCJK）。tikz 代码若自带 \documentclass 则原样用。 | function tikzDocument(code: string): string { |
| resolveTexBin@95 | function | L95-116 | 找一个能跑的 TeX bin 目录（含 xelatex 与 dvisvgm）。 | export function resolveTexBin(explicit?: string): string { |
| resolveTexBin.has@97 | arrow | L97-97 |  | const has = (bin: string) => existsSync(join(bin, `xelatex${exe}`)) &&… |
| DiagramService@118 | class | L118-315 |  | export class DiagramService { |
| DiagramService.cachePathFor@138 | method | L138-140 | 缓存文件路径（便于测试断言与排查）。 | cachePathFor(lang: DiagramLang, code: string): string { |
| DiagramService.hashOf@142 | method | L142-147 |  | private hashOf(lang: DiagramLang, code: string): string { |
| DiagramService.render@155 | method | L155-174 | 渲染一张图。命中磁盘缓存则直接返回（cached: true）。 | async render(lang: DiagramLang, code: string): Promise<DiagramRenderRe… |
| DiagramService.readCache@177 | method | L177-181 | 读缓存（供 GET /api/diagram/:hash 与 PDF 二次取用）；不存在返回 null。 | readCache(hash: string): string \| null { |
| DiagramService.normalizeSvg@188 | method | L188-195 | 统一的 SVG 后处理： | private normalizeSvg(svg: string): string { |
| DiagramService.mermaidJs@199 | method | L199-204 | ── mermaid ──────────────────────────────────────────────── | private mermaidJs(): string { |
| DiagramService.mermaidPage@206 | method | L206-219 |  | private async mermaidPage(): Promise<import('puppeteer-core').Page> { |
| DiagramService.renderMermaid@221 | method | L221-247 |  | private async renderMermaid(code: string): Promise<string> { |
| DiagramService.getD2@251 | method | L251-258 | ── d2 ───────────────────────────────────────────────────── | private async getD2() { |
| DiagramService.renderD2@260 | method | L260-267 |  | private async renderD2(code: string): Promise<string> { |
| DiagramService.renderTikz@271 | method | L271-304 | ── tikz ─────────────────────────────────────────────────── | private async renderTikz(code: string): Promise<string> { |
| DiagramService.dispose@307 | method | L307-314 | 关闭常驻资源（测试 / 优雅退出时调用）。 | async dispose(): Promise<void> { |
