---
covers:
  - packages/core/src/db/connection.ts
title: Semantic block index: connection.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：connection.ts（第4层）

**源码文件**：`packages/core/src/db/connection.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="packages/core/src/db/connection.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| openDatabase@24 | function | L24-51 | 打开（或创建）数据库文件并执行幂等建表。path 为 ':memory:' 时用于测试。 | export function openDatabase(path: string): DB { |
| migrate@54 | function | L54-151 | 幂等列迁移：为老库补新列（CREATE TABLE IF NOT EXISTS 不会改已存在的表）。 | function migrate(db: DB): void { |
| migrate.hasColumn@55 | arrow | L55-58 |  | const hasColumn = (table: string, col: string): boolean => { |
| migrate.addColumn@59 | arrow | L59-61 |  | const addColumn = (table: string, col: string, decl: string): void => … |
| migrateQuestionSkeleton@165 | function | L165-188 | v19 迁移：为存量题目回填题干骨架，并在骨架规则改版时重算全库。 | function migrateQuestionSkeleton(db: DB): void { |
| setMeta@190 | function | L190-194 |  | function setMeta(db: DB, key: string, value: string): void { |
| migrateDifficultyToRate@207 | function | L207-220 | v12 迁移：难度系数从「1-5 等级」改为「0-1 的得分期望比例」。 | function migrateDifficultyToRate(db: DB): void { |
| migrateQuestionKnowledge@227 | function | L227-253 | v5 迁移：把 question.relate_knowledge_ids（JSON 数组）填充到 question_knowledge 关联表。 | function migrateQuestionKnowledge(db: DB): void { |
| migrateQuestionFields@279 | function | L279-335 | v14 迁移：题目字段归一（R23）。 | function migrateQuestionFields(db: DB): void { |
| migrateQuestionFingerprint@346 | function | L346-372 | v15 迁移：题目 content_hash 从「仅题干」升级为「整题指纹」（题干 + 选项 + 答案）。 | function migrateQuestionFingerprint(db: DB): void { |
| rawStrings@375 | function | L375-382 | 只 JSON.parse 成字符串数组，不做任何归一（用于与归一结果比对）。 | function rawStrings(json: string \| null \| undefined): string[] { |
| getDatabase@385 | function | L385-391 | 进程级单例，供 server / MCP 薄客户端共享同一连接。 | export function getDatabase(path?: string): DB { |
| closeDatabase@393 | function | L393-398 |  | export function closeDatabase(): void { |
