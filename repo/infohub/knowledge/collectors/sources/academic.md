---
covers:
  - collector/zhihu_pipe/sources/academic.py
title: Collector: academic
updated: 2026-11-24
---

# 采集器：学术源（`academic.py`）

**模块**：知乎管道 → 平台采集器
**源码**：`collector/zhihu_pipe/sources/academic.py`

## 职责
学术来源统一适配：期刊、会议、预印本。

## 适用场景
- 需要调整学术源的抓取逻辑、请求头、翻页或字段映射时。
- 需要确认学术源适配器对外暴露的接口与数据结构时。

## 功能部件

| 部件 key | 类型 | 行号 | 作用 |
|:--|:--|:--|:--|
| `AcademicSource@96` | class | L96-230 | class AcademicSource: |
| `ArxivSource@235` | class | L235-378 | class ArxivSource(AcademicSource): |
| `S2Source@383` | class | L383-475 | class S2Source(AcademicSource): |
| `OpenAlexSource@480` | class | L480-592 | class OpenAlexSource(AcademicSource): |
| `PubmedSource@597` | class | L597-720 | class PubmedSource(AcademicSource): |
| `AcademicSource.set_min_interval@113` | def | L113-115 | def set_min_interval(self, seconds: float) -> None: |
| `AcademicSource.search@161` | def | L161-165 | def search(self, query: str, *, limit: int = 30, cursor: str \ |
| `AcademicSource.list_author@167` | def | L167-170 | def list_author(self, author_id: str, *, kinds: Iterable[str] \ |

> 共 57 个语义块，完整清单见第4层符号索引。

## 第4层语义块索引
- `collector-zhihu_pipe-sources-academic.py.md`: `../symbols/collector-zhihu_pipe-sources-academic.py.md`

## 下沉指引
```
read_block(path="collector/zhihu_pipe/sources/academic.py", key="AcademicSource@96")
read_block(path="collector/zhihu_pipe/sources/academic.py", key="ArxivSource@235")
```
