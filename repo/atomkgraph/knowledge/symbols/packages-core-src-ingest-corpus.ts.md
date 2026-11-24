---
covers:
  - packages/core/src/ingest/corpus.ts
title: Semantic block index: corpus.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：corpus.ts（第4层）

**源码文件**：`packages/core/src/ingest/corpus.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="packages/core/src/ingest/corpus.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| CorpusFile@29 | interface | L29-49 | 一份文件在清单里的样子。模型只看得到这个，看不到原文件。 | export interface CorpusFile { |
| FileHints@51 | interface | L51-60 |  | export interface FileHints { |
| PlannedFile@65 | interface | L65-68 |  | export interface PlannedFile { |
| CorpusGroupPlan@70 | interface | L70-79 |  | export interface CorpusGroupPlan { |
| CorpusPlan@81 | interface | L81-100 |  | export interface CorpusPlan { |
| parseTextDirs@137 | function | L137-143 | 解析 CLI 的 --text-dir（逗号分隔，可多个目录）。 | export function parseTextDirs(raw: string \| undefined): string[] { |
| listSources@152 | function | L152-176 | 递归列出可解析的源文件：PDF，以及 Office 转写出来的 Markdown / 纯文本。 | function listSources(roots: string[], skipPdf = false): Array<{ path: … |
| listSources.walk@158 | arrow | L158-172 |  | const walk = (d: string): void => { |
| sourceKindOf@179 | function | L179-184 | 从转写产物名（xxx.pptx.md）认出原始载体；认不出就当纯文本。导出给测试用。 | export function sourceKindOf(rel: string, ext: string): CorpusFile['so… |
| readHints@195 | function | L195-209 | 从文件名读线索。 | export function readHints(basename: string): FileHints { |
| digest@212 | function | L212-218 | 把正文压成一行，供模型判断这份文件到底是什么。 | function digest(markdown: string): string { |
| catalogCorpus@226 | function | L226-298 | 编目：把目录变成清单。 | export async function catalogCorpus( |
| buildPlanUserPrompt@342 | function | L342-361 |  | function buildPlanUserPrompt(files: CorpusFile[]): string { |
| RawPlan@363 | interface | L363-371 |  | interface RawPlan { |
| isExplanatory@385 | function | L385-388 |  | function isExplanatory(f: CorpusFile): boolean { |
| stripFence@391 | function | L391-394 | 去掉模型偶尔加的 json 围栏。 | function stripFence(s: string): string { |
| planCorpus@403 | function | L403-432 | 规划 + 校验。 | export async function planCorpus( |
| normalizePlan@435 | function | L435-578 | 把模型的自由输出收敛成可执行的计划，并把所有不合规点写进 problems。 | export function normalizePlan(root: string, files: CorpusFile[], raw: … |
| executableGroups@581 | function | L581-583 | 计划里每组「该读哪些文件」——给执行层用。skip 组不返回。 | export function executableGroups(plan: CorpusPlan): CorpusGroupPlan[] … |
