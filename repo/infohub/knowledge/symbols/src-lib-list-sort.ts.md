---
covers:
  - src/lib/list-sort.ts
title: Semantic block index: list-sort.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：list-sort.ts（第4层）

**源码文件**：`src/lib/list-sort.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="src/lib/list-sort.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| listSortKey@24 | function | L24-48 | 一行的排序键。空值返回 null，调用方据此把空值恒排最后（不随升降序翻转： | export function listSortKey(row: ListRow, col: string): string \| numb… |
| compareKeys@50 | function | L50-60 |  | function compareKeys(a: string \| number, b: string \| number, format?… |
| listRowComparator@71 | function | L71-85 | 行比较器：format 取领域包声明的列格式（date 走 ISO 文本序，不走中文拼音序）。 | export function listRowComparator(col: string, dir: 'asc' \| 'desc', f… |
