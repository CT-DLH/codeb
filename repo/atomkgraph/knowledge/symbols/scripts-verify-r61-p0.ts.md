---
covers:
  - scripts/verify-r61-p0.ts
title: Semantic block index: verify-r61-p0.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：verify-r61-p0.ts（第4层）

**源码文件**：`scripts/verify-r61-p0.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="scripts/verify-r61-p0.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| rank@159 | arrow | L159-159 | 分层必须严格：tier 逆序对为 0，且 unlinked 在末尾连续 | const rank = (n: number): number => (n <= 0 ? 2 : n === 1 ? 0 : 1) |
