---
covers:
  - collector/zhihu_pipe/sources/cnki.py
title: Collector: cnki
updated: 2026-11-24
---

# 采集器：知网（`cnki.py`）

**模块**：知乎管道 → 平台采集器
**源码**：`collector/zhihu_pipe/sources/cnki.py`

## 职责
知网文献检索与元数据采集。

## 适用场景
- 需要调整知网的抓取逻辑、请求头、翻页或字段映射时。
- 需要确认知网适配器对外暴露的接口与数据结构时。

## 功能部件

| 部件 key | 类型 | 行号 | 作用 |
|:--|:--|:--|:--|
| `NoSearchAvailable@141` | class | L141-142 | class NoSearchAvailable(NoSearch): |
| `CnkiSource@208` | class | L208-485 | class CnkiSource(BrowserSource): |
| `CnkiSource.capabilities@245` | def | L245-254 | def capabilities(self) -> frozenset[Capability]: |
| `CnkiSource.search@289` | def | L289-312 | def search(self, query: str, *, limit: int = 20, cursor: str \ |
| `CnkiSource.parse_url@357` | def | L357-368 | def parse_url(self, url: str) -> Item \ |
| `CnkiSource.fetch@389` | def | L389-393 | def fetch(self, ref: ContentRef) -> Document: |
| `CnkiSource.canonicalize@434` | def | L434-462 | def canonicalize(self, url: str) -> str: |
| `CnkiSource.health@464` | def | L464-480 | def health(self) -> Health: |

> 共 24 个语义块，完整清单见第4层符号索引。

## 第4层语义块索引
- `collector-zhihu_pipe-sources-cnki.py.md`: `../symbols/collector-zhihu_pipe-sources-cnki.py.md`

## 下沉指引
```
read_block(path="collector/zhihu_pipe/sources/cnki.py", key="NoSearchAvailable@141")
read_block(path="collector/zhihu_pipe/sources/cnki.py", key="CnkiSource@208")
```
