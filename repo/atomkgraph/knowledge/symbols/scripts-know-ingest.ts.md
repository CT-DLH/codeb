---
covers:
  - scripts/know-ingest.ts
title: Semantic block index: know-ingest.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：know-ingest.ts（第4层）

**源码文件**：`scripts/know-ingest.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="scripts/know-ingest.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| Args@26 | interface | L26-107 |  | interface Args { |
| parsePageRanges@110 | function | L110-126 | 22-25,48 → [22,23,24,25,48] | function parsePageRanges(s: string): number[] { |
| parseArgs@128 | function | L128-187 |  | function parseArgs(argv: string[]): Args { |
| parseArgs.get@129 | arrow | L129-132 |  | const get = (name: string): string \| undefined => { |
| loadDoc@189 | function | L189-204 |  | async function loadDoc(args: Args): Promise<ParsedDocument> { |
| sourceNameOf@217 | function | L217-225 | 书名：文件名去掉扩展名。source_detail 靠它溯源，不能空。 | function sourceNameOf(args: Args, doc: ParsedDocument \| null): string… |
| main@227 | function | L227-560 |  | async function main(): Promise<void> { |
| main.key@455 | arrow | L455-456 | 降级/失败类警告必须排在前面：全章 33 条警告里「语义查重已跳过」原本排在第 30 条， 截前 20 条会让「增强层静默失效」完全看不见，还以为计划是完整的。 | const key = (w: string): number => |
