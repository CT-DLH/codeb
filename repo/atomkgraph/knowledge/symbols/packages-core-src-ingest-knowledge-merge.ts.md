---
covers:
  - packages/core/src/ingest/knowledge-merge.ts
title: Semantic block index: knowledge-merge.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：knowledge-merge.ts（第4层）

**源码文件**：`packages/core/src/ingest/knowledge-merge.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="packages/core/src/ingest/knowledge-merge.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| SemDecision@36 | interface | L36-50 |  | export interface SemDecision { |
| MergeInputNode@52 | interface | L52-68 |  | export interface MergeInputNode { |
| MergeItem@70 | interface | L70-110 |  | export interface MergeItem { |
| MergePlan@112 | interface | L112-122 |  | export interface MergePlan { |
| MergeOp@124 | interface | L124-128 |  | export interface MergeOp { |
| MergePlanOptions@138 | interface | L138-172 | containerRefresh（默认开）：容器节点的正文是子节点摘要（LLM 导读）， | export interface MergePlanOptions { |
| MergeApplyResult@174 | interface | L174-192 |  | export interface MergeApplyResult { |
| mergeKey@243 | function | L243-246 | 合并匹配用的标题键：在 titleKey 之上再剥掉括注内容。 | export function mergeKey(title: string): string { |
| childOverlap@249 | function | L249-257 | 两个标题集合的重合度：按较小那侧算，允许「这轮多抽/少抽了几个子节点」。 | export function childOverlap(a: Set<string>, b: Set<string>): number { |
| descendantKeys@265 | function | L265-274 | 新节点所有后代（含多层）的标题键。 | export function descendantKeys(node: MergeInputNode): Set<string> { |
| normContent@277 | function | L277-283 | 内容归一：压空白、去首尾。只用于"是否同一份内容"的判断，不改写正文。 | function normContent(s: string): string { |
| relateContent@293 | function | L293-302 | 新旧正文关系。 | export function relateContent(oldC: string, newC: string): ContentRela… |
| contentBlocks@305 | function | L305-310 | 段落切块：按行切（md 的标题/列表/表格都是行），忽略空行 | function contentBlocks(s: string): string[] { |
| bigrams@313 | function | L313-318 | 字符二元组（去掉空白后再切，避免换行/空格把同一句话切成不同集合） | function bigrams(s: string): Set<string> { |
| containment@321 | function | L321-327 | 包含度 = 交集 / 较小集合。比 Jaccard 更适合「短段落是否已被长段落覆盖」 | function containment(a: Set<string>, b: Set<string>): number { |
| unionContent@339 | function | L339-399 | 段落级并集：保留 oldC 原文，把 newC 里旧正文没有的段落追加到末尾。 | export function unionContent( |
| pathJoin@401 | function | L401-403 |  | function pathJoin(prefix: string, title: string): string { |
| newKey@406 | function | L406-408 | 新建节点的临时父键：用路径而不是标题（标题会重复，同一节里两个「特点」很常见）。 | function newKey(path: string): string { |
| KnowledgeMerger@410 | class | L410-1114 |  | export class KnowledgeMerger { |
| KnowledgeMerger.plan@424 | method | L424-964 | 生成合并计划（纯读，一个字节不写）。 | plan(parentId: string, nodes: MergeInputNode[], opts: MergePlanOptions… |
| KnowledgeMerger.plan.subtreeIndex@478 | arrow | L478-493 |  | const subtreeIndex = (rootId: string): Map<string, Knowledge[]> => { |
| KnowledgeMerger.plan.oldChildKeys@502 | arrow | L502-508 |  | const oldChildKeys = (id: string): Set<string> \| null => { |
| KnowledgeMerger.plan.newChildKeys@509 | arrow | L509-510 |  | const newChildKeys = (n: MergeInputNode): Set<string> \| null => |
| KnowledgeMerger.plan.walk@512 | arrow | L512-932 |  | const walk = ( |
| KnowledgeMerger.plan.findUnique@583 | arrow | L583-588 |  | const findUnique = (rootId: string): { hit?: Knowledge; count: number … |
| KnowledgeMerger.isDescendantOf@967 | method | L967-976 | id 是不是 ancestorId 的后代（含自身）。用来拦住「改挂成环」。 | private isDescendantOf(id: string, ancestorId: string): boolean { |
| KnowledgeMerger.apply@986 | method | L986-1113 | 执行计划。默认 dry_run=true（只返回计划，不落库）——写入不可逆， | apply( |
| KnowledgeMerger.apply.blocked@1011 | arrow | L1011-1012 |  | const blocked = (p: string): boolean => |
| KnowledgeMerger.apply.run@1014 | arrow | L1014-1097 |  | const run = (): void => { |
| ExtractedSection@1123 | interface | L1123-1127 | 一节里抽出来的东西：原子点 + 容器导读。 | export interface ExtractedSection { |
| buildKnowledgeTree@1139 | function | L1139-1208 | 把「章节树 + 每节抽出的原子点」拼成待合并的树。 | export function buildKnowledgeTree( |
| buildKnowledgeTree.nextUid@1150 | arrow | L1150-1150 |  | const nextUid = (): string => `n${++seq}` |
| buildKnowledgeTree.convert@1152 | arrow | L1152-1190 |  | const convert = (sec: OutlineSection, prefix: string): MergeInputNode … |
| buildKnowledgeTree.pointChildren@1192 | arrow | L1192-1200 |  | const pointChildren = (n: SplitNode, path: string): MergeInputNode[] =… |
| outlineContent@1217 | function | L1217-1222 | 容器节点没有直属正文时的兜底内容。 | function outlineContent(children: MergeInputNode[]): string { |
