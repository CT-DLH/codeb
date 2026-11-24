---
covers:
  - apps/cli/src/index.ts
title: Semantic block index: index.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：index.ts（第4层）

**源码文件**：`apps/cli/src/index.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="apps/cli/src/index.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| Args@11 | interface | L11-14 | ---------- 参数解析 ---------- | interface Args { |
| parseArgs@16 | function | L16-35 |  | function parseArgs(argv: string[]): Args { |
| ApiError@38 | class | L38-45 | ---------- HTTP ---------- | class ApiError extends Error { |
| call@47 | function | L47-65 |  | async function call<T = unknown>(method: string, path: string, body?: … |
| out@68 | function | L68-70 | ---------- 输出 ---------- | function out(value: unknown): void { |
| need@72 | function | L72-76 |  | function need(flags: Record<string, string \| boolean>, key: string): … |
| opt@78 | function | L78-81 |  | function opt(flags: Record<string, string \| boolean>, key: string): s… |
| num@83 | function | L83-89 |  | function num(flags: Record<string, string \| boolean>, key: string): n… |
| renderTree@92 | function | L92-101 | 把扁平知识点数组渲染成缩进树（--human 时使用）。 | function renderTree(nodes: any[], depth = 0): string { |
| main@149 | function | L149-340 | ---------- 主入口 ---------- | async function main(): Promise<void> { |
