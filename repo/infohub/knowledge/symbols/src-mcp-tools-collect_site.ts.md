---
covers:
  - src/mcp/tools/collect_site.ts
title: Semantic block index: collect_site.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：collect_site.ts（第4层）

**源码文件**：`src/mcp/tools/collect_site.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="src/mcp/tools/collect_site.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| fail@43 | function | L43-52 |  | function fail( |
| shown@54 | arrow | L54-54 |  | const shown = (abs: string): string => relative(ROOT, abs).split(sep).… |
| quote@55 | arrow | L55-55 |  | const quote = (arg: string): string => (/[\s"]/.test(arg) ? `"${arg}"`… |
| tail@56 | arrow | L56-56 |  | const tail = (text: string, n = 4000): string => (text.length > n ? `…… |
| inspectSpec@63 | function | L63-87 | 本地 spec 体检：真跑前先挡掉「路径写错 / YAML 坏掉」，不白起一个 Python 进程。 | function inspectSpec(abs: string): { ok: boolean; errors: string[]; su… |
| extractReport@94 | function | L94-127 | 从 stdout 里取出 --json 报告：collect_site.py 先打一堆人读的文本行， | function extractReport(stdout: string): Record<string, unknown> \| nul… |
| reportSummary@130 | function | L130-143 | 只回报告的计数与关键字段，不把整批 items 塞进 MCP 返回值 | function reportSummary(report: Record<string, unknown>): Record<string… |
| reportSummary.count@131 | arrow | L131-132 |  | const count = (key: string): number \| null => |
| choosePython@146 | function | L146-151 | 站点采集脚本只依赖本地 site_crawl 包，任何能启动的解释器都能跑；不复用知乎源的 get_source 探测 | function choosePython(): { bin: string; from: string } { |
| registerCollectSite@153 | function | L153-352 |  | export function registerCollectSite(server: McpServer): void { |
