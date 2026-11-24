---
covers:
  - packages/core/src/llm/rotate.ts
title: Semantic block index: rotate.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：rotate.ts（第4层）

**源码文件**：`packages/core/src/llm/rotate.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="packages/core/src/llm/rotate.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| ModelProfile@50 | interface | L50-53 | 某些模型必须带私有参数才能干活，不能指望调用方每次记得。 | interface ModelProfile { |
| modelProfileOf@59 | function | L59-61 | 取某个模型的私有参数（供测试与诊断） | export function modelProfileOf(model: string): ModelProfile { |
| resolveModelChain@64 | function | L64-73 | --models a,b > LLM_CHAT_MODELS > 现役模型 + 备胎。去重后保持顺序。 | export function resolveModelChain(explicit?: string, env: NodeJS.Proce… |
| RotateEvent@75 | interface | L75-80 |  | export interface RotateEvent { |
| RotateOptions@82 | interface | L82-94 |  | export interface RotateOptions { |
| RotateStats@96 | interface | L96-101 |  | export interface RotateStats { |
| createRotatingChat@103 | function | L103-208 |  | export function createRotatingChat(opts: RotateOptions): { |
| createRotatingChat.bump@120 | arrow | L120-123 |  | const bump = (m: string, key: 'ok' \| 'failed'): void => { |
| createRotatingChat.chat@125 | arrow | L125-202 |  | const chat: InvokeFn = async (_cfg, messages, callOpts = {}) => { |
