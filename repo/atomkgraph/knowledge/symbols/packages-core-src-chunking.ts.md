---
covers:
  - packages/core/src/chunking.ts
title: Semantic block index: chunking.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：chunking.ts（第4层）

**源码文件**：`packages/core/src/chunking.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="packages/core/src/chunking.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| ChunkOptions@6 | interface | L6-11 | 目的：把知识点内容切成适合 embedding 的块——整块 embed 会让长文本语义被平均化，检索命中率低。 策略：按 Markdown 块（标题/代码块/文本）解析；代码块保持完整；目标/最大/ | export interface ChunkOptions { |
| Block@16 | interface | L16-19 |  | interface Block { |
| parseBlocks@22 | function | L22-64 | 解析 Markdown 为块：代码围栏整体成块，标题行独立成块，其余归文本。 | export function parseBlocks(md: string): Block[] { |
| parseBlocks.flushText@29 | arrow | L29-33 |  | const flushText = () => { |
| splitBySentence@67 | function | L67-88 | 超长文本按句子边界切；单句仍超限则硬切。 | function splitBySentence(text: string, max: number): string[] { |
| head@90 | function | L90-92 |  | function head(text: string, n: number): string { |
| chunkContent@95 | function | L95-155 | 把 Markdown 内容切分为 embedding 块（已应用重叠）。 | export function chunkContent(md: string, opts: ChunkOptions = {}): str… |
| chunkContent.pushCur@104 | arrow | L104-107 |  | const pushCur = () => { |
