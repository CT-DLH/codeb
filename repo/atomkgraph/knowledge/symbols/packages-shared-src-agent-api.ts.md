---
covers:
  - packages/shared/src/agent/api.ts
title: Semantic block index: api.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：api.ts（第4层）

**源码文件**：`packages/shared/src/agent/api.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="packages/shared/src/agent/api.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| TransportResponse@8 | interface | L8-11 | HTTP 传输：发一个请求，拿回「状态码 + 已解析的响应体」。 | export interface TransportResponse { |
| OutlineNode@20 | interface | L20-31 | 树视图瘦身节点的本地类型声明。 | export interface OutlineNode { |
| KnowledgeOutline@33 | interface | L33-40 |  | export interface KnowledgeOutline { |
| KnowledgeBrief@43 | interface | L43-51 | 列表瘦身节点（对应 core 的 KnowledgeBrief）。 | export interface KnowledgeBrief { |
| ApiError@53 | class | L53-61 |  | export class ApiError extends Error { |
| createApi@69 | function | L69-459 | 创建一套 API 方法（每个方法对应一条 server 路由）。 | export function createApi(transport: ApiTransport) { |
| createApi.request@70 | function | L70-81 |  | async function request<T>(method: string, path: string, body?: unknown… |
