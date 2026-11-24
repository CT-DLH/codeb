---
covers:
  - packages/core/src/llm/embedding-provider.ts
title: Semantic block index: embedding-provider.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：embedding-provider.ts（第4层）

**源码文件**：`packages/core/src/llm/embedding-provider.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="packages/core/src/llm/embedding-provider.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| ProbeResult@16 | interface | L16-23 |  | export interface ProbeResult { |
| Embedder@25 | interface | L25-32 |  | export interface Embedder { |
| OffEmbedder@35 | class | L35-50 | 关闭态：任何调用都失败，调用方据此走降级路径。 | export class OffEmbedder implements Embedder { |
| OffEmbedder.fail@38 | method | L38-40 |  | private fail(): never { |
| OffEmbedder.embed@41 | method | L41-43 |  | embed(): Promise<number[]> { |
| OffEmbedder.embedBatch@44 | method | L44-46 |  | embedBatch(): Promise<number[][]> { |
| OffEmbedder.probe@47 | method | L47-49 |  | async probe(): Promise<ProbeResult> { |
| OnlineEmbedder@53 | class | L53-97 | 在线 API 后端。apiKey 为空时调用即失败，由上层降级。 | export class OnlineEmbedder implements Embedder { |
| OnlineEmbedder.embed@62 | method | L62-74 |  | async embed(text: string, role: EmbedRole = 'passage'): Promise<number… |
| OnlineEmbedder.embedBatch@75 | method | L75-87 |  | async embedBatch(texts: string[], role: EmbedRole = 'passage'): Promis… |
| OnlineEmbedder.probe@88 | method | L88-96 |  | async probe(): Promise<ProbeResult> { |
| LocalHttpEmbedder@103 | class | L103-151 | 本地 HTTP 服务后端（Ollama / LM Studio / Xinference 等）。 | export class LocalHttpEmbedder implements Embedder { |
| LocalHttpEmbedder.url@113 | method | L113-115 |  | private url(): string { |
| LocalHttpEmbedder.post@117 | method | L117-128 |  | private async post(input: string \| string[]): Promise<number[][]> { |
| LocalHttpEmbedder.embed@130 | method | L130-133 |  | async embed(text: string): Promise<number[]> { |
| LocalHttpEmbedder.embedBatch@134 | method | L134-137 |  | async embedBatch(texts: string[]): Promise<number[][]> { |
| LocalHttpEmbedder.probe@138 | method | L138-150 |  | async probe(): Promise<ProbeResult> { |
| FeatureExtractor@154 | interface | L154-159 | transformers.js 的最小可用形态（避免为可选依赖强绑类型）。 | interface FeatureExtractor { |
| TransformersModule@160 | interface | L160-163 |  | interface TransformersModule { |
| BuiltinEmbedder@171 | class | L171-236 | 进程内推理后端。模型只加载一次并常驻（加载慢、推理快）。 | export class BuiltinEmbedder implements Embedder { |
| BuiltinEmbedder.load@181 | method | L181-206 |  | private static async load(model: string): Promise<FeatureExtractor> { |
| BuiltinEmbedder.run@208 | method | L208-217 |  | private async run(texts: string[]): Promise<number[][]> { |
| BuiltinEmbedder.embed@219 | method | L219-222 |  | async embed(text: string): Promise<number[]> { |
| BuiltinEmbedder.embedBatch@223 | method | L223-226 |  | async embedBatch(texts: string[]): Promise<number[][]> { |
| BuiltinEmbedder.probe@227 | method | L227-235 |  | async probe(): Promise<ProbeResult> { |
| createEmbedder@246 | function | L246-261 | 按设置构造后端实例。apiKey 由调用方解析好传入（库里优先、环境变量兜底）。 | export function createEmbedder(s: EmbeddingSettings, apiKey: string): … |
