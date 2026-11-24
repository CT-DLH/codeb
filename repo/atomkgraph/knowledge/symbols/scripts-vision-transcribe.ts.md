---
covers:
  - scripts/vision-transcribe.ts
title: Semantic block index: vision-transcribe.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：vision-transcribe.ts（第4层）

**源码文件**：`scripts/vision-transcribe.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="scripts/vision-transcribe.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| Args@23 | interface | L23-32 | 提示词只有一份，和线上链路共用（复制一份必然漂移） | interface Args { |
| parseArgs@34 | function | L34-59 |  | function parseArgs(argv: string[]): Args { |
| dataUrl@63 | function | L63-69 |  | async function dataUrl(path: string): Promise<string> { |
| main@71 | function | L71-132 |  | async function main(): Promise<void> { |
