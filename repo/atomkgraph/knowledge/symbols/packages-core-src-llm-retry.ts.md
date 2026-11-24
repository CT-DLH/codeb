---
covers:
  - packages/core/src/llm/retry.ts
title: Semantic block index: retry.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：retry.ts（第4层）

**源码文件**：`packages/core/src/llm/retry.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="packages/core/src/llm/retry.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| classifyTransient@29 | function | L29-44 | 判断这个错误值不值得重试。 | export function classifyTransient(e: unknown): 'network' \| 'timeout' … |
| RetryOptions@46 | interface | L46-53 |  | export interface RetryOptions { |
| sleep@55 | function | L55-57 |  | function sleep(ms: number): Promise<void> { |
| withTransientRetry@62 | function | L62-78 | 带退避的重试。所有尝试都失败时抛最后一次的错误（保留真实原因，不要抛「重试失败」这种空壳）。 | export async function withTransientRetry<T>(fn: () => Promise<T>, opts… |
