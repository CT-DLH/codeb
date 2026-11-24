---
covers:
  - packages/core/src/services/chat-service.ts
title: Semantic block index: chat-service.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：chat-service.ts（第4层）

**源码文件**：`packages/core/src/services/chat-service.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="packages/core/src/services/chat-service.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| ChatTurnResult@87 | interface | L87-93 | 本轮结果：整段会话消息 + 最终答复 + 本轮触及的知识点 id。 | export interface ChatTurnResult { |
| ChatServiceDeps@172 | interface | L172-203 |  | export interface ChatServiceDeps { |
| ChatService@205 | class | L205-684 |  | export class ChatService { |
| ChatService.createSession@233 | method | L233-235 | ---- 会话管理 ---- | createSession(input: { title?: string; anchor_id?: string \| null } = … |
| ChatService.listSessions@237 | method | L237-239 |  | listSessions(limit = 50): ChatSession[] { |
| ChatService.getSession@241 | method | L241-245 |  | getSession(id: string): { session: ChatSession; messages: ChatMessageR… |
| ChatService.deleteSession@247 | method | L247-249 |  | deleteSession(id: string): boolean { |
| ChatService.setAnchor@252 | method | L252-254 | 手动设定会话锚点（上下文按工作集裁剪时用）。 | setAnchor(id: string, anchorId: string \| null): ChatSession \| null { |
| ChatService.updateSessionMeta@257 | method | L257-262 | 改标题 / 锚点（PATCH：只改传入字段）。 | updateSessionMeta( |
| ChatService.listTools@268 | method | L268-270 | 可被模型调用的工具清单（前端据此标记写操作）。 | listTools(): ToolDef[] { |
| ChatService.sendMessage@274 | method | L274-459 | ---- 一轮对话 ---- | async sendMessage( |
| ChatService.execTool@462 | method | L462-479 | 执行一个工具调用，任何异常都转成 { error } 结果，不中断整轮。 | private async execTool(tc: ToolCall): Promise<unknown> { |
| ChatService.rescueVisualizationCall@486 | method | L486-538 | 拦下「把字段名当 action」的可视化调用，就地改写成合法的 update。 | private rescueVisualizationCall( |
| ChatService.salvageVisualization@549 | method | L549-574 | 把回复正文里那份 HTML 落到知识点的 visualizations 上。 | private async salvageVisualization( |
| ChatService.buildPrompt@584 | method | L584-667 | 组装这一轮发给模型的消息。 | private async buildPrompt(session: ChatSession): Promise<ChatMessage[]… |
| ChatService.resolveOne@670 | method | L670-683 | 解析一张图片 URL → data URL（带缓存；失败返回 null，不打断整轮）。 | private async resolveOne(url: string): Promise<string \| null> { |
| attachmentUrls@687 | function | L687-691 | 从消息 meta 里取图片 URL 列表（落库时存在 meta.attachments）。 | function attachmentUrls(m: ChatMessageRecord): string[] { |
| unwrapAgentEnvelope@699 | function | L699-718 | 模型偶尔会把「最终答复」也按工具调用的 JSON 协议包一层，比如： | export function unwrapAgentEnvelope(text: string): string { |
| extractLeadingJson@721 | function | L721-748 | 从字符串开头截出一个平衡的 JSON 对象（忽略字符串内的花括号），返回解析值与剩余文本。 | function extractLeadingJson(text: string): { value: unknown; rest: str… |
| wantsHeavyOutput@763 | function | L763-775 | 判断这一轮是否需要「重型输出」（自包含 HTML / 长代码），从而换用非推理模型。 | export function wantsHeavyOutput(userText: string): boolean { |
| extractStandaloneHtml@786 | function | L786-804 | 从回复正文里抠出一份「完整的、可独立运行的自包含 HTML」。 | export function extractStandaloneHtml(text: string): { html: string; r… |
| normalizeDoc@807 | function | L807-818 | 校验并规整一份 HTML 文档；不合格返回 null。 | function normalizeDoc(html: string): { html: string; title: string } \… |
| stripGlitchTokens@831 | function | L831-838 | 清洗模型输出里的畸形转义标记。 | export function stripGlitchTokens(text: string): string { |
| summarizeToolResult@841 | function | L841-856 | 工具结果压成一行摘要回灌给模型；完整结果留在 chat_message.meta.full（UI 可展开）。 | function summarizeToolResult(result: unknown): string { |
| collectTouchedKnowledge@865 | function | L865-886 | 从一次工具调用与其结果里收集被写入/触及的知识点 id。 | function collectTouchedKnowledge(tc: ToolCall, result: unknown): strin… |
| collectTouchedKnowledge.take@878 | arrow | L878-882 |  | const take = (v: unknown): void => { |
