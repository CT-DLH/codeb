---
covers:
  - packages/core/src/services/browser.ts
title: Semantic block index: browser.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：browser.ts（第4层）

**源码文件**：`packages/core/src/services/browser.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="packages/core/src/services/browser.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| chromeCandidates@9 | function | L9-29 | 浏览器探测顺序：环境变量优先，其次系统常见安装位置。 | export function chromeCandidates(): string[] { |
| findBrowser@32 | function | L32-44 | 找一个能用的浏览器；找不到就抛明确的错，不要留给 puppeteer 报一句天书。 | export function findBrowser(explicit?: string): string { |
