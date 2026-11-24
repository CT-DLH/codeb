---
covers:
  - packages/graph-engine/src/lod.ts
title: Semantic block index: lod.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：lod.ts（第4层）

**源码文件**：`packages/graph-engine/src/lod.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="packages/graph-engine/src/lod.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| clusterZoomBand@17 | function | L17-21 | 聚合 zoom 分档：把连续 zoom 量化到 ~12% 间隔的档位。 | export function clusterZoomBand(zoom: number, step = 1.12): number { |
| gridSizeForZoom@25 | function | L25-32 | 聚合网格大小（世界单位）。越大聚合越狠。 | export function gridSizeForZoom(zoom: number): number { |
| ClusterOptions@35 | interface | L35-63 | clusterNodes 的可选配置。 | export interface ClusterOptions { |
| clusterNodes@71 | function | L71-134 | 把节点聚合为渲染单元。 | export function clusterNodes( |
| clusterNodesByPartition@140 | function | L140-148 | 便捷入口：一次性算出分区并做父子感知聚合。 | export function clusterNodesByPartition( |
| partitionMap@151 | function | L151-155 | 供上层复用：从节点列表直接得到分区映射。 | export function partitionMap(nodes: GraphNode[]): ParentMap { |
| nodeToUnit@157 | function | L157-167 |  | function nodeToUnit(n: GraphNode): RenderUnit { |
