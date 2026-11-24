---
covers:
  - scripts/test-r62-delete-api.mjs
title: Semantic block index: test-r62-delete-api.mjs (layer 4)
updated: 2026-11-24
---

# 语义块索引：test-r62-delete-api.mjs（第4层）

**源码文件**：`scripts/test-r62-delete-api.mjs`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="scripts/test-r62-delete-api.mjs", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| assert@32 | function | L32-40 |  | function assert(cond, label, detail) { |
| get@53 | arrow | L53-62 |  | const get = async (url) => { |
| send@63 | arrow | L63-72 |  | const send = async (method, url, payload) => { |
| rawRow@75 | arrow | L75-78 |  | const rawRow = (id) => |
| liveCount@79 | arrow | L79-79 |  | const liveCount = () => db.prepare('SELECT COUNT(*) n FROM knowledge W… |
| relCount@80 | arrow | L80-80 |  | const relCount = () => db.prepare('SELECT COUNT(*) n FROM relation').g… |
| mk@82 | arrow | L82-89 |  | const mk = async (title, parent_id) => { |
| snap@126 | arrow | L126-132 | ========================================================================= 「一个字节没动」必须逐字段证明，不能只看 HTTP | const snap = () => ({ |
