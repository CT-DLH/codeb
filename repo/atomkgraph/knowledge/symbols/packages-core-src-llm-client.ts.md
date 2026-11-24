---
covers:
  - packages/core/src/llm/client.ts
title: Semantic block index: client.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：client.ts（第4层）

**源码文件**：`packages/core/src/llm/client.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="packages/core/src/llm/client.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| ChatMessage@15 | interface | L15-23 |  | export interface ChatMessage { |
| ToolCall@26 | interface | L26-31 | 一次工具调用：id 用于把结果回灌给对应调用。 | export interface ToolCall { |
| ToolSpec@34 | interface | L34-38 | 暴露给模型的工具声明（parameters 为 JSON Schema）。 | export interface ToolSpec { |
| AssistantToolResult@41 | interface | L41-46 | 带工具的一轮回复：可能既有正文又有工具调用。 | export interface AssistantToolResult { |
| messageText@49 | function | L49-55 | 取出消息里的纯文本部分（mock 回放、日志、anthropic 的 system 提取都要用）。 | export function messageText(content: string \| ContentPart[]): string … |
| LLMConfig@57 | interface | L57-62 |  | export interface LLMConfig { |
| loadConfig@84 | function | L84-89 | 从环境变量加载配置。prefix 区分拆解(SPLIT)与日常对话(CHAT)两套模型。 | export function loadConfig(prefix: 'SPLIT' \| 'CHAT'): LLMConfig { |
| loadVisualizeConfig@109 | function | L109-116 | 可视化生成（R60）用的配置。 | export function loadVisualizeConfig(): LLMConfig { |
| collectProviderKeys@135 | function | L135-146 | 视觉解析用的配置。 | export function collectProviderKeys(provider: string): string[] { |
| loadVisionConfig@148 | function | L148-156 |  | export function loadVisionConfig(): LLMConfig { |
| llmConfigFrom@164 | function | L164-178 | 用显式传入的字段构造配置 —— 设置页热切换对话模型时用。 | export function llmConfigFrom(input: { |
| envApiKey@181 | function | L181-183 | 某 provider 对应的环境变量 API key（无则空串）。设置页据此提示「已从 .env 读取」。 | export function envApiKey(provider: string): string { |
| mockResponse@186 | function | L186-197 | Mock 模式：无 API key 时返回可预测的占位响应，便于跑通流程。 | function mockResponse(messages: ChatMessage[]): string { |
| LLMError@216 | class | L216-236 |  | export class LLMError extends Error { |
| ProxyRuntime@246 | interface | L246-249 |  | interface ProxyRuntime { |
| proxyRuntimeOf@267 | function | L267-292 |  | async function proxyRuntimeOf(): Promise<ProxyRuntime \| null> { |
| proxyRuntimeOf.isLocal@279 | arrow | L279-279 |  | const isLocal = (url: string): boolean => /^https?:\/\/(localhost\|127… |
| rawFetch@300 | function | L300-310 | 统一的网络出口：有代理走 ProxyAgent，本地地址直连。 | async function rawFetch(url: string, init: RequestInit): Promise<Respo… |
| undiciModule@334 | function | L334-337 | 惰性加载一次 undici；环境里没有它就返回 null，调用方退回全局 fetch | function undiciModule(): Promise<typeof import('undici') \| null> { |
| longLivedDispatcher@339 | function | L339-355 |  | function longLivedDispatcher(): Promise<import('undici').Agent \| null… |
| fetchWithTimeout@357 | function | L357-422 |  | async function fetchWithTimeout( |
| ChatResult@425 | interface | L425-433 | 一次对话的完整结果。content 为空不再被伪装成成功，由调用方按 finish_reason 判断。 | export interface ChatResult { |
| StreamDelta@441 | interface | L441-444 | 流式增量片段（只在本 chunk 新增，不是累计全文）。 | export interface StreamDelta { |
| normalizeFinish@447 | function | L447-450 | 归一各家对「输出被截断」的叫法：anthropic 是 max_tokens，OpenAI 系是 length。 | function normalizeFinish(reason: string \| null \| undefined): string … |
| baseDetail@452 | function | L452-454 |  | function baseDetail(cfg: LLMConfig) { |
| toAnthropicContent@463 | function | L463-473 | 把 OpenAI 风格的内容块翻成 Anthropic 的 image block。 | function toAnthropicContent(content: string \| ContentPart[]): unknown… |
| streamLimits@488 | function | L488-498 | 流式的三道时间闸（都可在运行时用 env 覆盖，读在调用时而不是模块加载时，方便测试）。 | function streamLimits(): { totalMs: number; idleMs: number; firstByteM… |
| streamLimits.num@489 | arrow | L489-492 |  | const num = (v: string \| undefined, d: number): number => { |
| chatStreamOpenAi@510 | function | L510-669 | OpenAI 兼容端点的 SSE 流式请求：读完整个流、累积成与 chatDetailed 完全相同的 | async function chatStreamOpenAi( |
| chatStreamOpenAi.abortWith@522 | arrow | L522-526 |  | const abortWith = (r: StreamAbortReason): void => { |
| chatStreamOpenAi.armIdle@530 | arrow | L530-533 |  | const armIdle = (): void => { |
| chatStreamOpenAi.clearTimers@534 | arrow | L534-539 |  | const clearTimers = (): void => { |
| chatStreamOpenAi.handleLine@571 | arrow | L571-605 |  | const handleLine = (line: string): boolean => { |
| chatDetailed@675 | function | L675-791 | 结构化对话：只做传输，不替调用方「吃失败」。 | export async function chatDetailed( |
| chat@800 | function | L800-833 | 统一对话接口（严格版）：空正文或截断都会抛 LLMError，绝不静默返回 ''。 | export async function chat( |
| toOpenAiMessage@836 | function | L836-852 | 把内部消息转成 OpenAI 兼容格式（工具调用/结果都用 OpenAI 的字段名）。 | function toOpenAiMessage(m: ChatMessage): Record<string, unknown> { |
| chatWithTools@863 | function | L863-939 | 带工具的一轮对话（OpenAI 兼容 provider）。 | export async function chatWithTools( |
