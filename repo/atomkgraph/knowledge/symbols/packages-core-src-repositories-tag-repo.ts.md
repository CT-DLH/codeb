---
covers:
  - packages/core/src/repositories/tag-repo.ts
title: Semantic block index: tag-repo.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：tag-repo.ts（第4层）

**源码文件**：`packages/core/src/repositories/tag-repo.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="packages/core/src/repositories/tag-repo.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| TagRow@8 | interface | L8-16 |  | interface TagRow { |
| rowToTag@18 | function | L18-25 |  | function rowToTag(r: TagRow): Tag { |
| CreateTagInput@27 | interface | L27-32 |  | export interface CreateTagInput { |
| TagRepository@36 | class | L36-130 |  | export class TagRepository { |
| TagRepository.create@39 | method | L39-59 |  | create(input: CreateTagInput): Tag { |
| TagRepository.findById@61 | method | L61-64 |  | findById(id: string): Tag \| null { |
| TagRepository.findByName@67 | method | L67-74 | 按名称精确查找（导入去重用）。 | findByName(name: string, parentId: string \| null): Tag \| null { |
| TagRepository.findChildren@76 | method | L76-83 |  | findChildren(parentId: string \| null): Tag[] { |
| TagRepository.findAll@85 | method | L85-88 |  | findAll(): Tag[] { |
| TagRepository.findAncestors@91 | method | L91-101 | 从某标签向上回溯到根的完整路径（用于世界地图面包屑）。 | findAncestors(id: string): Tag[] { |
| TagRepository.update@103 | method | L103-120 |  | update(id: string, patch: UpdateTagInput): Tag \| null { |
| TagRepository.delete@123 | method | L123-129 | 硬删除标签；其直接子标签上提为顶级，避免悬挂引用。 | delete(id: string): boolean { |
