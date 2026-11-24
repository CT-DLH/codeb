---
covers:
  - collector/zhihu_pipe/sources/xiaohongshu.py
title: Collector: xiaohongshu
updated: 2026-11-24
---

# 采集器：小红书（`xiaohongshu.py`）

**模块**：知乎管道 → 平台采集器
**源码**：`collector/zhihu_pipe/sources/xiaohongshu.py`

## 职责
小红书笔记与作者内容采集。

## 适用场景
- 需要调整小红书的抓取逻辑、请求头、翻页或字段映射时。
- 需要确认小红书适配器对外暴露的接口与数据结构时。

## 功能部件

| 部件 key | 类型 | 行号 | 作用 |
|:--|:--|:--|:--|
| `NeedsLogin@132` | class | L132-137 | class NeedsLogin(QuotaExceeded): |
| `NoSearchAvailable@140` | class | L140-141 | class NoSearchAvailable(NoSearch): |
| `XhsSource@294` | class | L294-647 | class XhsSource(BrowserSource): |
| `initial_state@248` | def | L248-263 | def initial_state(html: str) -> dict \ |
| `find_note@266` | def | L266-291 | def find_note(state: dict) -> dict \ |
| `walk@277` | def | L277-288 | def walk(o): |
| `XhsSource.set_min_interval@341` | def | L341-344 | def set_min_interval(self, seconds: float) -> None: |
| `XhsSource.search@427` | def | L427-484 | def search(self, query: str, *, limit: int = 30, cursor: str \ |

> 共 27 个语义块，完整清单见第4层符号索引。

## 第4层语义块索引
- `collector-zhihu_pipe-sources-xiaohongshu.py.md`: `../symbols/collector-zhihu_pipe-sources-xiaohongshu.py.md`

## 下沉指引
```
read_block(path="collector/zhihu_pipe/sources/xiaohongshu.py", key="NeedsLogin@132")
read_block(path="collector/zhihu_pipe/sources/xiaohongshu.py", key="NoSearchAvailable@140")
```
