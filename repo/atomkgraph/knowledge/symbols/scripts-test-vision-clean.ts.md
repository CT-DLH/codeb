---
covers:
  - scripts/test-vision-clean.ts
title: Semantic block index: test-vision-clean.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：test-vision-clean.ts（第4层）

**源码文件**：`scripts/test-vision-clean.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="scripts/test-vision-clean.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| check@23 | function | L23-27 |  | function check(name: string, cond: unknown, detail?: unknown): void { |
| eq@28 | function | L28-32 |  | function eq(name: string, actual: unknown, expected: unknown): void { |
| good@90 | arrow | L90-90 |  | const good: CleanPageFn = async (_p, n) => ({ markdown: `第${n}页清洗后的正文。… |
| bad@91 | arrow | L91-94 |  | const bad: CleanPageFn = async (_p, n) => { |
| renderOne@262 | arrow | L262-262 |  | const renderOne = (page: number) => ({ engine: 'mock', pages: [{ page,… |
| good2@263 | arrow | L263-263 |  | const good2: CleanPageFn = async (_p, n) => ({ markdown: `第${n}页重洗后的正文… |
| bad2@280 | arrow | L280-283 | 重洗失败：旧正文要留住（不然一次失败把整页内容抹掉），但失败必须可见 | const bad2: CleanPageFn = async (_p, n) => { |
