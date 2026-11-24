---
covers:
  - scripts/test-feed.ts
title: Semantic block index: test-feed.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：test-feed.ts（第4层）

**源码文件**：`scripts/test-feed.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="scripts/test-feed.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| assert@8 | function | L8-10 |  | function assert(cond: unknown, msg: string): void { |
| ok@16 | arrow | L16-19 |  | const ok = (label: string): void => { |
| excerptHasLeftover@128 | function | L128-130 | 摘要是否仍残留 Markdown 标记字符（用于 [4] 的粗校验）。 | function excerptHasLeftover(s: string): boolean { |
