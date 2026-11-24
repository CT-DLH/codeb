---
covers:
  - scripts/test-perf-budget.ts
title: Semantic block index: test-perf-budget.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：test-perf-budget.ts（第4层）

**源码文件**：`scripts/test-perf-budget.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="scripts/test-perf-budget.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| assert@30 | function | L30-38 |  | function assert(cond: boolean, label: string, detail?: unknown): void … |
| medianMs@41 | function | L41-51 | 跑 runs 次取中位数；先跑一次预热（SQLite 页缓存冷启动会虚高一个数量级）。 | function medianMs(fn: () => unknown, runs = 5): number { |
| planOf@56 | function | L56-61 | EXPLAIN QUERY PLAN 的 detail 行（按循环嵌套顺序）。 | function planOf(db: DB, sql: string, params: unknown[] = []): string[]… |
| recursiveStepOf@70 | function | L70-73 | EXPLAIN QUERY PLAN 里「递归步」那一段（RECURSIVE STEP 之后的行）。 | function recursiveStepOf(plan: string[]): string { |
| assertBudget@75 | function | L75-104 |  | function assertBudget(tag: string, m: ReturnType<typeof measure>, b: B… |
| assertBudget.kb@87 | arrow | L87-87 |  | const kb = (n: number) => `${(n / 1024).toFixed(0)}KB` |
| buildSynthetic@115 | function | L115-172 | 造一棵 nodeCount 节点的树（三分叉，同 gen-synthetic.ts 的形状）+ 每 5 个节点一道题。 | function buildSynthetic(nodeCount: number): DB { |
| biggestRoot@175 | function | L175-184 | 顶级根里最大的那棵子树的根——scopeCondition 的递归子树以它为参数跑。 | function biggestRoot(db: DB): string { |
| Budget@188 | interface | L188-194 | ---------------------------------------------------------------- 断言集合 | interface Budget { |
| measure@206 | function | L206-238 |  | function measure(db: DB) { |
| report@240 | function | L240-247 |  | function report(tag: string, m: ReturnType<typeof measure>): void { |
| ratio@266 | arrow | L266-266 |  | const ratio = (a: number, b: number) => (b > 0.05 ? a / b : 1) |
