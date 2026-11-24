---
covers:
  - apps/web/src/components/editor/markdown.ts
title: Semantic block index: markdown.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：markdown.ts（第4层）

**源码文件**：`apps/web/src/components/editor/markdown.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="apps/web/src/components/editor/markdown.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| parseInline@16 | function | L16-151 | 行内 Markdown 解析：把一段文本切成 TipTap 的 inline 节点数组。 | export function parseInline(text: string): JSONContent[] { |
| parseInline.flush@21 | arrow | L21-26 |  | const flush = () => { |
| isTableDelim@154 | function | L154-156 | 是否是一个「分隔行」（\|---\|:--:\|） | function isTableDelim(line: string): boolean { |
| splitRow@159 | function | L159-164 | 拆分表格行成单元格（去掉首尾竖线）。 | function splitRow(line: string): string[] { |
| markdownToDoc@167 | function | L167-369 | 把一段 Markdown 文本解析为 TipTap 的 doc 节点。 | export function markdownToDoc(markdown: string): JSONContent { |
| markdownToDoc.takeParagraph@173 | arrow | L173-190 |  | const takeParagraph = (): string[] => { |
| markdownToDoc.cell@274 | arrow | L274-277 |  | const cell = (t: string): JSONContent => ({ |
| escapeText@389 | function | L389-403 | 最小转义：普通文本序列化回 Markdown 时，只转义真的会破坏解析的字符。 | function escapeText(t: string): string { |
| InlineMarks@407 | interface | L407-414 | 序列化 inline 节点为 Markdown 文本。 | interface InlineMarks { |
| marksOf@416 | function | L416-427 |  | function marksOf(n: JSONContent): InlineMarks { |
| marksKey@430 | function | L430-432 | 两段标记是否相同（决定能否合并成一个包裹）。 | function marksKey(m: InlineMarks): string { |
| wrapOpen@434 | function | L434-443 |  | function wrapOpen(m: InlineMarks): string { |
| wrapClose@445 | function | L445-453 |  | function wrapClose(m: InlineMarks): string { |
| inlineBody@456 | function | L456-475 | 单个内联节点的正文（不含外层标记包裹）。 | function inlineBody(n: JSONContent, m: InlineMarks): string { |
| serializeInline@486 | function | L486-517 | 序列化一段内联内容。 | function serializeInline(nodes: JSONContent[] \| undefined): string { |
| serializeInline.close@491 | arrow | L491-497 |  | const close = (): void => { |
| docToMarkdown@520 | function | L520-632 | 把 TipTap doc 节点序列化为 Markdown。 | export function docToMarkdown(doc: JSONContent): string { |
| docToMarkdown.walkBlocks@523 | arrow | L523-620 |  | const walkBlocks = (nodes: JSONContent[] \| undefined, indent = ''): v… |
| docToMarkdown.renderRow@592 | arrow | L592-597 |  | const renderRow = (r: JSONContent): string => |
| docToMarkdown.serializeListItem@623 | arrow | L623-627 |  | const serializeListItem = (item: JSONContent): string => { |
