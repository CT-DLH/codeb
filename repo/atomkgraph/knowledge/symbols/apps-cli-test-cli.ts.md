---
covers:
  - apps/cli/test-cli.ts
title: Semantic block index: test-cli.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：test-cli.ts（第4层）

**源码文件**：`apps/cli/test-cli.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="apps/cli/test-cli.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| assert@12 | function | L12-14 |  | function assert(cond: unknown, msg: string): void { |
| akgRaw@26 | function | L26-32 | 执行 akg 命令（node --import tsx 直跑 TS，避开 Windows 下 npx.cmd 解析问题）。 | async function akgRaw(args: string[]): Promise<string> { |
| akg@34 | function | L34-36 |  | async function akg(args: string[]): Promise<any> { |
