---
covers:
  - packages/core/src/services/pdf-export-service.ts
title: Semantic block index: pdf-export-service.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：pdf-export-service.ts（第4层）

**源码文件**：`packages/core/src/services/pdf-export-service.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="packages/core/src/services/pdf-export-service.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| PdfExportOptions@36 | interface | L36-61 | PDF 版式选项。questions / answers / maxDepth / refs 与 Markdown 导出同义。 | export interface PdfExportOptions extends ExportOptions { |
| PdfRenderResult@64 | interface | L64-86 | 渲染结果：HTML 供排查（--html 落盘），pdf 供下载。 | export interface PdfRenderResult { |
| esc@96 | function | L96-102 |  | function esc(s: string): string { |
| unescapeHtml@105 | function | L105-107 | 把 diagramPlaceholder 转义的源码还原（只转义过 & < > 三种）。 | function unescapeHtml(s: string): string { |
| inlineDiagrams@115 | function | L115-147 | 把正文 HTML 里的图表占位符整批替换成内联 SVG。 | async function inlineDiagrams(html: string, dsvc: DiagramService): Pro… |
| katexCss@157 | function | L157-180 |  | function katexCss(): string { |
| buildRenderer@183 | function | L183-236 | 与 web 端 MarkdownView 完全一致的渲染器（含 ==挖空== 与 $公式$）。 | function buildRenderer(onMathWarning: () => void): Marked { |
| buildRenderer.start@209 | method | L209-211 |  | start(src: string) { |
| buildRenderer.tokenizer@212 | method | L212-224 |  | tokenizer(src: string) { |
| buildRenderer.renderer@225 | method | L225-231 |  | renderer(this: unknown, token: unknown) { |
| stripOptionLabel@239 | function | L239-241 | 选项里若自带 A. / A、 前缀就去掉——外面会重新编字母，留着就是「A. A. …」。 | function stripOptionLabel(s: string): string { |
| PdfExportService@381 | class | L381-693 |  | export class PdfExportService { |
| PdfExportService.render@395 | method | L395-402 | Markdown → HTML（与网页同源）。 | private render(text: string \| null \| undefined): string { |
| PdfExportService.buildHtml@410 | method | L410-585 | 只生成 HTML（不启动浏览器）。 | async buildHtml(rootId?: string, options: PdfExportOptions = {}): Prom… |
| PdfExportService.renderQuestion@588 | method | L588-646 | 单题卡片（题干 → 选项 → 答案 → 解析；一题多解/多问各自成块）。 | private renderQuestion(q: Question, index: number, includeAnswer: bool… |
| PdfExportService.exportPdf@654 | method | L654-692 | 渲染成 PDF。 | async exportPdf(rootId?: string, options: PdfExportOptions = {}): Prom… |
