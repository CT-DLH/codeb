---
covers:
  - packages/core/src/ingest/dedupe.ts
title: Semantic block index: dedupe.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：dedupe.ts（第4层）

**源码文件**：`packages/core/src/ingest/dedupe.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="packages/core/src/ingest/dedupe.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| DupCandidate@36 | interface | L36-45 |  | export interface DupCandidate { |
| MergedSubQuestion@47 | interface | L47-51 |  | export interface MergedSubQuestion { |
| DupDecision@53 | interface | L53-65 |  | export interface DupDecision { |
| DedupeOptions@70 | interface | L70-86 |  | export interface DedupeOptions { |
| DedupeResult@88 | interface | L88-101 |  | export interface DedupeResult { |
| clip@130 | function | L130-133 |  | function clip(s: string, n = MAX_CONTENT_CHARS): string { |
| describeCandidate@135 | function | L135-142 |  | function describeCandidate(c: DupCandidate, i: number): string { |
| recallBySkeleton@157 | function | L157-205 |  | function recallBySkeleton(db: DB, skeleton: string, limit: number): Du… |
| recallBySkeleton.push@182 | arrow | L182-198 |  | const push = (rows: Row[], similarity: number) => { |
| escapeLike@208 | function | L208-210 | LIKE 里的 % _ \ 要转义，否则题干里的下划线（LaTeX 下标）会变成通配符。 | function escapeLike(s: string): string { |
| recallByVector@221 | function | L221-255 |  | function recallByVector(db: DB, vec: number[], limit: number): DupCand… |
| parseArray@257 | function | L257-264 |  | function parseArray(json: string \| null): string[] { |
| parseSubs@266 | function | L266-280 |  | function parseSubs(json: string \| null): Array<{ label: string; conte… |
| mergeCandidates@283 | function | L283-293 | 合并两路召回，按 id 去重（骨架命中优先，保持 similarity=1）。 | function mergeCandidates(a: DupCandidate[], b: DupCandidate[], max: nu… |
| parseJudge@296 | function | L296-308 | 宽松解析模型输出：可能是裸 JSON，也可能裹在 json 里。 | function parseJudge(raw: string): Record<string, unknown> \| null { |
| validMerged@311 | function | L311-322 | merged 是否符合落库要求：公共题干非空 + 至少两个非空小问。 | function validMerged(m: unknown): m is { content: string; sub_question… |
| normalizeVerdict@332 | function | L332-365 | 把模型输出收敛成一个合法决策。 | function normalizeVerdict( |
| dedupeQuestions@373 | function | L373-490 | 对一批待落库的题目做查重判定。 | export async function dedupeQuestions( |
