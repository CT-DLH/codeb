---
covers:
  - packages/core/src/services/judge-service.ts
title: Semantic block index: judge-service.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：judge-service.ts（第4层）

**源码文件**：`packages/core/src/services/judge-service.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="packages/core/src/services/judge-service.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| ProposeInput@20 | interface | L20-25 |  | export interface ProposeInput extends RecallInput { |
| ProposeResult@27 | interface | L27-36 |  | export interface ProposeResult { |
| JudgeService@38 | class | L38-98 |  | export class JudgeService { |
| JudgeService.propose@45 | method | L45-97 | 召回 + 判定一步到位（R7 propose 的核心）。 | async propose(input: ProposeInput): Promise<ProposeResult> { |
