---
covers:
  - apps/server/src/web.ts
title: Semantic block index: web.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：web.ts（第4层）

**源码文件**：`apps/server/src/web.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="apps/server/src/web.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| WebOptions@22 | interface | L22-25 |  | export interface WebOptions { |
| registerWeb@32 | function | L32-70 | 注册 Web 静态托管 + SPA 兜底。 | export function registerWeb(app: FastifyInstance, opts: WebOptions): v… |
| registerWeb.setHeaders@46 | method | L46-53 | 带 hash 的产物（/assets/index-xxxx.js）可长缓存；index.html 必须每次回源， 否则用户改完部署后浏览器仍加载旧入口、引用已删除的资源。 | setHeaders(reply, filePath) { |
