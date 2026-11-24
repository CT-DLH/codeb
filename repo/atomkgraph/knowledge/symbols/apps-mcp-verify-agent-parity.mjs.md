---
covers:
  - apps/mcp/verify-agent-parity.mjs
title: Semantic block index: verify-agent-parity.mjs (layer 4)
updated: 2026-11-24
---

# 语义块索引：verify-agent-parity.mjs（第4层）

**源码文件**：`apps/mcp/verify-agent-parity.mjs`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="apps/mcp/verify-agent-parity.mjs", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| check@33 | function | L33-41 |  | function check(cond, msg, detail = '') { |
| readSrc@43 | arrow | L43-43 |  | const readSrc = (rel) => readFileSync(fileURLToPath(new URL(rel, impor… |
| sortKeys@46 | function | L46-54 | 键排序后再序列化：JSON Schema 的键顺序不该影响「同参」判断。 | function sortKeys(v) { |
| stable@55 | arrow | L55-55 |  | const stable = (v) => JSON.stringify(sortKeys(v)) |
| skipBraced@214 | function | L214-237 | 从 src[i]（${ 的第一个 { 之后）扫到配对的 }，跳过字符串/嵌套模板；返回结束下标。 | function skipBraced(src, i) { |
| readPathLiteral@240 | function | L240-276 | 读一个路径字面量（'…' 或 …），返回 { value, end }。 | function readPathLiteral(src, i) { |
| norm@290 | arrow | L290-295 |  | const norm = (p) => |
| matches@297 | arrow | L297-305 |  | const matches = (a, b) => { |
| injectTransport@329 | arrow | L329-344 |  | const injectTransport = async (method, path, body) => { |
| call@347 | arrow | L347-347 |  | const call = (name, args) => byName.get(name).handler(args ?? {}) |
