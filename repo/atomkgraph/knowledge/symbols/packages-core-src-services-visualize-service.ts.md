---
covers:
  - packages/core/src/services/visualize-service.ts
title: Semantic block index: visualize-service.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：visualize-service.ts（第4层）

**源码文件**：`packages/core/src/services/visualize-service.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="packages/core/src/services/visualize-service.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| VisualizeOptions@86 | interface | L86-103 |  | export interface VisualizeOptions { |
| VisualizeResult@105 | interface | L105-119 |  | export interface VisualizeResult { |
| VisualizeService@121 | class | L121-396 |  | export class VisualizeService { |
| VisualizeService.existingOf@133 | method | L133-135 | 是否已有可视化（有就默认跳过：重跑一次不该把已有的挤成两条）。 | private existingOf(id: string): KnowledgeVisual[] { |
| VisualizeService.judge@138 | method | L138-161 | 只判不做：用于「先看模型会挑出哪些」，不花生成的钱。 | async judge(id: string): Promise<VisualizeResult> { |
| VisualizeService.childrenTitles@163 | method | L163-165 |  | private childrenTitles(id: string): string[] { |
| VisualizeService.runJudge@181 | method | L181-207 | 判定一次。 | private async runJudge( |
| VisualizeService.runGenerate@215 | method | L215-249 | 生成一次并审核。审核不通过时返回 null 与原因——由调用方决定是否带原因重试。 | private async runGenerate( |
| VisualizeService.run@257 | method | L257-380 | 单个知识点的完整流程：判定 → 生成 → 审核（带重试）→ 落库。 | async run(id: string, dryRun = false): Promise<VisualizeResult> { |
| VisualizeService.runMany@388 | method | L388-395 | 批量：逐个串行跑。 | async runMany(ids: string[], dryRun = false): Promise<VisualizeResult[… |
| statusLabel@399 | function | L399-410 | 结果里可直接展示给用户的短标签。 | export function statusLabel(s: VisualizeStatus): string { |
| isLlmError@413 | function | L413-415 | 判定/生成的 LLM 故障码，供 CLI 分类统计（与 LLMError 同口径）。 | export function isLlmError(e: unknown): e is LLMError { |
