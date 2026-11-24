---
covers:
  - console/server.ts
title: Semantic block index: server.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：server.ts（第4层）

**源码文件**：`console/server.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="console/server.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| HttpError@57 | class | L57-65 |  | class HttpError extends Error { |
| text@67 | arrow | L67-67 |  | const text = (value: unknown): string => (typeof value === 'string' ? … |
| quote@68 | arrow | L68-68 |  | const quote = (arg: string): string => (/[\s"]/.test(arg) ? `"${arg}"`… |
| displayCommand@69 | arrow | L69-69 |  | const displayCommand = (bin: string, argv: string[]): string => [bin, … |
| intIn@71 | arrow | L71-76 |  | const intIn = (value: unknown, name: string, min: number, max: number)… |
| RunRequest@78 | interface | L78-94 |  | interface RunRequest { |
| buildRun@100 | function | L100-219 | 参数白名单：控制台只拼 argv，不接受自由命令、不接受 shell | function buildRun(body: Record<string, unknown>, forStart: boolean): R… |
| preflight@221 | function | L221-266 |  | async function preflight(body: Record<string, unknown>): Promise<Recor… |
| startRun@268 | function | L268-311 |  | async function startRun(body: Record<string, unknown>): Promise<Record… |
| taskOptions@314 | function | L314-326 | 控制台请求体 → 任务参数：只认这几个白名单字段，取值范围由 tasks.ts 再收一遍 | function taskOptions(body: Record<string, unknown>): TaskRunOptions { |
| taskOptions.number@315 | arrow | L315-318 |  | const number = (value: unknown): number \| undefined => { |
| taskUnusableMessage@329 | function | L329-332 | 任务跑不起来的文案：把「哪个候选为什么不行」原样交给页面，别只说「失败」 | function taskUnusableMessage(id: TaskId, rejected: string[]): string { |
| SiteRequest@336 | interface | L336-342 |  | interface SiteRequest { |
| chooseSitePython@345 | function | L345-350 | 站点采集脚本只依赖本地 site_crawl 包，不复用知乎源的 get_source 探测 | function chooseSitePython(): { bin: string; from: string } { |
| buildSite@353 | function | L353-375 | 参数白名单 + 本地 spec 体检：路径写错 / YAML 坏掉先挡掉，不白起一个采集进程 | function buildSite(body: Record<string, unknown>): SiteRequest { |
| sitePreflight@378 | function | L378-400 | 对应 MCP collect_site 的 --check：只校验不发请求、不联网、不写盘 | function sitePreflight(body: Record<string, unknown>): Record<string, … |
| startSiteRun@402 | function | L402-420 |  | function startSiteRun(body: Record<string, unknown>): Record<string, u… |
| startExport@422 | function | L422-439 |  | function startExport(): Record<string, unknown> { |
| fileStat@441 | function | L441-449 |  | function fileStat(path: string): { path: string; exists: boolean; size… |
| overviewPayload@451 | function | L451-471 |  | function overviewPayload(): Record<string, unknown> { |
| hostAllowed@475 | arrow | L475-478 |  | const hostAllowed = (req: IncomingMessage): boolean => { |
| sameToken@480 | arrow | L480-484 |  | const sameToken = (value: string): boolean => { |
| cookieToken@486 | arrow | L486-493 |  | const cookieToken = (req: IncomingMessage): string => { |
| authed@495 | arrow | L495-495 |  | const authed = (req: IncomingMessage): boolean => sameToken(cookieToke… |
| postAllowed@497 | arrow | L497-501 |  | const postAllowed = (req: IncomingMessage): boolean => { |
| json@503 | function | L503-512 |  | function json(res: ServerResponse, status: number, payload: unknown): … |
| sendText@514 | function | L514-522 |  | function sendText(res: ServerResponse, status: number, body: string, t… |
| readJsonBody@524 | function | L524-552 |  | function readJsonBody(req: IncomingMessage): Promise<Record<string, un… |
| serveIndex@556 | function | L556-569 |  | function serveIndex(res: ServerResponse): void { |
| serveStream@576 | function | L576-624 |  | function serveStream(req: IncomingMessage, res: ServerResponse, id: st… |
| serveStream.send@589 | arrow | L589-591 |  | const send = (event: string, data: unknown): void => { |
| serveStream.unsubscribe@592 | arrow | L592-592 |  | let unsubscribe = (): void => {}; |
| serveStream.cleanup@594 | arrow | L594-598 |  | const cleanup = (): void => { |
| shutdown@872 | arrow | L872-877 |  | const shutdown = (): void => { |
