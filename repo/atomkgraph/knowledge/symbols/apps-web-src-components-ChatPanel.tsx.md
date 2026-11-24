---
covers:
  - apps/web/src/components/ChatPanel.tsx
title: Semantic block index: ChatPanel.tsx (layer 4)
updated: 2026-11-24
---

# 语义块索引：ChatPanel.tsx（第4层）

**源码文件**：`apps/web/src/components/ChatPanel.tsx`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="apps/web/src/components/ChatPanel.tsx", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| ChatAnchorInfo@41 | interface | L41-43 | 会话锚定信息（用于面板顶部显示「当前话题挂在哪个节点」）。 | export interface ChatAnchorInfo { |
| ChatPanelProps@45 | interface | L45-53 |  | interface ChatPanelProps { |
| getInitialChatWidth@61 | function | L61-69 |  | function getInitialChatWidth(): number { |
| fmtTime@71 | function | L71-76 |  | function fmtTime(iso: string): string { |
| fmtTime.p@74 | arrow | L74-74 |  | const p = (n: number) => String(n).padStart(2, '0') |
| extractJumpId@79 | function | L79-86 | 从工具结果的 JSON 里尽量挖出一个可跳转的知识点 id。 | function extractJumpId(msg: ChatMessageRecord): string \| null { |
| ToolCard@89 | function | L89-158 | 单个工具调用结果卡（默认折叠，点开看完整 JSON）。 | function ToolCard({ |
| AssistantMessage@161 | function | L161-202 | 一条助手消息：可能的正文 + 工具调用链（工具结果紧随其后）。 | function AssistantMessage({ |
| ChatPanel@204 | function | L204-616 |  | export function ChatPanel({ collapsed, onToggle, onJump, selectedId }:… |
| ChatPanel.onResizeStart@241 | arrow | L241-254 |  | const onResizeStart = (e: ReactMouseEvent) => { |
| ChatPanel.onMove@245 | arrow | L245-247 |  | const onMove = (ev: MouseEvent) => { |
| ChatPanel.onUp@248 | arrow | L248-251 |  | const onUp = () => { |
| ChatPanel.newSession@288 | arrow | L288-299 |  | const newSession = async () => { |
| ChatPanel.removeSession@301 | arrow | L301-309 |  | const removeSession = async (id: string) => { |
| ChatPanel.onPaste@330 | arrow | L330-345 | 粘贴时截获剪贴板里的图片文件。 | const onPaste = (e: ClipboardEvent<HTMLTextAreaElement>) => { |
| ChatPanel.send@347 | arrow | L347-404 |  | const send = async () => { |
