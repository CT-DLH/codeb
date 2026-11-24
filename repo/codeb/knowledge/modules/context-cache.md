---
covers:
  - distill/agent/context_cache.py
title: Context cache - component table (layer 3)
updated: 2026-11-22
---

# 模块：上下文缓存（context_cache.py）——部件细页表（第3层）

**项目**：codeb
**源码文件**：`distill/agent/context_cache.py`（解析器=ast，6 个语义块）
**第4层语义块索引**：[context_cache.py](../symbols/context_cache.py.md)
**写范围**：`distill/agent/context_cache.py`
**验证命令**：`& "_kbwork\agvenv\Scripts\python.exe" -X utf8 "_kbwork/test_context_cache.py"`

## 职责
实现上下文换页层：老工具结果（`function_call_output`）被换出上下文，正文留在 sidecar，用墓碑占位。通过 `RunConfig.call_model_input_filter` 注入过滤，只替换 `output` 字段，**绝不改 `call_id`/`type`**。被换出内容用 `cache_get(key)` 取回。

## 适用场景
- 改换页策略：`keep_recent`/`max_chars` 阈值、换出与取回逻辑。
- `call_model_input_filter` 行为异常（如 `CallModelData` 取字段报错）时查本模块。
- 确认墓碑文案与 `cache_get` 工具的配套。

## 功能部件

| 部件 key | 类型 | 行号 | 作用 |
|:--|:--|:--|:--|
| `ContextCache@20` | class | L20-81 | 上下文缓存类（换页+sidecar） |
| `ContextCache.__init__@29` | def | L29-34 | 初始化（keep_recent/max_chars） |
| `ContextCache._key@36` | def | L36-38 | 由消息生成缓存 key |
| `ContextCache.filter@40` | def | L40-73 | 过滤换页，仅替换 function_call_output.output |
| `ContextCache.get@75` | def | L75-76 | 从 sidecar 取回被换出正文 |
| `ContextCache.stats@78` | def | L78-81 | 换页统计 |

## 测试文件
- `_kbwork/test_context_cache.py`（15/0）
- `_kbwork/test_cache_e2e.py`（4/0，真实 LLM）
- `_kbwork/test_cache_get_e2e.py`（4/0，真实 LLM，序列含 cache_get）

## 下沉指引
```
选中部件 → 打开第4层 context_cache.py.md → read_block(path="distill/agent/context_cache.py", key="ContextCache.filter@40")
```
