---
covers:
  - scripts/test-extract-checkpoint.ts
title: Semantic block index: test-extract-checkpoint.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：test-extract-checkpoint.ts（第4层）

**源码文件**：`scripts/test-extract-checkpoint.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="scripts/test-extract-checkpoint.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| check@28 | function | L28-36 |  | function check(name: string, ok: boolean, detail?: unknown): void { |
| eq@37 | function | L37-39 |  | function eq<T>(name: string, actual: T, expected: T): void { |
| docOf@41 | function | L41-51 |  | function docOf(markdown: string): ParsedDocument { |
| flatOf@53 | function | L53-65 |  | function flatOf(patch: Partial<FlatSection> & { title: string; body: s… |
| safeApply@71 | function | L71-82 | 落库不该抛异常（逐条容错就是为了不抛）。真抛了也要变成一条断言失败， | function safeApply(db: DB, plan: UnifiedPlan): UnifiedApplyResult { |
| main@97 | function | L97-430 |  | async function main(): Promise<void> { |
| main.mkdir@99 | arrow | L99-103 |  | const mkdir = (): string => { |
| main.dbOf@105 | arrow | L105-109 |  | const dbOf = (dir: string): DB => { |
| main.healthy@208 | arrow | L208-223 |  | const healthy: ChatFn = async (_cfg, messages) => { |
| main.ok@212 | arrow | L212-212 |  | const ok = (content: string) => ({ content, finish_reason: 'stop', tru… |
| main.flaky@270 | arrow | L270-278 |  | const flaky: ChatFn = async (_cfg, messages) => { |
| main.chat@328 | arrow | L328-349 |  | const chat: ChatFn = async (_cfg, messages) => { |
| main.ok@331 | arrow | L331-331 |  | const ok = (content: string) => ({ content, finish_reason: 'stop', tru… |
| main.ok@390 | arrow | L390-390 |  | const ok = (content: string) => ({ content, finish_reason: 'stop', tru… |
