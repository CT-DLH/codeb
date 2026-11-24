---
covers:
  - packages/core/src/ingest/extract-knowledge.ts
title: Semantic block index: extract-knowledge.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：extract-knowledge.ts（第4层）

**源码文件**：`packages/core/src/ingest/extract-knowledge.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="packages/core/src/ingest/extract-knowledge.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| sha1@34 | function | L34-36 |  | function sha1(text: string): string { |
| sectionCacheKey@48 | function | L48-63 | 一节抽取结果的缓存 key。 | export function sectionCacheKey( |
| guideCacheKey@72 | function | L72-75 | 导读结果的缓存 key。 | export function guideCacheKey(sec: FlatSection): string { |
| ExtractKnowledgeOptions@77 | interface | L77-86 |  | export interface ExtractKnowledgeOptions { |
| SectionKnowledge@88 | interface | L88-107 |  | export interface SectionKnowledge { |
| sectionSystemPrompt@109 | function | L109-128 |  | export function sectionSystemPrompt(sec: FlatSection): string { |
| guideInput@149 | function | L149-163 | 拼导读的输入。抽出来是为了让缓存 key 与实际 payload 用同一段文本—— | function guideInput(sec: FlatSection): { body: string; childBrief: str… |
| extractSectionGuide@175 | function | L175-199 | 生成一节/章的导读。 | export async function extractSectionGuide( |
| splitLongText@202 | function | L202-218 | 按空行把超长正文切块，保留段落完整性（不切句子）。 | export function splitLongText(text: string, max: number): string[] { |
| hardSplit@220 | function | L220-224 |  | function hardSplit(text: string, max: number): string[] { |
| userPrompt@226 | function | L226-232 |  | function userPrompt(sec: FlatSection, text: string, part: number, part… |
| extractSectionKnowledge@240 | function | L240-328 | 抽取一节的知识点。 | export async function extractSectionKnowledge( |
| withContainerNote@337 | function | L337-342 | 折叠包装层时，把它承载的实质内容接进容器正文。 | export function withContainerNote(guide: string \| undefined, note: st… |
| normalizeNode@345 | function | L345-353 | 归一：title/content 去空白；非法 knowledge_type 留给落库层处理。 | function normalizeNode(n: SplitNode): SplitNode { |
| dedupeSplitNodes@366 | function | L366-382 | 同一层里同名节点合并。 | export function dedupeSplitNodes(nodes: SplitNode[]): SplitNode[] { |
| OutlineKnowledgeResult@384 | interface | L384-389 |  | export interface OutlineKnowledgeResult { |
| extractOutlineKnowledge@396 | function | L396-424 | 批量抽取（串行）。单节失败不中断整批，但一定出现在 failures 里。 | export async function extractOutlineKnowledge( |
| countNodes@426 | function | L426-433 |  | function countNodes(nodes: SplitNode[]): number { |
