---
covers:
  - scripts/verify-session.mjs
title: Semantic block index: verify-session.mjs (layer 4)
updated: 2026-11-24
---

# 语义块索引：verify-session.mjs（第4层）

**源码文件**：`scripts/verify-session.mjs`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="scripts/verify-session.mjs", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| log@28 | arrow | L28-28 |  | const log = (...a) => console.log(...a) |
| check@31 | arrow | L31-39 |  | const check = (name, ok, extra) => { |
| sleep@40 | arrow | L40-40 |  | const sleep = (ms) => new Promise((r) => setTimeout(r, ms)) |
| text@51 | arrow | L51-52 |  | const text = async (sel) => |
| findRow@66 | arrow | L66-84 | 定位树里某一行（返回 caret 与标题 span 的真实坐标），用真实鼠标点击触发 React 合成事件 | const findRow = (label) => |
