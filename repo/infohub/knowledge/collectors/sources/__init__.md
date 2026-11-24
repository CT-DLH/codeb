---
covers:
  - collector/zhihu_pipe/sources/__init__.py
title: Collector: __init__
updated: 2026-11-24
---

# 采集器：采集器注册表（`__init__.py`）

**模块**：知乎管道 → 平台采集器
**源码**：`collector/zhihu_pipe/sources/__init__.py`

## 职责
采集器注册与统一入口。

## 适用场景
- 需要调整采集器注册表的抓取逻辑、请求头、翻页或字段映射时。
- 需要确认采集器注册表适配器对外暴露的接口与数据结构时。

## 功能部件

| 部件 key | 类型 | 行号 | 作用 |
|:--|:--|:--|:--|
| `available@71` | def | L71-72 | def available() -> list[str]: |
| `site_source_names@75` | def | L75-77 | def site_source_names() -> tuple[str, ...]: |
| `is_site_source@80` | def | L80-81 | def is_site_source(name: str) -> bool: |
| `get_source@84` | def | L84-95 | def get_source(name: str) -> Source: |
| `enabled_sources@98` | def | L98-101 | def enabled_sources(names: Iterable[str] \ |
| `capability_report@104` | def | L104-138 | def capability_report() -> dict[str, dict]: |
| `body_capable_platforms@141` | def | L141-160 | def body_capable_platforms() -> tuple[set[str], dict[str, str]]: |

> 共 8 个语义块，完整清单见第4层符号索引。

## 第4层语义块索引
- `collector-zhihu_pipe-sources-__init__.py.md`: `../symbols/collector-zhihu_pipe-sources-__init__.py.md`

## 下沉指引
```
read_block(path="collector/zhihu_pipe/sources/__init__.py", key="available@71")
read_block(path="collector/zhihu_pipe/sources/__init__.py", key="site_source_names@75")
```
