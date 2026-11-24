---
covers:
  - packages/core/src/llm/explain-templates.ts
title: Semantic block index: explain-templates.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：explain-templates.ts（第4层）

**源码文件**：`packages/core/src/llm/explain-templates.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="packages/core/src/llm/explain-templates.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| TemplateSection@7 | interface | L7-16 |  | export interface TemplateSection { |
| ExplainTemplate@18 | interface | L18-24 |  | export interface ExplainTemplate { |
| pickTemplate@89 | function | L89-98 | 按知识类型选模板；有子节点（父节点）时优先综述型。 | export function pickTemplate( |
| renderTemplateHint@101 | function | L101-109 | 把模板骨架拼成给 AI 的提示文本（强调「示例、可自由调整」）。 | export function renderTemplateHint(tpl: ExplainTemplate): string { |
