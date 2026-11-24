---
covers:
  - packages/core/src/layout.ts
title: Semantic block index: layout.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：layout.ts（第4层）

**源码文件**：`packages/core/src/layout.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="packages/core/src/layout.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| Point@9 | interface | L9-12 |  | export interface Point { |
| PositionedNode@14 | interface | L14-21 |  | export interface PositionedNode { |
| dist@27 | function | L27-31 |  | export function dist(a: Point, b: Point): number { |
| SpatialGrid@34 | class | L34-68 | 空间网格索引：key = "gx,gy"，value = 该格内所有点 | export class SpatialGrid { |
| SpatialGrid.key@37 | method | L37-39 |  | private key(gx: number, gy: number): string { |
| SpatialGrid.add@41 | method | L41-48 |  | add(p: Point): void { |
| SpatialGrid.collides@51 | method | L51-67 | 检查点 p 是否与已有节点冲突（仅检查邻近 3x3 格） | collides(p: Point, minDist = MIN_DIST): boolean { |
| assignPosition@80 | function | L80-116 | 为新节点分配位置：以父节点为中心做黄金角螺旋采样，取首个无冲突点。 | export function assignPosition( |
| buildGrid@119 | function | L119-123 | 由已定位节点构建网格 | export function buildGrid(nodes: PositionedNode[]): SpatialGrid { |
| assignOrphanPosition@142 | function | L142-201 | 孤立节点（parent_id = null）的落位（R10）。 | export function assignOrphanPosition( |
| incrementalLayout@206 | function | L206-243 | 批量增量布局：按创建顺序为无坐标节点分配，不重排已有节点。 | export function incrementalLayout(nodes: Knowledge[]): PositionedNode[… |
