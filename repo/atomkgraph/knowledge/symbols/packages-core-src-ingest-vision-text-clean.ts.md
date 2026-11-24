---
covers:
  - packages/core/src/ingest/vision-text-clean.ts
title: Semantic block index: vision-text-clean.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：vision-text-clean.ts（第4层）

**源码文件**：`packages/core/src/ingest/vision-text-clean.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="packages/core/src/ingest/vision-text-clean.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| budgetFor@58 | function | L58-60 | 输出预算按输入字符数估算，而不是写死一个值。 | function budgetFor(chars: number): number { |
| TextCleanOptions@62 | interface | L62-74 |  | export interface TextCleanOptions { |
| TextCleanResult@76 | interface | L76-82 |  | export interface TextCleanResult { |
| protectChapterTitle@155 | function | L155-186 | 章标题保护：章扉页的标题不许被当成页眉删掉。 | function protectChapterTitle(cleaned: string, original: string): strin… |
| buildUser@188 | function | L188-218 |  | function buildUser(pages: Array<{ page: number; markdown: string }>): … |
| splitPages@221 | function | L221-230 | 把 LLM 输出按页标记拆开 | function splitPages(text: string): Map<number, string> { |
| textCleanCacheKey@251 | function | L251-256 | 缓存键：页面内容 + 版本 + 模型，任一变化都会自然失效 | function textCleanCacheKey(input: Array<{ page: number; markdown: stri… |
| readTextCleanCache@258 | function | L258-266 |  | function readTextCleanCache(cacheDir: string, key: string): Map<number… |
| writeTextCleanCache@268 | function | L268-275 |  | function writeTextCleanCache(cacheDir: string, key: string, got: Map<n… |
| cleanTextPages@277 | function | L277-385 |  | export async function cleanTextPages( |
| cleanTextPages.worker@295 | arrow | L295-301 |  | const worker = async (apiKey?: string): Promise<void> => { |
| cleanTextPages.runBatch@303 | arrow | L303-371 |  | const runBatch = async ( |
