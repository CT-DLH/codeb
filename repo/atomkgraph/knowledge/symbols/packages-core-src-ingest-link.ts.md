---
covers:
  - packages/core/src/ingest/link.ts
title: Semantic block index: link.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：link.ts（第4层）

**源码文件**：`packages/core/src/ingest/link.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="packages/core/src/ingest/link.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| LinkInput@26 | interface | L26-32 | 送去挂载的题目。question_id 可省略：dry-run 时题目还没落库。 | export interface LinkInput { |
| KnowledgePick@34 | interface | L34-41 |  | export interface KnowledgePick { |
| LinkDrop@43 | interface | L43-47 |  | export interface LinkDrop { |
| LinkDecision@49 | interface | L49-56 |  | export interface LinkDecision { |
| LinkOptions@58 | interface | L58-83 |  | export interface LinkOptions { |
| LinkStats@85 | interface | L85-104 |  | export interface LinkStats { |
| LinkResult@106 | interface | L106-109 |  | export interface LinkResult { |
| LinkError@112 | class | L112-112 | 知识树超出预算 / 题目为空等「用错了」的情况：直接报错，不静默降级。 | export class LinkError extends Error {} |
| KNode@114 | interface | L114-120 |  | interface KNode { |
| Tree@122 | interface | L122-127 |  | interface Tree { |
| resolveScopeId@133 | function | L133-146 | --link-scope 允许写节点 id 或标题（标题更顺手，但可能重名）。 | export function resolveScopeId(db: DB, ref: string): string { |
| buildKnowledgeOutline@154 | function | L154-222 | 把知识树摊平成「编号 + 缩进标题」的文本。 | export function buildKnowledgeOutline( |
| buildKnowledgeOutline.walk@186 | arrow | L186-196 |  | const walk = (parent: string \| null, depth: number): void => { |
| pathOf@224 | function | L224-236 |  | function pathOf(tree: Tree, id: string): string { |
| isAncestor@238 | function | L238-247 |  | function isAncestor(tree: Tree, ancestorId: string, id: string): boole… |
| clip@252 | function | L252-255 |  | function clip(s: string, n = MAX_CONTENT_CHARS): string { |
| describeQuestion@257 | function | L257-261 |  | function describeQuestion(q: LinkInput): string { |
| parseJson@275 | function | L275-287 |  | function parseJson(raw: string): Record<string, unknown> \| null { |
| aliasOf@290 | function | L290-295 | 从模型给的编号里取出 K 序号：K12、k12、K12 二重积分 都认。 | function aliasOf(v: unknown): string \| null { |
| RawPick@297 | interface | L297-301 |  | interface RawPick { |
| normalizePicks@309 | function | L309-366 | 模型输出 → 合法挂载。 | function normalizePicks( |
| linkQuestions@372 | function | L372-451 | 对一批题目给出挂载建议。只读不写：dry-run 与真写共用同一份决策， | export async function linkQuestions( |
| runBatch@454 | function | L454-513 | 跑一批；返回错误信息（成功则返回 null）。抽出来只为让主流程读起来是线性的。 | async function runBatch( |
| ApplyLinkResult@515 | interface | L515-522 |  | export interface ApplyLinkResult { |
| applyLinks@529 | function | L529-558 | 把决策写进 question_knowledge（source 默认 'ai'）。 | export function applyLinks( |
