---
covers:
  - apps/mcp/verify-r26-api.mjs
title: Semantic block index: verify-r26-api.mjs (layer 4)
updated: 2026-11-24
---

# 语义块索引：verify-r26-api.mjs（第4层）

**源码文件**：`apps/mcp/verify-r26-api.mjs`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="apps/mcp/verify-r26-api.mjs", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| check@38 | function | L38-46 |  | function check(cond, msg, detail = '') { |
| j@47 | arrow | L47-47 |  | const j = (v) => JSON.stringify(v) |
| callTool@65 | arrow | L65-79 | 调一个 MCP 工具，并把两种结局归一成 {ok, data} / {ok:false, error}： handler 成功时返回的是原始结果对象（MCP 信封由 setReques | const callTool = async (name, args) => { |
| req@81 | arrow | L81-94 |  | const req = async (method, path, body) => { |
| newK@96 | arrow | L96-97 |  | const newK = async (title, extra = {}) => |
| mkQ@203 | arrow | L203-213 |  | const mkQ = async (content, relateIds, extra = {}) => |
