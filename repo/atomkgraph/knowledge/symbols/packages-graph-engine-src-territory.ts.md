---
covers:
  - packages/graph-engine/src/territory.ts
title: Semantic block index: territory.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：territory.ts（第4层）

**源码文件**：`packages/graph-engine/src/territory.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="packages/graph-engine/src/territory.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| Territory@29 | interface | L29-37 | 分区领土：一个闭合多边形（世界坐标，可能为凹形）。 | export interface Territory { |
| TerritoryOptions@39 | interface | L39-44 |  | export interface TerritoryOptions { |
| TerritoryLevelInput@47 | interface | L47-51 | 一层领土计算的输入：该层分区列表（提取只需 id）+ 节点归属映射。 | export interface TerritoryLevelInput { |
| computeTerritories@61 | function | L61-68 | 计算各分区的领土多边形（互不重叠、允许接壤）——单层便捷入口。 | export function computeTerritories( |
| computeTerritoryHierarchy@82 | function | L82-175 | 计算多层嵌套领土（「像城市一样逐级细分」）。 | export function computeTerritoryHierarchy( |
| defaultCell@178 | function | L178-192 | 默认格步长：长边约切 100 格，兼顾贴合精度与顶点数。 | function defaultCell(nodes: GraphNode[]): number { |
| extractOneRegion@211 | function | L211-304 | 提取某个分区的领土多边形。 | function extractOneRegion( |
| extractOneRegion.own@225 | arrow | L225-226 |  | const own = (c: number, r: number): string \| null => |
| extractOneRegion.cellOwner@229 | arrow | L229-230 |  | const cellOwner = (ci: number, cj: number): string \| null => |
| extractOneRegion.isCell@231 | arrow | L231-231 |  | const isCell = (ci: number, cj: number): boolean => cellOwner(ci, cj) … |
| extractOneRegion.worldOf@238 | arrow | L238-241 |  | const worldOf = (c: number, r: number): Point => ({ |
| extractOneRegion.keyOf@242 | arrow | L242-242 |  | const keyOf = (c: number, r: number): string => c + ',' + r |
| extractOneRegion.cornersOf@255 | arrow | L255-260 |  | const cornersOf = (ci: number, cj: number): Array<[number, number]> =>… |
| fromKey@307 | function | L307-312 | 把 "c,r" 键还原为世界坐标点。 | function fromKey(key: string, minX: number, minY: number, cell: number… |
| signedArea2@315 | function | L315-323 | 有向面积的两倍（>0 为逆时针）。 | function signedArea2(poly: Point[]): number { |
| simplifyCollinear@326 | function | L326-349 | 去掉共线中间点（含重复点），减少绘制顶点数。 | function simplifyCollinear(poly: Point[]): Point[] { |
