---
covers:
  - scripts/verify-knowledge-api.ts
title: Semantic block index: verify-knowledge-api.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：verify-knowledge-api.ts（第4层）

**源码文件**：`scripts/verify-knowledge-api.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="scripts/verify-knowledge-api.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| ok@15 | function | L15-23 |  | function ok(cond: boolean, label: string, detail?: unknown): void { |
| eq@24 | function | L24-26 |  | function eq<T>(actual: T, expected: T, label: string): void { |
| post@50 | function | L50-59 |  | async function post(url: string, payload: unknown): Promise<{ status: … |
| get@60 | function | L60-63 |  | async function get(url: string): Promise<any> { |
| checkNoBody@169 | function | L169-171 |  | function checkNoBody(body: any, key: string): void { |
| multipart@177 | function | L177-189 | 手搓 multipart：@fastify/multipart 没开 attachFieldsToBody，字段只能走 parts()。 | function multipart(fields: Record<string, string>, file: { name: strin… |
| postFile@191 | function | L191-201 |  | async function postFile(fields: Record<string, string>): Promise<{ sta… |
