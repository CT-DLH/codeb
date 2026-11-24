---
covers:
  - packages/core/src/llm/embedding.ts
title: Semantic block index: embedding.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：embedding.ts（第4层）

**源码文件**：`packages/core/src/llm/embedding.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="packages/core/src/llm/embedding.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| EmbeddingConfig@7 | interface | L7-12 |  | export interface EmbeddingConfig { |
| loadEmbeddingConfig@28 | function | L28-33 | 从环境变量加载 embedding 配置。 | export function loadEmbeddingConfig(): EmbeddingConfig { |
| embedText@40 | function | L40-50 | 调在线 API 取单条文本的 embedding 向量（OpenAI 兼容 /embeddings）。 | export async function embedText( |
| EmbedRuntimeOptions@109 | interface | L109-116 | 批量取多段文本的 embedding（OpenAI 兼容 /embeddings 的 input 数组形态）。 | export interface EmbedRuntimeOptions { |
| embedTexts@118 | function | L118-159 |  | export async function embedTexts( |
| embedChunk@171 | function | L171-209 | 一批（≤128 条）向量化：超时就二分再试。 | async function embedChunk( |
| withTimeout@217 | function | L217-231 | 给一个 promise 套显式超时竞速，并在超时时 abort 底层请求。 | function withTimeout<T>(p: Promise<T>, deadline: number, controller: A… |
| embedTimeoutError@234 | function | L234-238 | 把 AbortError/TimeoutError 换成看得懂的文案；必须含 "timeout" 让 classifyTransient 判为可拆批重试。 | function embedTimeoutError(timeoutMs: number, phase: string): Error { |
| embedOnce@241 | function | L241-314 | 单次请求（不重试、不拆批）。 | async function embedOnce( |
| createEmbeddingFn@317 | function | L317-320 | 构造可用于 SearchService 的 EmbeddingFn（保留 role 透传）。 | export function createEmbeddingFn(cfg?: EmbeddingConfig): EmbeddingFn … |
| createEmbeddingBatchFn@323 | function | L323-326 | 构造批量 EmbeddingBatchFn（用于索引重建时按批调用）。 | export function createEmbeddingBatchFn(cfg?: EmbeddingConfig): Embeddi… |
