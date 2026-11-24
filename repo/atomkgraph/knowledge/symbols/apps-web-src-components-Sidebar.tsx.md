---
covers:
  - apps/web/src/components/Sidebar.tsx
title: Semantic block index: Sidebar.tsx (layer 4)
updated: 2026-11-24
---

# 语义块索引：Sidebar.tsx（第4层）

**源码文件**：`apps/web/src/components/Sidebar.tsx`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="apps/web/src/components/Sidebar.tsx", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| OrphanItem@27 | interface | L27-30 | 未归档的孤立知识点（R10「未归档岛」），附标签名。 | export interface OrphanItem { |
| getInitialCollapsed@46 | function | L46-52 | 读取折叠状态。 | export function getInitialCollapsed(): boolean { |
| getInitialExpanded@57 | function | L57-67 | 读取树展开集合（持久化）。返回 null = 无记录，用默认（前两层展开）。 | function getInitialExpanded(): Set<string> \| null { |
| defaultExpandedIds@70 | function | L70-81 | 默认展开集合：根节点与前两层。 | function defaultExpandedIds(tree: KnowledgeNavNode[]): Set<string> { |
| defaultExpandedIds.walk@72 | arrow | L72-78 |  | const walk = (nodes: KnowledgeNavNode[], depth: number): void => { |
| TreeNodeView@109 | function | L109-276 | 递归渲染树节点，可展开/收起。展开状态由父级统一持有并持久化。 | function TreeNodeView({ |
| TreeNodeView.contains@148 | arrow | L148-149 |  | const contains = (n: KnowledgeNavNode): boolean => |
| TreeNodeView.handleDragStart@163 | arrow | L163-171 | 不同父节点直接忽略——否则拖到别的分类下会变成「移动父节点」， 那是 reparent 的语义，不属于手动排序。 鼠标落在目标上半区 → 插到它之前（before_id），下半区 → 之后（after | const handleDragStart = (e: DragEvent) => { |
| TreeNodeView.handleDragEnd@173 | arrow | L173-177 |  | const handleDragEnd = () => { |
| TreeNodeView.handleDragOver@179 | arrow | L179-191 |  | const handleDragOver = (e: DragEvent) => { |
| TreeNodeView.handleDragLeave@193 | arrow | L193-193 |  | const handleDragLeave = () => setDropSide(null) |
| TreeNodeView.handleDrop@195 | arrow | L195-212 |  | const handleDrop = (e: DragEvent) => { |
| scrollIntoViewOnMount@279 | function | L279-284 | 恢复会话时把选中项滚进可视区（只在挂载后跑一次，避免打断用户滚动）。 | function scrollIntoViewOnMount(el: HTMLElement \| null): void { |
| SidebarProps@286 | interface | L286-309 |  | export interface SidebarProps { |
| getInitialWidth@316 | function | L316-324 | 读取侧栏宽度（含范围约束）。 | export function getInitialWidth(): number { |
| Sidebar@326 | function | L326-526 |  | export function Sidebar(props: SidebarProps) { |
| Sidebar.onResizeStart@382 | arrow | L382-396 | 拖拽调宽 | const onResizeStart = (e: ReactMouseEvent) => { |
| Sidebar.onMove@386 | arrow | L386-389 |  | const onMove = (ev: MouseEvent) => { |
| Sidebar.onUp@390 | arrow | L390-393 |  | const onUp = () => { |
