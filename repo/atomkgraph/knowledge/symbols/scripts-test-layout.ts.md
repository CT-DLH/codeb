---
covers:
  - scripts/test-layout.ts
title: Semantic block index: test-layout.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：test-layout.ts（第4层）

**源码文件**：`scripts/test-layout.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="scripts/test-layout.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| assert@30 | function | L30-34 |  | function assert(cond: unknown, msg: string): void { |
| eq@35 | function | L35-42 |  | function eq(msg: string, actual: unknown, expected: unknown): void { |
| problemsContain@43 | function | L43-45 |  | function problemsContain(list: string[], needle: string): boolean { |
| mkDoc@65 | function | L65-82 |  | function mkDoc(): ParsedDocument { |
| mkLayout@84 | function | L84-86 |  | function mkLayout(page: number, role: PageLayout['role'], blocks: Layo… |
| caseNormalizeNo@90 | function | L90-110 | --------------------------------------------------------------------------- | function caseNormalizeNo(): void { |
| caseCoverage@112 | function | L112-124 |  | function caseCoverage(): void { |
| caseStemNeedsNo@126 | function | L126-161 |  | function caseStemNeedsNo(): void { |
| caseContWithNo@163 | function | L163-179 |  | function caseContWithNo(): void { |
| caseAssemble@181 | function | L181-207 |  | function caseAssemble(): void { |
| caseCombinedAnswerBook@209 | function | L209-233 |  | function caseCombinedAnswerBook(): void { |
| caseOrphanSolution@235 | function | L235-252 |  | function caseOrphanSolution(): void { |
| caseMissingNo@254 | function | L254-270 |  | function caseMissingNo(): void { |
| caseSegments@272 | function | L272-294 |  | function caseSegments(): void { |
| caseTrailingPageNo@296 | function | L296-306 |  | function caseTrailingPageNo(): void { |
| caseFillInSplit@308 | function | L308-336 |  | function caseFillInSplit(): void { |
| caseReorder@338 | function | L338-379 |  | function caseReorder(): void { |
| caseCacheKey@381 | function | L381-399 |  | function caseCacheKey(): void { |
| caseCacheRoundtrip@401 | function | L401-448 |  | async function caseCacheRoundtrip(): Promise<void> { |
| caseCacheRoundtrip.one@416 | arrow | L416-419 |  | const one = (text: string): ParsedDocument => ({ |
| pageHeaders@452 | function | L452-455 |  | function pageHeaders(messages: unknown): number[] { |
| caseGroupCall@464 | function | L464-542 | 按组调用是这一层能不能跑得动的前提（端点延迟跟输入长度几乎无关： | async function caseGroupCall(): Promise<void> { |
| caseCoverageGate@551 | function | L551-602 | 覆盖闸门：模型「排了块」不等于「盖住了正文」。 | async function caseCoverageGate(): Promise<void> { |
| caseCoverageGate.mk@560 | arrow | L560-563 |  | const mk = (nos: number[], to: number) => |
| caseEmptyStem@610 | function | L610-638 | 有题号没正文：正文行被标成了页眉页脚/大题标题。 | function caseEmptyStem(): void { |
| caseSubNoQualify@640 | function | L640-698 |  | function caseSubNoQualify(): void { |
| main@700 | function | L700-720 |  | async function main(): Promise<void> { |
