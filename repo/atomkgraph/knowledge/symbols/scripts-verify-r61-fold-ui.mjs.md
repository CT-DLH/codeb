---
covers:
  - scripts/verify-r61-fold-ui.mjs
title: Semantic block index: verify-r61-fold-ui.mjs (layer 4)
updated: 2026-11-24
---

# 语义块索引：verify-r61-fold-ui.mjs（第4层）

**源码文件**：`scripts/verify-r61-fold-ui.mjs`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="scripts/verify-r61-fold-ui.mjs", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| sleep@27 | arrow | L27-27 |  | const sleep = (ms) => new Promise((r) => setTimeout(r, ms)) |
| assert@31 | function | L31-39 |  | function assert(cond, label, detail) { |
| waitFor@41 | function | L41-49 |  | async function waitFor(page, fn, { timeout = 15000, interval = 200 } =… |
