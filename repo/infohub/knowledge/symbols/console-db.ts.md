---
covers:
  - console/db.ts
title: Semantic block index: db.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：db.ts（第4层）

**源码文件**：`console/db.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="console/db.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| db@18 | function | L18-44 |  | function db(): DatabaseSync \| null { |
| query@47 | function | L47-51 | 长跑写库时查询可能 BUSY：调用方拿到 error 后提示刷新，而不是把服务打挂 | function query<T>(sql: string, params: Array<string \| number> = []): … |
| queryOne@53 | function | L53-55 |  | function queryOne<T>(sql: string, params: Array<string \| number> = []… |
| epochToIso@57 | arrow | L57-62 |  | const epochToIso = (value: unknown): string => { |
| dbStatus@64 | function | L64-73 |  | export function dbStatus(): { ok: boolean; path: string; readOnly: boo… |
| Overview@75 | interface | L75-83 |  | export interface Overview { |
| overview@85 | function | L85-119 |  | export function overview(): Overview { |
| ArticleRow@121 | interface | L121-138 |  | export interface ArticleRow { |
| toArticle@143 | function | L143-162 |  | function toArticle(row: Record<string, unknown>): ArticleRow { |
| ArticleQuery@164 | interface | L164-172 |  | export interface ArticleQuery { |
| listArticles@174 | function | L174-217 |  | export function listArticles(input: ArticleQuery): { |
| articleByKey@219 | function | L219-230 |  | export function articleByKey(key: string): (ArticleRow & { summary_pat… |
| rawTextOf@236 | function | L236-247 | 正文只在 raw/ 目录里找：数据库里的 raw_path 是相对 data/ 的路径， | export function rawTextOf(key: string): { ok: boolean; text?: string; … |
