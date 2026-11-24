---
covers:
  - apps/web/src/components/Sidebar.tsx
  - apps/web/src/api.ts
title: Sidebar Drag-Sort Module — Component Table (Layer 3)
updated: 2025-08-27
---

# 模块：侧边栏拖拽排序模块——部件细页表（第3层）

**项目**：atomkgraph
**源码文件**：`Sidebar.tsx`, `api.ts`
**第4层语义块索引**：
- [`Sidebar.tsx`](../symbols/Sidebar.tsx.md)
- [`api.ts`](../symbols/api.ts.md)
**写范围**：`Sidebar.tsx`, `api.ts`（不得碰 `packages/` 与 `apps/` 源码直调）
**验证命令**：`npx tsc -p apps/web/tsconfig.json --noEmit` 或 `npx tsc -p apps/server/tsconfig.json --noEmit`

## 职责
实现侧边栏树形图的拖拽排序功能：`Sidebar.tsx` 提供树形结构、拖拽起始/结束、放置悬停、放_drop 等视图交互；`api.ts` 提供树节点数据的上传/重排接口。共同完成知识树的结构重排与持久化。

## 适用场景
- 调整树节点拖拽阈值或行为（`Sidebar.tsx`——`handleDragStart`/`handleDrop`）—— 拖拽阈值与放置逻辑变更会影响用户体验。
- 修改树结构保存或冲突检测（`api.ts`——`req`/`json`/`uploadImage`等数据请求函数）—— API 层变更需同步 `Sidebar.tsx` 的放_drop 逻辑。
- 重构初始展开/收起状态（`Sidebar.tsx`——`getInitialCollapsed`/`getInitialExpanded`）—— 状态初始化变更会影响页面加载时的树形展开情况。
- 添加/修改节点拖拽反馈（`Sidebar.tsx`——`handleDragOver`/`handleDragLeave`）—— 悬浮反馈样式变更需要配合 CSS 更新。

## 功能部件

| 部件 key | 类型 | 行号 | 作用 |
|:--|:--|:--|:--|
| OrphanItem@27 | interface | 27 | 孤立节点数据结构，用于树形填充或异常节点处理 |
| getInitialCollapsed@46 | function | 46 | 获取初始所有折叠的节点 ID 集合 |
| getInitialExpanded@57 | function | 57 | 获取初始所有展开的节点 ID 集合 |
| defaultExpandedIds@70 | function | 70 | 计算默认展开的节点集合（基于树结构） |
| TreeNodeView.handleDragStart@163 | arrow function | 163 | 拖拽操作的起始捕获，记录源节点 |
| TreeNodeView.handleDrop@195 | arrow function | 195 | 放_drop 处理，确认目标位置并提交结构变更 |
| SidebarProps@286 | interface | 286 | 侧边栏组件的 Props 类型定义 |
| Sidebar@326 | function | 326 | 侧边栏主组件，包含整体布局与拖拽容器 |
| req@217 | function | 217 | 通用请求函数，发送 API 请求 |

## 测试文件
- 项目自有的单元测试：`packages/web/src/components/__tests__/Sidebar.test.tsx`、`packages/web/src/api.test.ts` 等

## 下沉指引
```
选中部件 → 打开第4层 symbols 文件 → read_block(path="Sidebar.tsx", key="TreeNodeView.handleDragStart@163")
read_block(path="Sidebar.tsx", key="TreeNodeView.handleDrop@195")
read_block(path="api.ts", key="req@217")
```