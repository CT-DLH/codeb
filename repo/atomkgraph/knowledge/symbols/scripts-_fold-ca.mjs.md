---
covers:
  - scripts/_fold-ca.mjs
title: Semantic block index: _fold-ca.mjs (layer 4)
updated: 2026-11-24
---

# 语义块索引：_fold-ca.mjs（第4层）

**源码文件**：`scripts/_fold-ca.mjs`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="scripts/_fold-ca.mjs", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| sleep@20 | arrow | L20-20 |  | const sleep = (ms) => new Promise((r) => setTimeout(r, ms)) |
| assert@24 | arrow | L24-32 |  | const assert = (c, label, d) => { |
| api@33 | arrow | L33-33 |  | const api = async (p, opt) => (await fetch(API + p, opt)).json() |
| waitForValue@35 | function | L35-44 |  | async function waitForValue(page, fn, expected, timeout = 25000) { |
| READ_SCOPE_TOTAL@45 | arrow | L45-51 |  | const READ_SCOPE_TOTAL = () => { |
