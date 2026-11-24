---
covers:
  - scripts/group-ingest.ts
title: Semantic block index: group-ingest.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：group-ingest.ts（第4层）

**源码文件**：`scripts/group-ingest.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="scripts/group-ingest.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| Args@48 | interface | L48-76 |  | interface Args { |
| parseArgs@78 | function | L78-118 |  | function parseArgs(argv: string[]): Args { |
| parseArgs.get@79 | arrow | L79-82 |  | const get = (name: string): string \| undefined => { |
| BuildOptions@121 | interface | L121-128 | 读一份卷/答案册时的开关。参数一多，位置参数就开始互相顶了，收成对象。 | interface BuildOptions { |
| Built@130 | interface | L130-141 |  | interface Built { |
| groupSourceHash@144 | function | L144-146 | 组身份 = 组内各文件 content_hash 排序后拼接再 hash。顺序无关，内容一变就变。 | export function groupSourceHash(hashes: string[]): string { |
| buildSegments@154 | function | L154-302 | 把一组文件读成「试题块 + 答案册文本」。 | async function buildSegments( |
| report@304 | function | L304-324 |  | function report(res: ExtractResult): void { |
| reportBind@326 | function | L326-341 |  | function reportBind(b: BindResult, res: ExtractResult): void { |
| extractStage@350 | function | L350-358 | 阶段 1：只喂试题块。答案册一个字都不给，模型专心认题。 | async function extractStage(built: Built, maxSegments?: number): Promi… |
| bindStage@361 | function | L361-366 | 阶段 2：题目清单 + 答案册 → 按题号回填。 | async function bindStage(built: Built, res: ExtractResult): Promise<Bi… |
| main@368 | function | L368-538 |  | async function main(): Promise<void> { |
