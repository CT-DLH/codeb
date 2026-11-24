---
covers:
  - packages/graph-engine/src/viewport.ts
title: Semantic block index: viewport.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：viewport.ts（第4层）

**源码文件**：`packages/graph-engine/src/viewport.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="packages/graph-engine/src/viewport.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| worldToScreen@10 | function | L10-20 | 世界坐标 → 屏幕坐标 | export function worldToScreen( |
| screenToWorld@23 | function | L23-33 | 屏幕坐标 → 世界坐标 | export function screenToWorld( |
| visibleWorldRect@36 | function | L36-48 | 当前视口对应的世界坐标矩形（用于裁剪） | export function visibleWorldRect( |
| cullNodes@51 | function | L51-65 | 裁剪：只返回视口矩形内（含边距）的节点。 | export function cullNodes( |
| lodForZoom@68 | function | L68-72 | 按缩放决定 LOD 层级：拉远看全貌，拉近看细节。 | export function lodForZoom(zoom: number): LodLevel { |
| ramp@75 | function | L75-79 | 把 x 从 [a,b] 线性映射到 [0,1]，并夹到边界。 | export function ramp(x: number, a: number, b: number): number { |
| smoothstep@82 | function | L82-84 | 平滑插值（smoothstep），让过渡在两端更柔和。 | export function smoothstep(t: number): number { |
| nodeRadiusForZoom@90 | function | L90-95 | 节点半径随缩放的连续插值（取代原来「cluster ? 10+… : 6」的硬编码）。 | export function nodeRadiusForZoom(zoom: number, isCluster = false, mem… |
| labelAlphaForZoom@103 | function | L103-107 | 标签透明度随缩放的连续渐变（取代「只有 detail 层才显示标签」的硬切）。 | export function labelAlphaForZoom(zoom: number): number { |
| revealThresholdFor@149 | function | L149-151 | 「层 parentLevel 的块」其子块浮现所需的最小屏幕短边（px）。 | export function revealThresholdFor(parentLevel: number): number { |
| childRevealProgress@157 | function | L157-160 | 某块的子块浮现进度（0~1）：由这块当前的屏幕短边与它所在层级的门槛决定。 | export function childRevealProgress(screenShortPx: number, parentLevel… |
| RevealMetrics@163 | interface | L163-165 | 揭示判据所需的度量：各层最大块的世界 bbox 短边（索引 = level-1）。 | export interface RevealMetrics { |
| showAtomicNodes@177 | function | L177-187 | 是否显示「原子知识点」：最深容器层（仍能按树拆出子块的最深层， | export function showAtomicNodes(zoom: number, depth: number, metrics?:… |
| zoomAt@190 | function | L190-203 | 缩放（以屏幕某点为锚点，保持该点世界坐标不变）。 | export function zoomAt( |
