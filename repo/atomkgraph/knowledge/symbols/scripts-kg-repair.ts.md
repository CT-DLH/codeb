---
covers:
  - scripts/kg-repair.ts
title: Semantic block index: kg-repair.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：kg-repair.ts（第4层）

**源码文件**：`scripts/kg-repair.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="scripts/kg-repair.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| flag@24 | function | L24-26 |  | function flag(name: string): boolean { |
| opt@27 | function | L27-30 |  | function opt(name: string): string \| undefined { |
| optsOf@31 | function | L31-40 |  | function optsOf(name: string): string[] { |
| usage@43 | function | L43-62 |  | function usage(msg?: string): never { |
| syncIndex@65 | function | L65-80 | apply 之后补索引：正文被换掉的节点如果不重新向量化，下次检索会召回旧内容。 | async function syncIndex(db: DB, ids: string[]): Promise<void> { |
| describe@82 | function | L82-94 |  | function describe(p: RepairPlanItem): string { |
| suggestTitles@117 | function | L117-173 | 让模型给「待改名」的条目起标题。 | async function suggestTitles(db: DB, pendings: RenamePlanItem[]): Prom… |
| main@175 | function | L175-354 |  | async function main(): Promise<void> { |
