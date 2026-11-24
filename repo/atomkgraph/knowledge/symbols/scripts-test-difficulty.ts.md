---
covers:
  - scripts/test-difficulty.ts
title: Semantic block index: test-difficulty.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：test-difficulty.ts（第4层）

**源码文件**：`scripts/test-difficulty.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="scripts/test-difficulty.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| check@24 | function | L24-32 |  | function check(cond: unknown, msg: string, extra = ''): void { |
| seedLegacy@68 | function | L68-80 | 打开库、把指定行改成「老刻度」值、关闭（模拟迁移前的历史数据）。 | function seedLegacy(oldLevels: number[]): void { |
| readBack@83 | function | L83-89 | 迁移后读出两侧难度（按标题排序——create_time 同毫秒，不能用来定序）。 | function readBack(): { k: number[]; q: number[] } { |
