---
covers:
  - packages/core/src/ingest/align-titles.ts
title: Semantic block index: align-titles.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：align-titles.ts（第4层）

**源码文件**：`packages/core/src/ingest/align-titles.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="packages/core/src/ingest/align-titles.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| ExistingNode@22 | interface | L22-34 | 库里已有的一个节点（给模型当对照表用） | export interface ExistingNode { |
| AlignRename@36 | interface | L36-39 |  | export interface AlignRename { |
| AlignPlan@41 | interface | L41-44 |  | export interface AlignPlan { |
| AlignOptions@46 | interface | L46-52 |  | export interface AlignOptions { |
| flattenForAlign@81 | function | L81-100 | 全树前序编号。模型只认编号，不认路径——路径里一个空格不同就指错人。 | export function flattenForAlign(nodes: MergeInputNode[]): { |
| flattenForAlign.walk@88 | arrow | L88-97 |  | const walk = (list: MergeInputNode[], depth: number): void => { |
| buildAlignUserPrompt@102 | function | L102-122 |  | export function buildAlignUserPrompt( |
| alignTitles@129 | function | L129-245 | 让模型把新树里「换了说法」的标题对齐到库里的原标题。 | export async function alignTitles( |
| applyAlign@248 | function | L248-279 | 落对齐计划：只改标题。返回新树（浅拷贝链，不改入参）。 | export function applyAlign( |
| applyAlign.walk@266 | arrow | L266-276 |  | const walk = (list: MergeInputNode[]): MergeInputNode[] => |
