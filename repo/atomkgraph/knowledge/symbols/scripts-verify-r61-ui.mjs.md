---
covers:
  - scripts/verify-r61-ui.mjs
title: Semantic block index: verify-r61-ui.mjs (layer 4)
updated: 2026-11-24
---

# 语义块索引：verify-r61-ui.mjs（第4层）

**源码文件**：`scripts/verify-r61-ui.mjs`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="scripts/verify-r61-ui.mjs", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| sleep@31 | arrow | L31-31 |  | const sleep = (ms) => new Promise((r) => setTimeout(r, ms)) |
| assert@35 | function | L35-43 |  | function assert(cond, label, detail) { |
| apiJson@46 | function | L46-49 | 从后端拿范围与预期值（前端显示必须与它一致）。 | async function apiJson(path) { |
| waitForValue@58 | function | L58-67 | 轮询直到 fn() 返回期望值（或超时）。 | async function waitForValue(page, fn, expected, { timeout = 15000, int… |
| waitFor@70 | function | L70-78 | 轮询直到 fn() 返回真值（用在「等到某元素出现」这类判据上）。 | async function waitFor(page, fn, { timeout = 15000, interval = 200 } =… |
| READ_SCOPE_TOTAL@81 | arrow | L81-87 |  | const READ_SCOPE_TOTAL = () => { |
| clickTreeNodeAndWait@96 | function | L96-104 | R61-P3 后范围由侧栏驱动（题库自己的「范围」左栏已删）。 | async function clickTreeNodeAndWait(page, id, expected) { |
| clickUnlinkedAndWait@107 | function | L107-113 | 点列表顶部的「未关联」提示条（P3：它不是树节点，改成提示条了）。 | async function clickUnlinkedAndWait(page, expected) { |
| scopeTotal@116 | function | L116-119 | 从后端取某个范围的题数（作为前端应显示的期望值）。 | async function scopeTotal(scopeParam) { |
