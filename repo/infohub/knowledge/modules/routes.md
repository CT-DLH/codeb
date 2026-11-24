---
covers:
  - src/routes/+page.ts
  - src/routes/[domain]/+page.server.ts
  - src/routes/[domain]/[card_id]/+page.server.ts
  - src/routes/api/assistant/+server.ts
  - src/routes/api/cards/[domain]/[card_id]/+server.ts
  - src/routes/api/cards/[domain]/index.json/+server.ts
  - src/routes/api/domains/+server.ts
  - src/routes/api/search/+server.ts
  - src/routes/reports/+page.server.ts
  - src/routes/reports/[slug]/+page.server.ts
title: Routes Module (Layer 3)
updated: 2026-11-24
---

# 模块：路由——部件细页表（第3层）

**项目**：infohub
**源码文件**：`src/routes/+page.ts`、`src/routes/[domain]/+page.server.ts`、`src/routes/[domain]/[card_id]/+page.server.ts`、`src/routes/api/assistant/+server.ts`、`src/routes/api/cards/[domain]/[card_id]/+server.ts`、`src/routes/api/cards/[domain]/index.json/+server.ts`、`src/routes/api/domains/+server.ts`、`src/routes/api/search/+server.ts`、`src/routes/reports/+page.server.ts`、`src/routes/reports/[slug]/+page.server.ts`
**第4层语义块索引**：
- `src-routes-+page.ts`: `../symbols/src-routes-+page.ts.md`
- `src-routes-[domain]-+page.server.ts`: `../symbols/src-routes-[domain]-+page.server.ts.md`
- `src-routes-[domain]-[card_id]-+page.server.ts`: `../symbols/src-routes-[domain]-[card_id]-+page.server.ts.md`
- `src-routes-api-assistant-+server.ts`: `../symbols/src-routes-api-assistant-+server.ts.md`
- `src-routes-api-cards-[domain]-[card_id]-+server.ts`: `../symbols/src-routes-api-cards-[domain]-[card_id]-+server.ts.md`
- `src-routes-api-cards-[domain]-index.json-+server.ts`: `../symbols/src-routes-api-cards-[domain]-index.json-+server.ts.md`
- `src-routes-api-domains-+server.ts`: `../symbols/src-routes-api-domains-+server.ts.md`
- `src-routes-api-search-+server.ts`: `../symbols/src-routes-api-search-+server.ts.md`
- `src-routes-reports-+page.server.ts`: `../symbols/src-routes-reports-+page.server.ts.md`
- `src-routes-reports-[slug]-+page.server.ts`: `../symbols/src-routes-reports-[slug]-+page.server.ts.md`
**写范围**：src/routes/**
**验证命令**：`powershell -NoProfile -ExecutionPolicy Bypass -File _kbwork/run_regression.ps1`

## 职责
SvelteKit 路由层：页面布局、卡片与内容的 HTTP 接口入口。

## 适用场景
- 需要定位或修改该模块内的源码部件时，先在此页选中部件，再下沉到第4层。
- 需要确认某个文件的语义块清单与行号时，打开对应 `symbols/` 页。

## 功能部件

| 部件 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| `load@2` | function | L2-6 | 首页：领域入口。卡片摘要不在这里预取——12k 行会让首屏变成 6MB HTML，改由「全部卡片」按需加载 | export async function load({ fetch }) { |
| `DomainEntry@14` | interface | L14-16 |  | export interface DomainEntry { |
| `entries@19` | function | L19-22 | 预渲染入口：枚举全部领域，静态模式下不依赖链接爬取 | export function entries(): DomainEntry[] { |
| `familyOf@38` | function | L38-45 | 这个领域属于哪个家族（看它 extends 指向谁）。 | function familyOf(domain: string, parents: Record<string, st… |
| `load@54` | function | L54-140 | 直接读源文件，绕开 HTTP；列与中文名全部来自领域包。 | export async function load({ params, url }: { params: { doma… |
| `CardEntry@4` | interface | L4-7 |  | export interface CardEntry { |
| `entries@13` | function | L13-15 | 预渲染入口：直接枚举 cards/ 源文件（不依赖构建产物）， | export async function entries(): Promise<CardEntry[]> { |
| `load@17` | function | L17-27 |  | export function load({ params }: { params: { domain: string;… |
| `AssistantAction@18` | interface | L18-23 |  | interface AssistantAction { |
| `CurrentState@54` | interface | L54-57 |  | interface CurrentState { |
| `buildPrompt@59` | function | L59-98 |  | function buildPrompt(domain: string, name: string, table: Li… |
| `sanitize@100` | function | L100-135 |  | function sanitize(parsed: any, table: ListMeta): AssistantAc… |
| `GET@7` | function | L7-11 |  | export function GET({ params }: { params: { domain: string; … |
| `entries@14` | function | L14-16 | 静态模式枚举全部卡片；dev 模式下被忽略（listAllEntries 现为异步，需 await） | export async function entries() { |
| `GET@14` | function | L14-19 |  | export async function GET({ params }: { params: { domain: st… |
| `entries@22` | function | L22-24 | 静态模式下靠它枚举要预渲染的领域；dev 模式下被忽略 | export function entries() { |
| `GET@11` | function | L11-13 |  | export function GET() { |
| `GET@14` | function | L14-22 |  | export function GET({ url }: { url: URL }) { |
| `load@11` | function | L11-18 |  | export function load() { |
| `entries@12` | function | L12-14 |  | export function entries() { |
| `load@16` | function | L16-20 |  | export function load({ params }: { params: { slug: string } … |

> 本模块共 **22** 个语义块，本页只列核心部件；完整清单见各 `symbols/` 页。

## 下沉指引
```
选中部件 → 打开第4层 symbols 文件 → read_block(path="src/routes/+page.ts", key="load@2")
选中部件 → 打开第4层 symbols 文件 → read_block(path="src/routes/[domain]/+page.server.ts", key="DomainEntry@14")
选中部件 → 打开第4层 symbols 文件 → read_block(path="src/routes/[domain]/[card_id]/+page.server.ts", key="CardEntry@4")
```
