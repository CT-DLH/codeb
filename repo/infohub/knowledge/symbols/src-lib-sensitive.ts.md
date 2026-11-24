---
covers:
  - src/lib/sensitive.ts
title: Semantic block index: sensitive.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：sensitive.ts（第4层）

**源码文件**：`src/lib/sensitive.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="src/lib/sensitive.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| envRaw@28 | function | L28-31 | 客户端 bundle 里可能没有 process，所以取值要兜底 | function envRaw(): string \| undefined { |
| localRuntime@38 | function | L38-40 | 确知是本地运行形态吗：dev 与 build:server 注入 false，静态发布注入 true。 | function localRuntime(): boolean { |
| showSensitive@43 | function | L43-46 | 本次运行是否输出敏感字段：显式环境变量优先，否则按运行形态（本地显示 / 发布剥离） | export function showSensitive(env: string \| undefined = envRaw()): bo… |
| specOf@49 | function | L49-55 | 缓存到领域包 mtime 之外不需要——只在构建/请求路径上跑一次，成本可忽略 | function specOf(domain: string): DomainSpec \| null { |
| sensitivePaths@61 | function | L61-76 | 领域包里 sensitive: true 的字段路径（相对卡片对象）。 | export function sensitivePaths(domain: string): string[] { |
| sensitivePaths.walk@65 | arrow | L65-72 |  | const walk = (fields: Record<string, FieldSpec>, prefix: string): void… |
| hiddenExtKeys@83 | function | L83-91 | 部署产物里连「这个字段存在」都不要说：字段中文名与 sensitive 标记本身也是情报 | export function hiddenExtKeys(domain: string): Set<string> { |
| prune@93 | function | L93-119 |  | function prune(node: unknown, parts: string[], removed: string[], pref… |
| RedactResult@121 | interface | L121-125 |  | export interface RedactResult<T> { |
| SensitiveValue@127 | interface | L127-130 |  | export interface SensitiveValue { |
| collectAt@141 | function | L141-157 |  | function collectAt(node: unknown, parts: string[], out: string[]): voi… |
| pushScalar@159 | function | L159-161 |  | function pushScalar(value: unknown, out: string[]): void { |
| sensitiveValues@164 | function | L164-175 | 按路径取出敏感字段的值（正文遮蔽与构建门禁共用这一份取值口径） | export function sensitiveValues(card: unknown, paths: string[]): Sensi… |
| replaceIn@180 | function | L180-197 |  | function replaceIn(node: unknown, needle: string, seen: Set<unknown>):… |
| redactPaths@200 | function | L200-217 | 纯剥离（不读领域包、不看开关），路径形如 ext.id_card / ext.members[].ssn | export function redactPaths<T>(card: T, paths: string[]): RedactResult… |
| redactCard@223 | function | L223-226 | 剥掉领域包标记的敏感字段（原地改，调用方给的都是本次请求/构建新解析出的对象）。 | export function redactCard<T>(domain: string, card: T, paths?: string[… |
| visibleColumns@232 | function | L232-236 | 列表页要展示的列：发布口径下把敏感列整列去掉（连表头，不留空列）， | export function visibleColumns(domain: string, columns: string[]): str… |
| pruneRelative@239 | function | L239-245 | 列值内部的剪法：parts 以 [] 开头表示「数组每一项」，否则按对象路径剪 | function pruneRelative(node: unknown, parts: string[], prefix: string)… |
| redactRowPaths@248 | function | L248-272 | 纯版本：行是按「列路径」平铺的（row['ext.family'] = 整个数组），剪进列值里 | export function redactRowPaths<T extends Record<string, any>>(row: T, … |
| redactRow@279 | function | L279-284 | 列表行是按「列路径」平铺的（row['ext.family'] = 整个对象/数组）， | export function redactRow<T extends Record<string, any>>(domain: strin… |
| redactRows@287 | function | L287-292 | 批量行只解析一次领域包：3602 行逐行调用 sensitivePaths 会把列表拖到十几秒 | export function redactRows<T extends Record<string, any>>(domain: stri… |
