---
covers:
  - apps/web/src/components/WritePanel.tsx
title: Semantic block index: WritePanel.tsx (layer 4)
updated: 2026-11-24
---

# 语义块索引：WritePanel.tsx（第4层）

**源码文件**：`apps/web/src/components/WritePanel.tsx`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="apps/web/src/components/WritePanel.tsx", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| DraftRow@43 | interface | L43-45 |  | interface DraftRow extends Draft { |
| fmtTime@47 | arrow | L47-48 |  | const fmtTime = (iso: string \| null): string => |
| WritePanel@50 | function | L50-433 |  | export function WritePanel({ |
| WritePanel.flash@115 | arrow | L115-118 |  | const flash = (text: string, error = false) => { |
| WritePanel.onNew@120 | arrow | L120-131 |  | const onNew = async () => { |
| WritePanel.save@134 | arrow | L134-148 |  | const save = async (silent = false): Promise<boolean> => { |
| WritePanel.onSave@150 | arrow | L150-150 |  | const onSave = () => void save(false) |
| WritePanel.openPublish@153 | arrow | L153-176 |  | const openPublish = async () => { |
| WritePanel.doPublish@179 | arrow | L179-197 |  | const doPublish = async (parentId: string \| null, label: string) => { |
| WritePanel.onProcess@200 | arrow | L200-215 |  | const onProcess = async () => { |
| WritePanel.onArchive@217 | arrow | L217-229 |  | const onArchive = async () => { |
| WritePanel.onUnarchive@231 | arrow | L231-243 |  | const onUnarchive = async () => { |
| WritePanel.onDelete@245 | arrow | L245-258 |  | const onDelete = async () => { |
| PublishConfirm@437 | function | L437-559 | ---------------------------------------------------------------- 发布确认面板 | function PublishConfirm({ |
| StagingArea@563 | function | L563-705 | ---------------------------------------------------------------- 暂存区（未归档岛） | function StagingArea({ |
| StagingArea.adopt@577 | arrow | L577-585 |  | const adopt = async (orphanId: string, parentId: string) => { |
| StagingArea.remove@587 | arrow | L587-596 |  | const remove = async (id: string) => { |
| StagingArea.askAdvice@599 | arrow | L599-619 |  | const askAdvice = async (o: OrphanItem) => { |
