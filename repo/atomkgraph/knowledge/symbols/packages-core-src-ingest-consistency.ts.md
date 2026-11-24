---
covers:
  - packages/core/src/ingest/consistency.ts
title: Semantic block index: consistency.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：consistency.ts（第4层）

**源码文件**：`packages/core/src/ingest/consistency.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="packages/core/src/ingest/consistency.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| MentionCandidate@15 | interface | L15-20 | 参与「找指代」的行。刻意不引 DB：纯函数才能在夹具上断言。 | export interface MentionCandidate { |
| MentionHit@23 | interface | L23-30 | 一处「旧节点正文里提到了新节点」的命中。 | export interface MentionHit { |
| ConsistencyPatch@33 | interface | L33-45 | 一条待确认的改法。 | export interface ConsistencyPatch { |
| titleVariants@48 | function | L48-55 | 新节点标题的几种写法：全名、剥掉括注后的核心名。 | export function titleVariants(title: string): string[] { |
| flatten@63 | function | L63-73 | 压掉空白后的字符串 + 每个字符在原串里的下标。 | function flatten(text: string): { flat: string; map: number[] } { |
| sentenceAt@76 | function | L76-93 | 把命中位置扩成完整句子（模型只能在这一句里改）。 | function sentenceAt(content: string, start: number, end: number): stri… |
| findMentions@101 | function | L101-144 | 找出所有提到 target 的旧节点。 | export function findMentions( |
| mentionNeedles@157 | function | L157-169 | 召回用的「说法片段」。标题本身 + 剥括注的核心名是不够的—— | export function mentionNeedles(title: string): string[] { |
| countOccurrences@170 | function | L170-181 |  | export function countOccurrences(haystack: string, needle: string): nu… |
| RejectReason@183 | interface | L183-187 |  | export interface RejectReason { |
| validatePatch@195 | function | L195-210 | 校验模型提议的改动。 | export function validatePatch( |
