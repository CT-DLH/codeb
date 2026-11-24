---
covers:
  - src/mcp/lib/collector-runtime.ts
title: Semantic block index: collector-runtime.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：collector-runtime.ts（第4层）

**源码文件**：`src/mcp/lib/collector-runtime.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="src/mcp/lib/collector-runtime.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| readCapabilities@29 | function | L29-78 | 源清单的唯一真值是插件注册表导出的 collector/capabilities.json（platforms 的键）。 | function readCapabilities(): { all: string[]; search: string[]; site: … |
| pythonCandidates@104 | function | L104-125 | 候选解释器。「文件在不在」不够：本机 PATH 上的 python 启动得了，但装的是另一套依赖， | export function pythonCandidates(): Bin[] { |
| pythonCandidates.push@106 | arrow | L106-109 |  | const push = (bin: string \| undefined, from: string) => { |
| probeScript@128 | arrow | L128-128 |  | const probeScript = (source: string) => `from zhihu_pipe.source import… |
| probePython@132 | function | L132-161 |  | function probePython({ bin }: Bin, source: string): { ok: boolean; rea… |
| probePython.run@136 | arrow | L136-143 |  | const run = (script: string) => |
| failureReason@167 | function | L167-173 | 失败理由要挑那句真正说清原因的话：Python 的 ModuleNotFoundError 在中间几行， | function failureReason(text: string \| undefined, fallback: string): s… |
| resolveCollectorPython@176 | function | L176-191 | 按候选顺序探测，第一个能加载该源的才算可用；全部失败时把每个候选的死因带回去 | export function resolveCollectorPython(source: string): { |
| runProbe@198 | function | L198-239 | 异步版本给控制台用：spawnSync 会把整个 HTTP 服务卡住，探测一个装错依赖的解释器 | function runProbe( |
| runProbe.done@213 | arrow | L213-218 |  | const done = (result: { status: number \| null; stdout: string; stderr… |
| probePythonAsync@243 | function | L243-271 |  | function probePythonAsync({ bin }: Bin, source: string): Promise<{ ok:… |
| resolveCollectorPythonAsync@273 | function | L273-288 |  | export async function resolveCollectorPythonAsync(source: string): Pro… |
| prerequisites@299 | function | L299-323 | 前置条件检查（只看文件，不联网）：登录态/配额这些坑必须在跑之前说清楚， | export function prerequisites(): { missing: string[]; notes: string[] … |
