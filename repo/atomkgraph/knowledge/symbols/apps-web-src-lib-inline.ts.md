---
covers:
  - apps/web/src/lib/inline.ts
title: Semantic block index: inline.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：inline.ts（第4层）

**源码文件**：`apps/web/src/lib/inline.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="apps/web/src/lib/inline.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| CommitOnBlurOptions@24 | interface | L24-37 | 输入框里的原始字符串 → 业务值；相等判断默认 Object.is。 | export interface CommitOnBlurOptions<T, El extends HTMLInputElement \|… |
| useCommitOnBlur@45 | function | L45-86 | 「输入框一直在那儿、失焦才提交」：元信息字段、可视化标题 / 源码都用它。 | export function useCommitOnBlur< |
| useInlineDraft@94 | function | L94-140 | 「平时是文本、点一下才变输入框」的状态机（知识点标题用）。 | export function useInlineDraft({ |
| useOutsideCommit@148 | function | L148-171 | 点「编辑区」以外任意处触发一次提交（题目卡片「点卡片外保存」）。 | export function useOutsideCommit<T extends HTMLElement>({ |
| useOutsideCommit.onDown@164 | arrow | L164-167 |  | const onDown = (e: MouseEvent) => { |
