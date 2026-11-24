---
covers:
  - collector/zhihu_pipe/sources/site.py
title: Collector: site
updated: 2026-11-24
---

# 采集器：站点订阅（`site.py`）

**模块**：知乎管道 → 平台采集器
**源码**：`collector/zhihu_pipe/sources/site.py`

## 职责
按站点配置的结构化列页采集。

## 适用场景
- 需要调整站点订阅的抓取逻辑、请求头、翻页或字段映射时。
- 需要确认站点订阅适配器对外暴露的接口与数据结构时。

## 功能部件

| 部件 key | 类型 | 行号 | 作用 |
|:--|:--|:--|:--|
| `SiteSource@56` | class | L56-267 | class SiteSource: |
| `SiteSource.search@124` | def | L124-132 | def search(self, query: str, *, limit: int, cursor: str \ |
| `SiteSource.list_author@134` | def | L134-139 | def list_author(self, author_id: str, *, kinds: Iterable[str] \ |
| `SiteSource.fetch@141` | def | L141-150 | def fetch(self, ref: ContentRef) -> Document: |
| `SiteSource.canonicalize@227` | def | L227-251 | def canonicalize(self, url: str) -> str: |
| `SiteSource.health@253` | def | L253-267 | def health(self) -> Health: |

> 共 13 个语义块，完整清单见第4层符号索引。

## 第4层语义块索引
- `collector-zhihu_pipe-sources-site.py.md`: `../symbols/collector-zhihu_pipe-sources-site.py.md`

## 下沉指引
```
read_block(path="collector/zhihu_pipe/sources/site.py", key="SiteSource@56")
read_block(path="collector/zhihu_pipe/sources/site.py", key="SiteSource.search@124")
```
