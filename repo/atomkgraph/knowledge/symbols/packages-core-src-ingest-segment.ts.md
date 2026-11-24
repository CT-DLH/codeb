---
covers:
  - packages/core/src/ingest/segment.ts
title: Semantic block index: segment.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：segment.ts（第4层）

**源码文件**：`packages/core/src/ingest/segment.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="packages/core/src/ingest/segment.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| Segment@16 | interface | L16-32 |  | export interface Segment { |
| finish@59 | function | L59-74 |  | function finish( |
| pageRangeOf@77 | function | L77-88 | 从块文本里取页码范围。块里一个页标记都没有（无分页文档）时回落到 fallback。 | function pageRangeOf(text: string, fallback = 1): { from: number; to: … |
| segmentPaper@90 | function | L90-127 |  | function segmentPaper(doc: ParsedDocument): Segment[] { |
| segmentMaterial@129 | function | L129-169 |  | function segmentMaterial(doc: ParsedDocument): Segment[] { |
| segmentDocument@171 | function | L171-173 |  | export function segmentDocument(doc: ParsedDocument, mode: SegmentMode… |
