---
covers:
  - packages/core/src/services/recall-service.ts
title: Semantic block index: recall-service.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：recall-service.ts（第4层）

**源码文件**：`packages/core/src/services/recall-service.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="packages/core/src/services/recall-service.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| toHalfWidth@28 | function | L28-30 | 全角转半角。 | export function toHalfWidth(s: string): string { |
| normalizeForMatch@36 | function | L36-41 | 归一化：全角转半角 + 小写 + 去空白 + 去标点符号。 | export function normalizeForMatch(s: string): string { |
| bigrams@49 | function | L49-56 | 中文友好的 bigram 切分。 | export function bigrams(s: string): string[] { |
| RecallInput@60 | interface | L60-66 | ---------------------------------------------------------------- 类型 | export interface RecallInput { |
| RecallHit@71 | interface | L71-86 |  | export interface RecallHit { |
| ChannelDiagnostic@88 | interface | L88-94 |  | export interface ChannelDiagnostic { |
| RecallResult@96 | interface | L96-101 |  | export interface RecallResult { |
| NodeLite@103 | interface | L103-110 |  | interface NodeLite { |
| RecallService@114 | class | L114-439 | ---------------------------------------------------------------- 服务 | export class RecallService { |
| RecallService.loadNodes@128 | method | L128-150 | 读取全部未删除知识点的精简视图（一次查询，供各通道复用）。 | private loadNodes(): NodeLite[] { |
| RecallService.loadTagIndex@153 | method | L153-178 | 标签 id → 名称，以及 id → 祖先链（用于路径匹配）。 | private loadTagIndex(): { nameOf: Map<string, string>; ancestorsOf: Ma… |
| RecallService.loadTagIndex.walk@166 | arrow | L166-175 |  | const walk = (id: string, seen: Set<string>): string[] => { |
| RecallService.chHash@183 | method | L183-188 | 通道 1：内容指纹完全一致 —— 真重复，最强信号。 | private chHash(input: RecallInput, nodes: NodeLite[]): string[] { |
| RecallService.chTitle@191 | method | L191-213 | 通道 2：标题归一化匹配（完全相同 > 互相包含 > bigram 相似）。 | private chTitle(input: RecallInput, nodes: NodeLite[]): string[] { |
| RecallService.lexSignature@216 | method | L216-224 | 词法倒排缓存签名：条数 + 最后更新时间，变了就重建。 | private lexSignature(): string { |
| RecallService.buildLexical@227 | method | L227-251 | 构建（或复用）bigram 倒排索引。 | private buildLexical(nodes: NodeLite[]): { |
| RecallService.chLexical@254 | method | L254-289 | 通道 3：词法检索（TF-IDF 加权的 bigram 余弦）。 | private chLexical(input: RecallInput, nodes: NodeLite[]): string[] { |
| RecallService.chVector@292 | method | L292-298 | 通道 4：向量语义检索（后端不可用时返回空，不抛错）。 | private async chVector(input: RecallInput, excludeId?: string): Promis… |
| RecallService.chTag@301 | method | L301-320 | 通道 5：标签路径匹配（同标签 / 共享祖先越近越强）。 | private chTag(input: RecallInput, nodes: NodeLite[]): string[] { |
| RecallService.recall@328 | method | L328-413 | 多路召回 + RRF 融合，返回候选列表。 | async recall(input: RecallInput, limit?: number): Promise<RecallResult… |
| RecallService.recall.record@336 | arrow | L336-352 |  | const record = async ( |
| RecallService.recall.buildPath@380 | arrow | L380-391 |  | const buildPath = (n: NodeLite): string => { |
| RecallService.loadMissingParent@416 | method | L416-438 | 父节点不在未删除集合里时（如父被软删）单独查一次，且不缓存。 | private loadMissingParent(id: string): NodeLite \| null { |
