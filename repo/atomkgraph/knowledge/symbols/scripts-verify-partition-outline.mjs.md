---
covers:
  - scripts/verify-partition-outline.mjs
title: Semantic block index: verify-partition-outline.mjs (layer 4)
updated: 2026-11-24
---

# 语义块索引：verify-partition-outline.mjs（第4层）

**源码文件**：`scripts/verify-partition-outline.mjs`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="scripts/verify-partition-outline.mjs", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| check@24 | arrow | L24-27 |  | const check = (name, ok, extra) => { |
| sleep@28 | arrow | L28-28 |  | const sleep = (ms) => new Promise((r) => setTimeout(r, ms)) |
| isPartitionColor@52 | arrow | L52-52 | 是否含分区色（88,166,255） | const isPartitionColor = (s) => /88,\s*166,\s*255/.test(s) |
| getZoom@74 | arrow | L74-80 | 读取画布的 zoom（工具栏「缩放 0.60（domain）」） | const getZoom = () => |
| canvasBox@84 | arrow | L84-84 | 把画布调到指定 zoom：Ctrl+wheel（模拟触控板捏合）→ 缩放 每步 factor = exp(-deltaY*0.01)，取 deltaY=±10 → 每步约 1.105 倍，避免过冲 | const canvasBox = async () => page.$eval(M, (el) => { const r = el.get… |
| setZoom@86 | arrow | L86-104 |  | const setZoom = async (target) => { |
| snapshot@105 | arrow | L105-120 |  | const snapshot = () => |
| measure@129 | arrow | L129-142 | ② settle 后 reset 探针 ③ 再打一次「1 单位」的极小缩放抖动 → 只此一帧被计入 这样拿到的就是「目标 zoom 下」的纯净一帧。 | const measure = async (target) => { |
