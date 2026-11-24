---
covers:
  - apps/web/src/api.ts
title: api.ts semantic block index (layer 4)
updated: 2025-08-27
---

# 语义块索引：api.ts（第4层）

**源码文件**：`apps/web/src/api.ts`

**解析器**：`typescript` · **解析器**：`typescript` · **第5层完整正文**：`read_block(path="apps/web/src/api.ts", key="TreeNode@27")`

| 语义块 key | 类型 | 行号 | 作用 |
|:--|:--|:--|:--|
| TreeNode@27 | interface | L27-30 | export interface TreeNode { |
| RemoveKnowledgeResult@44 | interface | L44-59 | export interface RemoveKnowledgeResult { |
| TagTreeNode@61 | interface | L61-63 | export interface TagTreeNode extends Tag { |
| QuestionRow@73 | interface | L73-90 | export interface QuestionRow extends Question { |
| FacetItem@92 | interface | L92-96 | export interface FacetItem { |
| QuestionFacets@98 | interface | L98-105 | export interface QuestionFacets { |
| QuestionViewResult@107 | interface | L107-122 | export interface QuestionViewResult { |
| PaperRow@125 | interface | L125-127 | export interface PaperRow extends PaperWithStats { |
| QuestionViewParams@132 | interface | L132-158 | export interface QuestionViewParams { |
| buildViewQuery@168 | function | L168-196 | export function buildViewQuery(p: QuestionViewParams): string { |
| uploadImage@200 | function | L200-215 | export async function uploadImage(file: File): Promise<{ ok: boolean; … |
| req@217 | function | L217-241 | async function req<T>(path: string, init?: RequestInit): Promise<T> { |
| json@243 | arrow | L243-247 | const json = (method: string, body: unknown): RequestInit => ({ |
| ChatSession@889 | interface | L889-896 | export interface ChatSession { |
| ChatToolCall@899 | interface | L899-903 | export interface ChatToolCall { |
| ChatMessageRecord@905 | interface | L905-916 | export interface ChatMessageRecord { |
| ChatSessionDetail@918 | interface | L918-921 | export interface ChatSessionDetail { |
| ChatTurnResult@923 | interface | L923-929 | export interface ChatTurnResult { |
| ChatStreamEvent@932 | interface | L932-940 | export interface ChatStreamEvent { |
| PublicEmbeddingSettings@947 | interface | L947-958 | export interface PublicEmbeddingSettings { |
| PublicChatProfile@963 | interface | L963-975 | export interface PublicChatProfile { |
| PublicChatSettings@978 | interface | L978-981 | export interface PublicChatSettings { |
| PublicSettings@983 | interface | L983-988 | export interface PublicSettings { |
| SettingsPatch@990 | interface | L990-1009 | export interface SettingsPatch { |
| ChatProbeResult@1012 | interface | L1012-1025 | export interface ChatProbeResult { |
| RecallHit@1027 | interface | L1027-1035 | export interface RecallHit { |
| RecallResult@1037 | interface | L1037-1041 | export interface RecallResult { |
| FeedItem@1044 | interface | L1044-1056 | export interface FeedItem { |
| FeedResult@1058 | interface | L1058-1064 | export interface FeedResult { |
| ProposeResult@1066 | interface | L1066-1075 | export interface ProposeResult extends RecallResult { |
| NeighborhoodItem@1078 | interface | L1078-1084 | export interface NeighborhoodItem { |
| NeighborhoodResult@1087 | interface | L1087-1094 | export interface NeighborhoodResult { |
