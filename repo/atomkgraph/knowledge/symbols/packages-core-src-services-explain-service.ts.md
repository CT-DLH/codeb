---
covers:
  - packages/core/src/services/explain-service.ts
title: Semantic block index: explain-service.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：explain-service.ts（第4层）

**源码文件**：`packages/core/src/services/explain-service.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="packages/core/src/services/explain-service.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| ExplainResult@20 | interface | L20-25 |  | export interface ExplainResult { |
| createLlmExplainFn@28 | function | L28-41 | 基于 LLM 的默认讲解器。推理模型需要较大的 max_tokens（思维链会占用额度）。 | export function createLlmExplainFn(cfg?: LLMConfig): ExplainFn { |
| ExplainService@43 | class | L43-86 |  | export class ExplainService { |
| ExplainService.generate@56 | method | L56-60 | 为已存在知识点生成讲解（不落库）。 | async generate(knowledgeId: string): Promise<ExplainResult \| null> { |
| ExplainService.generateAndSave@63 | method | L63-67 | 生成讲解并写回知识点 content（走 KnowledgeService.update 会存历史版本）。 | async generateAndSave(knowledgeId: string): Promise<ExplainResult \| n… |
| ExplainService.runFor@69 | method | L69-85 |  | private async runFor(k: Knowledge, save: boolean): Promise<ExplainResu… |
