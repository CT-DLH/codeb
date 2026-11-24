---
covers:
  - scripts/bench-nvidia-models.ts
title: Semantic block index: bench-nvidia-models.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：bench-nvidia-models.ts（第4层）

**源码文件**：`scripts/bench-nvidia-models.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="scripts/bench-nvidia-models.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| argOf@47 | arrow | L47-50 |  | const argOf = (name: string): string \| undefined => { |
| has@51 | arrow | L51-51 |  | const has = (name: string): boolean => argv.includes(`--${name}`) |
| findImage@129 | function | L129-140 | 找一张真实页面图片做视觉探针。 | function findImage(): string \| null { |
| TaskResult@143 | interface | L143-153 | ── 任务定义 ────────────────────────────────────────────────────────────── | interface TaskResult { |
| Task@155 | interface | L155-164 |  | interface Task { |
| now@166 | arrow | L166-166 |  | const now = () => Date.now() |
| makeChatTask@168 | function | L168-215 |  | function makeChatTask( |
| shortErr@217 | function | L217-223 |  | function shortErr(e: unknown): string { |
| run@392 | method | L392-428 |  | async run(): Promise<TaskResult> { |
| Row@432 | interface | L432-438 | ── 跑 ──────────────────────────────────────────────────────────────────── | interface Row { |
| median@440 | arrow | L440-445 |  | const median = (xs: number[]): number => { |
| main@447 | function | L447-536 |  | async function main(): Promise<void> { |
