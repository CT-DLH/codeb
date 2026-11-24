---
covers:
  - distill/agent/pi_probe.mjs
title: Semantic block index: pi_probe.mjs (layer 4)
updated: 2026-11-24
---

# 语义块索引：pi_probe.mjs（第4层）

**源码文件**：`distill/agent/pi_probe.mjs`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="distill/agent/pi_probe.mjs", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| loadEnv@13 | function | L13-26 | 凭据不在环境变量里，在 infohub 的 .env 中（与 distill.py 同一真源） | function loadEnv() { |
| kbTool@60 | function | L60-87 | 实测 in-process 54ms vs subprocess 261ms；而且工具定义不用重写一遍。 这里仍然 spawn 一次 python 进程，但那是因为 kb.py 是 Python —— | function kbTool(name, label, description, paramSchema, buildArgs) { |
