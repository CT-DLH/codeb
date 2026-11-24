---
covers:
  - scripts/verify-graph-gesture.mjs
title: Semantic block index: verify-graph-gesture.mjs (layer 4)
updated: 2026-11-24
---

# 语义块索引：verify-graph-gesture.mjs（第4层）

**源码文件**：`scripts/verify-graph-gesture.mjs`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="scripts/verify-graph-gesture.mjs", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| check@13 | function | L13-16 |  | function check(cond, msg, detail = '') { |
| pageZoom@27 | arrow | L27-31 | 顶层页面缩放检测（对比 devicePixelRatio 与 visualViewport.scale） | const pageZoom = async () => page.evaluate(() => ({ |
| canvasZoom@34 | arrow | L34-37 | 读取工具栏里的缩放文本「缩放 0.60（domain）」 | const canvasZoom = async () => { |
| rect@39 | arrow | L39-39 |  | const rect = async () => page.locator(M).boundingBox() |
