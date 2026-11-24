---
covers:
  - packages/core/src/llm/key-pool.ts
title: Semantic block index: key-pool.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：key-pool.ts（第4层）

**源码文件**：`packages/core/src/llm/key-pool.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="packages/core/src/llm/key-pool.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| KeyPool@36 | interface | L36-43 | 多 key 轮转：把「N 个 key」变成「N 个可用并发位」。 | export interface KeyPool { |
| createKeyPool@45 | function | L45-93 |  | export function createKeyPool(keys: string[]): KeyPool { |
| createKeyPool.acquire@55 | arrow | L55-61 |  | const acquire = (): Promise<number> => { |
| createKeyPool.release@63 | arrow | L63-71 |  | const release = (i: number): void => { |
| createKeyPool.withKey@79 | method | L79-88 |  | async withKey<T>(fn: (key: string, index: number) => Promise<T>): Prom… |
| createKeyPool.stats@89 | method | L89-91 |  | stats() { |
