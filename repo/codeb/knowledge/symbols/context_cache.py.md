---
covers:
  - distill/agent/context_cache.py
title: context_cache.py semantic block index (layer 4)
updated: 2026-11-22
---

# 语义块索引：context_cache.py（第4层）

**源码文件**：`distill/agent/context_cache.py`（解析器=ast，6 个语义块）
**第5层完整正文**：`read_block(path="distill/agent/context_cache.py", key="<name>@<line>")`

| 语义块 key | 类型 | 行号 | 作用 |
|:--|:--|:--|:--|
| `ContextCache@20` | class | L20-81 | 上下文缓存类（换页+sidecar） |
| `ContextCache.__init__@29` | def | L29-34 | 初始化（keep_recent/max_chars） |
| `ContextCache._key@36` | def | L36-38 | 由消息生成缓存 key |
| `ContextCache.filter@40` | def | L40-73 | 过滤换页，仅替换 function_call_output.output |
| `ContextCache.get@75` | def | L75-76 | 从 sidecar 取回被换出正文 |
| `ContextCache.stats@78` | def | L78-81 | 换页统计 |

**关键约束**：`filter` 只替换 `function_call_output["output"]`，**绝不改 `call_id`/`type`**。墓碑文案与 `cache_get` 工具配套。
