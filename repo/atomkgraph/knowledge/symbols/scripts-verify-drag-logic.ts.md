---
covers:
  - scripts/verify-drag-logic.ts
title: Semantic block index: verify-drag-logic.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：verify-drag-logic.ts（第4层）

**源码文件**：`scripts/verify-drag-logic.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="scripts/verify-drag-logic.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| ok@4 | arrow | L4-6 |  | const ok = (c: boolean, label: string) => { |
| canDrop@9 | function | L9-16 | 复刻组件里的判断：同 parent_id 才允许，且不能是自己。 | function canDrop( |
| dropSide@19 | function | L19-21 | 复刻「鼠标在上半区 = before」的判定。 | function dropSide(clientY: number, rectTop: number, height: number): '… |
| body@52 | arrow | L52-53 |  | const body = (side: 'before' \| 'after', targetId: string) => |
