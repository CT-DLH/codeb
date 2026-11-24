---
covers:
  - src/lib/markdown.ts
title: Semantic block index: markdown.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：markdown.ts（第4层）

**源码文件**：`src/lib/markdown.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="src/lib/markdown.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| escapeAttr@27 | arrow | L27-28 | - 知道原文地址 → 按原文地址解析成绝对链接（点出去才是该去的地方）； - 不知道 → 去掉 href 变成不可跳转的文本，原路径留在 title 里。 宁可少一个链接，也不留一个会把用户带到 40 | const escapeAttr = (text: string): string => |
| isRelative@31 | arrow | L31-37 |  | const isRelative = (href: unknown): href is string => |
| resolve@39 | function | L39-46 |  | function resolve(href: string, baseUrl: string \| null): string \| nul… |
| renderMarkdown@93 | function | L93-95 | @param source 卡片正文（非字符串按空处理） @param baseUrl 原文的绝对地址（卡片的 source_ref 或 ext.url），用来解析正文里的相对链接与图片 | export function renderMarkdown(source: unknown, baseUrl?: string \| nu… |
