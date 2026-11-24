---
covers:
  - packages/core/src/difficulty.ts
title: Semantic block index: difficulty.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：difficulty.ts（第4层）

**源码文件**：`packages/core/src/difficulty.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="packages/core/src/difficulty.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| clampDifficulty@29 | function | L29-36 | 归一化难度到 [0,1]：非数字 / NaN / 越界一律收敛，绝不抛错。 | export function clampDifficulty(value: unknown): number { |
| difficultyWeight@45 | function | L45-47 | 难度 → 权重（1-5）。 | export function difficultyWeight(difficulty: unknown): number { |
