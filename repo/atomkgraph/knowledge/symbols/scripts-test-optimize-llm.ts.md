---
covers:
  - scripts/test-optimize-llm.ts
title: Semantic block index: test-optimize-llm.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：test-optimize-llm.ts（第4层）

**源码文件**：`scripts/test-optimize-llm.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="scripts/test-optimize-llm.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| assert@25 | function | L25-32 |  | function assert(cond: unknown, msg: string): void { |
| eq@33 | function | L33-38 |  | function eq(msg: string, actual: unknown, expected: unknown): void { |
| add@42 | arrow | L42-49 |  | const add = (id: string, title: string, parent: string \| null, conten… |
| gen@51 | arrow | L51-52 |  | const gen = (n: number, offset: number): string => |
| no@86 | arrow | L86-86 |  | const no = (id: string): number => inv.byId.get(id)!.no |
| res@87 | arrow | L87-91 |  | const res = (obj: unknown): { content: string; finish_reason: string; … |
| crossChat@161 | arrow | L161-182 |  | const crossChat: ChatFn = async (_cfg, msgs) => { |
| chat@202 | arrow | L202-305 |  | const chat: ChatFn = async (_cfg, msgs) => { |
| byId@318 | arrow | L318-318 |  | const byId = (id: string) => r.plan.proposals.find((p) => p.targetIds.… |
| emptyChat@412 | arrow | L412-412 |  | const emptyChat: ChatFn = async () => ({ content: '', finish_reason: '… |
