---
covers:
  - packages/core/src/services/settings-service.ts
title: Semantic block index: settings-service.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：settings-service.ts（第4层）

**源码文件**：`packages/core/src/services/settings-service.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="packages/core/src/services/settings-service.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| EmbeddingSettings@17 | interface | L17-31 |  | export interface EmbeddingSettings { |
| RecallChannels@34 | interface | L34-45 | 召回通道开关。任何通道都可独立关闭——单通道不可靠，但组合起来互补。 | export interface RecallChannels { |
| RecallSettings@47 | interface | L47-51 |  | export interface RecallSettings { |
| JudgeSettings@53 | interface | L53-56 |  | export interface JudgeSettings { |
| ChatProfile@65 | interface | L65-77 | 侧边对话 Agent 的一套模型配置（R50 引入，R62 改为多档）。 | export interface ChatProfile { |
| ChatSettings@89 | interface | L89-93 | 侧边对话模型配置：多档 + 一个启用的（R62）。 | export interface ChatSettings { |
| AppSettings@95 | interface | L95-100 |  | export interface AppSettings { |
| PublicChatProfile@103 | interface | L103-106 | 对外返回的单个档位（密钥脱敏）。 | export interface PublicChatProfile extends Omit<ChatProfile, 'apiKey'>… |
| PublicSettings@109 | interface | L109-114 | 对外返回的设置（密钥脱敏）。 | export interface PublicSettings { |
| SettingsPatch@116 | interface | L116-129 |  | export interface SettingsPatch { |
| seedEmbeddingFromEnv@165 | function | L165-171 | 首次启动（库里还没有配置）时，从环境变量推断初始值 —— | function seedEmbeddingFromEnv(): Partial<EmbeddingSettings> { |
| seedChatFromEnv@177 | function | L177-189 | 首次启动时从环境变量推断对话档位 —— 与视觉解析同一口径 | function seedChatFromEnv(): ChatProfile \| null { |
| nextProfileId@192 | function | L192-197 | 生成一个不与现有档位冲突的 id。 | function nextProfileId(used: Set<string>): string { |
| normalizeChat@209 | function | L209-249 | 把存的对话配置归一成 { profiles, activeId }。 | function normalizeChat(raw: unknown, fromEnv: ChatProfile \| null): Ch… |
| SettingsService@251 | class | L251-391 |  | export class SettingsService { |
| SettingsService.readRaw@254 | method | L254-265 |  | private readRaw<T>(key: string): Partial<T> \| null { |
| SettingsService.writeRaw@267 | method | L267-273 |  | private writeRaw(key: string, value: unknown): void { |
| SettingsService.get@276 | method | L276-298 | 读取完整配置（含默认值合并 + 环境变量种子）。 | get(): AppSettings { |
| SettingsService.save@301 | method | L301-340 | 局部更新（只覆盖传了的字段），返回更新后的完整配置。 | save(patch: SettingsPatch): AppSettings { |
| SettingsService.activeChatProfile@346 | method | L346-349 | 当前启用的对话档位。启用 id 失效时回落到第一个； | activeChatProfile(s: AppSettings = this.get()): ChatProfile \| null { |
| SettingsService.resolveApiKey@355 | method | L355-358 | 当前生效的 API key：库里的优先，为空则回退环境变量。 | resolveApiKey(s: EmbeddingSettings): string { |
| SettingsService.hasEnvKey@361 | method | L361-363 | 环境变量里是否已有该 provider 的 key（用于设置页提示「已从 .env 读取」）。 | hasEnvKey(s: EmbeddingSettings): boolean { |
| SettingsService.publicView@366 | method | L366-390 | 对外视图：密钥只暴露「有没有」，不回传明文。 | publicView(): PublicSettings { |
