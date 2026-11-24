---
covers:
  - scripts/test-question-view.ts
title: Semantic block index: test-question-view.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：test-question-view.ts（第4层）

**源码文件**：`scripts/test-question-view.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="scripts/test-question-view.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| assert@34 | function | L34-42 |  | function assert(cond: boolean, label: string, detail?: unknown): void … |
| sqlCount@81 | arrow | L81-82 | · 逐行翻页收齐的 fullSet —— 层级 / 失效边（§4 用它对 facet） 拿 facet 或 scope.total 自己的数当基线会退化成自证，那条路只用来交叉验证。 ======== | const sqlCount = (sql: string, ...args: unknown[]): number => |
| subtreeQuestionIds@88 | function | L88-105 | 某节点子树里挂着的活题 id。 | function subtreeQuestionIds(anchorId: string): Set<string> { |
| directCount@108 | arrow | L108-115 |  | const directCount = (anchorId: string): number => |
| unassignedIds@118 | function | L118-130 | 「未关联」= 没有任何活关联的活题（指向软删节点的死边不算关联）。 | function unassignedIds(): Set<string> { |
| paperedCount@133 | arrow | L133-136 |  | const paperedCount = (): number => |
| looseInSubtree@139 | function | L139-148 | 某子树里「还没归卷」的题数（§7 的散题池分组按范围切，口径要跟着范围走）。 | function looseInSubtree(anchorId: string): number { |
| fetchAll@186 | function | L186-196 | 按给定查询翻遍所有页，收齐全部行（分页上限 200，所以必须翻页）。 | function fetchAll(q: Parameters<QuestionQueryService['query']>[0] = {}… |
| tierOf@394 | arrow | L394-394 |  | const tierOf = (k: keyof typeof tierBase) => facets.tiers.find((t) => … |
