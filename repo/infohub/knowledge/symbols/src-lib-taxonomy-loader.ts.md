---
covers:
  - src/lib/taxonomy/loader.ts
title: Semantic block index: loader.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：loader.ts（第4层）

**源码文件**：`src/lib/taxonomy/loader.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="src/lib/taxonomy/loader.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| Taxonomy@37 | interface | L37-41 |  | export interface Taxonomy { |
| RawNode@44 | interface | L44-51 | YAML 一份文档里的 nodes 数组条目（宽松取值，逐字段归一化） | interface RawNode { |
| readNodes@53 | function | L53-65 |  | function readNodes(file: string): TaxonomyNodeInput[] { |
| loadTaxonomy@70 | function | L70-77 | 加载三份 YAML，构建索引并校验。结果缓存；返回 problems 而不抛错。 | export function loadTaxonomy(): Taxonomy { |
| ancestorsOf@80 | function | L80-91 | 沿 parent 链上溯，返回从父到根的所有祖先 ID（不含自身）。未知 ID 返回空。 | export function ancestorsOf(id: string, tax: Taxonomy = loadTaxonomy()… |
| descendantsOf@94 | function | L94-107 | 沿 childrenOf 下展，返回所有后代 ID（不含自身）。叶子 / 非树节点返回空。 | export function descendantsOf(id: string, tax: Taxonomy = loadTaxonomy… |
| labelOf@110 | function | L110-112 | 取节点中文显示名；未知 ID 返回 undefined。 | export function labelOf(id: string, tax: Taxonomy = loadTaxonomy()): s… |
| resolveLegacyId@115 | function | L115-117 | legacy_id（旧完整点分 ID）→ 新单段 ID；未登记的返回 undefined。 | export function resolveLegacyId(legacyId: string, tax: Taxonomy = load… |
