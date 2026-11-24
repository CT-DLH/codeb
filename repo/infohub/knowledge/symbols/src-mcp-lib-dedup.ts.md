---
covers:
  - src/mcp/lib/dedup.ts
title: Semantic block index: dedup.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：dedup.ts（第4层）

**源码文件**：`src/mcp/lib/dedup.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="src/mcp/lib/dedup.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| SimilarCard@7 | interface | L7-16 |  | export interface SimilarCard { |
| SimilarQuery@18 | interface | L18-25 |  | export interface SimilarQuery { |
| DuplicateWarning@27 | interface | L27-36 |  | export interface DuplicateWarning { |
| aliasPairs@44 | function | L44-58 |  | function aliasPairs(query: SimilarQuery, candidate: Record<string, any… |
| matchCandidate@60 | function | L60-139 |  | function matchCandidate( |
| findSimilarCards@142 | function | L142-173 | 在指定领域内查找相似卡片，按得分倒序返回 | export function findSimilarCards(query: SimilarQuery, limit = 5): Simi… |
| buildDuplicateWarning@176 | function | L176-198 | 把高相似候选转成 card_create 的非阻断警告 | export function buildDuplicateWarning(candidates: SimilarCard[]): Dupl… |
