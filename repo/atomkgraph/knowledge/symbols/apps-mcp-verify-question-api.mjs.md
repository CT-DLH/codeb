---
covers:
  - apps/mcp/verify-question-api.mjs
title: Semantic block index: verify-question-api.mjs (layer 4)
updated: 2026-11-24
---

# 语义块索引：verify-question-api.mjs（第4层）

**源码文件**：`apps/mcp/verify-question-api.mjs`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="apps/mcp/verify-question-api.mjs", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| check@40 | function | L40-48 |  | function check(cond, msg, detail = '') { |
| callTool@66 | arrow | L66-70 |  | const callTool = (name, args) => { |
| tryTool@77 | arrow | L77-83 | 调工具并把 HTTP 错误吞成 null。 用于「预期可能失败」的断言（如回滚一个不存在的版本）——否则一条失守会抛异常， 把后面几十条断言一起带走，变异测试就看不出到底哪几条真的没被覆盖。 | const tryTool = async (name, args) => { |
| req@85 | arrow | L85-98 |  | const req = async (method, path, body) => { |
| snapOf@298 | arrow | L298-304 | 取快照里的字段：?. + try/catch 是为了让「实现被注掉」时断言干净变红， 而不是抛异常把后面几十条断言一起带走（崩了就看不出到底是哪条失守）。 | const snapOf = (rev) => { |
| revListOf@305 | arrow | L305-308 |  | const revListOf = async (id) => { |
