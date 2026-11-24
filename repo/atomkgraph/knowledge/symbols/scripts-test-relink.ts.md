---
covers:
  - scripts/test-relink.ts
title: Semantic block index: test-relink.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：test-relink.ts（第4层）

**源码文件**：`scripts/test-relink.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="scripts/test-relink.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| assert@28 | function | L28-36 |  | function assert(cond: boolean, label: string, detail?: unknown): void … |
| picksFor@101 | arrow | L101-107 | 用 Q1…Q5 编号一起送进一次调用（见 link.ts 的 runBatch）。只回 q:1 的话每批只有第一道题有 picks——18 道里只有 4 道挂上，而统计看上去「跑了 4 次调用 | const picksFor = (n: number): string => |
| chatAll@109 | arrow | L109-113 |  | const chatAll: ChatFn = async () => ({ |
| chatNone@142 | arrow | L142-146 | 模型说「没有合适节点」 | const chatNone: ChatFn = async () => ({ |
| chatThrow@158 | arrow | L158-160 | 模型调用抛错 | const chatThrow: ChatFn = async () => { |
| chatBadJson@177 | arrow | L177-181 | 模型输出坏 JSON | const chatBadJson: ChatFn = async () => ({ |
| chatLowConf@191 | arrow | L191-197 | 「不硬凑」：minConfidence 不给就别放宽。模型给 0.2 的把握，默认阈值 0.4 应丢弃 | const chatLowConf: ChatFn = async () => ({ |
