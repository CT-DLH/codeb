---
covers:
  - scripts/_proto-v3.ts
title: Semantic block index: _proto-v3.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：_proto-v3.ts（第4层）

**源码文件**：`scripts/_proto-v3.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="scripts/_proto-v3.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| cellOf@50 | arrow | L50-53 |  | const cellOf = (x: number, y: number): [number, number] => [ |
| nearestDist@62 | function | L62-82 | 到最近其他知识点的距离（世界单位）。环形扩散搜索，找到就停。 | function nearestDist(x: number, y: number, skipSelf = false): number { |
| warp@102 | function | L102-107 |  | function warp(x: number, y: number): [number, number] { |
| naturalTerrain@110 | function | L110-123 | 自然地形高程（不含知识点影响）：值域约 [-1,1]，>0 陆、<0 海。 | function naturalTerrain(x: number, y: number): number { |
| knowledgeField@130 | function | L130-154 | 知识场（0~1）：知识点密集处接近 1，远处衰减到 0。 | function knowledgeField(x: number, y: number): number { |
| colorOf@198 | function | L198-246 |  | function colorOf(hh: number, sx: number, sy: number, out: Uint8Array, … |
| slAt@248 | function | L248-255 |  | function slAt(px: number, py: number): { sx: number; sy: number } { |
| slAt.at@249 | arrow | L249-250 |  | const at = (x: number, y: number): number => |
| contourHit@268 | function | L268-273 |  | function contourHit(h0: number, h1: number): boolean { |
| isRiver@329 | arrow | L329-329 |  | const isRiver = (i: number): boolean => flow[i]! >= riverThresh |
| drawCity@363 | function | L363-385 | ---------------------------------------------------- 城市点 | function drawCity(x: number, y: number): void { |
| crc32@389 | function | L389-396 | ---------------------------------------------------- PNG 编码 | function crc32(buf: Uint8Array): number { |
| chunk@397 | function | L397-405 |  | function chunk(type: string, data: Uint8Array): Uint8Array { |
