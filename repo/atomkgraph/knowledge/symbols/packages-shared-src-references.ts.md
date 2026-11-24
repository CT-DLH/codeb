---
covers:
  - packages/shared/src/references.ts
title: Semantic block index: references.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：references.ts（第4层）

**源码文件**：`packages/shared/src/references.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="packages/shared/src/references.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| normalizeReferences@63 | function | L63-88 | 把任意形状的「参考文献」入参归一为去重的字符串数组。 | export function normalizeReferences(raw: unknown): string[] { |
| composeReferencesMarkdown@100 | function | L100-109 | 合成「附在内容最后」的那一节：### 参考文献 + 编号清单。 | export function composeReferencesMarkdown( |
| withReferences@117 | function | L117-126 | 合成「正文 + 参考文献」的完整 Markdown。 | export function withReferences( |
| buildSearchKey@155 | function | L155-165 | 原文 → 搜索键，同时记下每个键字符在原文中的下标。 | function buildSearchKey(ref: string): { key: string; map: number[] } { |
| ReferenceSearchHit@168 | interface | L168-177 | 单个知识点的文献命中结果。 | export interface ReferenceSearchHit { |
| ReferenceSearchResult@180 | interface | L180-188 | 文献检索的整体结果。 | export interface ReferenceSearchResult { |
| ReferenceMatch@191 | interface | L191-198 | 一条文献的命中证据。 | export interface ReferenceMatch { |
| MatchReferencesOptions@200 | interface | L200-211 |  | export interface MatchReferencesOptions { |
| snippetAround@216 | function | L216-236 | 从原文里截一段命中处附近的文本（保留原文标点，方便肉眼核对）。 | function snippetAround(ref: string, map: number[], key: string, tokens… |
| matchReferences@245 | function | L245-270 | 在一份文献清单里检索，返回命中证据。 | export function matchReferences( |
