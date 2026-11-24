---
covers:
  - scripts/test-model-rotation.ts
title: Semantic block index: test-model-rotation.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：test-model-rotation.ts（第4层）

**源码文件**：`scripts/test-model-rotation.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="scripts/test-model-rotation.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| check@11 | function | L11-19 |  | function check(name: string, ok: boolean, detail?: unknown): void { |
| eq@20 | function | L20-22 |  | function eq<T>(name: string, actual: T, expected: T): void { |
| okResult@26 | arrow | L26-26 |  | const okResult = (content = '{"a":1}') => ({ content, finish_reason: '… |
| invokeOf@29 | function | L29-43 | 每个模型的行为：ok / empty / notjson / throw。默认 ok | function invokeOf(behaviors: Record<string, string>): { invoke: Invoke… |
| invokeOf.invoke@32 | arrow | L32-41 |  | const invoke: InvokeFn = async (cfg, _messages, callOpts) => { |
| main@45 | function | L45-293 |  | async function main(): Promise<void> { |
| main.invoke@135 | arrow | L135-139 |  | const invoke: InvokeFn = async (cfg) => { |
| main.invoke@168 | arrow | L168-172 |  | const invoke: InvokeFn = async (cfg) => { |
| main.invoke@263 | arrow | L263-266 |  | const invoke: InvokeFn = async (_cfg, _msgs, callOpts) => { |
