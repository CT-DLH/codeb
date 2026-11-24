---
covers:
  - packages/core/src/services/import-service.ts
title: Semantic block index: import-service.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：import-service.ts（第4层）

**源码文件**：`packages/core/src/services/import-service.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="packages/core/src/services/import-service.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| SplitNode@18 | interface | L18-24 | 拆解出的单个知识点（递归树）。与 shared 的 SplitResult 对齐。 | export interface SplitNode { |
| ImportOptions@29 | interface | L29-44 |  | export interface ImportOptions { |
| ImportResult@46 | interface | L46-66 |  | export interface ImportResult { |
| salvageNodes@77 | function | L77-87 | 从被截断的 JSON 里救回完整节点：复用通用实现，再按拆解节点的字段要求过滤。 | export function salvageNodes(text: string): SplitNode[] { |
| parseSplitJson@90 | function | L90-104 | 解析 LLM 返回的 JSON：先机械修复，仍失败且是截断产物则按完整节点闭合，都失败才抛 LLM_BAD_JSON。 | export function parseSplitJson(raw: string, opts: { truncated?: boolea… |
| SplitFnOptions@106 | interface | L106-109 |  | export interface SplitFnOptions { |
| createLlmSplitFn@112 | function | L112-153 | 基于 LLM 的默认拆解器：空正文 / 截断 / 坏 JSON 都会显式抛 LLMError，绝不静默返回空数组。 | export function createLlmSplitFn(cfg?: LLMConfig, opts: SplitFnOptions… |
| createLlmSplitFn.empty@120 | arrow | L120-127 |  | const empty = (r: { finish_reason: string \| null; reasoning?: string … |
| ImportService@155 | class | L155-237 |  | export class ImportService { |
| ImportService.importText@171 | method | L171-180 | 从纯文本导入：拆解 → 落库，返回创建结果。 | async importText(text: string, opts: ImportOptions = {}): Promise<Impo… |
| ImportService.importMarkdown@183 | method | L183-185 | 从 Markdown 文件内容导入（Phase 1 最小导入：直接把正文交给拆解器）。 | async importMarkdown(markdown: string, opts: ImportOptions = {}): Prom… |
| ImportService.persist@188 | method | L188-236 | 把拆解树写入知识库：深度优先，先建父再挂子。 | private persist(nodes: SplitNode[], opts: ImportOptions, chunks = 1): … |
| ImportService.persist.walk@201 | arrow | L201-223 |  | const walk = (node: SplitNode, parentId: string \| null, isRoot: boole… |
| countNodes@239 | function | L239-246 |  | function countNodes(nodes: SplitNode[]): number { |
