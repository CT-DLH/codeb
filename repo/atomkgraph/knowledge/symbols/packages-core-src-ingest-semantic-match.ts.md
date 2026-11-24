---
covers:
  - packages/core/src/ingest/semantic-match.ts
title: Semantic block index: semantic-match.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：semantic-match.ts（第4层）

**源码文件**：`packages/core/src/ingest/semantic-match.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="packages/core/src/ingest/semantic-match.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| SubTreeNode@33 | interface | L33-40 |  | export interface SubTreeNode { |
| SemCandidate@42 | interface | L42-58 |  | export interface SemCandidate { |
| SemReconcileResult@61 | interface | L61-68 |  | export interface SemReconcileResult { |
| SemReconcileOptions@70 | interface | L70-83 |  | export interface SemReconcileOptions { |
| vecText@86 | function | L86-88 | 向量文本怎么拼：标题权重最高，正文只取开头——整段里图注/题号会把相似度稀释掉 | function vecText(title: string, content: string): string { |
| cosine@90 | function | L90-102 |  | export function cosine(a: number[], b: number[]): number { |
| titlePrefixMatch@110 | function | L110-115 | 标题前后缀包含（去掉括注后 ≥4 字）：流量控制 vs 流量控制与双工模式。 | export function titlePrefixMatch(a: string, b: string): boolean { |
| recallTopK@118 | function | L118-133 | 取 top-k 候选（纯函数；同分按库顺序，保证重跑结果一致） | export function recallTopK( |
| buildSemanticPrompt@161 | function | L161-185 |  | export function buildSemanticPrompt( |
| collectSubtree@191 | function | L191-217 | 从挂载点向下收集整棵子树（不读 deleted）。 | export function collectSubtree(db: DB, rootId: string): SubTreeNode[] … |
| collectSubtree.walk@199 | arrow | L199-213 |  | const walk = (id: string, prefix: string): void => { |
| validateRelations@228 | function | L228-295 | 批内校验：编号要存在、关系合法、target 必须来自该编号的候选。 | export function validateRelations( |
| semanticReconcile@302 | function | L302-540 | 主入口：召回 + 判决，返回 uid → 决策。 | export async function semanticReconcile( |
| semanticReconcile.ask@414 | arrow | L414-432 | 端点偶尔不按格式回，而是吐一串数字（实测 {"relations":[99]}、{"relations":[9575837732928164000]}）—— 这不是判决，是模型走神。整批结论会 | const ask = async (nudge: boolean): Promise<string> => { |
| semanticReconcile.markAncestors@508 | arrow | L508-514 |  | const markAncestors = (list: MergeInputNode[], chain: string[]): void … |
| flattenWithUid@543 | function | L543-557 | 展开整棵树，给每个节点保证一个 uid（buildKnowledgeTree 已生成；外部构造的节点在这里补） | export function flattenWithUid(nodes: MergeInputNode[]): Array<{ node:… |
| flattenWithUid.walk@546 | arrow | L546-554 |  | const walk = (list: MergeInputNode[]): void => { |
