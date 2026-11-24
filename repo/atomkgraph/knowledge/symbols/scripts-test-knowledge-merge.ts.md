---
covers:
  - scripts/test-knowledge-merge.ts
title: Semantic block index: test-knowledge-merge.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：test-knowledge-merge.ts（第4层）

**源码文件**：`scripts/test-knowledge-merge.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="scripts/test-knowledge-merge.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| check@22 | function | L22-30 |  | function check(name: string, ok: boolean, detail?: unknown): void { |
| eq@31 | function | L31-33 |  | function eq<T>(name: string, actual: T, expected: T): void { |
| docOf@35 | function | L35-45 |  | function docOf(markdown: string): ParsedDocument { |
| main@50 | function | L50-1250 |  | async function main(): Promise<void> { |
| main.mkItem@326 | arrow | L326-334 |  | const mkItem = (path: string, title: string, parentId: string) => ({ |
| main.g@379 | arrow | L379-379 | 导读长度按真实数据来（库里实测 100~1300 字）：十几字的样例会让「兜底导读」的字数下限 判别失效——那种长度本身就该被当成生成失败的兜底，不该拿来当正例。 | const g = (s: string): string => s.repeat(6) // 每个样例约 100~150 字 |
