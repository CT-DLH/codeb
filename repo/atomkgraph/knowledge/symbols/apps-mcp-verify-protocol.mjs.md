---
covers:
  - apps/mcp/verify-protocol.mjs
title: Semantic block index: verify-protocol.mjs (layer 4)
updated: 2026-11-24
---

# 语义块索引：verify-protocol.mjs（第4层）

**源码文件**：`apps/mcp/verify-protocol.mjs`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="apps/mcp/verify-protocol.mjs", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| check@30 | function | L30-39 |  | function check(cond, msg, detail = '') { |
| rpc@87 | function | L87-99 |  | function rpc(id, method, params) { |
| callTool@102 | function | L102-107 | 调用工具并把返回的 content[0].text 解析出来（后端都返回 JSON 文本）。 | async function callTool(id, name, args) { |
