---
covers:
  - src/core/attach.ts
title: Semantic block index: attach.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：attach.ts（第4层）

**源码文件**：`src/core/attach.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="src/core/attach.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| AttachOptions@21 | interface | L21-32 |  | export interface AttachOptions { |
| AttachDetail@36 | interface | L36-46 |  | export interface AttachDetail { |
| AttachReport@48 | interface | L48-69 |  | export interface AttachReport { |
| walk@73 | function | L73-80 |  | function walk(dir: string, out: string[] = []): string[] { |
| declaredIndexOf@83 | function | L83-87 | 目录名（如 15至19）只是压缩包顺序号，原样带进报告供人工核对 | function declaredIndexOf(root: string, file: string): string { |
| hasHeading@89 | function | L89-91 |  | function hasHeading(body: string, heading: string): boolean { |
| fieldsFromAttachment@94 | function | L94-103 | 附件能提供的字段只有题目和表头 meta（姓名/学号一类），meta 按 ext_fields 的 label 反查路径 | function fieldsFromAttachment(parsed: ParsedAttachment, spec: DomainSp… |
| alreadyAttached@105 | function | L105-108 |  | function alreadyAttached(fm: Record<string, any>, sourceFile: string):… |
| attachDirectory@110 | function | L110-340 |  | export function attachDirectory(options: AttachOptions): AttachReport … |
