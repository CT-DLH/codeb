---
covers:
  - scripts/_proto-region.ts
title: Semantic block index: _proto-region.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：_proto-region.ts（第4层）

**源码文件**：`scripts/_proto-region.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="scripts/_proto-region.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| Kn@26 | interface | L26-32 |  | interface Kn { |
| warp@157 | function | L157-162 |  | function warp(x: number, y: number): [number, number] { |
| isRiver@235 | arrow | L235-235 |  | const isRiver = (i: number): boolean => flow[i]! >= riverThresh |
| findCitySpot@245 | function | L245-268 | ---------------------------------------------------- ⑤ 城市选址（就近吸附到平台） | function findCitySpot(x: number, y: number): { r: number; c: number } … |
| colorAt@277 | function | L277-344 |  | function colorAt(hh: number, plat: number, sx: number, sy: number, out… |
| slAt@346 | function | L346-350 |  | function slAt(r: number, c: number): { sx: number; sy: number } { |
| slAt.at@347 | arrow | L347-348 |  | const at = (rr: number, cc: number): number => |
| drawLine@423 | function | L423-451 |  | function drawLine(a: { x: number; y: number }, b: { x: number; y: numb… |
| drawCity@480 | function | L480-510 | 城市点（金色） | function drawCity(c: { r: number; c: number }): void { |
| crc32@514 | function | L514-521 | ---------------------------------------------------- PNG 编码 | function crc32(buf: Uint8Array): number { |
| chunk@522 | function | L522-530 |  | function chunk(type: string, data: Uint8Array): Uint8Array { |
