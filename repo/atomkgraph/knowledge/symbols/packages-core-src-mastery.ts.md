---
covers:
  - packages/core/src/mastery.ts
title: Semantic block index: mastery.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：mastery.ts（第4层）

**源码文件**：`packages/core/src/mastery.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="packages/core/src/mastery.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| MasteryWeights@12 | interface | L12-21 | ---- 多因子综合掌握度（计划书模块4）---- 主因子：难度加权正确率 + SM-2 派生分；小幅修正：学习时长 + 提问次数。 默认权重 50/30/20（计划书 8B「三因子权重 50/30/ | export interface MasteryWeights { |
| weightedAccuracy@41 | function | L41-53 | 难度加权正确率（0-1）。 | export function weightedAccuracy( |
| effortFactor@59 | function | L59-63 | 学习投入修正项（0-1）：时长与提问次数各占一半，均设饱和上限。 | export function effortFactor(studyMinutes: number, askCount: number): … |
| readingFactor@70 | function | L70-75 | R5 阅读维度（0-1）：阅读次数与停留时长各占一半，均设饱和上限。 | export function readingFactor(readCount: number, readDurationSec: numb… |
| compositeMastery@82 | function | L82-116 | 综合掌握度（0-100）。 | export function compositeMastery(input: { |
| aggregateMastery@124 | function | L124-141 | 父节点掌握度聚合（计划书 5.0）： | export function aggregateMastery( |
| inferFromParent@147 | function | L147-155 | 冷启动智能推断（计划书模块4）： | export function inferFromParent( |
