---
covers:
  - packages/graph-engine/src/status.ts
title: Semantic block index: status.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：status.ts（第4层）

**源码文件**：`packages/graph-engine/src/status.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="packages/graph-engine/src/status.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| masteryStatus@6 | function | L6-11 | 掌握度 → 状态（与 ReviewService 默认阈值一致）。 | export function masteryStatus(score: number, weak = 40, mastered = 80)… |
| colorForMastery@21 | function | L21-23 | 节点填充色。 | export function colorForMastery(score: number): string { |
| edgeStyleFor@26 | function | L26-37 | 关系类型 → 边的样式（前置=实线箭头，相关=虚线，易混=点线）。 | export function edgeStyleFor(type: string): { dash: number[]; color: s… |
