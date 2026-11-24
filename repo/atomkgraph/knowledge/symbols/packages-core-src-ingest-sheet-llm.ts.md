---
covers:
  - packages/core/src/ingest/sheet-llm.ts
title: Semantic block index: sheet-llm.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：sheet-llm.ts（第4层）

**源码文件**：`packages/core/src/ingest/sheet-llm.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="packages/core/src/ingest/sheet-llm.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| RawQuestion@54 | interface | L54-63 | 模型返回的单个题目：只有锚点，没有偏移、没有正文 | interface RawQuestion { |
| RawGroup@65 | interface | L65-69 |  | interface RawGroup { |
| RawSheet@71 | interface | L71-73 |  | interface RawSheet { |
| toStoreType@82 | function | L82-87 | 切分用的 SheetQuestionKind（choice/multiple/judge/blank/short） | function toStoreType(k: SheetQuestionKind): BuiltQuestion['type'] { |
| normKind@89 | function | L89-97 |  | function normKind(v: string \| undefined, hasOptions: boolean): SheetQ… |
| locate@110 | function | L110-140 | 在原文里找锚点，返回起始下标；找不到返回 -1。 | function locate(text: string, anchor: string, from: number, minLen = 4… |
| exactLocate@149 | function | L149-173 | 严格定位：字符必须逐一相同，只容忍空白差异。 | function exactLocate(text: string, anchor: string, from: number, minLe… |
| parseJson@175 | function | L175-197 |  | function parseJson(raw: string): RawSheet \| null {  let body = raw.tr… |
| parseJson.tryParse@181 | arrow | L181-188 |  | const tryParse = (t: string): RawSheet \| null => { |
| SheetCutResult@199 | interface | L199-214 |  | export interface SheetCutResult { |
| cacheKey@252 | function | L252-262 | 内容哈希：同一对节文本 + 同一模型必得同一份切分结果 | function cacheKey(exercise: string, answer: string, model: string): st… |
| CutOptions@264 | interface | L264-275 |  | export interface CutOptions { |
| splitAnswerAndAnalysis@296 | function | L296-326 | 从锚点位置列表切出每个锚点对应的区间（到下一个锚点为止） | export function splitAnswerAndAnalysis(raw: string): { answer: string;… |
| slicesFrom@328 | function | L328-336 |  | function slicesFrom(pos: number[], textLen: number): Array<[number, nu… |
| cutSheetWithLlm@344 | function | L344-634 | 走 LLM 切分一对习题/答案节。 | export async function cutSheetWithLlm( |
| cutSheetWithLlm.Plan@401 | interface | L401-407 | ---- 第一遍：把每题、每答案的锚点都定位到原文坐标 ---- | interface Plan { |
