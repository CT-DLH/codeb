---
covers:
  - scripts/verify-r61-nav.mjs
title: Semantic block index: verify-r61-nav.mjs (layer 4)
updated: 2026-11-24
---

# 语义块索引：verify-r61-nav.mjs（第4层）

**源码文件**：`scripts/verify-r61-nav.mjs`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="scripts/verify-r61-nav.mjs", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| sleep@39 | arrow | L39-39 |  | const sleep = (ms) => new Promise((r) => setTimeout(r, ms)) |
| assert@43 | arrow | L43-51 |  | const assert = (cond, label, detail) => { |
| waitForValue@54 | function | L54-66 | 轮询直到 fn() 等于期望值（判据必须是「等于」，truthy 会读到点击后仍渲染着的旧值）。 | async function waitForValue(page, fn, expected, { timeout = 20000, int… |
| api@68 | arrow | L68-68 |  | const api = async (p) => (await fetch(BASE + p)).json() |
| waitUp@92 | function | L92-104 |  | async function waitUp(timeoutMs = 45000) { |
| READ_SCOPE_TOTAL@107 | arrow | L107-113 | 页内取子：范围内计数、面包屑标题、aside 数量 | const READ_SCOPE_TOTAL = () => { |
| READ_CRUMB@114 | arrow | L114-117 |  | const READ_CRUMB = () => { |
| countReqs@159 | arrow | L159-159 |  | const countReqs = (needle) => reqs.filter((r) => r.includes(needle)).l… |
| walk@187 | arrow | L187-192 |  | const walk = (ns, depth) => { |
