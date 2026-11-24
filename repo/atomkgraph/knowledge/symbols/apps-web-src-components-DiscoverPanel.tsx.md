---
covers:
  - apps/web/src/components/DiscoverPanel.tsx
title: Semantic block index: DiscoverPanel.tsx (layer 4)
updated: 2026-11-24
---

# 语义块索引：DiscoverPanel.tsx（第4层）

**源码文件**：`apps/web/src/components/DiscoverPanel.tsx`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="apps/web/src/components/DiscoverPanel.tsx", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| fmtTime@29 | arrow | L29-34 |  | const fmtTime = (iso: string): string => { |
| p@32 | arrow | L32-32 |  | const p = (n: number) => String(n).padStart(2, '0') |
| fmtAgo@37 | arrow | L37-48 |  | const fmtAgo = (iso: string): string => { |
| DiscoverPanel@50 | function | L50-241 |  | export function DiscoverPanel({ onJump }: { /** 点击卡片 → 跳到该知识点详情（树干详情视图… |
| FeedCard@245 | function | L245-284 | ---------------------------------------------------------------- 卡片组件 | function FeedCard({ item, onClick }: { item: FeedItem; onClick: () => … |
| RecallCard@286 | function | L286-315 |  | function RecallCard({ hit, onClick }: { hit: RecallHit; onClick: () =>… |
| Centered@317 | function | L317-324 |  | function Centered({ children }: { children: React.ReactNode }) { |
| Empty@326 | function | L326-333 |  | function Empty({ icon, children }: { icon: React.ReactNode; children: … |
| ErrorBox@335 | function | L335-347 |  | function ErrorBox({ msg, retry }: { msg: string; retry?: () => void })… |
