---
covers:
  - console/tasks.ts
title: Semantic block index: tasks.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：tasks.ts（第4层）

**源码文件**：`console/tasks.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="console/tasks.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| TaskRunOptions@20 | interface | L20-26 |  | export interface TaskRunOptions { |
| TaskDef@28 | interface | L28-45 |  | export interface TaskDef { |
| IdleSettings@47 | interface | L47-53 |  | export interface IdleSettings { |
| TaskProbe@55 | interface | L55-60 |  | export interface TaskProbe { |
| TaskView@62 | interface | L62-75 |  | export interface TaskView { |
| clampInt@119 | function | L119-123 |  | function clampInt(value: number, min: number, max: number): number { |
| taskDef@125 | function | L125-129 |  | export function taskDef(id: string): TaskDef { |
| readSettings@133 | function | L133-146 |  | export function readSettings(): IdleSettings { |
| writeSettings@148 | function | L148-158 |  | export function writeSettings(next: Partial<IdleSettings>): IdleSettin… |
| runDryRun@162 | function | L162-180 |  | function runDryRun(def: TaskDef, bin: Bin): Promise<TaskProbe> { |
| firstReason@183 | function | L183-189 | 解释器缺哪个包就报哪一行——只写「探测失败」四个字对排查毫无帮助 | function firstReason(text: string): string { |
| resolveTaskRunner@196 | function | L196-217 | 选解释器的判据是「这个任务的 --dry-run 真跑得起来」，不是文件在不在—— | export async function resolveTaskRunner(task: TaskId, force = false): … |
| activeTaskJob@221 | function | L221-223 |  | export function activeTaskJob(task: TaskId): JobMeta \| null { |
| startTask@225 | function | L225-246 |  | export function startTask(task: TaskId, opts: TaskRunOptions & { timeo… |
| llmHolder@249 | function | L249-262 | 心跳过期就不算——崩掉的采集不该永久挡住空闲任务 | export function llmHolder(): { kind: string; note: string; age_s: numb… |
| taskStatus@264 | function | L264-284 |  | export async function taskStatus(force = false): Promise<TaskView[]> { |
| IdleApply@288 | interface | L288-292 |  | export interface IdleApply { |
| applyIdleSettings@298 | function | L298-332 | 保存设置并把常驻任务起停到位。 | export async function applyIdleSettings(patch: Partial<IdleSettings>):… |
| resumeIdleOnBoot@335 | function | L335-338 | 控制台启动时按上次的设置恢复空闲任务——「启动后 LLM 空闲就去总结论文」就落在这里 | export async function resumeIdleOnBoot(): Promise<IdleApply \| null> { |
