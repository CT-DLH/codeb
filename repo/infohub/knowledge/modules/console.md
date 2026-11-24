---
covers:
  - console/collector-state.ts
  - console/db.ts
  - console/jobs.ts
  - console/public/console.js
  - console/server.ts
  - console/tasks.ts
title: Console Module (Layer 3)
updated: 2026-11-24
---

# 模块：控制台——部件细页表（第3层）

**项目**：infohub
**源码文件**：`console/collector-state.ts`、`console/db.ts`、`console/jobs.ts`、`console/public/console.js`、`console/server.ts`、`console/tasks.ts`
**第4层语义块索引**：
- `console-collector-state.ts`: `../symbols/console-collector-state.ts.md`
- `console-db.ts`: `../symbols/console-db.ts.md`
- `console-jobs.ts`: `../symbols/console-jobs.ts.md`
- `console-public-console.js`: `../symbols/console-public-console.js.md`
- `console-server.ts`: `../symbols/console-server.ts.md`
- `console-tasks.ts`: `../symbols/console-tasks.ts.md`
**写范围**：console/**
**验证命令**：`powershell -NoProfile -ExecutionPolicy Bypass -File _kbwork/run_regression.ps1`

## 职责
采集控制台与运维页面：采集任务状态、数据库与任务调度的 Web 控制台。

## 适用场景
- 需要定位或修改该模块内的源码部件时，先在此页选中部件，再下沉到第4层。
- 需要确认某个文件的语义块清单与行号时，打开对应 `symbols/` 页。

## 功能部件

| 部件 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| `readJson@9` | arrow | L9-15 |  | const readJson = (path: string): Record<string, unknown> \ |
| `meta@17` | arrow | L17-24 |  | const meta = (path: string): { exists: boolean; mtime: strin… |
| `Progress@40` | interface | L40-53 |  | export interface Progress { |
| `collectorState@55` | function | L55-129 |  | export function collectorState(): { |
| `db@18` | function | L18-44 |  | function db(): DatabaseSync \ |
| `query@47` | function | L47-51 | 长跑写库时查询可能 BUSY：调用方拿到 error 后提示刷新，而不是把服务打挂 | function query<T>(sql: string, params: Array<string \ |
| `queryOne@53` | function | L53-55 |  | function queryOne<T>(sql: string, params: Array<string \ |
| `epochToIso@57` | arrow | L57-62 |  | const epochToIso = (value: unknown): string => { |
| `JobMeta@27` | interface | L27-43 |  | export interface JobMeta { |
| `LogLine@45` | interface | L45-50 |  | export interface LogLine { |
| `JobSpec@52` | interface | L52-62 |  | export interface JobSpec { |
| `siteJobSpec@70` | function | L70-98 | 站点采集任务（裁决 7）：按 spec 路径触发 collect_site.py，不带 --source。 | export function siteJobSpec(opts: { |
| `$@4` | arrow | L4-4 |  | const $ = (selector) => document.querySelector(selector); |
| `$$@5` | arrow | L5-5 |  | const $$ = (selector) => Array.from(document.querySelectorAl… |
| `esc@38` | arrow | L38-39 |  | const esc = (value) => |
| `fmtTime@41` | arrow | L41-45 |  | const fmtTime = (iso) => { |
| `HttpError@57` | class | L57-65 |  | class HttpError extends Error { |
| `TaskRunOptions@20` | interface | L20-26 |  | export interface TaskRunOptions { |
| `TaskDef@28` | interface | L28-45 |  | export interface TaskDef { |
| `IdleSettings@47` | interface | L47-53 |  | export interface IdleSettings { |
| `TaskProbe@55` | interface | L55-60 |  | export interface TaskProbe { |

> 本模块共 **148** 个语义块，本页只列核心部件；完整清单见各 `symbols/` 页。

## 下沉指引
```
选中部件 → 打开第4层 symbols 文件 → read_block(path="console/collector-state.ts", key="readJson@9")
选中部件 → 打开第4层 symbols 文件 → read_block(path="console/db.ts", key="db@18")
选中部件 → 打开第4层 symbols 文件 → read_block(path="console/jobs.ts", key="JobMeta@27")
```
