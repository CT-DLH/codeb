---
covers:
  - packages/core/src/ingest/outline.ts
title: Semantic block index: outline.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：outline.ts（第4层）

**源码文件**：`packages/core/src/ingest/outline.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="packages/core/src/ingest/outline.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| OutlineSection@19 | interface | L19-33 |  | export interface OutlineSection { |
| OutlineOptions@35 | interface | L35-38 |  | export interface OutlineOptions { |
| kindOf@56 | function | L56-61 |  | function kindOf(title: string): SectionKind { |
| stripPageNo@69 | function | L69-71 | 剥掉 OCR 粘在标题尾巴上的页码（物理层33、数据链路层·.. 50、本章小结及疑难点.28）。 | function stripPageNo(s: string): string { |
| cleanTitle@74 | function | L74-79 | 标题清洗：去掉 OCR 残留的尾导引点、页码、行尾标点。 | function cleanTitle(raw: string): string { |
| cjkCount@81 | function | L81-83 |  | function cjkCount(s: string): number { |
| baseOf@85 | function | L85-87 |  | function baseOf(label: string): string { |
| labelOfHeading@100 | function | L100-105 | 找正文起点（= 目录/扉页/前言结束的那一行）。 | function labelOfHeading(s: string): string \| null { |
| isAncestorLabel@108 | function | L108-116 | anc 是 desc 的严格上层标题吗（1.1 之于 1.1.1、第1章 之于 1.2） | function isAncestorLabel(anc: string, desc: string): boolean { |
| findBodyStart@118 | function | L118-151 |  | function findBodyStart(lines: string[]): number { |
| findBodyStart.isHeadingish@120 | arrow | L120-120 |  | const isHeadingish = (s: string): boolean => SECTION_RE.test(s) \|\| C… |
| extendToOpeningChapter@166 | function | L166-185 | 把起点往前补到「文档开头的那个章标题」。 | function extendToOpeningChapter(lines: string[], start: number, isHead… |
| asSection@191 | function | L191-206 | 章节行 → { level, label, title }；不像标题返回 null。 | function asSection( |
| modeTitle@209 | function | L209-217 | 一组的众数；并列时取更短的（噪声常表现为多出字符）。 | function modeTitle(cands: string[]): string { |
| buildTree@219 | function | L219-231 |  | function buildTree(sections: Array<Omit<OutlineSection, 'children'>>):… |
| buildOutline@238 | function | L238-373 | 从 ParsedDocument 建章节树。 | export function buildOutline(doc: ParsedDocument, opts: OutlineOptions… |
| buildOutline.flush@280 | arrow | L280-292 |  | const flush = (): void => { |
| FlatSection@375 | interface | L375-381 |  | export interface FlatSection extends OutlineSection { |
| chapterMatches@390 | function | L390-399 | --chapter 选择器：第3章 / 第3章 数据链路层 / 数据链路层 都认。 | export function chapterMatches(ch: OutlineSection, sel: string): boole… |
| selectChapters@402 | function | L402-404 | 按选择器过滤（空结果由调用方报错，别静默当成「全书」）。 | export function selectChapters(tree: OutlineSection[], sel: string): O… |
| flattenOutline@406 | function | L406-419 | 把树摊平，补上 path / path_key。 | /** 把树摊平，补上 path / path_key。 */export function flattenOutline(tree: Ou… |
| titleKey@427 | function | L427-435 | 标题归一化（比对用的身份键）。 | export function titleKey(title: string): string { |
