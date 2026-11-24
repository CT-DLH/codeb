---
covers:
  - src/routes/api/cards/[domain]/[card_id]/+server.ts
title: Semantic block index: +server.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：+server.ts（第4层）

**源码文件**：`src/routes/api/cards/[domain]/[card_id]/+server.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="src/routes/api/cards/[domain]/[card_id]/+server.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| GET@7 | function | L7-11 |  | export function GET({ params }: { params: { domain: string; card_id: s… |
| entries@14 | function | L14-16 | 静态模式枚举全部卡片；dev 模式下被忽略（listAllEntries 现为异步，需 await） | export async function entries() { |
