---
covers:
  - scripts/bench-pipeline-e2e.ts
title: Semantic block index: bench-pipeline-e2e.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：bench-pipeline-e2e.ts（第4层）

**源码文件**：`scripts/bench-pipeline-e2e.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="scripts/bench-pipeline-e2e.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| argOf@35 | arrow | L35-38 |  | const argOf = (n: string): string \| undefined => { |
| asDoc@100 | function | L100-110 |  | function asDoc(markdown: string, title: string): ParsedDocument { |
| Step@112 | interface | L112-119 |  | interface Step { |
| rec@122 | function | L122-125 |  | function rec(model: string, pipeline: string, ok: boolean, ms: number,… |
| runQuestions@128 | function | L128-148 | A. 题目链路：切段 → 抽题。抽题内部会按 batchSize 串行多次调用。 | async function runQuestions(cfg: LLMConfig): Promise<void> { |
| runKnowledge@151 | function | L151-186 | B. 知识点链路：章节目录 → 逐节抽取。真实链路每节至少一次调用（+ 导读 + 整形）。 | async function runKnowledge(cfg: LLMConfig): Promise<void> { |
| main@188 | function | L188-228 |  | async function main(): Promise<void> { |
