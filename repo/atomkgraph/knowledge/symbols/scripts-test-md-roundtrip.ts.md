---
covers:
  - scripts/test-md-roundtrip.ts
title: Semantic block index: test-md-roundtrip.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：test-md-roundtrip.ts（第4层）

**源码文件**：`scripts/test-md-roundtrip.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="scripts/test-md-roundtrip.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| norm@16 | function | L16-45 |  | function norm(s: string): string { |
| blockTypes@53 | function | L53-62 | 结构断言：往返之后，块级结构的类型序列必须与输入一致。 | function blockTypes(md: string): string { |
| roundtrip@65 | function | L65-73 | 往返一次：md → doc → md2，比较归一化后是否一致。 | function roundtrip(md: string): { ok: boolean; md2: string; structOk: … |
