---
covers:
  - collector/zhihu_pipe/sources/bilibili.py
title: Collector: bilibili
updated: 2026-11-24
---

# 采集器：B站（`bilibili.py`）

**模块**：知乎管道 → 平台采集器
**源码**：`collector/zhihu_pipe/sources/bilibili.py`

## 职责
B 站视频与 UP 主内容采集。

## 适用场景
- 需要调整B站的抓取逻辑、请求头、翻页或字段映射时。
- 需要确认B站适配器对外暴露的接口与数据结构时。

## 功能部件

| 部件 key | 类型 | 行号 | 作用 |
|:--|:--|:--|:--|
| `RiskControl@70` | class | L70-74 | class RiskControl(QuotaExceeded): |
| `BiliSource@215` | class | L215-691 | class BiliSource: |
| `BiliSource.set_min_interval@265` | def | L265-272 | def set_min_interval(self, seconds: float) -> None: |
| `BiliSource.search@405` | def | L405-420 | def search(self, query: str, *, limit: int = 30, cursor: str \ |
| `BiliSource.list_author@422` | def | L422-451 | def list_author(self, author_id: str, *, kinds: Iterable[str] \ |
| `BiliSource.fetch@453` | def | L453-474 | def fetch(self, ref: ContentRef) -> Document: |
| `BiliSource.fetch_audience@476` | def | L476-574 | def fetch_audience(self, ref: ContentRef, *, max_comment_pages: … |
| `BiliSource.is_zh@623` | def | L623-625 | def is_zh(t: dict) -> bool: |

> 共 32 个语义块，完整清单见第4层符号索引。

## 第4层语义块索引
- `collector-zhihu_pipe-sources-bilibili.py.md`: `../symbols/collector-zhihu_pipe-sources-bilibili.py.md`

## 下沉指引
```
read_block(path="collector/zhihu_pipe/sources/bilibili.py", key="RiskControl@70")
read_block(path="collector/zhihu_pipe/sources/bilibili.py", key="BiliSource@215")
```
