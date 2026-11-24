---
covers:
  - packages/core/src/ingest/ocr.ts
title: Semantic block index: ocr.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：ocr.ts（第4层）

**源码文件**：`packages/core/src/ingest/ocr.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="packages/core/src/ingest/ocr.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| OcrPage@19 | interface | L19-31 |  | export interface OcrPage { |
| OcrResult@33 | interface | L33-42 |  | export interface OcrResult { |
| OcrError@52 | class | L52-60 |  | export class OcrError extends Error { |
| OcrOptions@62 | interface | L62-75 |  | export interface OcrOptions { |
| runProcess@86 | function | L86-116 | 跑一个子进程并收集输出。 | export function runProcess( |
| resolveScript@119 | function | L119-133 | 侧车脚本位置：env 覆盖 → cwd 下 → 从模块目录逐级向上找（apps/* 里跑也能找到）。 | export function resolveScript(): string \| null { |
| probePython@143 | function | L143-161 | 探测 python 是否有 rapidocr。 | export async function probePython(python: string, timeoutMs = 30_000):… |
| resolvePython@164 | function | L164-176 | 依次尝试 env 指定 → python → python3 → py。返回可用命令；全不可用返回 null。 | export async function resolvePython(explicit?: string): Promise<{ pyth… |
| ocrStatus@179 | function | L179-191 | 引擎是否可用（供路由/CLI 提前给可操作提示，而不是等到跑 20 分钟才失败）。 | export async function ocrStatus(): Promise<{ available: boolean; pytho… |
| parseOutput@193 | function | L193-205 |  | function parseOutput(stdout: string): Record<string, unknown> \| null … |
| ocrPdf@213 | function | L213-286 | 对 PDF 指定页跑 OCR。返回逐页文本。 | export async function ocrPdf(filePath: string, opts: OcrOptions = {}):… |
