---
covers:
  - packages/core/src/ingest/kg-optimizer.ts
title: Semantic block index: kg-optimizer.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：kg-optimizer.ts（第4层）

**源码文件**：`packages/core/src/ingest/kg-optimizer.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="packages/core/src/ingest/kg-optimizer.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| OptNode@20 | interface | L20-31 |  | export interface OptNode { |
| DuplicateCluster@33 | interface | L33-52 |  | export interface DuplicateCluster { |
| FlattenCandidate@54 | interface | L54-61 |  | export interface FlattenCandidate { |
| DeepChain@63 | interface | L63-68 |  | export interface DeepChain { |
| OptimizeReport@70 | interface | L70-89 |  | export interface OptimizeReport { |
| ScopeInfo@93 | interface | L93-97 | ---------------- 子树范围 ---------------- | export interface ScopeInfo { |
| ScopeResolution@99 | interface | L99-106 |  | export interface ScopeResolution extends ScopeInfo { |
| resolveScope@115 | function | L115-176 | 把用户给的 --scope 解析成一组子树 id。 | export function resolveScope(db: DB, specs: string[], depth?: number):… |
| normTitle@195 | function | L195-199 | 标题归一：保留括号内容，只去空白与标点。用于判「父子名字是否冗余」。 | function normTitle(s: string): string { |
| loadNodes@201 | function | L201-227 |  | function loadNodes(db: DB, inScope?: Set<string>): OptNode[] { |
| loadNodes.depth@213 | arrow | L213-221 |  | const depth = (id: string, seen = new Set<string>()): number => { |
| analyzeDuplicates@230 | function | L230-271 | 重名分组 → 合并/改名建议。只处理 ≥2 个节点的组。 | function analyzeDuplicates( |
| analyzeFlatten@274 | function | L274-303 | 单子节点容器 → 扁平化候选。范围模式下要求容器和子节点都在范围内。 | function analyzeFlatten(nodes: OptNode[], scoped: boolean): FlattenCan… |
| analyzeDeepChains@306 | function | L306-346 | 连续单子节点形成的过深链：从每个叶子往上追溯完整单子链，取最长的一条。 | function analyzeDeepChains(nodes: OptNode[], scoped: boolean): DeepCha… |
| analyzeGraph@354 | function | L354-383 | 存量分析（只读）。 | export function analyzeGraph( |
| OptimizeProposal@398 | interface | L398-417 |  | export interface OptimizeProposal { |
| OptimizePlan@419 | interface | L419-431 |  | export interface OptimizePlan { |
| IndexStaleReport@433 | interface | L433-438 |  | export interface IndexStaleReport { |
| graphFingerprint@441 | function | L441-455 | 全库指纹：节点集合 + 标题 + 父子 + 正文 hash。任何结构或正文改动都会变。 | export function graphFingerprint(db: DB): string { |
| indexStale@458 | function | L458-482 | 索引漂移：正文改过没重建 / 从没建过。批量脚本绕过 autoIndex 时静默产生。 | export function indexStale(db: DB, scopeIds?: Set<string>): IndexStale… |
| proposalId@484 | function | L484-487 |  | function proposalId(kind: string, ids: string[]): string { |
| minPairSimilarity@490 | function | L490-498 | 组内两两最低相似度：合并到 keeper 时，最不像的那对决定内容策略。 | function minPairSimilarity(nodes: OptNode[]): number { |
| maxPairSimilarity@501 | function | L501-509 | 组内两两最高相似度：跨父判定用（同父那部分已被拆走，不能沿用整组的 similarity）。 | function maxPairSimilarity(nodes: OptNode[]): number { |
| titleGroupKind@523 | function | L523-534 | 一组撞了归一键的标题，到底是同一概念的不同写法，还是纯属归一化撞车。 | function titleGroupKind(titles: string[]): 'same' \| 'variant' \| 'dis… |
| titleGroupKind.strip@525 | arrow | L525-525 |  | const strip = (s: string): string => s.replace(/\s+/g, '') |
| duplicateProposals@536 | function | L536-720 |  | function duplicateProposals(db: DB, d: DuplicateCluster): OptimizeProp… |
| duplicateProposals.titleOf@571 | arrow | L571-571 |  | const titleOf = (n: OptNode): string \| null => d.parentTitles[d.nodes… |
| collapseProposal@729 | function | L729-804 | 扁平化：只有「父子名字冗余」才值得做，标题无关的单子容器等它自然长出第二个孩子。 | export function collapseProposal( |
| coreTitle@807 | function | L807-812 | 去掉括注（中英对照 / 补充说明）与空白后的标题核心。 | function coreTitle(s: string): string { |
| namingVariant@824 | function | L824-832 | 父子是不是同一个概念的两种写法（中英对照、加括注、加「概述」）。 | function namingVariant(containerTitle: string, childTitle: string): bo… |
| ProposeOptions@839 | interface | L839-843 |  | export interface ProposeOptions { |
| proposeOptimizations@846 | function | L846-923 | 存量优化提案：检测 → 分档 → 可执行载荷。纯读，不写库。 | export function proposeOptimizations(db: DB, opts: ProposeOptions = {}… |
