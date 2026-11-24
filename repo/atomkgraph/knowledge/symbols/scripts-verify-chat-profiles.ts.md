---
covers:
  - scripts/verify-chat-profiles.ts
title: Semantic block index: verify-chat-profiles.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：verify-chat-profiles.ts（第4层）

**源码文件**：`scripts/verify-chat-profiles.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="scripts/verify-chat-profiles.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| sleep@37 | arrow | L37-37 |  | const sleep = (ms: number) => new Promise((r) => setTimeout(r, ms)) |
| rawChatSnapshot@53 | function | L53-63 |  | function rawChatSnapshot(): string \| null { |
| rawChatRestore@65 | function | L65-79 |  | function rawChatRestore(value: string \| null): void { |
| check@82 | function | L82-85 |  | function check(cond: unknown, msg: string, detail = ''): void { |
| api@90 | function | L90-108 |  | async function api( |
| testLegacyMigration@111 | function | L111-199 | [1] 旧库迁移 —— 在临时库上验，不碰用户真实配置。 | function testLegacyMigration(): void { |
| testHttp@202 | function | L202-284 | [2]–[8] 打真 server。 | async function testHttp(): Promise<void> { |
| testFrontend@287 | function | L287-389 | [7] 前端真实浏览器。 | async function testFrontend(): Promise<void> { |
