---
covers:
  - scripts/seed-calculus.mjs
title: Semantic block index: seed-calculus.mjs (layer 4)
updated: 2026-11-24
---

# 语义块索引：seed-calculus.mjs（第4层）

**源码文件**：`scripts/seed-calculus.mjs`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="scripts/seed-calculus.mjs", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| post@4 | function | L4-13 |  | async function post(path, body) { |
| patch@15 | function | L15-24 |  | async function patch(path, body) { |
| listAll@27 | function | L27-30 | 幂等：按标题查已有节点（顶级或指定父下） | async function listAll() { |
| ensure@32 | function | L32-42 |  | async function ensure(title, parentId, extra = {}) { |
| relate@44 | function | L44-48 |  | async function relate(fromId, toId, type = 'prerequisite') { |
| findId@51 | function | L51-55 | 找顶级或某父下的节点 id（用于迁移） | async function findId(title) { |
