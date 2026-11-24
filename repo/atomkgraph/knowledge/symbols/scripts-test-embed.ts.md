---
covers:
  - scripts/test-embed.ts
title: Semantic block index: test-embed.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：test-embed.ts（第4层）

**源码文件**：`scripts/test-embed.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="scripts/test-embed.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| EmbedConfig@8 | interface | L8-13 |  | interface EmbedConfig { |
| loadEmbedConfig@15 | function | L15-32 |  | function loadEmbedConfig(): EmbedConfig { |
| genSampleTexts@35 | function | L35-43 | 生成模拟的原子知识点文本（中文，长度接近真实） | function genSampleTexts(n: number): string[] { |
| embedBatch@45 | function | L45-64 |  | async function embedBatch(cfg: EmbedConfig, texts: string[]): Promise<… |
| main@66 | function | L66-120 |  | async function main() { |
