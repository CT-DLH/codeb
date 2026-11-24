---
covers:
  - src/mcp/tools/card_derive.ts
title: Semantic block index: card_derive.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：card_derive.ts（第4层）

**源码文件**：`src/mcp/tools/card_derive.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="src/mcp/tools/card_derive.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| fail@12 | function | L12-17 |  | function fail(errors: string[], extra: Record<string, unknown> = {}) { |
| shape@20 | function | L20-24 | 样值只给形状不给内容：派生出来的东西经常本身就是敏感信息 | function shape(value: unknown): string { |
| RuleStat@26 | interface | L26-37 |  | interface RuleStat { |
| registerCardDerive@39 | function | L39-212 |  | export function registerCardDerive(server: McpServer): void { |
| readSimple@214 | function | L214-221 |  | function readSimple(card: Record<string, any>, path: string): unknown … |
