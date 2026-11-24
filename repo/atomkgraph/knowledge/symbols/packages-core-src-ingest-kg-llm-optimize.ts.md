---
covers:
  - packages/core/src/ingest/kg-llm-optimize.ts
title: Semantic block index: kg-llm-optimize.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：kg-llm-optimize.ts（第4层）

**源码文件**：`packages/core/src/ingest/kg-llm-optimize.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="packages/core/src/ingest/kg-llm-optimize.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| InventoryEntry@50 | interface | L50-62 |  | export interface InventoryEntry { |
| TitleInventory@64 | interface | L64-74 |  | export interface TitleInventory { |
| renderLine@77 | function | L77-82 | 一行清单：缩进 + 序号 + 标题 + 字数 + 子节点数。导出供测试核对格式。 | export function renderLine(e: InventoryEntry): string { |
| buildTitleInventory@90 | function | L90-176 | 构造整树标题清单。 | export function buildTitleInventory( |
| LlmOptimizeOptions@180 | interface | L180-195 | ─────────────────────────── 缓存 ─────────────────────────── | export interface LlmOptimizeOptions { |
| sha1@197 | function | L197-199 |  | function sha1(s: string): string { |
| readCache@201 | function | L201-209 |  | function readCache<T>(dir: string, key: string): T \| null { |
| writeCache@211 | function | L211-218 |  | function writeCache(dir: string, key: string, value: unknown): void { |
| DuplicateGroup@255 | interface | L255-260 |  | export interface DuplicateGroup { |
| pickArray@262 | function | L262-272 |  | function pickArray(parsed: unknown): unknown[] { |
| toNum@274 | function | L274-281 |  | function toNum(x: unknown): number \| null { |
| resolveRefs@289 | function | L289-306 | 模型可能给序号数组、单个序号、或直接给知识 id —— 三种都收。 | function resolveRefs(raw: unknown, inv: TitleInventory): InventoryEntr… |
| isAncestorOf@308 | function | L308-318 |  | function isAncestorOf(aId: string, bId: string, parentOf: Map<string, … |
| SanitizeResult@320 | interface | L320-324 |  | export interface SanitizeResult { |
| sanitizeGroups@345 | function | L345-411 | 校验模型报的重复组。 | export function sanitizeGroups(raw: unknown[], inv: TitleInventory): S… |
| Verdict@418 | interface | L418-428 |  | export interface Verdict { |
| NodeDetail@430 | interface | L430-439 |  | interface NodeDetail { |
| loadDetails@441 | function | L441-477 |  | function loadDetails(db: DB, ids: string[], inScope: Set<string> \| nu… |
| buildVerdictPrompt@516 | function | L516-552 |  | function buildVerdictPrompt(group: DuplicateGroup, details: NodeDetail… |
| pathOfTitlePlaceholder@554 | function | L554-556 |  | function pathOfTitlePlaceholder(n: NodeDetail): string { |
| pickVerdict@558 | function | L558-607 |  | function pickVerdict(parsed: unknown, group: DuplicateGroup): Verdict … |
| proposalId@611 | function | L611-613 | ─────────────────────────── 提案构造 ─────────────────────────── | function proposalId(kind: string, ids: string[]): string { |
| tierOf@615 | function | L615-620 |  | function tierOf(p: { identical: boolean; policy: MergePolicy; confiden… |
| BuildCtx@622 | interface | L622-625 |  | interface BuildCtx { |
| coreTitleLite@628 | function | L628-633 | 去掉括注与空白后的标题核心，只用于「父容器是不是 keeper 的同名副本」这一道顺序护栏。 | function coreTitleLite(s: string): string { |
| verdictProposal@635 | function | L635-830 |  | function verdictProposal(group: DuplicateGroup, v: Verdict, ctx: Build… |
| LlmOptimizePlan@834 | interface | L834-841 | ─────────────────────────── 主流程 ─────────────────────────── | export interface LlmOptimizePlan extends OptimizePlan { |
| LlmOptimizeResult@843 | interface | L843-854 |  | export interface LlmOptimizeResult { |
| callJson@856 | function | L856-879 |  | async function callJson( |
| proposeByLlm@890 | function | L890-1062 | 用 LLM 做存量重复检测，产出与其他提案同构的 OptimizePlan。 | export async function proposeByLlm( |
| finish@1064 | function | L1064-1112 |  | function finish( |
