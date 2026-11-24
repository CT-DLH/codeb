---
covers:
  - packages/core/src/ingest/kg-doctor.ts
title: Semantic block index: kg-doctor.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：kg-doctor.ts（第4层）

**源码文件**：`packages/core/src/ingest/kg-doctor.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="packages/core/src/ingest/kg-doctor.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| DoctorNode@23 | interface | L23-31 |  | export interface DoctorNode { |
| DuplicateGroup@35 | interface | L35-42 |  | export interface DuplicateGroup { |
| BrokenNode@44 | interface | L44-47 |  | export interface BrokenNode extends DoctorNode { |
| DoctorReport@49 | interface | L49-57 |  | export interface DoctorReport { |
| Row@62 | interface | L62-69 |  | interface Row { |
| bigrams@71 | function | L71-76 |  | function bigrams(text: string): Set<string> { |
| textSimilarity@79 | function | L79-86 | 字符二元组 Jaccard：0=毫无重合，1=完全一致。对改写/增删句敏感但不会因换行标点抖。 | export function textSimilarity(a: string, b: string): number { |
| scanDoctor@88 | function | L88-236 |  | export function scanDoctor(db: DB): DoctorReport { |
| scanDoctor.pathOf@104 | arrow | L104-118 |  | const pathOf = (r: Row): { path: string[]; cycle: boolean } => { |
| scanDoctor.isAncestor@121 | arrow | L121-131 |  | const isAncestor = (a: string, b: string): boolean => { |
| scanDoctor.toNode@133 | arrow | L133-140 |  | const toNode = (r: Row): DoctorNode => ({ |
