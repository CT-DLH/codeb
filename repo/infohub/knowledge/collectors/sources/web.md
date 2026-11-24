---
covers:
  - collector/zhihu_pipe/sources/web.py
title: Collector: web
updated: 2026-11-24
---

# 采集器：通用网页（`web.py`）

**模块**：知乎管道 → 平台采集器
**源码**：`collector/zhihu_pipe/sources/web.py`

## 职责
任意网页正文抽取。

## 适用场景
- 需要调整通用网页的抓取逻辑、请求头、翻页或字段映射时。
- 需要确认通用网页适配器对外暴露的接口与数据结构时。

## 功能部件

| 部件 key | 类型 | 行号 | 作用 |
|:--|:--|:--|:--|
| `WebSource@230` | class | L230-645 | class WebSource: |
| `WebSource.set_min_interval@275` | def | L275-279 | def set_min_interval(self, seconds: float) -> None: |
| `WebSource.search@303` | def | L303-323 | def search(self, query: str, *, limit: int, cursor: str \ |
| `WebSource.canonicalize@540` | def | L540-552 | def canonicalize(self, url: str) -> str: |
| `WebSource.parse_url@561` | def | L561-590 | def parse_url(self, url: str) -> Item \ |
| `WebSource.fetch@592` | def | L592-618 | def fetch(self, ref: ContentRef) -> Document: |
| `WebSource.health@632` | def | L632-645 | def health(self) -> Health: |

> 共 24 个语义块，完整清单见第4层符号索引。

## 第4层语义块索引
- `collector-zhihu_pipe-sources-web.py.md`: `../symbols/collector-zhihu_pipe-sources-web.py.md`

## 下沉指引
```
read_block(path="collector/zhihu_pipe/sources/web.py", key="WebSource@230")
read_block(path="collector/zhihu_pipe/sources/web.py", key="WebSource.set_min_interval@275")
```
