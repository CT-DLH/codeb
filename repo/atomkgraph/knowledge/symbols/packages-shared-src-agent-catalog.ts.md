---
covers:
  - packages/shared/src/agent/catalog.ts
title: Semantic block index: catalog.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：catalog.ts（第4层）

**源码文件**：`packages/shared/src/agent/catalog.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="packages/shared/src/agent/catalog.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| ToolCatalog@16 | interface | L16-19 | 工具目录：legacy = 原始 63 个（规格自检用），tools = 对外 12 个 action 派发工具。 | export interface ToolCatalog { |
| MergedToolSpec@21 | interface | L21-31 |  | export interface MergedToolSpec { |
| createToolCatalog@37 | function | L37-2451 | 装配工具目录。传什么传输就走什么路径： | export function createToolCatalog(api: Api): ToolCatalog { |
| createToolCatalog.str@38 | arrow | L38-38 |  | const str = (desc: string) => ({ type: 'string', description: desc }) |
| createToolCatalog.resolveContentFile@57 | function | L57-103 |  | function resolveContentFile(a: Record<string, unknown>): void { |
| createToolCatalog.resolveVisualizationFile@130 | function | L130-180 |  | function resolveVisualizationFile(a: Record<string, unknown>): void { |
| createToolCatalog.itemSearchReplaceField@223 | function | L223-238 | R55：数组条目 search_replace 的 schema 片段（题目的选项 / 多解 / 小问共用）。 | function itemSearchReplaceField(subject: string, keyHint: string) { |
| createToolCatalog.itemRemoveField@241 | function | L241-250 | R55：数组条目 remove 的 schema 片段。 | function itemRemoveField(subject: string, keyHint: string) { |
| createToolCatalog.outlineSuffix@438 | function | L438-449 | 单个节点的尾注：标签 / 未归档 / 计数 / 截断提示。 | function outlineSuffix(n: { |
| createToolCatalog.OutlineNode@465 | interface | L465-473 | 渲染骨架树为缩进文本。 | interface OutlineNode { |
| createToolCatalog.renderOutlineText@475 | function | L475-520 |  | function renderOutlineText(o: { |
| createToolCatalog.renderOutlineText.walk@502 | arrow | L502-512 |  | const walk = ( |
| createToolCatalog.renderBriefText@523 | function | L523-541 | 渲染扁平骨架列表为文本（一行一个知识点）。 | function renderBriefText( |
| createToolCatalog.d@2043 | arrow | L2043-2043 |  | const d = (...lines: string[]): string => lines.join('\n') |
| createToolCatalog.findLegacy@2045 | function | L2045-2049 |  | function findLegacy(name: string): ToolDef { |
| createToolCatalog.exampleForFirstAction@2058 | function | L2058-2082 | 为一个合并工具生成「照着抄就能用」的调用示例（用它的第一个 action）。 | function exampleForFirstAction(actions: Array<[string, string]>): stri… |
| createToolCatalog.exampleForFirstAction.sample@2065 | arrow | L2065-2074 |  | const sample = (k: string): unknown => { |
| createToolCatalog.inferAction@2094 | function | L2094-2140 | 从参数反推 action（只在信号明确时猜，猜不出返回 null）。 | function inferAction( |
| createToolCatalog.buildMergedTool@2143 | function | L2143-2247 | 把资源域的多个旧工具合成一个 action 派发工具。 | function buildMergedTool(spec: MergedToolSpec): ToolDef { |
