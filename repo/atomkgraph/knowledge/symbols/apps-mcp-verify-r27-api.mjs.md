---
covers:
  - apps/mcp/verify-r27-api.mjs
title: Semantic block index: verify-r27-api.mjs (layer 4)
updated: 2026-11-24
---

# 语义块索引：verify-r27-api.mjs（第4层）

**源码文件**：`apps/mcp/verify-r27-api.mjs`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="apps/mcp/verify-r27-api.mjs", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| check@29 | function | L29-37 |  | function check(cond, msg, detail = '') { |
| j@38 | arrow | L38-38 |  | const j = (v) => JSON.stringify(v) |
| callTool@56 | arrow | L56-70 | 调一个 MCP 工具，并把两种结局归一成 {ok, data} / {ok:false, error}。 handler 成功时返回原始结果对象（MCP 信封由 setRequestH | const callTool = async (name, args) => { |
| req@72 | arrow | L72-85 |  | const req = async (method, path, body) => { |
| newK@87 | arrow | L87-88 |  | const newK = async (title, extra = {}) => |
| relsOf@90 | arrow | L90-90 |  | const relsOf = async (id) => (await req('GET', `/api/knowledge/${id}/r… |
