---
covers:
  - packages/graph-engine/src/path.ts
title: Semantic block index: path.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：path.ts（第4层）

**源码文件**：`packages/graph-engine/src/path.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="packages/graph-engine/src/path.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| isPrereq@7 | function | L7-9 |  | function isPrereq(e: GraphEdge): boolean { |
| PrereqGraph@11 | interface | L11-16 |  | interface PrereqGraph { |
| buildPrereqGraph@19 | function | L19-40 | 构建 prerequisite 邻接表/反邻接表/入度（仅两端都在 ids 内、排除自环）。 | function buildPrereqGraph(nodeIds: string[], edges: GraphEdge[]): Prer… |
| topoSortPrerequisite@48 | function | L48-72 | Kahn 拓扑排序（仅 prerequisite 边）。 | export function topoSortPrerequisite(nodeIds: string[], edges: GraphEd… |
| MainlineEdge@74 | interface | L74-77 |  | export interface MainlineEdge { |
| Mainline@80 | interface | L80-87 | 主线：最长前置链的关键路径子图（可含多条平行主线）。 | export interface Mainline { |
| computeMainline@99 | function | L99-155 | 求连通子图内的主线（最长前置链，平局时合并为平行主线）。 | export function computeMainline(nodeIds: string[], edges: GraphEdge[])… |
| mainlineToChain@161 | function | L161-187 | 从主线 DAG 中提取一条代表性线性链（用于简单场景 / 单链 Tour）。 | export function mainlineToChain(mainline: Mainline): string[] { |
| shortestPath@193 | function | L193-227 | BFS 求两点间最短依赖路径（可穿反向边）。 | export function shortestPath(fromId: string, toId: string, edges: Grap… |
| shortestPath.add@196 | arrow | L196-200 |  | const add = (a: string, b: string) => { |
