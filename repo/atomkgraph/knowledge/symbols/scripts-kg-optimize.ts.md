---
covers:
  - scripts/kg-optimize.ts
title: Semantic block index: kg-optimize.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：kg-optimize.ts（第4层）

**源码文件**：`scripts/kg-optimize.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="scripts/kg-optimize.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| flag@38 | arrow | L38-38 |  | const flag = (n: string): boolean => argv.includes(`--${n}`) |
| opt@39 | arrow | L39-42 |  | const opt = (n: string): string \| undefined => { |
| multi@44 | arrow | L44-50 |  | const multi = (n: string): string[] => { |
| close@59 | arrow | L59-62 | 显式标注类型（不是靠推断），否则 TS 的控制流分析不认「调用后不可达」， 下面的 if (!x) close(1) 之后仍然认为 x 可能为 undefined | const close: (code?: number) => never = (code = 0) => { |
| say@107 | arrow | L107-110 |  | const say = (s = ''): void => { |
| say@321 | arrow | L321-324 |  | const say = (s = ''): void => { |
| byTier@420 | arrow | L420-420 | 分档不同的下一步不一样：auto 档常常只有「重建索引」，那不是 apply 能干的活 | const byTier = (t: OptimizeTier): OptimizeProposal[] => plan.proposals… |
