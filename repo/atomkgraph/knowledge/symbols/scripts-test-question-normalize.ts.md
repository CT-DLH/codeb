---
covers:
  - scripts/test-question-normalize.ts
title: Semantic block index: test-question-normalize.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：test-question-normalize.ts（第4层）

**源码文件**：`scripts/test-question-normalize.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="scripts/test-question-normalize.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| check@29 | function | L29-37 |  | function check(cond: unknown, msg: string, extra = ''): void { |
| seedLegacy@345 | function | L345-371 | 直接写库伪造「迁移前」的形态：绕过归一，模拟历史数据。 | function seedLegacy(): void { |
| MigRow@373 | interface | L373-380 |  | interface MigRow { |
| readBack@383 | function | L383-392 | 迁移后读回全部题目（按 content 排序——create_time 同毫秒，不能用来定序）。 | function readBack(): MigRow[] { |
| optList@397 | arrow | L397-404 |  | const optList = (r?: MigRow): string[] => { |
| findOpt@405 | arrow | L405-405 |  | const findOpt = (kw: string): MigRow \| undefined => first.find((r) =>… |
| findText@406 | arrow | L406-406 |  | const findText = (kw: string): MigRow \| undefined => first.find((r) =… |
