---
covers:
  - packages/core/src/ingest/figures.ts
title: Semantic block index: figures.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：figures.ts（第4层）

**源码文件**：`packages/core/src/ingest/figures.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="packages/core/src/ingest/figures.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| FigureRegion@22 | interface | L22-42 |  | export interface FigureRegion { |
| FigureOptions@44 | interface | L44-62 |  | export interface FigureOptions { |
| FigureResult@64 | interface | L64-68 |  | export interface FigureResult { |
| resolveFigureScript@70 | function | L70-82 |  | function resolveFigureScript(): string \| null { |
| pickPython@84 | function | L84-88 |  | function pickPython(explicit?: string): string { |
| figureDiagnosticsProblems@96 | function | L96-109 | 把侧车的「静默页」诊断变成人能看懂的 problems。 | export function figureDiagnosticsProblems( |
| extractFigures@112 | function | L112-176 | 区域提取：调 python 侧车（PyMuPDF 画矢量图，比例尺与页面无关）。 | export async function extractFigures(pdfPath: string, opts: FigureOpti… |
| norm@179 | function | L179-184 | 归一比较用：去掉空白、标点、LaTeX 命令，只留汉字字母数字。 | function norm(s: string): string { |
| questionNoFromAnchor@187 | function | L187-190 | 从锚点行里认题号：四、(本题 15 分) / 17. 设三棱锥 | export function questionNoFromAnchor(text: string): string \| null { |
| AttachOptions@192 | interface | L192-199 |  | export interface AttachOptions { |
| AttachResult@201 | interface | L201-207 |  | export interface AttachResult { |
| attachFigures@220 | function | L220-321 | 把区域图落盘并插进题干。 | export async function attachFigures( |
| insertMarkdown@329 | function | L329-346 | 在 anchor 之后插入图片；anchor 找不到就追加到末尾。 | function insertMarkdown(stem: string, anchor: string, markdown: string… |
| summarizeFigures@349 | function | L349-354 | 一条题（或整份卷）的配图统计，给报告用。 | export function summarizeFigures(doc: ParsedDocument, regions: FigureR… |
| figureUrlsIn@359 | function | L359-361 |  | export function figureUrlsIn(text: string): string[] { |
| collectFiguresByQuestion@369 | function | L369-379 | 结构层题目 → 「归一题号 → 该题挂上的图」。必须在 attachFigures 之后调用。 | export function collectFiguresByQuestion(questions: LayoutQuestion[]):… |
| RepairResult@381 | interface | L381-387 |  | export interface RepairResult { |
| repairExtractedFigures@399 | function | L399-437 | 抽题后校验：原题里的配图有没有在模型输出里活下来。 | export function repairExtractedFigures( |
