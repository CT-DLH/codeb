---
covers:
  - scripts/test-question-search.ts
title: Semantic block index: test-question-search.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：test-question-search.ts（第4层）

**源码文件**：`scripts/test-question-search.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="scripts/test-question-search.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| assert@10 | function | L10-12 |  | function assert(cond: unknown, msg: string): void { |
| mockEmbed@16 | function | L16-27 | 确定性 mock：字符 bigram → 维度 hash 累加 → L2 归一化。共享字词多则向量接近。 | function mockEmbed(text: string): number[] { |
