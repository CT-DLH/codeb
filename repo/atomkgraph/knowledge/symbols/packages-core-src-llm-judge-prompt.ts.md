---
covers:
  - packages/core/src/llm/judge-prompt.ts
title: Semantic block index: judge-prompt.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：judge-prompt.ts（第4层）

**源码文件**：`packages/core/src/llm/judge-prompt.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="packages/core/src/llm/judge-prompt.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| JudgeCandidate@13 | interface | L13-21 |  | export interface JudgeCandidate { |
| JudgeDecision@23 | interface | L23-31 |  | export interface JudgeDecision { |
| buildJudgeMessages@51 | function | L51-85 | 构造判定请求的消息列表。 | export function buildJudgeMessages(input: { |
| parseJudgeDecision@93 | function | L93-116 | 解析 LLM 输出。容错处理：模型常把 JSON 包在 json 里或前后带解释。 | export function parseJudgeDecision(raw: string): JudgeDecision \| null… |
| validateDecision@122 | function | L122-127 | 校验决策的自洽性：除了 new，其余动作必须指向一个真实候选。 | export function validateDecision(d: JudgeDecision, validIds: Set<strin… |
