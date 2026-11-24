---
covers:
  - scripts/verify-md-parity.mjs
title: Semantic block index: verify-md-parity.mjs (layer 4)
updated: 2026-11-24
---

# 语义块索引：verify-md-parity.mjs（第4层）

**源码文件**：`scripts/verify-md-parity.mjs`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="scripts/verify-md-parity.mjs", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| check@40 | function | L40-48 |  | function check(cond, msg, detail = '') { |
| j@49 | arrow | L49-49 |  | const j = (v) => JSON.stringify(v) |
| hasKatexError@52 | function | L52-54 | 渲染结果里有没有 katex 的报错（行内是 .katex-error，块级只是染红）。 | function hasKatexError(html) { |
| countRenderedFormulas@57 | function | L57-59 | 渲染结果里有没有成功渲染出来的公式（class="katex" 是每个公式的根 span）。 | function countRenderedFormulas(html) { |
| countAttemptedFormulas@68 | function | L68-70 | 「尝试渲染的公式」数量：成功的 class="katex" + 行内报错的 class="katex-error"。 | function countAttemptedFormulas(html) { |
| render@72 | function | L72-84 |  | function render(src) { |
