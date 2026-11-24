---
covers:
  - scripts/verify-r27-ui.mjs
title: Semantic block index: verify-r27-ui.mjs (layer 4)
updated: 2026-11-24
---

# 语义块索引：verify-r27-ui.mjs（第4层）

**源码文件**：`scripts/verify-r27-ui.mjs`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="scripts/verify-r27-ui.mjs", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| sleep@54 | arrow | L54-54 |  | const sleep = (ms) => new Promise((r) => setTimeout(r, ms)) |
| check@57 | function | L57-60 |  | function check(cond, msg, detail = '') { |
| api@62 | arrow | L62-76 |  | const api = async (method, path, body) => { |
| clickSoft@162 | arrow | L162-168 |  | const clickSoft = async (sel) => { |
| typeSoft@172 | arrow | L172-179 | （U5 变异实测：块被注掉后 page.type 直接抛，后面 6 条断言全部失踪）。 */ | const typeSoft = async (sel, text) => { |
| settle@183 | arrow | L183-191 | 后端 PATCH 成功 ≠ 页面已重渲染——两者之间隔着一次 fetch + React 提交， 抢跑会得到「后端对了、DOM 还没变」的假红（本轮 [6b]/[7] 就是这么翻的）。 */ | const settle = async (timeout = 8000) => { |
| waitDom@195 | arrow | L195-202 | 在浏览器上下文里不存在，必须显式传参（本轮实测踩到：rel1 is not defined）。 */ | const waitDom = async (fn, ...args) => { |
