---
covers:
  - console/jobs.ts
title: Semantic block index: jobs.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：jobs.ts（第4层）

**源码文件**：`console/jobs.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="console/jobs.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| JobMeta@27 | interface | L27-43 |  | export interface JobMeta { |
| LogLine@45 | interface | L45-50 |  | export interface LogLine { |
| JobSpec@52 | interface | L52-62 |  | export interface JobSpec { |
| siteJobSpec@70 | function | L70-98 | 站点采集任务（裁决 7）：按 spec 路径触发 collect_site.py，不带 --source。 | export function siteJobSpec(opts: { |
| ActiveJob@100 | interface | L100-109 |  | interface ActiveJob { |
| now@124 | arrow | L124-124 |  | const now = (): string => new Date().toISOString(); |
| rel@125 | arrow | L125-125 |  | const rel = (path: string): string => relative(ROOT, path).split(sep).… |
| displayCommand@127 | arrow | L127-130 |  | const displayCommand = (bin: string, argv: string[]): string => { |
| quote@128 | arrow | L128-128 |  | const quote = (a: string) => (/[\s"]/.test(a) ? `"${a}"` : a); |
| loadHistory@132 | function | L132-152 |  | function loadHistory(): void { |
| appendHistory@154 | function | L154-159 |  | function appendHistory(meta: JobMeta): void { |
| emit@161 | function | L161-169 |  | function emit(id: string, ev: ListenerEvent): void { |
| pushLine@171 | function | L171-182 |  | function pushLine(job: ActiveJob, stream: LogLine['stream'], raw: stri… |
| finish@184 | function | L184-215 |  | function finish(job: ActiveJob, exitCode: number \| null, error?: stri… |
| killTree@217 | function | L217-243 |  | function killTree(job: ActiveJob, reason: string): void { |
| startJob@245 | function | L245-327 |  | export function startJob(spec: JobSpec): JobMeta { |
| cancelJob@329 | function | L329-343 |  | export function cancelJob(id: string): { ok: boolean; error?: string }… |
| foreignRuns@349 | function | L349-352 | 别的进程正在占用采集器：命令行起的 crawl_long 长跑、另一个控制台进程起的任务。 | export function foreignRuns(): ActiveRun[] { |
| activeRunSource@354 | function | L354-365 |  | export function activeRunSource(): string \| null { |
| asForeignMeta@368 | function | L368-384 | 外部进程的任务在本控制台只读：能看见、看不了它的日志、也取消不了 | function asForeignMeta(run: ActiveRun): JobMeta { |
| getJob@386 | function | L386-391 |  | export function getJob(id: string): { meta: JobMeta; buffer: LogLine[]… |
| listJobs@393 | function | L393-401 |  | export function listJobs(): { active: JobMeta[]; recent: JobMeta[] } { |
| subscribe@403 | function | L403-411 |  | export function subscribe(id: string, fn: (ev: ListenerEvent) => void)… |
| readLog@414 | function | L414-447 | 读取日志尾部：历史任务没有内存缓冲，只能从落盘日志取最后 N 行 | export function readLog(id: string, tail = 500): { ok: boolean; text?:… |
| cancelAll@449 | function | L449-462 |  | export function cancelAll(): void { |
