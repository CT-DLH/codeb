---
covers:
  - packages/core/src/llm/visualize-prompt.ts
title: Semantic block index: visualize-prompt.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：visualize-prompt.ts（第4层）

**源码文件**：`packages/core/src/llm/visualize-prompt.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="packages/core/src/llm/visualize-prompt.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| VizRejectError@38 | class | L38-45 |  | export class VizRejectError extends Error { |
| VizVerdict@48 | interface | L48-55 | 判定结果。worth 为 false 时其余字段仅供报告。 | export interface VizVerdict { |
| VizArtifact@58 | interface | L58-63 | 生成结果，直接对应 KnowledgeVisual 的字段（id 交给归一阶段补）。 | export interface VizArtifact { |
| VizJudgeContext@185 | interface | L185-191 |  | export interface VizJudgeContext { |
| buildVizJudgePrompt@196 | function | L196-206 |  | export function buildVizJudgePrompt(ctx: VizJudgeContext): string { |
| VizGenContext@208 | interface | L208-212 |  | export interface VizGenContext { |
| buildVizGenPrompt@223 | function | L223-238 | 生成用的 user 提示词。 | export function buildVizGenPrompt(ctx: VizGenContext, retryReason?: st… |
| asString@244 | function | L244-248 | ─────────────────────────────────────────────────────────────────────────── 解析与审核（纯函数，可单测） ───────── | function asString(v: unknown): string { |
| parseVizVerdict@259 | function | L259-279 | 解析判定结果。 | export function parseVizVerdict(raw: string): VizVerdict { |
| pickComment@282 | function | L282-285 | 从注释头里取一个字段，如 <!--TITLE: xxx-->。 | function pickComment(s: string, key: string): string { |
| firstIndexOf@288 | function | L288-295 | 数组里第一个命中的下标，都不命中返回 -1。 | function firstIndexOf(s: string, patterns: RegExp[]): number { |
| HtmlAudit@312 | interface | L312-317 |  | export interface HtmlAudit { |
| auditHtml@325 | function | L325-362 | 生成结果的硬审核。这些判据全部可被代码判定，不依赖模型自觉。 | export function auditHtml(html: string): HtmlAudit { |
| parseVizArtifact@371 | function | L371-411 | 解析生成结果。 | export function parseVizArtifact(raw: string, fallbackTitle = ''): Viz… |
