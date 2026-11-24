---
covers:
  - scripts/scan-nvidia-models.ts
title: Semantic block index: scan-nvidia-models.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：scan-nvidia-models.ts（第4层）

**源码文件**：`scripts/scan-nvidia-models.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="scripts/scan-nvidia-models.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| argOf@28 | arrow | L28-31 |  | const argOf = (n: string): string \| undefined => { |
| kindOf@38 | function | L38-43 |  | function kindOf(id: string): Kind { |
| ProbeRow@45 | interface | L45-65 |  | interface ProbeRow { |
| probeChat@67 | function | L67-108 |  | async function probeChat(id: string): Promise<ProbeRow> { |
| probeEmbed@110 | function | L110-128 |  | async function probeEmbed(id: string): Promise<ProbeRow> { |
| main@130 | function | L130-222 |  | async function main(): Promise<void> { |
| main.worker@149 | function | L149-168 |  | async function worker(): Promise<void> { |
