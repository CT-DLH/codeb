---
covers:
  - collector/site_crawl/adapters/__init__.py
  - collector/site_crawl/adapters/teacher_home.py
  - collector/site_crawl/column.py
  - collector/site_crawl/runner.py
  - collector/site_crawl/specs.py
  - collector/site_crawl/store.py
title: Site Configuration & Crawl Module (Layer 3)
updated: 2026-11-24
---

# 模块：站点爬取——部件细页表（第3层）

**项目**：infohub
**源码文件**：`collector/site_crawl/adapters/__init__.py`、`collector/site_crawl/adapters/teacher_home.py`、`collector/site_crawl/column.py`、`collector/site_crawl/runner.py`、`collector/site_crawl/specs.py`、`collector/site_crawl/store.py`
**第4层语义块索引**：
- `collector-site_crawl-adapters-__init__.py`: `../symbols/collector-site_crawl-adapters-__init__.py.md`
- `collector-site_crawl-adapters-teacher_home.py`: `../symbols/collector-site_crawl-adapters-teacher_home.py.md`
- `collector-site_crawl-column.py`: `../symbols/collector-site_crawl-column.py.md`
- `collector-site_crawl-runner.py`: `../symbols/collector-site_crawl-runner.py.md`
- `collector-site_crawl-specs.py`: `../symbols/collector-site_crawl-specs.py.md`
- `collector-site_crawl-store.py`: `../symbols/collector-site_crawl-store.py.md`
**写范围**：collector/site_crawl/**
**验证命令**：`powershell -NoProfile -ExecutionPolicy Bypass -File _kbwork/run_regression.ps1`

## 职责
站点配置与爬取协调模块，定义爬取规格、解析列页、管理 HTTP 会话、提供健壮的存储层。从 spec 加载到 runner 执行的全链路桥梁，确保列数据、爬取任务与结果的生命周期可控。

## 适用场景
- 实现或改进列报解析（`_parse_items`、`_attachment_links`、`crawl_column`）
- 爬行任务的启动、调度、中断与重试机制（`run`、`_brief`、`_print_brief`）
- Spec 的加载、校验与汇总（`load_spec`、`spec_summary`、`_validate_*` 一系列校验函数）
- Store 的事务、缓存、teacher 与内容指纹（`_canonical`、`teacher_sha1`、`content_cache_cold`、`upsert_teacher`）

## 功能部件

| 部件 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| `get_adapter@19` | def | L19-22 |  | def get_adapter(kind: str): |
| `TeacherHomeAdapter@183` | class | L183-533 |  | class TeacherHomeAdapter: |
| `slug_of@32` | def | L32-49 | 把 URL 或裸 slug 还原成主页标识；外域返回空字符串。 | def slug_of(value: str, host: str = "homepage.hit.edu.cn") -… |
| `split_title@52` | def | L52-60 | 栏目名可能写成「研究方向 Research Direction」，中文在前、英文在后。 | def split_title(title: str) -> tuple[str, str]: |
| `first_sentence@63` | def | L63-70 |  | def first_sentence(text: str, limit: int = 180) -> str: |
| `ColumnReport@35` | class | L35-46 |  | class ColumnReport: |
| `_CachedHttp@110` | class | L110-129 | 按 URL 缓存一次 fetch 的结果。 | class _CachedHttp: |
| `ColumnReport.summary@43` | def | L43-46 |  | def summary(self) -> str: |
| `_CachedHttp.fetch@122` | def | L122-126 |  | def fetch(self, url: str, **kw): |
| `run@111` | def | L111-228 | 跑一轮站点同步。 | def run( |
| `SpecError@71` | class | L71-72 | 配置不合法。消息里带配置路径，便于直接定位。 | class SpecError(ValueError): |
| `load_spec@190` | def | L190-203 |  | def load_spec(path: str \ |
| `spec_summary@206` | def | L206-230 |  | def spec_summary(spec: dict) -> str: |
| `Store@147` | class | L147-262 |  | class Store: |
| `teacher_sha1@99` | def | L99-109 |  | def teacher_sha1(row: dict) -> str: |
| `content_fingerprint@119` | def | L119-126 | 给一份采集记录算内容指纹（与 cache_put 存进 sha1 列的口径完全一致）。 | def content_fingerprint(rec: dict) -> str: |
| `now_stamp@143` | def | L143-144 |  | def now_stamp() -> str: |

> 本模块共 **71** 个语义块，本页只列核心部件；完整清单见各 `symbols/` 页。

## 下沉指引
```
选中部件 → 打开第4层 symbols 文件 → read_block(path="collector/site_crawl/adapters/__init__.py", key="get_adapter@19")
选中部件 → 打开第4层 symbols 文件 → read_block(path="collector/site_crawl/adapters/teacher_home.py", key="slug_of@32")
选中部件 → 打开第4层 symbols 文件 → read_block(path="collector/site_crawl/column.py", key="ColumnReport@35")
```
