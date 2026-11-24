---
covers:
  - apps/web/src/components/GraphView.tsx
title: Semantic block index: GraphView.tsx (layer 4)
updated: 2026-11-24
---

# 语义块索引：GraphView.tsx（第4层）

**源码文件**：`apps/web/src/components/GraphView.tsx`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="apps/web/src/components/GraphView.tsx", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| distance@43 | arrow | L43-44 |  | const distance = (a: { x: number; y: number }, b: { x: number; y: numb… |
| traceRoundedPolygon@50 | function | L50-80 | 画「圆角化」凸包路径：每个顶点用二次贝塞尔过渡，形成圆润的城区轮廓。 | function traceRoundedPolygon( |
| polyArea@83 | function | L83-91 | 多边形有向面积的绝对值（用于排序：大领土先画）。 | function polyArea(pts: Array<{ x: number; y: number }>): number { |
| worldBBox@94 | function | L94-111 | 世界坐标包围盒（territoryLevels memo 时算一次，渲染帧内只做相交判定）。 | function worldBBox(pts: Array<{ x: number; y: number }>): { |
| clipPolyToRect@120 | function | L120-162 | Sutherland–Hodgman：把屏幕多边形裁剪到矩形 [minX,maxX]×[minY,maxY] 内。 | function clipPolyToRect( |
| clipPolyToRect.clipEdge@127 | arrow | L127-143 |  | const clipEdge = ( |
| toScreenSparse@171 | function | L171-203 | 世界多边形 → 屏幕多边形（裁剪 + 稀疏化两级）： | function toScreenSparse( |
| hashSeed@208 | function | L208-215 | 块 id → 稳定噪声种子（FNV-1a：同 id 恒同 seed，重排不换地形）。 | function hashSeed(s: string): number { |
| BakedTile@218 | interface | L218-222 | 一块烘焙产物的形状（ref 缓存条目）。 | interface BakedTile { |
| bakeTerrainTile@235 | function | L235-274 | 烘焙一块地形贴图：高程场 → 逐像素色带+hillshade（ImageData）→ 离屏 canvas。 | function bakeTerrainTile(polygon: Point[], seed: number): BakedTile \|… |
| GraphView@276 | function | L276-978 |  | export function GraphView({ |
| GraphView.isTag@506 | arrow | L506-506 |  | const isTag = (id: string) => kindOf.get(id) === 'tag' |
| GraphView.shortOf@531 | arrow | L531-532 |  | const shortOf = (bb: { minX: number; minY: number; maxX: number; maxY:… |
| GraphView.overlaps@656 | arrow | L656-657 |  | const overlaps = (r: typeof rect): boolean => |
| GraphView.localPoint@814 | arrow | L814-818 |  | const localPoint = (e: { clientX: number; clientY: number }): { x: num… |
| GraphView.canvasSize@820 | arrow | L820-823 |  | const canvasSize = (): { width: number; height: number } => ({ |
| GraphView.onPointerDown@854 | arrow | L854-877 |  | const onPointerDown = (e: React.PointerEvent<HTMLCanvasElement>) => { |
| GraphView.onPointerMove@879 | arrow | L879-910 |  | const onPointerMove = (e: React.PointerEvent<HTMLCanvasElement>) => { |
| GraphView.endPointer@912 | arrow | L912-927 |  | const endPointer = (e: React.PointerEvent<HTMLCanvasElement>) => { |
| GraphView.onClick@929 | arrow | L929-948 |  | const onClick = (e: React.MouseEvent<HTMLCanvasElement>) => { |
| GraphView.zoomBy@950 | arrow | L950-953 |  | const zoomBy = (factor: number) => { |
