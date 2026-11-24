---
covers:
  - scripts/test-references.ts
title: Semantic block index: test-references.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：test-references.ts（第4层）

**源码文件**：`scripts/test-references.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="scripts/test-references.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| check@32 | function | L32-40 |  | function check(cond: unknown, msg: string, detail = ''): void { |
| j@41 | arrow | L41-41 |  | const j = (v: unknown): string => JSON.stringify(v) |
| safe@187 | function | L187-195 | 吞掉异常的 update。 | function safe(fn: () => unknown): string \| null { |
| tryUpdate@196 | arrow | L196-197 |  | const tryUpdate = (id: string, patch: Record<string, unknown>): string… |
