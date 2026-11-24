---
covers:
  - packages/graph-engine/src/terrain.ts
title: Semantic block index: terrain.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：terrain.ts（第4层）

**源码文件**：`packages/graph-engine/src/terrain.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="packages/graph-engine/src/terrain.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| TerrainOptions@22 | interface | L22-44 |  | export interface TerrainOptions { |
| TerrainLevelInput@47 | interface | L47-51 | 一层地形领土计算的输入：该层分区列表 + 节点归属映射（与 territory 层输入同构）。 | export interface TerrainLevelInput { |
| mulberry32@56 | function | L56-64 | mulberry32：确定性 PRNG，用于打乱 Simplex 置换表。 | export function mulberry32(seed: number): () => number { |
| Simplex@80 | class | L80-132 | 2D Simplex 噪声（Gustavson 式），输出约 [-1,1]。 | export class Simplex { |
| Simplex.noise@95 | method | L95-131 |  | noise(xin: number, yin: number): number { |
| fbm@135 | function | L135-147 | fBm：多倍频叠加，归一回约 [-1,1]。 | export function fbm(nz: Simplex, x: number, y: number, octaves: number… |
| computeTerrainHierarchy@163 | function | L163-252 | 计算多层有机斑块领土（语义噪声地形版）。 | export function computeTerrainHierarchy( |
| computeTerrainHierarchy.jitterAt@191 | arrow | L191-194 |  | const jitterAt = (x: number, y: number): Point => ({ |
| PatchParams@255 | interface | L255-266 | 造块所需的地形参数（内部传递）。 | interface PatchParams { |
| buildPatch@282 | function | L282-378 | 为一个分区造一块有机领土。 | function buildPatch( |
| buildPatch.distTo@316 | arrow | L316-325 |  | const distTo = (pts: GraphNode[], x: number, y: number): number => { |
| computeTerrain@381 | function | L381-388 | 单层便捷入口（语义与 computeTerritories 对齐）。 | export function computeTerrain( |
| defaultSpacing@400 | function | L400-418 | 节点平均最近邻间距（世界单位）——块大小与格粒度的统一尺度基准。 | function defaultSpacing(nodes: GraphNode[]): number { |
| polygonCentroid@426 | function | L426-449 | 多边形（简单、闭合、首尾不重复）的面积加权质心。 | function polygonCentroid(poly: Point[]): { cx: number; cy: number } { |
| extractPatchRing@462 | function | L462-538 | 提取单一块的边界格点环（格点下标序列，未抖动、未平滑）。 | function extractPatchRing( |
| extractPatchRing.isCell@468 | arrow | L468-469 |  | const isCell = (ci: number, cj: number): boolean => |
| extractPatchRing.vx@505 | arrow | L505-505 |  | const vx = (v: number): number => v % cols |
| extractPatchRing.vy@506 | arrow | L506-506 |  | const vy = (v: number): number => Math.floor(v / cols) |
| simplifyRing@541 | function | L541-555 | 去掉共线中间点（格点环专用）。 | function simplifyRing(ring: number[]): number[] { |
| decorateRing@564 | function | L564-610 | 把格点环变成有机边界：细分 → 抖动 → 闭式 Chaikin。 | function decorateRing( |
| decorateRing.edgeDense@575 | arrow | L575-587 |  | const edgeDense = (from: number, to: number): Point[] => { |
| chaikinClosed@613 | function | L613-627 | Chaikin 切角（闭式，循环）。 | function chaikinClosed(pts: Point[], passes: number): Point[] { |
