---
covers:
  - scripts/test-chat-tools.ts
title: Semantic block index: test-chat-tools.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：test-chat-tools.ts（第4层）

**源码文件**：`scripts/test-chat-tools.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="scripts/test-chat-tools.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| check@21 | arrow | L21-24 |  | const check = (ok: boolean, msg: string, detail = '') => { |
| str@28 | arrow | L28-28 | handler 的返回值是 unknown（工具面前后端共用同一份定义），取值一律走收窄：拿不到就给空串， 让失败信息是「期望的文案不在」而不是「Cannot read property of und | const str = (v: unknown): string => (typeof v === 'string' ? v : '') |
| pick@31 | function | L31-38 | 取工具：目录装配坏了就该立刻停，别让后续断言在 undefined 上崩出天书。 | function pick(tools: ToolDef[], name: string): ToolDef { |
