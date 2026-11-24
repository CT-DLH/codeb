---
covers:
  - scripts/_e2e-repair.ts
title: Semantic block index: _e2e-repair.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：_e2e-repair.ts（第4层）

**源码文件**：`scripts/_e2e-repair.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="scripts/_e2e-repair.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| rows@26 | function | L26-40 | 全库签名：节点身份/位置/内容/删除状态 + 两种边。回滚后必须原样回退到这里。 | function rows(): { nodes: SigRow[]; qk: SigRow[]; rel: SigRow[] } { |
| signature@42 | function | L42-44 |  | function signature(): string { |
| diffRows@135 | arrow | L135-151 |  | const diffRows = (label: string, a: SigRow[], b: SigRow[], key: string… |
