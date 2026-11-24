---
covers:
  - scripts/test-markdown-check.ts
title: Semantic block index: test-markdown-check.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：test-markdown-check.ts（第4层）

**源码文件**：`scripts/test-markdown-check.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="scripts/test-markdown-check.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| check@22 | function | L22-30 |  | function check(cond: unknown, msg: string, detail = ''): void { |
| j@31 | arrow | L31-31 |  | const j = (v: unknown): string => JSON.stringify(v) |
| safe@34 | function | L34-40 | 安全执行：让「应该被拒绝/不该抛」的分支变成红断言，而不是让脚本崩掉。 | function safe<T>(fn: () => T): { v: T \| null; err: string } { |
| kinds@42 | arrow | L42-45 |  | const kinds = (r: { errors: { kind: string }[]; warnings: { kind: stri… |
