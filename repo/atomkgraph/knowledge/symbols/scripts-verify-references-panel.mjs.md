---
covers:
  - scripts/verify-references-panel.mjs
title: Semantic block index: verify-references-panel.mjs (layer 4)
updated: 2026-11-24
---

# 语义块索引：verify-references-panel.mjs（第4层）

**源码文件**：`scripts/verify-references-panel.mjs`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="scripts/verify-references-panel.mjs", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| sleep@40 | arrow | L40-40 |  | const sleep = (ms) => new Promise((r) => setTimeout(r, ms)) |
| check@43 | function | L43-46 |  | function check(cond, msg, detail = '') { |
| api@48 | arrow | L48-62 |  | const api = async (method, path, body) => { |
| clickSoft@111 | arrow | L111-117 |  | const clickSoft = async (sel) => { |
| commitRefs@190 | arrow | L190-201 | ⚠️ 必须先 focus() 再 blur()：对没有焦点的元素调 blur() 不会派发任何事件， React 的 onBlur（基于 focusout）也就永远不触发——「改完没保 | const commitRefs = async (text) => { |
