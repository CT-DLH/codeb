---
covers:
  - scripts/test-terrain.ts
title: Semantic block index: test-terrain.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：test-terrain.ts（第4层）

**源码文件**：`scripts/test-terrain.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="scripts/test-terrain.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| assert@22 | function | L22-30 |  | function assert(cond: boolean, label: string): void { |
| N@32 | arrow | L32-41 |  | const N = (id: string, parentId: string \| null, x: number, y: number,… |
| pointInPolygon@43 | function | L43-53 |  | function pointInPolygon(p: Point, poly: Point[]): boolean { |
| distToPolygon@55 | function | L55-69 |  | function distToPolygon(p: Point, poly: Point[]): number { |
| bboxOf@71 | function | L71-83 |  | function bboxOf(poly: Point[]): { x0: number; y0: number; x1: number; … |
| signedArea2@85 | function | L85-93 |  | function signedArea2(poly: Point[]): number { |
| makeNodes@98 | function | L98-123 | ------------------------------------------------------------------ 测试数据：3 根 × 若干分支 × 若干叶子（坐标故意乱放——布局 | function makeNodes(): GraphNode[] { |
| leavesOf@172 | arrow | L172-181 | [A5] 子树聚团：三个根子树的叶子包围盒互不侵入（允许 1e-6 误差） | const leavesOf = (root: string): Point[] => |
| sep@183 | arrow | L183-184 |  | const sep = (a: ReturnType<typeof bboxOf>, b: ReturnType<typeof bboxOf… |
| descendants@191 | arrow | L191-201 | [A6] 多子内部节点 = 后代质心 | const descendants = (id: string): string[] => { |
| walk@193 | arrow | L193-198 |  | const walk = (x: string): void => { |
| boxOf@241 | arrow | L241-247 |  | const boxOf = (id: string): ReturnType<typeof bboxOf> => { |
| gapBetween@248 | arrow | L248-255 |  | const gapBetween = (a: ReturnType<typeof bboxOf>, b: ReturnType<typeof… |
| boxOf0@268 | arrow | L268-274 |  | const boxOf0 = (id: string): ReturnType<typeof bboxOf> => { |
