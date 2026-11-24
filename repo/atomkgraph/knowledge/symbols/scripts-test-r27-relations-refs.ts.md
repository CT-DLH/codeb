---
covers:
  - scripts/test-r27-relations-refs.ts
title: Semantic block index: test-r27-relations-refs.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：test-r27-relations-refs.ts（第4层）

**源码文件**：`scripts/test-r27-relations-refs.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="scripts/test-r27-relations-refs.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| check@19 | function | L19-27 |  | function check(cond: unknown, msg: string, detail = ''): void { |
| j@28 | arrow | L28-28 |  | const j = (v: unknown): string => JSON.stringify(v) |
| attempt@37 | function | L37-43 | 包一层执行：Repository 抛异常时（比如外键约束）转成返回体，而不是让脚本崩掉。 | function attempt<T>(fn: () => T): { result: T \| null; error: string }… |
| exists@104 | arrow | L104-104 |  | const exists = (id: string): boolean => ks.get(id) !== null |
