---
covers:
  - scripts/verify-inline-editor.mjs
title: Semantic block index: verify-inline-editor.mjs (layer 4)
updated: 2026-11-24
---

# 语义块索引：verify-inline-editor.mjs（第4层）

**源码文件**：`scripts/verify-inline-editor.mjs`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="scripts/verify-inline-editor.mjs", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| sleep@27 | arrow | L27-27 |  | const sleep = (ms) => new Promise((r) => setTimeout(r, ms)) |
| check@30 | function | L30-33 |  | function check(cond, msg, detail = '') { |
| setReactInput@41 | function | L41-54 | 给 React 受控 input 赋值。 | async function setReactInput(page, selector, value) { |
| dblclickAt@261 | function | L261-270 | 用真实鼠标事件双击第 index 个匹配元素（合成 dblclick 会绕过浏览器的手势判定）。 | async function dblclickAt(sel, index = 0) { |
| clozeTargetId@433 | function | L433-435 | 当前页面停留的节点 id（可从 URL 的 ?node= 读）。 | function clozeTargetId() { |
