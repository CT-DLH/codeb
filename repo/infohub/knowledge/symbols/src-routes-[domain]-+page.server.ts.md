---
covers:
  - src/routes/[domain]/+page.server.ts
title: Semantic block index: +page.server.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：+page.server.ts（第4层）

**源码文件**：`src/routes/[domain]/+page.server.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="src/routes/[domain]/+page.server.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| DomainEntry@14 | interface | L14-16 |  | export interface DomainEntry { |
| entries@19 | function | L19-22 | 预渲染入口：枚举全部领域，静态模式下不依赖链接爬取 | export function entries(): DomainEntry[] { |
| familyOf@38 | function | L38-45 | 这个领域属于哪个家族（看它 extends 指向谁）。 | function familyOf(domain: string, parents: Record<string, string>): { |
| load@54 | function | L54-140 | 直接读源文件，绕开 HTTP；列与中文名全部来自领域包。 | export async function load({ params, url }: { params: { domain: string… |
