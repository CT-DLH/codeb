---
covers:
  - scripts/verify-perf.mjs
title: Semantic block index: verify-perf.mjs (layer 4)
updated: 2026-11-24
---

# 语义块索引：verify-perf.mjs（第4层）

**源码文件**：`scripts/verify-perf.mjs`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="scripts/verify-perf.mjs", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| sleep@23 | arrow | L23-23 |  | const sleep = (ms) => new Promise((r) => setTimeout(r, ms)) |
| bandIdx@27 | arrow | L27-27 |  | const bandIdx = (z) => Math.round(Math.log(Math.max(0.05, z)) / LOG_ST… |
| check@30 | arrow | L30-33 |  | const check = (ok, msg, detail = '') => { |
| canvasBox@51 | arrow | L51-52 |  | const canvasBox = async () => |
| frame@53 | arrow | L53-53 |  | const frame = () => page.evaluate(() => window.__akgFrame ?? null) |
| setZoom@56 | arrow | L56-76 | 精确调zoom：每 tick 的对数步长自适应（远跳大步、近调细步），以光标为锚点 Ctrl+wheel | const setZoom = async (target) => { |
| startRec@79 | arrow | L79-98 | 逐帧采样器：页面内 rAF 循环读取 __akgFrame | const startRec = () => |
| loop@83 | arrow | L83-96 |  | const loop = () => { |
| stopRec@99 | arrow | L99-99 |  | const stopRec = () => page.evaluate(() => { window.__recStop = true }) |
| takeRec@100 | arrow | L100-100 |  | const takeRec = () => page.evaluate(() => window.__rec) |
| avg@133 | arrow | L133-133 |  | const avg = (a) => a.reduce((s, x) => s + x, 0) / a.length |
