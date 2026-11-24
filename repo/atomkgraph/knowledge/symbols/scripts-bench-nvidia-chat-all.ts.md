---
covers:
  - scripts/bench-nvidia-chat-all.ts
title: Semantic block index: bench-nvidia-chat-all.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：bench-nvidia-chat-all.ts（第4层）

**源码文件**：`scripts/bench-nvidia-chat-all.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="scripts/bench-nvidia-chat-all.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| argOf@36 | arrow | L36-39 |  | const argOf = (n: string): string \| undefined => { |
| has@40 | arrow | L40-40 |  | const has = (n: string): boolean => argv.includes(`--${n}`) |
| Res@70 | interface | L70-81 |  | interface Res { |
| classifyErr@83 | function | L83-94 |  | function classifyErr(e: unknown): { verdict: string; err: string; stat… |
| light@97 | function | L97-127 | 档位 1：轻量。只要它回一句正文，就说明「活着且能出 content」。 | async function light(cfg: LLMConfig): Promise<Res> { |
| heavy@130 | function | L130-194 | 档位 2：真实抽题。判据与录入链路一致——3 道题必须抽出 3 道且 JSON 合法。 | async function heavy(cfg: LLMConfig): Promise<Res> { |
| Row@196 | interface | L196-203 |  | interface Row { |
| main@205 | function | L205-309 |  | async function main(): Promise<void> { |
| main.secs@264 | arrow | L264-264 |  | const secs = (ms?: number): string => (ms === undefined ? '-' : (ms / … |
