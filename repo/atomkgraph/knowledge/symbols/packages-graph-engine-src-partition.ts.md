---
covers:
  - packages/graph-engine/src/partition.ts
title: Semantic block index: partition.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：partition.ts（第4层）

**源码文件**：`packages/graph-engine/src/partition.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="packages/graph-engine/src/partition.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| Partition@20 | interface | L20-44 | 一个分区（= 顶层知识树的一棵子树）。 | export interface Partition { |
| Point@46 | interface | L46-49 |  | export interface Point { |
| buildParentMap@55 | function | L55-59 | 由节点列表构建父子索引。 | export function buildParentMap(nodes: GraphNode[]): ParentMap { |
| highestAncestor@66 | function | L66-75 | 向上回溯到该节点所属的最高层祖先（分区根）。 | export function highestAncestor(id: string, parents: ParentMap): strin… |
| convexHull@85 | function | L85-125 | 凸包（Andrew's monotone chain，O(n log n)）。 | export function convexHull(points: Point[]): Point[] { |
| convexHull.cross@97 | arrow | L97-98 |  | const cross = (o: Point, a: Point, b: Point): number => |
| assignPartitions@131 | function | L131-192 | 把节点按 parent_id 归入分区。 | export function assignPartitions(nodes: GraphNode[]): { |
| partitionOf@195 | function | L195-197 | 单点查询：某节点属于哪个分区（返回分区根 id；节点不存在时返回 null）。 | export function partitionOf(id: string, parents: ParentMap): string \|… |
| subgroupByParent@204 | function | L204-215 | 分区内的子分组：按「分区内的直接父节点」把成员分堆。 | export function subgroupByParent(nodes: GraphNode[], partitionId: stri… |
| topChildWithin@218 | function | L218-229 | 找到节点在指定分区内的「顶层子节点」（分区根的直接子节点）。 | function topChildWithin(id: string, partitionId: string, parents: Pare… |
| ancestorChain@239 | function | L239-251 | 节点 id 自身 → 逐层父 → 最高祖先 的链（含自身；防环，链断裂即止）。 | export function ancestorChain(id: string, parents: ParentMap): string[… |
| PartitionLevelInfo@254 | interface | L254-261 | 一个层级分区的静态信息（领土/绘制只需这些）。 | export interface PartitionLevelInfo { |
| PartitionLevel@262 | interface | L262-268 |  | export interface PartitionLevel { |
| PartitionLevelOptions@270 | interface | L270-279 |  | export interface PartitionLevelOptions { |
| buildPartitionLevels@290 | function | L290-326 | 逐层构建分区（层级化）。 | export function buildPartitionLevels( |
| deepestContainerLevel@338 | function | L338-344 | 「最深容器层」（R3-b4c）：仍存在多成员分区（memberIds.length > 1，即还能 | export function deepestContainerLevel(levels: PartitionLevel[]): numbe… |
