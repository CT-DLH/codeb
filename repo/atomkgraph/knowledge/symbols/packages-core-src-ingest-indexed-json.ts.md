---
covers:
  - packages/core/src/ingest/indexed-json.ts
title: Semantic block index: indexed-json.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：indexed-json.ts（第4层）

**源码文件**：`packages/core/src/ingest/indexed-json.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="packages/core/src/ingest/indexed-json.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| coerceIndex@15 | function | L15-24 | 1 / "1" / "#1" / "编号 1" / "第1条" → 1；认不出返回 undefined | export function coerceIndex(v: unknown): number \| undefined { |
| pickIndex@43 | function | L43-50 | 从条目里取编号（遍历别名，认出第一个有效的） | export function pickIndex(it: Record<string, unknown>): number \| unde… |
| pickString@56 | function | L56-63 | 从条目里取字符串字段（按候选键顺序，返回第一个非空值）。 | export function pickString(it: Record<string, unknown>, keys: readonly… |
| isPlainObject@65 | function | L65-67 |  | function isPlainObject(v: unknown): v is Record<string, unknown> { |
| unwrapIndexedWrapper@78 | function | L78-90 | 把一个「只有单个编号键」的包装对象拆开： | function unwrapIndexedWrapper( |
| looksLikeItemArray@93 | function | L93-95 | [{"…"}] 这种「全是对象的数组」才可能是条目列表 | function looksLikeItemArray(v: unknown): v is unknown[] { |
| looksLikeIndexedMap@98 | function | L98-102 | {"1":{…},"2":{…}}：键全部是编号 | function looksLikeIndexedMap(v: unknown): boolean { |
| indexedItems@118 | function | L118-176 | 归一化「带编号的条目列表」。 | export function indexedItems( |
| indexedItems.norm@124 | arrow | L124-149 |  | const norm = (list: unknown, d: number): Array<Record<string, unknown>… |
