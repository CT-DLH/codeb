---
covers:
  - scripts/test-ocr.ts
title: Semantic block index: test-ocr.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：test-ocr.ts（第4层）

**源码文件**：`scripts/test-ocr.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="scripts/test-ocr.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| ok@33 | function | L33-41 |  | function ok(cond: unknown, label: string): void { |
| eq@43 | function | L43-47 |  | function eq(actual: unknown, expected: unknown, label: string): void { |
| makeMixedPdf@60 | function | L60-90 | 造一份「1 页文本层 + N 页纯图片」的 PDF，当扫描件夹具。 | function makeMixedPdf(path: string, imagePages: number): void { |
| fakeRunner@93 | function | L93-116 | 假侧车：按 pages 返回可预期的文本，并像真侧车一样写页级缓存。 | function fakeRunner(seen: number[][]): OcrRunner { |
| main@118 | function | L118-284 |  | async function main(): Promise<void> { |
| main.runner@167 | arrow | L167-174 |  | const runner: OcrRunner = async (_f, opts) => { |
