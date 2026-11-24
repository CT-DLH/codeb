---
covers:
  - packages/core/src/ingest/text-layer-quality.ts
title: Semantic block index: text-layer-quality.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：text-layer-quality.ts（第4层）

**源码文件**：`packages/core/src/ingest/text-layer-quality.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="packages/core/src/ingest/text-layer-quality.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| LayerPageDiag@47 | interface | L47-62 |  | export interface LayerPageDiag { |
| LayerDiag@64 | interface | L64-71 |  | export interface LayerDiag { |
| isHan@73 | function | L73-75 |  | function isHan(code: number): boolean { |
| isCjkPunct@77 | function | L77-79 |  | function isCjkPunct(code: number): boolean { |
| diagnosePageText@87 | function | L87-134 | 体检单页文本。 | export function diagnosePageText(page: number, text: string): LayerPag… |
| diagnoseTextLayer@137 | function | L137-163 | 体检整份文档：只要有一页乱码，这份文档就得走修复路线。 | export function diagnoseTextLayer(pages: Array<{ page: number; text: s… |
| RouteDecision@165 | interface | L165-172 |  | export interface RouteDecision { |
| recommendRoute@185 | function | L185-216 | 由体检结果推荐解析路线。 | export function recommendRoute( |
| shouldEscalateToVision@227 | function | L227-247 | 抽题之后的升级判据（兜住「体检判不出」的那类故障）。 | export function shouldEscalateToVision( |
| shouldEscalateOnEmpty@261 | function | L261-274 | 抽题交白卷时的升级判据（兜住上面那条闸门的另一侧）。 | export function shouldEscalateOnEmpty(opts: { |
