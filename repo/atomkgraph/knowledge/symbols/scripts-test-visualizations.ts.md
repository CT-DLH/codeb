---
covers:
  - scripts/test-visualizations.ts
title: Semantic block index: test-visualizations.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：test-visualizations.ts（第4层）

**源码文件**：`scripts/test-visualizations.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="scripts/test-visualizations.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| check@27 | function | L27-35 |  | function check(cond: unknown, msg: string, detail = ''): void { |
| j@36 | arrow | L36-36 |  | const j = (v: unknown): string => JSON.stringify(v) |
| codeOf@134 | arrow | L134-134 | R54：逐条可视化操作（search_replace / upsert / remove）——都不必整组重发。 归一后 id 稳定，所以「按 id 定位一条」才成立（这正是「独立 id」的价值）。 | const codeOf = (e: unknown): string => (e as { code?: string })?.code … |
