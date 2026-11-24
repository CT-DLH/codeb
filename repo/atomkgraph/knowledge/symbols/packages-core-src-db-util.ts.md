---
covers:
  - packages/core/src/db/util.ts
title: Semantic block index: util.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：util.ts（第4层）

**源码文件**：`packages/core/src/db/util.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="packages/core/src/db/util.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| newId@6 | function | L6-8 | 生成带前缀的唯一 ID，便于从主键直接识别实体类型。 | export function newId(prefix: string): string { |
| contentHash@11 | function | L11-15 | 内容指纹：用于导入去重与防 AI 重复生成（计划书 5.1 content_hash）。 | export function contentHash(text: string): string { |
| nowIso@18 | function | L18-20 | 统一 ISO 时间戳，便于排序与跨端解析。 | export function nowIso(): string { |
| toBool@23 | function | L23-25 | SQLite 无布尔类型，统一用 0/1 存取。 | export function toBool(v: unknown): boolean { |
| fromBool@27 | function | L27-29 |  | export function fromBool(v: boolean \| undefined): number { |
| parseJsonArray@32 | function | L32-40 | JSON 列的安全解析（存储为 TEXT）。 | export function parseJsonArray(raw: unknown): string[] { |
