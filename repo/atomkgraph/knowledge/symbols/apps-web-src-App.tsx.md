---
covers:
  - apps/web/src/App.tsx
title: Semantic block index: App.tsx (layer 4)
updated: 2026-11-24
---

# 语义块索引：App.tsx（第4层）

**源码文件**：`apps/web/src/App.tsx`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="apps/web/src/App.tsx", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| focusEditor@46 | function | L46-54 | 滚动并聚焦正文编辑器。 | function focusEditor(): void { |
| UiState@58 | interface | L58-77 |  | interface UiState { |
| loadUi@78 | function | L78-84 |  | function loadUi(): UiState { |
| saveUi@85 | function | L85-91 |  | function saveUi(s: UiState): void { |
| readSession@102 | function | L102-136 | 恢复上次会话：优先 URL 查询参数（可分享、刷新最可靠），否则回退到 localStorage。 | function readSession(): { mode?: ViewMode; selectedId?: string \| null… |
| fmtTime@139 | function | L139-145 | 时间展示（YYYY-MM-DD HH:mm）。 | function fmtTime(iso: string \| null): string { |
| fmtTime.p@143 | arrow | L143-143 |  | const p = (n: number) => String(n).padStart(2, '0') |
| findInTree@148 | function | L148-163 | 递归在导航树里按 id 找节点（返回「命中节点到根」的祖先链，用于自动展开侧栏）。 | function findInTree( |
| collectTitles@171 | function | L171-180 | 拍平导航树的 id → 标题映射。 | function collectTitles( |
| App@182 | function | L182-1063 |  | export function App() { |
| App.t@217 | arrow | L217-217 |  | const t = (key: string, params?: Record<string, string>) => translate(… |
| App.changeLang@220 | arrow | L220-223 |  | const changeLang = (next: Lang) => { |
| App.onAnswer@467 | arrow | L467-476 |  | const onAnswer = async (grade: number) => { |
| App.startDelete@510 | arrow | L510-536 | 为什么不直接弹「确定删除吗」：删中间层会把子节点上提到祖父，这个副作用 用户看不见就无法决策。先把真实影响面取回来渲染成弹窗，再让用户决定。 | const startDelete = async () => { |
| App.confirmDelete@555 | arrow | L555-588 | selected === null 时刻意保留旧 id（防刷新瞬间误清），所以这里不主动清， 下次刷新就会白跑一次 api.detail(已删id)； 3. reload() 刷新 | const confirmDelete = async () => { |
| App.onKey@593 | arrow | L593-595 |  | const onKey = (e: KeyboardEvent) => { |
