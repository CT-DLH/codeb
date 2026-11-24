---
covers:
  - packages/core/src/ingest/kg-llm-refine.ts
title: Semantic block index: kg-llm-refine.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：kg-llm-refine.ts（第4层）

**源码文件**：`packages/core/src/ingest/kg-llm-refine.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="packages/core/src/ingest/kg-llm-refine.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| RefineNode@38 | interface | L38-44 |  | export interface RefineNode { |
| ContainerAtLevel@46 | interface | L46-49 |  | export interface ContainerAtLevel { |
| RefineOptions@51 | interface | L51-61 |  | export interface RefineOptions { |
| sha1@66 | function | L66-68 |  | function sha1(s: string): string { |
| readCache@70 | function | L70-78 |  | function readCache<T>(dir: string, key: string): T \| null { |
| writeCache@80 | function | L80-87 |  | function writeCache(dir: string, key: string, value: unknown): void { |
| containersAtLevel@94 | function | L94-138 | 取指定层的容器（有直接子节点的节点）。 | export function containersAtLevel(db: DB, scope: ScopeResolution, leve… |
| containersAtLevel.nodeOf@102 | arrow | L102-108 |  | const nodeOf = (r: (typeof rows)[number]): RefineNode => ({ |
| RefineDecision@170 | interface | L170-175 |  | export interface RefineDecision { |
| buildPrompt@177 | function | L177-197 |  | function buildPrompt(containers: ContainerAtLevel[]): string { |
| sanitizeDecisions@200 | function | L200-252 | 校验模型的结构判断：编号、动作、子节点归属三类幻觉都要拦。 | export function sanitizeDecisions( |
| LlmRefinePlan@254 | interface | L254-261 |  | export interface LlmRefinePlan extends OptimizePlan { |
| LlmRefineResult@263 | interface | L263-267 |  | export interface LlmRefineResult { |
| proposalId@269 | function | L269-271 |  | function proposalId(kind: string, ids: string[]): string { |
| refineLevel@273 | function | L273-446 |  | export async function refineLevel(db: DB, opts: RefineOptions): Promis… |
| emptyPlan@448 | function | L448-479 |  | function emptyPlan( |
