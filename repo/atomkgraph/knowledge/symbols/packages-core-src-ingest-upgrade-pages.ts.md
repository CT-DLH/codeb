---
covers:
  - packages/core/src/ingest/upgrade-pages.ts
title: Semantic block index: upgrade-pages.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：upgrade-pages.ts（第4层）

**源码文件**：`packages/core/src/ingest/upgrade-pages.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="packages/core/src/ingest/upgrade-pages.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| UpgradePagesOptions@24 | interface | L24-52 |  | export interface UpgradePagesOptions { |
| PageContinuity@55 | interface | L55-64 | 一页的边界信息：跨页续接 + 图 + 存疑，全部来自模型的结构化输出 | export interface PageContinuity { |
| ContinuityBreak@67 | interface | L67-71 | 跨页连续性对不上的边界——可能真的丢了内容，必须报出来给人看 | export interface ContinuityBreak { |
| UpgradePagesResult@73 | interface | L73-92 |  | export interface UpgradePagesResult { |
| exercisePages@100 | function | L100-114 | 大纲里「习题 / 答案」两类节的页范围（去重、升序）。 | export function exercisePages(doc: ParsedDocument, opts: { chapter?: s… |
| exercisePages.walk@102 | arrow | L102-109 |  | const walk = (secs: ReturnType<typeof buildOutline>): void => { |
| exerciseSectionStarts@126 | function | L126-138 | 章 / 节 / 习题节各自的起始页。 | export function exerciseSectionStarts(doc: ParsedDocument, opts: { cha… |
| exerciseSectionStarts.walk@128 | arrow | L128-133 |  | const walk = (secs: ReturnType<typeof buildOutline>): void => { |
| chapterLastPage@146 | function | L146-159 | 本章（或全书）内容的最后一页。 | export function chapterLastPage(doc: ParsedDocument, opts: { chapter?:… |
| chapterLastPage.walk@151 | arrow | L151-156 |  | const walk = (secs: ReturnType<typeof buildOutline>): void => { |
| pageEndsClosed@172 | function | L172-177 |  | export function pageEndsClosed(text: string): boolean { |
| checkContinuity@189 | function | L189-223 | 跨页连续性校验（R44：模型告知，代码裁决）。 | export function checkContinuity( |
| rebuildMarkdown@226 | function | L226-228 | 按 <!-- page N --> 的既有格式把页文本重新拼成 markdown（与 parse.ts 的 buildMarkdown 同构） | function rebuildMarkdown(pages: ParsedPage[]): string { |
| upgradeExercisePages@236 | function | L236-360 | 对指定页做视觉重转录并把文本换进文档。返回新的 doc（不改入参）。 | export async function upgradeExercisePages( |
