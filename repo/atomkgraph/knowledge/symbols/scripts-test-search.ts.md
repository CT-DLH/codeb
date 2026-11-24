---
covers:
  - scripts/test-search.ts
title: Semantic block index: test-search.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：test-search.ts（第4层）

**源码文件**：`scripts/test-search.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="scripts/test-search.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| assert@15 | function | L15-20 |  | function assert(cond: unknown, msg: string): void { |
| eq@23 | function | L23-30 | 断言相等并回显实际值——只写 assert(a===b) 时失败信息看不出差在哪。 | function eq(msg: string, actual: unknown, expected: unknown): void { |
| mockEmbed@34 | arrow | L34-43 | mock embedding：字符袋直方图（32 维）。共享字符越多 → 向量越近， 用于在无 API key 时验证索引/检索逻辑（真实场景用在线 embedding 模型）。 | const mockEmbed: EmbeddingFn = async (text: string) => { |
| boom@136 | arrow | L136-138 | 5-6 embedding 失败不能先把状态记成「新鲜」——否则下次检查直接漏掉它 | const boom: EmbeddingFn = async () => { |
| dim16@162 | arrow | L162-167 | 5-9 换 embedding 模型（维度变了）后旧状态必须作废： 向量表会被重建，若状态还留着「已索引」，就会出现「看着新鲜、其实一条向量都没有」 | const dim16: EmbeddingFn = async (text: string) => { |
