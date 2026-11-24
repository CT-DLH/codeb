---
covers:
  - collector/zhihu_pipe/sources/crossref.py
title: Collector: crossref
updated: 2026-11-24
---

# 采集器：Crossref（`crossref.py`）

**模块**：知乎管道 → 平台采集器
**源码**：`collector/zhihu_pipe/sources/crossref.py`

## 职责
Crossref DOI 元数据与引用解析。

## 适用场景
- 需要调整Crossref的抓取逻辑、请求头、翻页或字段映射时。
- 需要确认Crossref适配器对外暴露的接口与数据结构时。

## 功能部件

| 部件 key | 类型 | 行号 | 作用 |
|:--|:--|:--|:--|
| `CrossrefSource@43` | class | L43-147 | class CrossrefSource(AcademicSource): |
| `CrossrefSource.canonicalize@135` | def | L135-138 | def canonicalize(self, url: str) -> str: |
| `CrossrefSource.health@140` | def | L140-147 | def health(self) -> Health: |

> 共 10 个语义块，完整清单见第4层符号索引。

## 第4层语义块索引
- `collector-zhihu_pipe-sources-crossref.py.md`: `../symbols/collector-zhihu_pipe-sources-crossref.py.md`

## 下沉指引
```
read_block(path="collector/zhihu_pipe/sources/crossref.py", key="CrossrefSource@43")
read_block(path="collector/zhihu_pipe/sources/crossref.py", key="CrossrefSource.canonicalize@135")
```
