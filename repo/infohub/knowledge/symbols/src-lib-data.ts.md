---
covers:
  - src/lib/data.ts
title: Semantic block index: data.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：data.ts（第4层）

**源码文件**：`src/lib/data.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="src/lib/data.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| getJson@3 | function | L3-9 |  | async function getJson<T>(url: string): Promise<T> { |
| fetchIndex@12 | function | L12-14 | 领域索引：GET /data/index.json | export function fetchIndex(): Promise<DomainIndex> { |
| fetchSummaries@17 | function | L17-19 | 某领域的全部卡片摘要：GET /data/{domain}-summaries.json | export function fetchSummaries(domain: string): Promise<CardSummary[]>… |
| fetchCard@22 | function | L22-24 | 单卡完整详情（按需加载）：GET /data/cards/{domain}/{cardId}.json | export function fetchCard(domain: string, cardId: string): Promise<Car… |
