---
covers:
  - scripts/verify-r62-delete-ui.mjs
title: Semantic block index: verify-r62-delete-ui.mjs (layer 4)
updated: 2026-11-24
---

# 语义块索引：verify-r62-delete-ui.mjs（第4层）

**源码文件**：`scripts/verify-r62-delete-ui.mjs`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="scripts/verify-r62-delete-ui.mjs", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| sleep@78 | arrow | L78-78 |  | const sleep = (ms) => new Promise((r) => setTimeout(r, ms)) |
| check@81 | function | L81-84 |  | function check(cond, msg, detail = '') { |
| note@96 | function | L96-99 |  | function note(msg, detail = '') { |
| api@101 | arrow | L101-115 |  | const api = async (method, path, body) => { |
| die@126 | arrow | L126-129 | Assertion failed: !(handle->flags & UV_HANDLE_CLOSING), file src\win\async.c， 进程以 0xC0000409 崩溃——把 | const die = (code, msg) => { |
| pidAlive@151 | arrow | L151-160 |  | const pidAlive = (pid) => { |
| readLockPid@163 | arrow | L163-170 |  | const readLockPid = () => { |
| lockRefuse@172 | arrow | L172-182 |  | const lockRefuse = (why) => |
| destroy@240 | arrow | L240-247 |  | const destroy = async (id) => { |
| T@260 | arrow | L260-260 |  | const T = (s) => `__R62UI ${s} ${TOK}__` |
| mk@286 | arrow | L286-300 | 主场景：root → mid → (leaf1, leaf2)，另加一个关系对端 peer（peer→mid 一条入边， 让「关系数 M」是个非零且唯一的数字，避免 0 在文案里到处命中造成假 | const mk = async (title, parent_id) => { |
| cleanup@328 | arrow | L328-330 |  | const cleanup = async (ids) => { |
| clickSoft@361 | arrow | L361-368 |  | const clickSoft = async (sel) => { |
| waitDom@372 | arrow | L372-379 | 浏览器上下文里不存在，必须显式传参（R27 实测踩到：rel1 is not defined）。 */ | const waitDom = async (fn, ...args) => { |
| settle@382 | arrow | L382-390 |  | const settle = async (timeout = 8000) => { |
| sel@392 | arrow | L392-392 |  | const sel = (t) => `[data-testid="${t}"]` |
| nodeOf@393 | arrow | L393-393 |  | const nodeOf = (id) => `[data-tree-node="${id}"]` |
| parentOf@402 | arrow | L402-402 | 我第一版写成 data.parent_id → 恒为 undefined → [4b]/[7c]/[8b] 恒红， 连正确实现也会被判失败（假红）。这类「读错响应形状」的 bug 是验 | const parentOf = (r) => r?.data?.knowledge?.parent_id |
| readErrorTexts@417 | arrow | L417-427 | 比对失真（实测基线里真的扫到过 ["删除"]）。 所以这里排除交互控件（button/a/input）与删除弹窗内部的节点， 只留纯展示型横幅。 | const readErrorTexts = () => |
