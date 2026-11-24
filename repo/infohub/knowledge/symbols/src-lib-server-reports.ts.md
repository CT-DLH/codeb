---
covers:
  - src/lib/server/reports.ts
title: Semantic block index: reports.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：reports.ts（第4层）

**源码文件**：`src/lib/server/reports.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="src/lib/server/reports.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| ReportMeta@28 | interface | L28-42 |  | export interface ReportMeta { |
| Report@44 | interface | L44-46 |  | export interface Report extends ReportMeta { |
| parseFrontmatter@53 | function | L53-99 | 极简 frontmatter 解析：只认 key: "value" / key: N / key:\n - "item" 三种形态。 | function parseFrontmatter(raw: string): { meta: Record<string, any>; b… |
| toMeta@101 | function | L101-116 |  | function toMeta(slug: string, meta: Record<string, any>, body: string)… |
| toMeta.arr@102 | arrow | L102-102 |  | const arr = (v: any): string[] => (Array.isArray(v) ? v.map(String) : … |
| listReports@119 | function | L119-136 | 全部报告，按 updated_at 倒序（最近的在前） | export function listReports(): ReportMeta[] { |
| readReport@139 | function | L139-151 | 读一份报告；slug 是文件名主干（中文文件名直接用，调用方负责 URL 解码） | export function readReport(slug: string): Report \| null { |
| hasReport@154 | function | L154-157 | 报告是否存在（详情页 404 判定用，比 readReport 便宜些） | export function hasReport(slug: string): boolean { |
