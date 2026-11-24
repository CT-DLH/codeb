---
covers:
  - scripts/verify-comment-reply.ts
title: Semantic block index: verify-comment-reply.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：verify-comment-reply.ts（第4层）

**源码文件**：`scripts/verify-comment-reply.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="scripts/verify-comment-reply.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| assert@14 | function | L14-22 |  | function assert(cond: boolean, label: string): void { |
| fakeCritic@30 | arrow | L30-30 | 假挑刺器：不联网 | const fakeCritic: CriticFn = async () => ({ content: '这里没讲清', suggesti… |
| fakeReplier@34 | arrow | L34-37 |  | const fakeReplier = async (input: { targetType: 'question' \| 'knowled… |
| main@39 | function | L39-144 |  | async function main() { |
