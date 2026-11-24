---
covers:
  - apps/web/src/components/KnowledgeVisualizations.tsx
title: Semantic block index: KnowledgeVisualizations.tsx (layer 4)
updated: 2026-11-24
---

# 语义块索引：KnowledgeVisualizations.tsx（第4层）

**源码文件**：`apps/web/src/components/KnowledgeVisualizations.tsx`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="apps/web/src/components/KnowledgeVisualizations.tsx", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| openInNewWindow@48 | function | L48-53 | 新窗口打开：走 blob URL。用户主动点击，等同打开一个本地 HTML 文件。 | function openInNewWindow(html: string): void { |
| KnowledgeVisualizations@66 | function | L66-184 | 承载区。 | export function KnowledgeVisualizations({ |
| KnowledgeVisualizations.update@89 | arrow | L89-94 |  | const update = (index: number, next: KnowledgeVisual): void => { |
| KnowledgeVisualizations.remove@95 | arrow | L95-98 |  | const remove = (index: number): void => { |
| KnowledgeVisualizations.add@100 | arrow | L100-106 |  | const add = (viz: KnowledgeVisual): void => { |
| VizCard@187 | function | L187-300 | 单条可视化卡片：标题（可改）+ 操作按钮 + 沙箱 iframe + 可选源码编辑。 | function VizCard({ |
| byteLength@303 | function | L303-309 | UTF-8 字节数。与 normalizeVisualizations 同一口径，前端先拦一道给出人话提示。 | function byteLength(s: string): number { |
| VisualAddForm@321 | function | L321-428 | 「+ 添加」展开的粘贴表单（R58）：标题 + 可选高度 + HTML 源码。 | function VisualAddForm({ |
| VisualAddForm.pickFile@334 | arrow | L334-345 |  | const pickFile = (file: File \| undefined): void => { |
| VisualAddForm.submit@347 | arrow | L347-370 |  | const submit = (): void => { |
