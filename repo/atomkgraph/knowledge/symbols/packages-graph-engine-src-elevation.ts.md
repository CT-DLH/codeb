---
covers:
  - packages/graph-engine/src/elevation.ts
title: Semantic block index: elevation.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：elevation.ts（第4层）

**源码文件**：`packages/graph-engine/src/elevation.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="packages/graph-engine/src/elevation.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| ElevationOptions@20 | interface | L20-31 |  | export interface ElevationOptions { |
| ElevationField@34 | interface | L34-47 | 一个块的高程场（局部网格，世界坐标 = x0 + col×cell）。 | export interface ElevationField { |
| rasterize@55 | function | L55-89 | 多边形栅格化（扫描线，偶奇规则）→ 0/1 掩码。 | function rasterize( |
| chamferSignedDistance@95 | function | L95-159 | 两遍 chamfer 距离变换（3-4 权重 ≈ 欧氏 ×cell）。 | function chamferSignedDistance( |
| buildElevationField@172 | function | L172-242 | 为一个块构建高程场。 | export function buildElevationField(polygon: Point[], opts: ElevationO… |
| largestComponent@248 | function | L248-288 | 掩码最大 4-连通域（8 邻域用 4 邻域近似即可——贴图细节容差）。 | function largestComponent(mask: Uint8Array, cols: number, rows: number… |
| largestComponent.push@266 | arrow | L266-273 | 4 邻域 | const push = (rr: number, cc: number): void => { |
| contourSegments@293 | function | L293-344 | 单条等高线的全部线段（世界坐标）。marching squares，线性插值交点。 | export function contourSegments(field: ElevationField, level: number):… |
| contourSegments.val@296 | arrow | L296-296 |  | const val = (r: number, c: number): number => h[r * cols + c]! |
| contourSegments.lerp@297 | arrow | L297-300 |  | const lerp = (a: number, b: number): number => { |
| contourSegments.ptH@303 | arrow | L303-306 |  | const ptH = (r: number, c: number, a: number, b: number): [number, num… |
| contourSegments.ptV@307 | arrow | L307-310 |  | const ptV = (r: number, c: number, a: number, b: number): [number, num… |
| contourSegments.top@324 | arrow | L324-324 | 四边的交点（需要时才算） | const top = (): [number, number] => ptH(r, c, tl, tr) |
| contourSegments.right@325 | arrow | L325-325 |  | const right = (): [number, number] => ptV(r, c + 1, tr, br) |
| contourSegments.bottom@326 | arrow | L326-326 |  | const bottom = (): [number, number] => ptH(r + 1, c, bl, br) |
| contourSegments.left@327 | arrow | L327-327 |  | const left = (): [number, number] => ptV(r, c, tl, bl) |
| contourSegments.push@328 | arrow | L328-330 |  | const push = (p: [number, number], q: [number, number]): void => { |
| contourRings@350 | function | L350-405 | 把线段拼接成折线（闭合环或边缘开链）。 | export function contourRings(field: ElevationField, level: number): Po… |
| contourRings.key@354 | arrow | L354-354 | 端点键：把坐标量化到 1e-4（同一边的交点由同一次插值算出，逐位相同） | const key = (x: number, y: number): string => `${Math.round(x * 1e4)}:… |
| elevationColor@419 | function | L419-469 | 高程 + 坡度 → RGB（暗色卫星图色带 + hillshade）。 | export function elevationColor(h: number, slopeX: number, slopeY: numb… |
| fieldSlope@472 | function | L472-479 | 网格差分坡度（1/世界单位）：供 elevationColor 的 hillshade。 | export function fieldSlope(field: ElevationField, r: number, c: number… |
| fieldSlope.at@474 | arrow | L474-475 |  | const at = (rr: number, cc: number): number => |
| BuildingRect@484 | interface | L484-493 | 一个小建筑矩形（世界坐标，绕自身中心旋转）。 | export interface BuildingRect { |
| cityTexture@500 | function | L500-529 | 城镇肌理（L4）：每个成员点周围生成一小簇矩形「建筑」。 | export function cityTexture( |
