---
covers:
  - scripts/test-question-field-ops.ts
title: Semantic block index: test-question-field-ops.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：test-question-field-ops.ts（第4层）

**源码文件**：`scripts/test-question-field-ops.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="scripts/test-question-field-ops.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| check@25 | function | L25-33 |  | function check(cond: unknown, msg: string, detail = ''): void { |
| throwsCode@35 | function | L35-43 | 断言某次调用抛出指定 code 的 FieldOpError。 | function throwsCode(fn: () => unknown, code: string, msg: string): voi… |
| reload@47 | arrow | L47-47 |  | const reload = (id: string): Question => repo.findById(id) as Question |
| newQ@50 | function | L50-65 | 造一道有选项 / 多解 / 小问的题，供各段独立使用（互不污染）。 | function newQ() { |
