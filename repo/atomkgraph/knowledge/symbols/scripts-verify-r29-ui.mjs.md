---
covers:
  - scripts/verify-r29-ui.mjs
title: Semantic block index: verify-r29-ui.mjs (layer 4)
updated: 2026-11-24
---

# 语义块索引：verify-r29-ui.mjs（第4层）

**源码文件**：`scripts/verify-r29-ui.mjs`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="scripts/verify-r29-ui.mjs", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| sleep@45 | arrow | L45-45 |  | const sleep = (ms) => new Promise((r) => setTimeout(r, ms)) |
| check@48 | function | L48-51 |  | function check(cond, msg, detail = '') { |
| api@53 | arrow | L53-67 |  | const api = async (method, path, body) => { |
| clickSoft@205 | arrow | L205-212 |  | const clickSoft = async (sel) => { |
| waitDom@216 | arrow | L216-223 | 闭包变量在浏览器上下文里不存在，必须显式传参（本项目栽过两次）。 */ | const waitDom = async (fn, ...args) => { |
| setValue@226 | arrow | L226-240 |  | const setValue = async (sel, value) => { |
