---
covers:
  - collector/zhihu_pipe/sources/github.py
title: Collector: github
updated: 2026-11-24
---

# 采集器：GitHub（`github.py`）

**模块**：知乎管道 → 平台采集器
**源码**：`collector/zhihu_pipe/sources/github.py`

## 职责
GitHub 仓库与项目内容采集。

## 适用场景
- 需要调整GitHub的抓取逻辑、请求头、翻页或字段映射时。
- 需要确认GitHub适配器对外暴露的接口与数据结构时。

## 功能部件

| 部件 key | 类型 | 行号 | 作用 |
|:--|:--|:--|:--|
| `RateLimited@50` | class | L50-51 | class RateLimited(QuotaExceeded): |
| `GitHubSource@63` | class | L63-328 | class GitHubSource: |
| `GitHubSource.set_min_interval@101` | def | L101-108 | def set_min_interval(self, seconds: float) -> None: |
| `GitHubSource.search@208` | def | L208-234 | def search(self, query: str, *, limit: int = 30, cursor: str \ |
| `GitHubSource.list_author@236` | def | L236-245 | def list_author(self, author_id: str, *, kinds: Iterable[str] \ |
| `GitHubSource.fetch@247` | def | L247-250 | def fetch(self, ref: ContentRef) -> Document: |
| `GitHubSource.canonicalize@308` | def | L308-313 | def canonicalize(self, url: str) -> str: |
| `GitHubSource.health@315` | def | L315-328 | def health(self) -> Health: |

> 共 16 个语义块，完整清单见第4层符号索引。

## 第4层语义块索引
- `collector-zhihu_pipe-sources-github.py.md`: `../symbols/collector-zhihu_pipe-sources-github.py.md`

## 下沉指引
```
read_block(path="collector/zhihu_pipe/sources/github.py", key="RateLimited@50")
read_block(path="collector/zhihu_pipe/sources/github.py", key="GitHubSource@63")
```
