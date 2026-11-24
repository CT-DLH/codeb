---
covers:
  - scripts/test-repair.ts
title: Semantic block index: test-repair.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：test-repair.ts（第4层）

**源码文件**：`scripts/test-repair.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="scripts/test-repair.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| assert@22 | function | L22-28 |  | function assert(cond: unknown, msg: string): void { |
| eq@29 | function | L29-38 |  | function eq(msg: string, actual: unknown, expected: unknown): void { |
| throws@39 | function | L39-53 |  | function throws(msg: string, fn: () => unknown, needle?: string): void… |
| freshDb@59 | function | L59-61 |  | function freshDb(): DB { |
| Fixture@63 | interface | L63-69 |  | interface Fixture { |
| fixture@71 | function | L71-80 |  | function fixture(): Fixture { |
| node@82 | function | L82-84 |  | function node(f: Fixture, title: string, content: string, parentId: st… |
| question@86 | function | L86-90 |  | function question(f: Fixture, id: string, content = '题干'): void { |
| link@93 | function | L93-99 | 直接建挂载边（绕开来源判定，测试只关心「边有没有跟着节点走」）。 | function link(f: Fixture, questionId: string, knowledgeId: string, sou… |
| linksOf@101 | function | L101-106 |  | function linksOf(f: Fixture, knowledgeId: string): string[] { |
| isDeleted@108 | function | L108-113 |  | function isDeleted(f: Fixture, id: string): boolean { |
| parentOf@115 | function | L115-120 |  | function parentOf(f: Fixture, id: string): string \| null { |
| titleOf@122 | function | L122-127 |  | function titleOf(f: Fixture, id: string): string { |
| editCountOf@129 | function | L129-134 |  | function editCountOf(f: Fixture, id: string): number { |
| hashOf@136 | function | L136-141 |  | function hashOf(f: Fixture, id: string): string { |
| contentOf@143 | function | L143-148 |  | function contentOf(f: Fixture, id: string): string { |
| rel@166 | arrow | L166-175 |  | const rel = (id: string, s: string, t: string, type = 'related') => ({ |
| none@177 | arrow | L177-177 |  | const none = () => false |
| byKind@467 | arrow | L467-468 |  | const byKind = (k: string, from?: string) => |
