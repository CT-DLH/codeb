---
covers:
  - apps/web/src/components/CommentPanel.tsx
title: CommentPanel.tsx semantic block index (layer 4)
updated: 2025-08-27
---

# 语义块索引：CommentPanel.tsx（第4层）

**源码文件**：`apps/web/src/components/CommentPanel.tsx`

**解析器**：`typescript` · **解析器**：`typescript` · **第5层完整正文**：`read_block(path="apps/web/src/components/CommentPanel.tsx", key="CommentPanel@43")`

| 语义块 key | 类型 | 行号 | 作用 |
|:--|:--|:--|:--|
| fmtTime@30 | arrow | L30-35 | const fmtTime = (iso: string): string => { |
| p@33 | arrow | L33-33 | const p = (n: number) => String(n).padStart(2, '0') |
| isCritique@41 | arrow | L41-41 | const isCritique = (c: Comment): boolean => c.author === 'ai' && c.par… |
| CommentPanel@43 | function | L43-396 | export function CommentPanel({ |
| CommentPanel.flash@65 | arrow | L65-68 | const flash = (text: string, error = false) => { |
| CommentPanel.onGenerate@95 | arrow | L95-107 | const onGenerate = async () => { |
| CommentPanel.onSend@110 | arrow | L110-124 | const onSend = async () => { |
| CommentPanel.onReply@127 | arrow | L127-144 | const onReply = async (id: string) => { |
| CommentPanel.setStatus@146 | arrow | L146-160 | const setStatus = async (c: Comment, status: Comment['status']) => { |
| CommentPanel.onDelete@162 | arrow | L162-172 | const onDelete = async (c: Comment) => { |
| CommentPanel.copySuggestion@174 | arrow | L174-182 | const copySuggestion = async (c: Comment) => { |
