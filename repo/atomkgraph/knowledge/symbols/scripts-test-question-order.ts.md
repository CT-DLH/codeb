---
covers:
  - scripts/test-question-order.ts
title: Semantic block index: test-question-order.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：test-question-order.ts（第4层）

**源码文件**：`scripts/test-question-order.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="scripts/test-question-order.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| assert@27 | function | L27-35 |  | function assert(cond: boolean, label: string, detail?: unknown): void … |
| fakeChat@137 | arrow | L137-141 | 假模型：固定给「香农定理」这个节点（树里的 K 编号由 buildKnowledgeOutline 生成， 这里不依赖具体编号——只断言「有 picks」即可，编号正确性由 test-ingest 覆 | const fakeChat: ChatFn = async () => ({ |
| Row@188 | interface | L188-194 |  | interface Row { |
| mk@197 | arrow | L197-204 |  | const mk = (r: Row) => ({ |
