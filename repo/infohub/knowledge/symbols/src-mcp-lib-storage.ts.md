---
covers:
  - src/mcp/lib/storage.ts
title: Semantic block index: storage.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：storage.ts（第4层）

**源码文件**：`src/mcp/lib/storage.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="src/mcp/lib/storage.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| domainDir@19 | function | L19-22 | domain 值 → 卡片目录（与 src/lib/server/card-store.ts 的 domainDir 同一口径）。 | export function domainDir(domain: string): string { |
| computeRevision@28 | function | L28-30 | 内容哈希（替代 Git blob SHA，零依赖、跨平台） | export function computeRevision(content: string): string { |
| stableValue@35 | function | L35-45 |  | function stableValue(value: unknown): unknown { |
| contentFingerprint@51 | function | L51-59 | 内容指纹：frontmatter（忽略 created_at / edited_at，键序无关）+ 正文。 | export function contentFingerprint(frontmatter: Record<string, any>, b… |
| CardRecord@61 | interface | L61-69 |  | export interface CardRecord { |
| walkMd@71 | function | L71-80 |  | function walkMd(dir: string, out: string[]): void { |
| listCardFiles@82 | function | L82-88 |  | export function listCardFiles(domain?: string): string[] { |
| readCardFile@90 | function | L90-108 |  | export function readCardFile(file: string): CardRecord \| null { |
| findCardFile@110 | function | L110-116 |  | export function findCardFile(cardId: string): string \| null { |
| readCard@118 | function | L118-121 |  | export function readCard(cardId: string): CardRecord \| null { |
| writeCardFile@129 | function | L129-154 | 写卡唯一入口：顺带维护 created_at / edited_at。 | export function writeCardFile(file: string, raw: string): string { |
| stringifyCard@156 | function | L156-158 |  | export function stringifyCard(frontmatter: Record<string, any>, body: … |
| moveToTrash@161 | function | L161-167 | 删除 = 移入 .trash/（可恢复、Git 忽略），不做物理抹除。card_delete / card_batch / 导入并卡共用 | export function moveToTrash(file: string, cardId: string): string { |
| StagingRecord@171 | interface | L171-177 |  | export interface StagingRecord { |
| stageUpdate@179 | function | L179-195 |  | export function stageUpdate( |
| readStaging@197 | function | L197-206 |  | export function readStaging(pendingId: string): StagingRecord \| null … |
| deleteStaging@208 | function | L208-214 |  | export function deleteStaging(pendingId: string): void { |
| ConflictRecord@218 | interface | L218-226 |  | export interface ConflictRecord { |
| createConflictRecord@228 | function | L228-240 |  | export function createConflictRecord( |
| listConflictRecords@242 | function | L242-260 |  | export function listConflictRecords(cardId?: string): ConflictRecord[]… |
| readConflictRecord@262 | function | L262-267 |  | export function readConflictRecord(conflictId: string): ConflictRecord… |
| deleteConflictRecord@269 | function | L269-279 |  | export function deleteConflictRecord(conflictId: string): boolean { |
