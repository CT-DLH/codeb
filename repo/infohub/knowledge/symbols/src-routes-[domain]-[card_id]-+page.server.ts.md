---
covers:
  - src/routes/[domain]/[card_id]/+page.server.ts
title: Semantic block index: +page.server.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：+page.server.ts（第4层）

**源码文件**：`src/routes/[domain]/[card_id]/+page.server.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="src/routes/[domain]/[card_id]/+page.server.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| CardEntry@4 | interface | L4-7 |  | export interface CardEntry { |
| entries@13 | function | L13-15 | 预渲染入口：直接枚举 cards/ 源文件（不依赖构建产物）， | export async function entries(): Promise<CardEntry[]> { |
| load@17 | function | L17-27 |  | export function load({ params }: { params: { domain: string; card_id: … |
