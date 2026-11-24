---
covers:
  - scripts/test-territory.ts
title: Semantic block index: test-territory.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：test-territory.ts（第4层）

**源码文件**：`scripts/test-territory.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="scripts/test-territory.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| assert@18 | function | L18-26 |  | function assert(cond: boolean, label: string): void { |
| N@28 | arrow | L28-37 |  | const N = (id: string, parentId: string \| null, x: number, y: number,… |
| pointInPolygon@40 | function | L40-50 | 点是否在多边形内（射线法）。 | function pointInPolygon(p: Point, poly: Point[]): boolean { |
| overlapRatio@53 | function | L53-63 | 用稠密栅格采样，统计两多边形「同时被覆盖」的采样点比例（≈ 重叠面积占比）。 | function overlapRatio(a: Point[], b: Point[], bounds: Bounds, step = 4… |
| Bounds@65 | interface | L65-70 |  | interface Bounds { |
| boundsOf@72 | function | L72-86 |  | function boundsOf(tss: Territory[]): Bounds { |
| shareEdge@125 | function | L125-138 | 检查是否存在一条边，被两个多边形的边「重合」（相邻分区沿同一格边贴合） | function shareEdge(a: Point[], b: Point[]): boolean { |
| shareEdge.keyOf@126 | arrow | L126-129 |  | const keyOf = (p: Point, q: Point): string => { |
| outsideParentRatio@225 | function | L225-245 | 子层领土必须落在父层领土内部（采样：在子层包围盒内取半格偏移点） | function outsideParentRatio(child: Point[], parent: Point[], step = 5)… |
| parentOf@252 | arrow | L252-256 | 层 3 ⊂ 层 2：进程管理 ⊂ 操作系统，数据链路层 ⊂ 计算机网络 | const parentOf = (title: string): Point[] => { |
| bboxShort@322 | arrow | L322-334 |  | const bboxShort = (poly: Point[]): number => { |
