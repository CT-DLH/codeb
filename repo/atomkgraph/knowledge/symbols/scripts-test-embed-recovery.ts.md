---
covers:
  - scripts/test-embed-recovery.ts
title: Semantic block index: test-embed-recovery.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：test-embed-recovery.ts（第4层）

**源码文件**：`scripts/test-embed-recovery.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="scripts/test-embed-recovery.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| assert@11 | function | L11-15 |  | function assert(cond: unknown, msg: string): void { |
| vec@18 | arrow | L18-18 |  | const vec = (i: number) => [i, i + 1, i + 2] |
| okResponse@21 | function | L21-26 | 构造一个成功的 /embeddings 响应，返回顺序与 input 对应。 | function okResponse(input: string[]): Response { |
| input@27 | arrow | L27-27 |  | const input = (n: number) => Array.from({ length: n }, (_, i) => `文本${… |
| start@49 | method | L49-49 | 每次调用新建 stream（重试不能复用同一个已锁住的 body） | const hangingBody = new ReadableStream<Uint8Array>({ start() { /* 永不 e… |
| start@78 | method | L78-78 | 大批：返回永不完成的 body，逼出超时→拆批 | const hanging = new ReadableStream<Uint8Array>({ start() {} }) |
| start@120 | method | L120-120 |  | const hanging = new ReadableStream<Uint8Array>({ start() {} }) |
