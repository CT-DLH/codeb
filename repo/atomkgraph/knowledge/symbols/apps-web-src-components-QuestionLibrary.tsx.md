---
covers:
  - apps/web/src/components/QuestionLibrary.tsx
title: Semantic block index: QuestionLibrary.tsx (layer 4)
updated: 2026-11-24
---

# 语义块索引：QuestionLibrary.tsx（第4层）

**源码文件**：`apps/web/src/components/QuestionLibrary.tsx`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="apps/web/src/components/QuestionLibrary.tsx", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| QuestionLibrary@51 | function | L51-651 |  | export function QuestionLibrary({ |
| QuestionLibrary.toggleIn@237 | arrow | L237-239 |  | const toggleIn = (arr: string[], set: (v: string[]) => void, key: stri… |
| QuestionLibrary.resetFilters@242 | arrow | L242-250 |  | const resetFilters = (): void => { |
| QuestionLibrary.toggleSelect@253 | arrow | L253-260 |  | const toggleSelect = (id: string): void => { |
| QuestionLibrary.doFold@268 | arrow | L268-302 | 目标卷为空 + 填了标题 → 新建卷；否则归入已有卷。 归卷后 paper_order 由后端顺序生成（前端不传顺序——传了就会与已有题撞号）。 | const doFold = async (): Promise<void> => { |
| FacetGroup@654 | function | L654-687 | 一组 facet 勾选（可多选）。 | function FacetGroup({ |
| Row@698 | function | L698-751 | 一行题。 | function Row({ |
| byKnowledge@763 | function | L763-780 | 按归属知识点分桶（仅用于把本页的题分行显示）。 | function byKnowledge(rows: QuestionRow[]): Array<{ |
