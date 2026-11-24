---
covers:
  - apps/web/src/components/editor/extensions.ts
title: Semantic block index: extensions.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：extensions.ts（第4层）

**源码文件**：`apps/web/src/components/editor/extensions.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="apps/web/src/components/editor/extensions.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| FieldSpec@32 | interface | L32-37 | 就地编辑表单里的一个字段。 | interface FieldSpec { |
| buildAttrForm@49 | function | L49-126 | 构建「就地属性编辑表单」。 | function buildAttrForm( |
| buildAttrForm.gather@60 | arrow | L60-66 |  | const gather = (): Record<string, string> => { |
| buildAttrForm.submit@69 | arrow | L69-75 |  | const submit = (): void => { |
| buildAttrForm.cancel@77 | arrow | L77-81 |  | const cancel = (): void => { |
| buildAttrForm.onKeyDown@93 | arrow | L93-102 | 阻止 ProseMirror 把按键当文档操作（Enter 会切段、Esc 会失焦保存）。 | const onKeyDown = (e: KeyboardEvent): void => { |
| inlineEditable@139 | function | L139-196 | 把三个节点视图里「双击 → 就地编辑」的公共部分收拢到一处。 | function inlineEditable(opts: { |
| inlineEditable.start@164 | arrow | L164-189 |  | const start = (): void => { |
| nodeViewResult@208 | function | L208-229 | 节点视图返回值的公共部分：除了 dom / update，还必须声明 | function nodeViewResult(opts: { |
| addAttributes@239 | method | L239-247 |  | addAttributes() { |
| parseHTML@249 | method | L249-251 |  | parseHTML() { |
| renderHTML@253 | method | L253-255 |  | renderHTML({ HTMLAttributes }) { |
| addNodeView@257 | method | L257-305 |  | addNodeView() { |
| addNodeView.paint@264 | arrow | L264-273 |  | const paint = (): void => { |
| addAttributes@315 | method | L315-323 |  | addAttributes() { |
| parseHTML@325 | method | L325-327 |  | parseHTML() { |
| renderHTML@329 | method | L329-331 |  | renderHTML({ HTMLAttributes }) { |
| addNodeView@333 | method | L333-382 |  | addNodeView() { |
| addNodeView.paint@340 | arrow | L340-349 |  | const paint = (): void => { |
| addAttributes@393 | method | L393-406 |  | addAttributes() { |
| parseHTML@408 | method | L408-410 |  | parseHTML() { |
| renderHTML@412 | method | L412-414 |  | renderHTML({ HTMLAttributes }) { |
| addNodeView@416 | method | L416-465 |  | addNodeView() { |
| addNodeView.paint@423 | arrow | L423-430 |  | const paint = (): void => { |
