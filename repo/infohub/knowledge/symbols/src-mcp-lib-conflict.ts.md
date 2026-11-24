---
covers:
  - src/mcp/lib/conflict.ts
title: Semantic block index: conflict.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：conflict.ts（第4层）

**源码文件**：`src/mcp/lib/conflict.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="src/mcp/lib/conflict.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| isPlainObject@4 | function | L4-6 |  | function isPlainObject(v: unknown): v is Record<string, any> { |
| expandDotPaths@22 | function | L22-53 | 把「点号路径」的 changes 展开成嵌套结构。 | export function expandDotPaths( |
| applyChanges@56 | function | L56-69 | 把 changes 应用到 frontmatter：ext 做浅合并，其余键覆盖 | export function applyChanges( |
| buildDraftContent@72 | function | L72-74 | 生成“应用 changes 之后”的完整文件内容（草稿） | export function buildDraftContent(card: CardRecord, changes: Record<st… |
| detectRevisionDrift@77 | function | L77-79 | 当前文件是否与 _base_revision 不一致（版本漂移） | export function detectRevisionDrift(card: CardRecord, baseRevision: st… |
