---
covers:
  - src/core/parsers/task-book.ts
title: Semantic block index: task-book.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：task-book.ts（第4层）

**源码文件**：`src/core/parsers/task-book.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="src/core/parsers/task-book.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| bare@26 | arrow | L26-26 |  | const bare = (s: string): string => stripSpace(s).replace(/[:：]/g, '')… |
| fromTable@29 | function | L29-74 | 表格模板：题目行 → 之后每行的「标签：正文」 | function fromTable( |
| fromParagraphs@77 | function | L77-96 | 段落模板：题目 行 → 下一行；章节名单独成行，正文是其后的段落直到下一个章节名 | function fromParagraphs(paras: string[]): { title: string; sections: P… |
| buildWarnings@99 | function | L99-105 | 空栏目与条目编号都要出声：前者说明任务书本身没填，后者说明模板跟主流不一致 | function buildWarnings(parsed: { sections: ParsedSection[]; blank: str… |
| parse@110 | method | L110-133 |  | parse(file, sourceFile): ParsedAttachment \| null { |
