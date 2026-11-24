---
covers:
  - src/lib/schemas.ts
title: Semantic block index: schemas.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：schemas.ts（第4层）

**源码文件**：`src/lib/schemas.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="src/lib/schemas.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| DeriveRule@23 | interface | L23-30 | 派生字段规则（见 src/core/derive.ts 的 applyDerives） | export interface DeriveRule { |
| FieldSpec@32 | interface | L32-70 |  | export interface FieldSpec { |
| buildShape@72 | function | L72-78 |  | function buildShape(fields: Record<string, FieldSpec>): Record<string,… |
| buildZodFromSpec@81 | function | L81-109 | 递归地把 YAML 字段规格转换为 Zod 类型（不硬编码任何字段名） | export function buildZodFromSpec(spec: FieldSpec): z.ZodTypeAny { |
| readYaml@111 | function | L111-116 |  | function readYaml(file: string): any { |
| domainInheritanceIds@124 | function | L124-141 | 领域包的继承链 ID，根在前、叶在后：_base → person → student。 | export function domainInheritanceIds(domainId: string): string[] { |
| ChainCacheEntry@150 | interface | L150-153 | 继承链合并结果缓存。 | interface ChainCacheEntry { |
| chainSignature@156 | function | L156-166 |  | function chainSignature(ids: string[]): string { |
| clearSchemaCache@169 | function | L169-172 | 领域包写盘后必须调用：漏一处就会「改完 YAML 刷新没反应」 | export function clearSchemaCache(domainId?: string): void { |
| mergeChain@181 | function | L181-208 | 合并继承链： | function mergeChain(domainId: string): any { |
| isAbstractDomain@211 | function | L211-217 | 抽象父包：只提供字段与身份默认值，不能落卡，也不出现在导航 / API / 列表页里 | export function isAbstractDomain(domainId: string): boolean { |
| domainExtendsMap@223 | function | L223-234 | 直接父包映射（子 → 父）。改父包会顺着这条边影响所有后代， | export function domainExtendsMap(): Record<string, string> { |
| listAllDomainIds@244 | function | L244-250 | 全部领域包 ID（含抽象父包），供领域维护与 extends 校验用。 | export function listAllDomainIds(): string[] { |
| listDomainIds@253 | function | L253-255 | 可落卡的领域 ID（domains/*.yaml，排除 _ 开头的通用文件与 abstract 父包） | export function listDomainIds(): string[] { |
| DomainMeta@257 | interface | L257-270 |  | export interface DomainMeta { |
| ImportStrategyDefaults@278 | interface | L278-284 | 导入策略的领域级默认值：card_import 的优先级是 | export interface ImportStrategyDefaults { |
| parseImportStrategies@294 | function | L294-305 |  | function parseImportStrategies(raw: any): ImportStrategyDefaults \| nu… |
| importsForApi@308 | function | L308-310 | 回给工具/接口的形态：与领域包 YAML 键名一致 | export function importsForApi(cfg: ImportStrategyDefaults \| null): Re… |
| AttachmentConfig@317 | interface | L317-326 | 附件 = 往已有卡上挂正文，不是新实体。 | export interface AttachmentConfig { |
| parseAttachments@328 | function | L328-348 |  | function parseAttachments(raw: any): AttachmentConfig \| null { |
| parseAttachments.list@331 | arrow | L331-332 |  | const list = (value: unknown): string[] => |
| attachmentsForApi@351 | function | L351-362 | 回给工具与接口的形态：与领域包 YAML 的键名一致，照着抄就能写回 domain_update | export function attachmentsForApi(cfg: AttachmentConfig \| null): Reco… |
| IdentityConfig@370 | interface | L370-378 | 标识位：去重、card_id 生成、实体合并三处逻辑的唯一依据。 | export interface IdentityConfig { |
| parseIdentity@380 | function | L380-406 |  | function parseIdentity(raw: any): IdentityConfig \| null { |
| parseIdentity.list@383 | arrow | L383-384 |  | const list = (value: unknown): string[] => |
| loadDomainMeta@408 | function | L408-420 |  | export function loadDomainMeta(domainId: string): DomainMeta { |
| DomainSpec@422 | interface | L422-433 |  | export interface DomainSpec { |
| loadDomainSpec@436 | function | L436-450 | 领域包的原始规格（未经 Zod 转换），用于 Schema 发现 / 自省 | export function loadDomainSpec(domainId: string): DomainSpec { |
| loadDomainBaseShape@453 | function | L453-456 | 通用字段（_base + 继承链上声明的 base 字段）的 Zod shape | export function loadDomainBaseShape(domainId: string): Record<string, … |
| loadDomainExtShape@459 | function | L459-462 | 领域扩展字段的 Zod shape（含从父包继承的字段，否则继承来的字段会被校验拒写） | export function loadDomainExtShape(domainId: string): Record<string, z… |
| loadDomainSchema@472 | function | L472-486 | 领域卡片 Schema： | export function loadDomainSchema(domainId: string): z.ZodObject<any> { |
| collectUnknownFields@495 | function | L495-519 | 收集卡片里未被领域包声明的字段（供 validate / build 输出警告用）。 | export function collectUnknownFields(domainId: string, data: Record<st… |
