---
covers:
  - collector/zhihu_pipe/sources/browser.py
title: Collector: browser
updated: 2026-11-24
---

# 采集器：浏览器渲染（`browser.py`）

**模块**：知乎管道 → 平台采集器
**源码**：`collector/zhihu_pipe/sources/browser.py`

## 职责
需要 JS 渲染的页面抓取。

## 适用场景
- 需要调整浏览器渲染的抓取逻辑、请求头、翻页或字段映射时。
- 需要确认浏览器渲染适配器对外暴露的接口与数据结构时。

## 功能部件

| 部件 key | 类型 | 行号 | 作用 |
|:--|:--|:--|:--|
| `BrowserUnavailable@90` | class | L90-91 | class BrowserUnavailable(RuntimeError): |
| `NeedManualAction@94` | class | L94-99 | class NeedManualAction(QuotaExceeded): |
| `BrowserBlocked@102` | class | L102-107 | class BrowserBlocked(QuotaExceeded): |
| `BrowserConfig@203` | class | L203-220 | class BrowserConfig: |
| `BrowserSession@223` | class | L223-445 | class BrowserSession: |
| `BrowserSource@468` | class | L468-500 | class BrowserSource: |
| `browser_available@110` | def | L110-115 | def browser_available() -> bool: |
| `challenge_reason@118` | def | L118-127 | def challenge_reason(url: str = "", text: str = "") -> str: |

> 共 41 个语义块，完整清单见第4层符号索引。

## 第4层语义块索引
- `collector-zhihu_pipe-sources-browser.py.md`: `../symbols/collector-zhihu_pipe-sources-browser.py.md`

## 下沉指引
```
read_block(path="collector/zhihu_pipe/sources/browser.py", key="BrowserUnavailable@90")
read_block(path="collector/zhihu_pipe/sources/browser.py", key="NeedManualAction@94")
```
