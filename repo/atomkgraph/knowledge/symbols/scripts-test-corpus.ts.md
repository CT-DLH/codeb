---
covers:
  - scripts/test-corpus.ts
title: Semantic block index: test-corpus.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：test-corpus.ts（第4层）

**源码文件**：`scripts/test-corpus.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="scripts/test-corpus.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| assert@25 | function | L25-29 |  | function assert(cond: unknown, msg: string): void { |
| eq@30 | function | L30-37 |  | function eq(msg: string, actual: unknown, expected: unknown): void { |
| hasProblem@39 | function | L39-41 | problems 里是否有一条包含某片段——判据要打在该校验自己那句话上，不能只看"有错" | function hasProblem(plan: CorpusPlan, needle: string): boolean { |
| hasWarning@42 | function | L42-44 |  | function hasWarning(plan: CorpusPlan, needle: string): boolean { |
| mkFile@46 | function | L46-48 |  | function mkFile(id: string, layer: CorpusFile['layer'], rel: string): … |
