---
covers:
  - packages/core/src/services/export-service.ts
title: Semantic block index: export-service.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：export-service.ts（第4层）

**源码文件**：`packages/core/src/services/export-service.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="packages/core/src/services/export-service.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| ExportBundle@12 | interface | L12-19 |  | export interface ExportBundle { |
| RestoreResult@21 | interface | L21-27 |  | export interface RestoreResult { |
| ExportOptions@33 | interface | L33-46 |  | export interface ExportOptions { |
| TreeNodeBundle@66 | interface | L66-69 | 子树里的一条节点（前序位置 + 深度）。 | export interface TreeNodeBundle { |
| TreeBundle@72 | interface | L72-83 | 子树取数结果：导出类功能（Markdown / PDF）共用的中间层。 | export interface TreeBundle { |
| ExportService@85 | class | L85-393 |  | export class ExportService { |
| ExportService.exportJson@99 | method | L99-108 | 导出全库为 JSON bundle。 | exportJson(): ExportBundle { |
| ExportService.collectTree@124 | method | L124-167 | 把子树拉平成前序列表 —— 导出类功能共用的取数层。 | collectTree(rootId?: string): TreeBundle \| null { |
| ExportService.collectTree.walk@140 | arrow | L140-143 |  | const walk = (n: Knowledge, depth: number): void => { |
| ExportService.exportTreeMarkdown@178 | method | L178-300 | 导出知识点树为 Markdown（层级 = 节点深度）。 | exportTreeMarkdown(rootId?: string, options: ExportOptions = {}): stri… |
| ExportService.exportTreeMarkdown.heading@200 | arrow | L200-203 |  | const heading = (depth: number, title: string, anchor?: string): strin… |
| ExportService.exportTreeMarkdown.renderQuestion@204 | arrow | L204-223 |  | const renderQuestion = (q: Question, idx: number, includeAnswer: boole… |
| ExportService.exportTreeMarkdown.renderNode@226 | arrow | L226-254 |  | const renderNode = (node: Knowledge, depth: number): void => { |
| ExportService.importJson@306 | method | L306-392 | 从 JSON bundle 导入（恢复/迁移）。 | importJson(bundle: ExportBundle): RestoreResult { |
