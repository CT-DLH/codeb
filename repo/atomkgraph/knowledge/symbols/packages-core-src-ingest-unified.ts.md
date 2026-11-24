---
covers:
  - packages/core/src/ingest/unified.ts
title: Semantic block index: unified.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：unified.ts（第4层）

**源码文件**：`packages/core/src/ingest/unified.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="packages/core/src/ingest/unified.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| collectExistingNodes@58 | function | L58-92 | 挂载点子树里已有的节点（给标题对齐当对照表）。 | export function collectExistingNodes(db: DB, parentId: string, topTitl… |
| collectExistingNodes.walk@63 | arrow | L63-75 |  | const walk = (id: string, prefix: string): void => { |
| semanticScopeId@102 | function | L102-109 | 语义召回的范围：本次要处理的那一章，不是挂载点。 | function semanticScopeId(db: DB, parentId: string, nodes: MergeInputNo… |
| UnifiedOptions@111 | interface | L111-188 |  | export interface UnifiedOptions { |
| AttachedQuestion@190 | interface | L190-196 |  | export interface AttachedQuestion { |
| attachPaperFields@218 | function | L218-232 | 把 BuiltQuestion 的卷面字段名（group / no）翻成 ExtractedQuestion 的字段名 | function attachPaperFields(q: BuiltQuestion): BuiltQuestion & { |
| UnifiedPlan@234 | interface | L234-279 |  | export interface UnifiedPlan { |
| Entry@281 | interface | L281-285 |  | interface Entry { |
| collectEntries@287 | function | L287-296 |  | function collectEntries(chapters: OutlineSection[]): Entry[] { |
| collectEntries.walk@289 | arrow | L289-293 |  | const walk = (sec: OutlineSection, prefix: string, parentPath: string … |
| pruneToSections@308 | function | L308-316 | 剪出「只含指定叶子」的子树（祖先自动保留）。 | export function pruneToSections(chapters: OutlineSection[], keep: Set<… |
| pairSheets@319 | function | L319-333 | 习题与答案按「同一个父节下、出现顺序」配对。 | function pairSheets(entries: Entry[]): Array<{ exercise: Entry; answer… |
| planUnifiedIngest@341 | function | L341-729 | 生成计划：跑抽取 + 切题，一个字节不写库。 | export async function planUnifiedIngest(doc: ParsedDocument, opts: Uni… |
| incompletePlanReason@739 | function | L739-755 | 计划能不能落库。返回 null 表示可以，否则返回要打印的拒绝理由。 | export function incompletePlanReason(plan: UnifiedPlan): string \| nul… |
| toFlat@762 | function | L762-769 | plan 需要 DB 连接（要读同父兄弟做比对），所以 UnifiedOptions.db 是必填—— | function toFlat(e: Entry): FlatSection { |
| UnifiedApplyResult@771 | interface | L771-793 |  | export interface UnifiedApplyResult { |
| PendingLink@795 | interface | L795-803 |  | export interface PendingLink { |
| applyUnifiedPlan@816 | function | L816-930 | 落库：先建/更新知识点树，再建题。 | export function applyUnifiedPlan( |
| LinkStageResult@932 | interface | L932-944 |  | export interface LinkStageResult { |
| scopeIdOf@954 | function | L954-960 | 挂载候选树的范围：本次建出来的那一章，不是挂载点。 | function scopeIdOf(plan: UnifiedPlan, applied: UnifiedApplyResult): st… |
| linkIngestedQuestions@970 | function | L970-1029 | 挂载阶段：让模型从知识点树里选题该挂在哪。 | export async function linkIngestedQuestions( |
| extractEmbeddedQuestions@1045 | function | L1045-1098 | 把 LLM 把多道题挤进单条 analysis 里的情况拆开为独立题目。 | function extractEmbeddedQuestions(built: BuiltQuestion[]): BuiltQuesti… |
