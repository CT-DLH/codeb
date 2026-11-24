---
covers:
  - scripts/test-elevation.ts
title: Semantic block index: test-elevation.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：test-elevation.ts（第4层）

**源码文件**：`scripts/test-elevation.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="scripts/test-elevation.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| assert@18 | function | L18-26 |  | function assert(cond: boolean, label: string): void { |
| circlePoly@29 | function | L29-36 | 合成圆形多边形（n 边形，半径 R，中心 cx,cy）——足够大的「岛」。 | function circlePoly(cx: number, cy: number, R: number, n = 64): Point[… |
| sampleH@39 | function | L39-52 | 场内任意点的高程（双线性插值），供等高线验证。 | function sampleH(field: ReturnType<typeof buildElevationField>, x: num… |
