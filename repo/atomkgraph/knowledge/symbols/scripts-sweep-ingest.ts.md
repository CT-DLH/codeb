---
covers:
  - scripts/sweep-ingest.ts
title: Semantic block index: sweep-ingest.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：sweep-ingest.ts（第4层）

**源码文件**：`scripts/sweep-ingest.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="scripts/sweep-ingest.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| Args@54 | interface | L54-71 |  | interface Args { |
| parseArgs@73 | function | L73-108 |  | function parseArgs(argv: string[]): Args { |
| parseArgs.get@74 | arrow | L74-77 |  | const get = (name: string): string \| undefined => { |
| findPdfs@111 | function | L111-122 | 递归找 PDF，按路径排序（同届的卷子挨着跑，缓存命中更稳）。 | function findPdfs(dir: string): string[] { |
| findPdfs.walk@113 | arrow | L113-119 |  | const walk = (d: string): void => { |
| loadDone@130 | function | L130-143 | 已跑过且成功的文件（断点续跑：崩了重跑不重做 OCR / 不重花 token）。 | function loadDone(outPath: string): Set<string> { |
| dropFailures@146 | function | L146-168 | 删掉上一次的失败记录，让续跑能重做它们（成功条目保留）。 | function dropFailures(outPath: string): number { |
| probeRoute@174 | function | L174-201 | 廉价探路：ocr=off 读一次文本层，秒级、不写缓存。 | async function probeRoute( |
| FileRecord@203 | interface | L203-252 |  | interface FileRecord { |
| reparseVision@255 | function | L255-271 | 用视觉重解析整份文件，并把新的分块结果记进 rec（升级只有换引擎才叫升级）。 | async function reparseVision( |
| isNetworkError@274 | function | L274-276 | 看起来是网络/上游问题（不是这份 PDF 本身的问题）。 | function isNetworkError(msg: string): boolean { |
| sleep@278 | function | L278-280 |  | function sleep(ms: number): Promise<void> { |
| blankRecord@291 | function | L291-322 |  | function blankRecord(file: string): FileRecord { |
| runOne@324 | function | L324-509 |  | async function runOne( |
| fmtCounts@511 | function | L511-515 |  | function fmtCounts(c: Record<string, number>): string { |
| main@517 | function | L517-630 |  | async function main(): Promise<void> { |
