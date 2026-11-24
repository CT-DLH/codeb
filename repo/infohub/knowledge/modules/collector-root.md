---
covers:
  - collector/frontmatter.py
  - collector/survey_refs.py
title: Collector Root Module (Layer 3)
updated: 2026-11-24
---

# 模块：采集根级模块——部件细页表（第3层）

**项目**：infohub
**源码文件**：`collector/frontmatter.py`、`collector/survey_refs.py`
**第4层语义块索引**：
- `collector-frontmatter.py`: `../symbols/collector-frontmatter.py.md`
- `collector-survey_refs.py`: `../symbols/collector-survey_refs.py.md`
**写范围**：collector/*.py
**验证命令**：`powershell -NoProfile -ExecutionPolicy Bypass -File _kbwork/run_regression.ps1`

## 职责
采集器的根级公共模块：frontmatter 解析、跨站点调研与引用汇总。

## 适用场景
- 需要定位或修改该模块内的源码部件时，先在此页选中部件，再下沉到第4层。
- 需要确认某个文件的语义块清单与行号时，打开对应 `symbols/` 页。

## 功能部件

| 部件 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| `split_frontmatter@22` | def | L22-35 | 返回 (yaml 文本, 正文)。没有成对的分隔行时前者为 None，正文原样返回。 | def split_frontmatter(text: str) -> tuple[str \ |
| `body_of@38` | def | L38-39 |  | def body_of(text: str) -> str: |
| `read_frontmatter@42` | def | L42-52 | 读一个 markdown 文件的 (frontmatter, 正文)；解析失败时 frontmatter 为 None。 | def read_frontmatter(path: Path) -> tuple[dict \ |
| `RefTarget@119` | class | L119-137 | 一条引用解析到的采集卡。字段只放「解析与判定需要的」，不放整份 frontmatter。 | class RefTarget: |
| `CollectIndex@140` | class | L140-229 | cards/collect//*.md 的只读索引：URL/规范化键/content_id → 采集卡。 | class CollectIndex: |
| `SeqRefs@352` | class | L352-373 | 一个实体的索引投影结果——直接对应信息卡上的那几个字段。 | class SeqRefs: |
| `url_key@71` | def | L71-87 | URL 的比较键：只保留 host + path，把「同一页面的不同写法」抹平。 | def url_key(url: str) -> str: |

> 本模块共 **25** 个语义块，本页只列核心部件；完整清单见各 `symbols/` 页。

## 下沉指引
```
选中部件 → 打开第4层 symbols 文件 → read_block(path="collector/frontmatter.py", key="split_frontmatter@22")
选中部件 → 打开第4层 symbols 文件 → read_block(path="collector/survey_refs.py", key="url_key@71")
```
