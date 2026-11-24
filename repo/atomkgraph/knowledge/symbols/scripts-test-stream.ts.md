---
covers:
  - scripts/test-stream.ts
title: Semantic block index: test-stream.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：test-stream.ts（第4层）

**源码文件**：`scripts/test-stream.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="scripts/test-stream.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| check@12 | function | L12-20 |  | function check(name: string, ok: boolean, detail?: unknown): void { |
| eq@21 | function | L21-23 |  | function eq<T>(name: string, actual: T, expected: T): void { |
| withDeadline@29 | function | L29-40 | 给单测加一个兜底死线：真挂了就报失败，而不是让整个脚本卡住 | async function withDeadline<T>(p: Promise<T>, ms = 6000): Promise<T> { |
| expectTimeout@43 | function | L43-54 | 断言一次流式调用抛 LLM_TIMEOUT，且消息里带指定片段 | async function expectTimeout(name: string, cfg: Parameters<typeof chat… |
| main@56 | function | L56-275 |  | async function main(): Promise<void> { |
| main.send@85 | arrow | L85-87 |  | const send = (o: unknown): void => { |
| main.cfgOf@164 | arrow | L164-169 |  | const cfgOf = (s: string): Parameters<typeof chatDetailed>[0] => ({ |
| main.setLimits@177 | arrow | L177-184 |  | const setLimits = (total?: string, idle?: string, first?: string): voi… |
