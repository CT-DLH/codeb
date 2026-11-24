---
covers:
  - scripts/test-semantic-match.ts
title: Semantic block index: test-semantic-match.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：test-semantic-match.ts（第4层）

**源码文件**：`scripts/test-semantic-match.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="scripts/test-semantic-match.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| check@39 | function | L39-47 |  | function check(name: string, ok: boolean, detail?: unknown): void { |
| eq@48 | function | L48-50 |  | function eq<T>(name: string, actual: T, expected: T): void { |
| vecOf@53 | function | L53-61 | 确定性向量：按字符码累加到 8 维再归一化。重合字越多，余弦越高 | function vecOf(t: string): number[] { |
| fakeEmbed@63 | arrow | L63-63 |  | const fakeEmbed = async (texts: string[]): Promise<number[][]> => text… |
| fakeChat@66 | function | L66-74 | 固定回复的 chat 替身。按调用序号取 replies，用完后重复最后一条 | function fakeChat(replies: unknown[]): { chat: ChatFn; calls: () => nu… |
| node@78 | function | L78-80 |  | function node(title: string, content: string, children?: MergeInputNod… |
| main@82 | function | L82-723 |  | async function main(): Promise<void> { |
| main.timeoutErr@628 | arrow | L628-632 |  | const timeoutErr = (): Error => { |
