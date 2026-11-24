---
covers:
  - collector/zhihu_pipe/sources/
title: Collectors (Platform Adapters)
updated: 2026-11-24
---

# 采集模块：平台采集器

> 每个平台一个适配器，负责该平台的抓取与字段映射。
> 本页是「采集模块」的下一层，再往下才是各采集器的功能部件。

## 职责
按平台拆分采集实现：统一接口（`source.py`）定义契约，各平台适配器实现抓取细节。

## 下级

| 采集器 | 说明 | 知识页 |
|:--|:--|:--|
| 知乎采集器 | 知乎内容采集：热榜、问题、回答与作者主页。 | [sources/zhihu.md](sources/zhihu.md) |
| B站采集器 | B 站视频与 UP 主内容采集。 | [sources/bilibili.md](sources/bilibili.md) |
| 小红书采集器 | 小红书笔记与作者内容采集。 | [sources/xiaohongshu.md](sources/xiaohongshu.md) |
| GitHub采集器 | GitHub 仓库与项目内容采集。 | [sources/github.md](sources/github.md) |
| 知网采集器 | 知网文献检索与元数据采集。 | [sources/cnki.md](sources/cnki.md) |
| Crossref采集器 | Crossref DOI 元数据与引用解析。 | [sources/crossref.md](sources/crossref.md) |
| 学术源采集器 | 学术来源统一适配：期刊、会议、预印本。 | [sources/academic.md](sources/academic.md) |
| 通用网页采集器 | 任意网页正文抽取。 | [sources/web.md](sources/web.md) |
| 站点订阅采集器 | 按站点配置的结构化列页采集。 | [sources/site.md](sources/site.md) |
| 浏览器渲染采集器 | 需要 JS 渲染的页面抓取。 | [sources/browser.md](sources/browser.md) |
| 采集器注册表采集器 | 采集器注册与统一入口。 | [sources/__init__.md](sources/__init__.md) |

## 适用场景
- 新增一个平台采集器：照现有适配器实现统一接口，并在 `sources/__init__.py` 注册。
- 定位某平台的抓取实现：从本页下钻到对应采集器。

## 下沉指引
```
本页 → 选中平台采集器 → 该采集器的功能部件表 → read_block 取正文
```
