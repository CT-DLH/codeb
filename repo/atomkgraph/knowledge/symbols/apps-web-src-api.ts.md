---
covers:
  - apps/web/src/api.ts
title: Semantic block index: api.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：api.ts（第4层）

**源码文件**：`apps/web/src/api.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="apps/web/src/api.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| TreeNode@27 | interface | L27-30 |  | export interface TreeNode { |
| RemoveKnowledgeResult@44 | interface | L44-59 | R62：删除知识点返回的影响面（不是只有 {ok:true}）。 | export interface RemoveKnowledgeResult { |
| TagTreeNode@61 | interface | L61-63 |  | export interface TagTreeNode extends Tag { |
| QuestionRow@73 | interface | L73-90 | R61：题库视图里的一行题。 | export interface QuestionRow extends Question { |
| FacetItem@92 | interface | L92-96 |  | export interface FacetItem { |
| QuestionFacets@98 | interface | L98-105 |  | export interface QuestionFacets { |
| QuestionViewResult@107 | interface | L107-122 |  | export interface QuestionViewResult { |
| PaperRow@125 | interface | L125-127 | R61：卷列表行（含统计）。散题池条目多一个 is_loose。 | export interface PaperRow extends PaperWithStats { |
| QuestionViewParams@132 | interface | L132-158 | R61 题库视图的查询参数（前端 → query string）。 | export interface QuestionViewParams { |
| buildViewQuery@168 | function | L168-196 | 拼查询串。 | export function buildViewQuery(p: QuestionViewParams): string { |
| uploadImage@200 | function | L200-215 | 上传图片（本地图床），返回可引用的 URL。 | export async function uploadImage(file: File): Promise<{ ok: boolean; … |
| req@217 | function | L217-241 |  | async function req<T>(path: string, init?: RequestInit): Promise<T> { |
| json@243 | arrow | L243-247 |  | const json = (method: string, body: unknown): RequestInit => ({ |
| ChatSession@889 | interface | L889-896 | ---------------------------------------------------------------- 侧边对话类型 | export interface ChatSession { |
| ChatToolCall@899 | interface | L899-903 | 一次模型发起的工具调用（OpenAI 兼容格式）。 | export interface ChatToolCall { |
| ChatMessageRecord@905 | interface | L905-916 |  | export interface ChatMessageRecord { |
| ChatSessionDetail@918 | interface | L918-921 |  | export interface ChatSessionDetail { |
| ChatTurnResult@923 | interface | L923-929 |  | export interface ChatTurnResult { |
| ChatStreamEvent@932 | interface | L932-940 | 流式接口推给前端的事件（见 server routes 的 SSE 路由）。 | export interface ChatStreamEvent { |
| PublicEmbeddingSettings@947 | interface | L947-958 |  | export interface PublicEmbeddingSettings { |
| PublicChatProfile@963 | interface | L963-975 | 侧边对话 Agent 的单个模型档位（密钥脱敏）。 | export interface PublicChatProfile { |
| PublicChatSettings@978 | interface | L978-981 | 侧边对话模型配置：多档 + 一个启用的（R62）。 | export interface PublicChatSettings { |
| PublicSettings@983 | interface | L983-988 |  | export interface PublicSettings { |
| SettingsPatch@990 | interface | L990-1009 |  | export interface SettingsPatch { |
| ChatProbeResult@1012 | interface | L1012-1025 | 对话档位连通性探测结果（R62）。 | export interface ChatProbeResult { |
| RecallHit@1027 | interface | L1027-1035 |  | export interface RecallHit { |
| RecallResult@1037 | interface | L1037-1041 |  | export interface RecallResult { |
| FeedItem@1044 | interface | L1044-1056 | 发现页 feed 卡片（与 core 的 KnowledgeFeedItem 对齐）。 | export interface FeedItem { |
| FeedResult@1058 | interface | L1058-1064 |  | export interface FeedResult { |
| ProposeResult@1066 | interface | L1066-1075 |  | export interface ProposeResult extends RecallResult { |
| NeighborhoodItem@1078 | interface | L1078-1084 | 小图谱上的一个节点（与 core 的 NeighborhoodNode 对齐，不含正文）。 | export interface NeighborhoodItem { |
| NeighborhoodResult@1087 | interface | L1087-1094 | 知识点邻域：祖先链 + 自身 + 一层子节点。 | export interface NeighborhoodResult { |
