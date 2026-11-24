---
covers:
  - scripts/_proto-terrain.ts
title: Semantic block index: _proto-terrain.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：_proto-terrain.ts（第4层）

**源码文件**：`scripts/_proto-terrain.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="scripts/_proto-terrain.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| Kn@20 | interface | L20-24 |  | interface Kn { |
| warp@78 | function | L78-83 | domain warp（让山脉弯曲、河谷蜿蜒） | function warp(x: number, y: number): [number, number] { |
| traceDown@121 | function | L121-165 |  | function traceDown(r0: number, c0: number): { sinkR: number; sinkC: nu… |
| isRiver@233 | arrow | L233-233 |  | const isRiver = (i: number): boolean => flow[i]! >= riverThresh |
| isWater@284 | arrow | L284-287 | ---------------------------------------------------- 城市选址（知识点） 知识点 → 城市：只在「平原」（0.06 ~ 0.30）、且不贴水（离水 | const isWater = (r: number, c: number): boolean => { |
| findCitySpot@288 | function | L288-329 |  | function findCitySpot(x: number, y: number): { r: number; c: number; h… |
| elevationColor@341 | function | L341-397 |  | function elevationColor(hh: number, sx: number, sy: number, out: Uint8… |
| slopeAt@400 | function | L400-407 | 计算坡度 | function slopeAt(r: number, c: number): { sx: number; sy: number } { |
| slopeAt.at@401 | arrow | L401-402 |  | const at = (rr: number, cc: number): number => |
| drawRiverLine@432 | function | L432-462 | 叠加河流：把河道折线画到像素缓冲（Bresenham 风格的粗线段 + 抗锯齿近似） | function drawRiverLine(a: { x: number; y: number }, b: { x: number; y:… |
| drawCity@477 | function | L477-510 | 叠加城市（金色点 + 光圈） | function drawCity(c: { r: number; c: number }, mastery: number): void … |
| crc32@517 | function | L517-526 | ---------------------------------------------------- PNG 编码（无外部依赖） | function crc32(buf: Uint8Array): number { |
| chunk@528 | function | L528-537 |  | function chunk(type: string, data: Uint8Array): Uint8Array { |
