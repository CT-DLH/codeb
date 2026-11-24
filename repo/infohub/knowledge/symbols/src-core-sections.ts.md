---
covers:
  - src/core/sections.ts
title: Semantic block index: sections.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：sections.ts（第4层）

**源码文件**：`src/core/sections.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="src/core/sections.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| H2@10 | arrow | L10-10 | 但「上游派生内容」（AI 摘要、采集信息）属于投影，不是人工修订——它们该跟着采集库变。 那条通道由 _replace_sections 显式声明，走 replaceSection / re | const H2 = (section: string) => `## ${section}`; |
| sectionRange@13 | function | L13-25 | 小节标题行的位置范围 [start, end)：start 是标题行，end 是下一个一/二级标题 | function sectionRange(lines: string[], section: string): [number, numb… |
| appendToSection@27 | function | L27-39 |  | export function appendToSection(body: string, section: string, text: s… |
| extractSection@42 | function | L42-48 | 取某一小节的正文（不含标题行）。没有该小节时返回 undefined，调用方据此判断「上游没给这一节」 | export function extractSection(body: string, section: string): string … |
| replaceSection@54 | function | L54-63 | 用 text 覆盖某一小节的内容；卡片没有这一节时退回追加。 | export function replaceSection(body: string, section: string, text: st… |
| extractLead@66 | function | L66-79 | 取正文开头那段引用块（> 一句话结论：…）；没有则返回 undefined | export function extractLead(body: string): string \| undefined { |
| replaceLead@82 | function | L82-101 | 替换正文开头那段引用块（> 一句话结论：…）；没有就以新结论开头 | export function replaceLead(body: string, text: string): string { |
