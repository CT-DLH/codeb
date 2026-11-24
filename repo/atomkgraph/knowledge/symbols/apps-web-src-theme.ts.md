---
covers:
  - apps/web/src/theme.ts
title: Semantic block index: theme.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：theme.ts（第4层）

**源码文件**：`apps/web/src/theme.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="apps/web/src/theme.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| getInitialTheme@9 | function | L9-20 | 读取初始主题：localStorage 优先，否则跟随系统 prefers-color-scheme。 | export function getInitialTheme(): Theme { |
| applyTheme@23 | function | L23-30 | 应用主题（写 html 属性 + 持久化）。 | export function applyTheme(theme: Theme): void { |
