---
covers:
  - apps/server/src/routes.ts
title: routes.ts semantic block index (layer 4)
updated: 2025-08-27
---

# 语义块索引：routes.ts（第4层）

**源码文件**：`apps/server/src/routes.ts`

**解析器**：`typescript` · **解析器**：`typescript` · **第5层完整正文**：`read_block(path="apps/server/src/routes.ts", key="slimOutline@83")`

| 语义块 key | 类型 | 行号 | 作用 |
|:--|:--|:--|:--|
| slimOutline@83 | function | L83-93 | function slimOutline(n: OutlineSection): unknown { |
| llmErrorReply@103 | function | L103-112 | function llmErrorReply(reply: { code: (n: number) => { send: (b: unkno… |
| RegisterRoutesOptions@114 | interface | L114-117 | export interface RegisterRoutesOptions { |
| readAssetAsDataUrl@136 | function | L136-150 | async function readAssetAsDataUrl(assetsDir: string, url: string): Pro… |
| registerRoutes@152 | function | L152-3194 | export function registerRoutes(app: FastifyInstance, db: DB, opts: Reg… |
| registerRoutes.placeholderEmbed@171 | arrow | L171-172 | const placeholderEmbed: EmbeddingFn = () => |
| registerRoutes.applyEmbedder@177 | arrow | L177-185 | const applyEmbedder = (): Embedder => { |
| registerRoutes.fn@180 | arrow | L180-180 | const fn: EmbeddingFn = (text, role) => embedder.embed(text, role) |
| registerRoutes.batch@181 | arrow | L181-181 | const batch: EmbeddingBatchFn = (texts, role) => embedder.embedBatch(t… |
| registerRoutes.injectTransport@205 | arrow | L205-221 | const injectTransport: ApiTransport = async (method, path, body) => { |
| registerRoutes.autoIndex@240 | arrow | L240-246 | const autoIndex = (ids: string \| string[]): void => { |
| registerRoutes.qAutoIndex@249 | arrow | L249-255 | const qAutoIndex = (ids: string \| string[]): void => { |
| registerRoutes.autoLink@258 | arrow | L258-262 | const autoLink = (knowledgeId: string, title: string, content: string)… |
| registerRoutes.num@351 | arrow | L351-355 | const num = (v: string \| undefined): number \| undefined => { |
| registerRoutes.num@402 | arrow | L402-406 | const num = (v: string \| undefined): number \| undefined => { |
| registerRoutes.num@444 | arrow | L444-448 | const num = (v: string \| undefined): number \| undefined => { |
| registerRoutes.resolveIngestDoc@1024 | arrow | L1024-1053 | const resolveIngestDoc = async ( |
| registerRoutes.build@1612 | arrow | L1612-1613 | const build = (parentId: string \| null): unknown[] => |
| registerRoutes.num@1835 | arrow | L1835-1839 | const num = (v: string \| undefined): number \| undefined => { |
| registerRoutes.bool@1840 | arrow | L1840-1843 | const bool = (v: string \| undefined): boolean \| undefined => { |
| registerRoutes.list@1844 | arrow | L1844-1848 | const list = (v: string \| undefined): string[] \| undefined => { |
| registerRoutes.numOrNull@2552 | arrow | L2552-2553 | const numOrNull = (v?: string): number \| null \| undefined => |
| registerRoutes.getDiagramSvc@2584 | arrow | L2584-2587 | const getDiagramSvc = (): DiagramService => { |
| registerRoutes.parseTarget@2750 | arrow | L2750-2755 | const parseTarget = (q: Record<string, unknown>): { targetType: 'knowl… |
| registerRoutes.emit@3158 | arrow | L3158-3160 | const emit = (event: unknown): void => { |
