---
covers:
  - src/core/attach.ts
  - src/core/derive.ts
  - src/core/ingest.ts
  - src/core/normalize.ts
  - src/core/parsers/course-syllabus.ts
  - src/core/parsers/docx.ts
  - src/core/parsers/generic-docx.ts
  - src/core/parsers/index.ts
  - src/core/parsers/pdf-text.ts
  - src/core/parsers/task-book.ts
  - src/core/parsers/types.ts
  - src/core/pdf.ts
  - src/core/platform-domain.ts
  - src/core/sections.ts
  - src/core/summary.ts
title: Core Domain Logic Module (Layer 3)
updated: 2026-11-24
---

# 模块：核心领域逻辑——部件细页表（第3层）

**项目**：infohub
**源码文件**：`src/core/attach.ts`、`src/core/derive.ts`、`src/core/ingest.ts`、`src/core/normalize.ts`、`src/core/parsers/course-syllabus.ts`、`src/core/parsers/docx.ts`、`src/core/parsers/generic-docx.ts`、`src/core/parsers/index.ts`、`src/core/parsers/pdf-text.ts`、`src/core/parsers/task-book.ts`、`src/core/parsers/types.ts`、`src/core/pdf.ts`、`src/core/platform-domain.ts`、`src/core/sections.ts`、`src/core/summary.ts`
**第4层语义块索引**：
- `src-core-attach.ts`: `../symbols/src-core-attach.ts.md`
- `src-core-derive.ts`: `../symbols/src-core-derive.ts.md`
- `src-core-ingest.ts`: `../symbols/src-core-ingest.ts.md`
- `src-core-normalize.ts`: `../symbols/src-core-normalize.ts.md`
- `src-core-parsers-course-syllabus.ts`: `../symbols/src-core-parsers-course-syllabus.ts.md`
- `src-core-parsers-docx.ts`: `../symbols/src-core-parsers-docx.ts.md`
- `src-core-parsers-generic-docx.ts`: `../symbols/src-core-parsers-generic-docx.ts.md`
- `src-core-parsers-index.ts`: `../symbols/src-core-parsers-index.ts.md`
- `src-core-parsers-pdf-text.ts`: `../symbols/src-core-parsers-pdf-text.ts.md`
- `src-core-parsers-task-book.ts`: `../symbols/src-core-parsers-task-book.ts.md`
- `src-core-parsers-types.ts`: `../symbols/src-core-parsers-types.ts.md`
- `src-core-pdf.ts`: `../symbols/src-core-pdf.ts.md`
- `src-core-platform-domain.ts`: `../symbols/src-core-platform-domain.ts.md`
- `src-core-sections.ts`: `../symbols/src-core-sections.ts.md`
- `src-core-summary.ts`: `../symbols/src-core-summary.ts.md`
**写范围**：src/core/**
**验证命令**：`powershell -NoProfile -ExecutionPolicy Bypass -File _kbwork/run_regression.ps1`

## 职责
卡片领域模型的核心逻辑：导入、归一化、解析器、PDF 文本提取、章节与摘要。

## 适用场景
- 需要定位或修改该模块内的源码部件时，先在此页选中部件，再下沉到第4层。
- 需要确认某个文件的语义块清单与行号时，打开对应 `symbols/` 页。

## 功能部件

| 部件 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| `AttachOptions@21` | interface | L21-32 |  | export interface AttachOptions { |
| `AttachDetail@36` | interface | L36-46 |  | export interface AttachDetail { |
| `AttachReport@48` | interface | L48-69 |  | export interface AttachReport { |
| `walk@73` | function | L73-80 |  | function walk(dir: string, out: string[] = []): string[] { |
| `DeriveSkipped@17` | interface | L17-21 |  | export interface DeriveSkipped { |
| `DeriveOutcome@23` | interface | L23-28 |  | export interface DeriveOutcome { |
| `deriveRules@31` | function | L31-44 | 递归收集领域包里声明了 derive 的字段（含 object 子字段与数组 item） | export function deriveRules(spec: DomainSpec): Array<{ path:… |
| `deriveRules.walk@33` | arrow | L33-40 |  | const walk = (fields: Record<string, FieldSpec>, prefix: str… |
| `Issue@52` | interface | L52-58 |  | export interface Issue { |
| `toIssues@61` | function | L61-73 | Zod 错误 → 可直接 JSON 解析的 issues（替代文本拼接） | export function toIssues(err: ZodError): Issue[] { |
| `ParsedFile@79` | interface | L79-87 |  | export interface ParsedFile { |
| `detectFormat@89` | function | L89-99 |  | export function detectFormat(filePath: string): TableFormat … |
| `asText@7` | function | L7-9 | 录入通道的统一归一化规则。 | export function asText(value: unknown): string { |
| `asList@11` | function | L11-13 |  | export function asList(value: unknown): string[] { |
| `nonEmpty@15` | function | L15-17 |  | export function nonEmpty(value: unknown): boolean { |
| `toHalfWidth@20` | function | L20-24 | 全角转半角（含全角空格），中文表格里最常见的噪声来源 | export function toHalfWidth(input: string): string { |
| `escapeRe@32` | arrow | L32-32 |  | const escapeRe = (s: string) => s.replace(/[.*+?^${}()\ |
| `clean@49` | arrow | L49-53 |  | const clean = (value: string): string => |
| `squeezeNumber@55` | function | L55-58 |  | function squeezeNumber(value: string): string { |
| `readLabels@61` | function | L61-84 | 一行里可能挤着多个标签（课程学时：32 讲课学时：24 实验学时：8） | function readLabels(line: string, into: Record<string, strin… |
| `DocxText@9` | interface | L9-16 |  | export interface DocxText { |
| `unescapeXml@18` | arrow | L18-19 |  | const unescapeXml = (s: string): string => |
| `collectText@22` | function | L22-41 | 一个 XML 片段（单元格或段落外部）内的全部 w:t，按 w:p 分组后拼回文本 | function collectText(fragment: string): string { |
| `readDocxText@43` | function | L43-64 |  | export function readDocxText(file: string): DocxText { |
| `isHeading@11` | arrow | L11-16 |  | const isHeading = (line: string): boolean => { |
| `basename@18` | function | L18-21 |  | function basename(file: string): string { |
| `parse@26` | method | L26-51 |  | parse(file, sourceFile) { |
| `isSupported@19` | function | L19-21 |  | export function isSupported(file: string): boolean { |
| `ParseOptions@23` | interface | L23-28 |  | export interface ParseOptions { |
| `parseAttachment@30` | function | L30-48 |  | export function parseAttachment(file: string, options: Parse… |
| `pdfToParagraphs@9` | function | L9-11 |  | export function pdfToParagraphs(file: string): string[] { |
| `parse@16` | method | L16-22 |  | parse(file, sourceFile): ParsedAttachment \ |
| `bare@26` | arrow | L26-26 |  | const bare = (s: string): string => stripSpace(s).replace(/[… |
| `fromTable@29` | function | L29-74 | 表格模板：题目行 → 之后每行的「标签：正文」 | function fromTable( |
| `fromParagraphs@77` | function | L77-96 | 段落模板：题目 行 → 下一行；章节名单独成行，正文是其后的段落直到下一个章节名 | function fromParagraphs(paras: string[]): { title: string; s… |
| `buildWarnings@99` | function | L99-105 | 空栏目与条目编号都要出声：前者说明任务书本身没填，后者说明模板跟主流不一致 | function buildWarnings(parsed: { sections: ParsedSection[]; … |
| `ParsedSection@7` | interface | L7-10 | 附件解析的统一产物契约。 | export interface ParsedSection { |
| `ParsedAttachment@12` | interface | L12-21 |  | export interface ParsedAttachment { |
| `AttachmentParser@23` | interface | L23-29 |  | export interface AttachmentParser { |
| `pdfText@11` | function | L11-21 |  | function pdfText(file: string, mode: PdfMode): string { |
| `pdfPages@24` | function | L24-26 | 按页切分：pdftotext 用 \f 分页，每页的字符网格缩放可能不同 | export function pdfPages(file: string, mode: PdfMode = 'layo… |
| `pdfLines@29` | function | L29-34 | 保留缩进的原始行：缩进就是列位置，去掉缩进表格就散了 | function pdfLines(file: string, mode: PdfMode = 'layout'): s… |
| `pdfParagraphs@37` | function | L37-39 | 去掉首尾空白的紧凑行，供章节/标签类解析用 | export function pdfParagraphs(file: string): string[] { |
| `domainForPlatform@38` | function | L38-47 | 领域 → 该领域唯一可用于取回本轮行的平台集合（反向索引）。 | export function domainForPlatform(platform: string): string … |
| `knownPlatforms@50` | function | L50-52 | 已知平台清单（报错信息与预演报告用）。 | export function knownPlatforms(): string[] { |
| `H2@10` | arrow | L10-10 | 但「上游派生内容」（AI 摘要、采集信息）属于投影，不是人工修订——它们该跟着采集库变。 那条通道由 _replace_sections 显… | const H2 = (section: string) => `## ${section}`; |
| `sectionRange@13` | function | L13-25 | 小节标题行的位置范围 [start, end)：start 是标题行，end 是下一个一/二级标题 | function sectionRange(lines: string[], section: string): [nu… |
| `appendToSection@27` | function | L27-39 |  | export function appendToSection(body: string, section: strin… |
| `extractSection@42` | function | L42-48 | 取某一小节的正文（不含标题行）。没有该小节时返回 undefined，调用方据此判断「上游没给这一节」 | export function extractSection(body: string, section: string… |
| `SummaryProjection@10` | interface | L10-19 |  | export interface SummaryProjection { |
| `projectSummary@23` | function | L23-44 |  | export function projectSummary(raw: string): SummaryProjecti… |

> 本模块共 **152** 个语义块，本页只列核心部件；完整清单见各 `symbols/` 页。

## 下沉指引
```
选中部件 → 打开第4层 symbols 文件 → read_block(path="src/core/attach.ts", key="AttachOptions@21")
选中部件 → 打开第4层 symbols 文件 → read_block(path="src/core/derive.ts", key="DeriveSkipped@17")
选中部件 → 打开第4层 symbols 文件 → read_block(path="src/core/ingest.ts", key="Issue@52")
```
