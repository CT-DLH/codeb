---
covers:
  - src/mcp/lib/schema-loader.ts
title: Semantic block index: schema-loader.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：schema-loader.ts（第4层）

**源码文件**：`src/mcp/lib/schema-loader.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="src/mcp/lib/schema-loader.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| domainExists@12 | function | L12-14 |  | export function domainExists(domain: string): boolean { |
| validateFull@17 | function | L17-19 | 全量校验（card_create 用） | export function validateFull(domain: string, fields: Record<string, an… |
| messageOf@21 | function | L21-24 |  | function messageOf(issue: { message: string; received?: string; input?… |
| issueMessage@26 | function | L26-28 |  | function issueMessage(err: z.ZodError): string { |
| formatIssues@31 | function | L31-37 | Zod 错误 → "字段路径: 消息" 列表（ext.company: Required 风格，带回显完整路径） | export function formatIssues(err: z.ZodError): string[] { |
| describeDomainSchema@40 | function | L40-121 | 领域 Schema 自省描述：字段名 / 类型 / 必填 / 枚举 / ext 嵌套子结构 | export function describeDomainSchema(domain: string): Record<string, u… |
| describeDomainSchema.describe@42 | arrow | L42-67 |  | const describe = (s: any): any => { |
| validatePartial@124 | function | L124-159 | 部分校验（card_update 用）：逐键校验，允许只更新部分字段 | export function validatePartial( |
