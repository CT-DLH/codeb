---
covers:
  - scripts/verify-question-panel.mjs
title: Semantic block index: verify-question-panel.mjs (layer 4)
updated: 2026-11-24
---

# 语义块索引：verify-question-panel.mjs（第4层）

**源码文件**：`scripts/verify-question-panel.mjs`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="scripts/verify-question-panel.mjs", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| sleep@30 | arrow | L30-30 |  | const sleep = (ms) => new Promise((r) => setTimeout(r, ms)) |
| check@33 | function | L33-36 |  | function check(cond, msg, detail = '') { |
| setReactInput@42 | function | L42-55 | 给 React 受控 input 赋值（直接改 el.value 不会触发 onChange）。 | async function setReactInput(page, selector, value) { |
| api@58 | arrow | L58-72 | ── 准备被试数据（走真实 HTTP，跑完清理） ───────────────────────────────── | const api = async (method, path, body) => { |
| cleanup@93 | function | L93-100 |  | async function cleanup() { |
| cardSel@314 | arrow | L314-314 | ── [5] 题目来源（R20） ─────────────────────────────────────────────────── | const cardSel = (id) => `[data-question-card="${id}"]` |
| clickSoft@507 | arrow | L507-507 | 注意：下面几处点击都用 .catch(() => {}) 吞掉「元素不存在」—— 若图整块没渲染出来（例如实现被注掉），我们要的是随后那些断言变红， 而不是在这里抛异常把后面几十条断言一起 | const clickSoft = (sel) => page.click(sel).catch(() => {}) |
