---
covers:
  - scripts/test-reconcile-update.ts
title: Semantic block index: test-reconcile-update.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：test-reconcile-update.ts（第4层）

**源码文件**：`scripts/test-reconcile-update.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="scripts/test-reconcile-update.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| assert@13 | function | L13-17 |  | function assert(cond: unknown, msg: string): void { |
| eq@18 | function | L18-20 |  | function eq(msg: string, actual: unknown, expected: unknown): void { |
| embed@35 | arrow | L35-39 | 固定的假 embedding：按标题首字给向量，保证「字符计数」节点召回到 A | const embed = async (texts: string[]) => texts.map((t) => { |
| chat@51 | arrow | L51-54 |  | const chat = async () => ({ content: JSON.stringify({ results: [ |
| chat@69 | arrow | L69-72 |  | const chat = async (_cfg: any, msgs: any[]) => { |
| chat@81 | arrow | L81-81 |  | const chat = async () => ({ content: JSON.stringify({ results: [{ inde… |
| chat@89 | arrow | L89-89 |  | const chat = async () => ({ content: '这不是 JSON', finish_reason: 'stop'… |
| chat@95 | arrow | L95-95 |  | const chat = async () => ({ content: '', finish_reason: 'stop' }) as a… |
| badEmbed@103 | arrow | L103-103 |  | const badEmbed = async () => { throw new Error('network down') } |
