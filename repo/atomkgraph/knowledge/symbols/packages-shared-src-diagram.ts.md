---
covers:
  - packages/shared/src/diagram.ts
title: Semantic block index: diagram.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：diagram.ts（第4层）

**源码文件**：`packages/shared/src/diagram.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="packages/shared/src/diagram.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| isDiagramLang@19 | function | L19-22 | 判断某个 info string 是不是图表语言（mermaid、d2、tikz，忽略大小写）。 | export function isDiagramLang(lang: string \| undefined \| null): lang… |
| escapeHtml@24 | function | L24-29 |  | function escapeHtml(s: string): string { |
| diagramPlaceholder@41 | function | L41-48 | 生成图表占位符 HTML。 | export function diagramPlaceholder(lang: DiagramLang, code: string): s… |
| diagramBlockExtension@56 | function | L56-79 | marked 的块级扩展：把 mermaid / d2 / tikz 代码块换成图表占位符。 | export function diagramBlockExtension() { |
| diagramBlockExtension.start@60 | method | L60-63 |  | start(src: string): number \| undefined { |
| diagramBlockExtension.tokenizer@64 | method | L64-72 |  | tokenizer(src: string): { type: string; raw: string; lang: DiagramLang… |
| diagramBlockExtension.renderer@73 | method | L73-77 |  | renderer(token: unknown): string { |
