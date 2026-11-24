---
covers:
  - collector/zhihu_pipe/sources/zhihu.py
title: Collector: zhihu
updated: 2026-11-24
---

# 采集器：知乎（`zhihu.py`）

**模块**：知乎管道 → 平台采集器
**源码**：`collector/zhihu_pipe/sources/zhihu.py`

## 职责
知乎内容采集：热榜、问题、回答与作者主页。

## 适用场景
- 需要调整知乎的抓取逻辑、请求头、翻页或字段映射时。
- 需要确认知乎适配器对外暴露的接口与数据结构时。

## 功能部件

| 部件 key | 类型 | 行号 | 作用 |
|:--|:--|:--|:--|
| `ZhihuSource@21` | class | L21-116 | class ZhihuSource: |
| `ZhihuSource.search@72` | def | L72-79 | def search(self, query: str, *, limit: int = 30, cursor: str \ |
| `ZhihuSource.list_author@81` | def | L81-91 | def list_author(self, author_id: str, *, kinds: Iterable[str] \ |
| `ZhihuSource.fetch@93` | def | L93-103 | def fetch(self, ref: ContentRef) -> Document: |
| `ZhihuSource.canonicalize@105` | def | L105-107 | def canonicalize(self, url: str) -> str: |
| `ZhihuSource.health@109` | def | L109-116 | def health(self) -> Health: |

> 共 8 个语义块，完整清单见第4层符号索引。

## 第4层语义块索引
- `collector-zhihu_pipe-sources-zhihu.py.md`: `../symbols/collector-zhihu_pipe-sources-zhihu.py.md`

## 下沉指引
```
read_block(path="collector/zhihu_pipe/sources/zhihu.py", key="ZhihuSource@21")
read_block(path="collector/zhihu_pipe/sources/zhihu.py", key="ZhihuSource.search@72")
```
