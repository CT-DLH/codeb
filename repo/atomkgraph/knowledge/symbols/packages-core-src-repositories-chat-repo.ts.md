---
covers:
  - packages/core/src/repositories/chat-repo.ts
title: Semantic block index: chat-repo.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：chat-repo.ts（第4层）

**源码文件**：`packages/core/src/repositories/chat-repo.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="packages/core/src/repositories/chat-repo.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| ChatSession@9 | interface | L9-15 | 对话会话。anchor_id 可选地把会话锚定到一个知识点，供上下文裁剪。 | export interface ChatSession { |
| ChatMessageRecord@26 | interface | L26-36 | 一条对话消息。 | export interface ChatMessageRecord { |
| SessionRow@38 | interface | L38-44 |  | interface SessionRow { |
| MessageRow@46 | interface | L46-56 |  | interface MessageRow { |
| parseJson@58 | function | L58-65 |  | function parseJson<T>(raw: string \| null, fallback: T): T { |
| rowToSession@67 | function | L67-75 |  | function rowToSession(r: SessionRow): ChatSession { |
| rowToMessage@77 | function | L77-89 |  | function rowToMessage(r: MessageRow): ChatMessageRecord { |
| CreateChatSessionInput@91 | interface | L91-94 |  | export interface CreateChatSessionInput { |
| AddChatMessageInput@96 | interface | L96-103 |  | export interface AddChatMessageInput { |
| ChatRepository@105 | class | L105-220 |  | export class ChatRepository { |
| ChatRepository.createSession@110 | method | L110-126 | ---- 会话 ---- | createSession(input: CreateChatSessionInput = {}): ChatSession { |
| ChatRepository.findSession@128 | method | L128-133 |  | findSession(id: string): ChatSession \| null { |
| ChatRepository.listSessions@135 | method | L135-140 |  | listSessions(limit = 50): ChatSession[] { |
| ChatRepository.updateSession@142 | method | L142-160 |  | updateSession( |
| ChatRepository.touchSession@163 | method | L163-167 | 触碰会话更新时间（发消息后调用，让列表按最近活跃排序）。 | touchSession(id: string): void { |
| ChatRepository.deleteSession@169 | method | L169-175 |  | deleteSession(id: string): boolean { |
| ChatRepository.addMessage@179 | method | L179-205 | ---- 消息 ---- | addMessage(sessionId: string, input: AddChatMessageInput): ChatMessage… |
| ChatRepository.listMessages@207 | method | L207-212 |  | listMessages(sessionId: string): ChatMessageRecord[] { |
| ChatRepository.countMessages@214 | method | L214-219 |  | countMessages(sessionId: string): number { |
