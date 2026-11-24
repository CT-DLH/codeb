---
covers:
  - packages/core/src/ingest/extract-checkpoint.ts
title: Semantic block index: extract-checkpoint.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：extract-checkpoint.ts（第4层）

**源码文件**：`packages/core/src/ingest/extract-checkpoint.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="packages/core/src/ingest/extract-checkpoint.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| SectionSnapshot@29 | interface | L29-37 |  | export interface SectionSnapshot { |
| CheckpointFile@39 | interface | L39-46 |  | interface CheckpointFile { |
| sha@49 | function | L49-51 | 稳定的短 hash：key 里带正文，太长会把文件名撑爆。 | function sha(text: string): string { |
| sourceCheckpointKey@64 | function | L64-66 | 稳定的「源身份」：按源文件位置算（不按正文内容），用作检查点文件名。 | export function sourceCheckpointKey(sourcePath: string): string { |
| ExtractCheckpoint@75 | class | L75-155 | 抽取检查点。每次 put 都立刻落盘（不是退出时才写）——退出时才写等于没解决断电/被 kill。 | export class ExtractCheckpoint { |
| ExtractCheckpoint.load@88 | method | L88-115 |  | private load(sourceKey: string): CheckpointFile { |
| ExtractCheckpoint.getSection@117 | method | L117-122 |  | getSection(key: string): SectionSnapshot \| undefined { |
| ExtractCheckpoint.putSection@124 | method | L124-127 |  | putSection(key: string, snap: SectionSnapshot): void { |
| ExtractCheckpoint.getGuide@129 | method | L129-134 |  | getGuide(key: string): string \| undefined { |
| ExtractCheckpoint.putGuide@136 | method | L136-139 |  | putGuide(key: string, guide: string): void { |
| ExtractCheckpoint.summary@142 | method | L142-146 | 已复用 / 需新抽 的节数（导读也计数，用于一句人话总结）。 | summary(): string { |
| ExtractCheckpoint.flush@148 | method | L148-154 |  | private flush(): void { |
