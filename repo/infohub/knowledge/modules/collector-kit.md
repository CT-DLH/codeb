---
covers:
  - collector/kit/blob.py
  - collector/kit/html.py
  - collector/kit/http.py
  - collector/kit/paging.py
  - collector/kit/store.py
title: Collector Kit Module (Layer 3)
updated: 2026-11-24
---

# 模块：采集核心工具——部件细页表（第3层）

**项目**：infohub
**源码文件**：`collector/kit/blob.py`、`collector/kit/html.py`、`collector/kit/http.py`、`collector/kit/paging.py`、`collector/kit/store.py`
**第4层语义块索引**：
- `collector-kit-blob.py`: `../symbols/collector-kit-blob.py.md`
- `collector-kit-html.py`: `../symbols/collector-kit-html.py.md`
- `collector-kit-http.py`: `../symbols/collector-kit-http.py.md`
- `collector-kit-paging.py`: `../symbols/collector-kit-paging.py.md`
- `collector-kit-store.py`: `../symbols/collector-kit-store.py.md`
**写范围**：collector/kit/**
**验证命令**：`powershell -NoProfile -ExecutionPolicy Bypass -File _kbwork/run_regression.ps1`

## 职责
采集器核心工具箱，提供 Blob 二进制包装、HTML 文本提取、HTTP 请求与节流、分页导航、SQLite 存储持久化等基础组件。用于下层采集流程的原材料准备与结果持久化。

## 适用场景
- 实现或改进 Blob 二进制解析与Kind判断（`_kind_from_url`、`_kind_from_ctype`、`sniff_kind`）
- HTML 内容提取、链接提取、清洗与正则匹配（`parse_html`、`extract_links`、`clean_text`）
- HTTP 请求发送、响应文本/JSON 解码、Robots.txt 与节流（`Http.fetch`、`Http.text`、`Http.json`、`Throttle`）
- 多页爬取与分页标识（`is_paging_label`、`find_next_page`、`iter_pages`）
- SQLite 数据库建表、迁移、CRUD 与缓存（`connect`、`migrate`、`ensure_columns`、`cache_get`/`cache_put`）

## 功能部件

| 部件 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| `Blob@141` | class | L141-163 | 一个附件（或任何非 HTML 响应）的原始字节及其元信息。 | class Blob: |
| `Unparsed@166` | class | L166-183 | 抽文失败。reason 是机器可判定码，detail 说清是哪个后端/哪一步。 | class Unparsed(RuntimeError): |
| `Blob.size@161` | def | L161-163 | 字节数。语义上等价于旧 FetchResult.bytes，但不等于传输职责。 | def size(self) -> int: |
| `sniff_kind@253` | def | L253-284 | 判断字节是什么。内容优先，Content-Type 次之，扩展名最后。 | def sniff_kind(data: bytes, content_type: str = "", url: str… |
| `Extraction@521` | class | L521-528 |  | class Extraction: |
| `parse_html@75` | def | L75-90 | HTML 字符串 → lxml 根节点；空输入或坏文档返回 None（不抛异常）。 | def parse_html(html: str): |
| `select@93` | def | L93-102 | CSS 选择器取后代节点。选择器写错直接抛错，不静默返回 []。 | def select(node, selector: str) -> list: |
| `select_one@105` | def | L105-107 |  | def select_one(node, selector: str): |
| `FetchResult@216` | class | L216-231 |  | class FetchResult: |
| `FetchError@234` | class | L234-240 | 抓取失败。reason 是机器可判定码，detail 是完整结果。 | class FetchError(RuntimeError): |
| `Http@246` | class | L246-439 | 带「按 host 节流」与 robots 闸的 urllib 封装。 | class Http: |
| `Throttle@445` | class | L445-564 | 四种限速策略的统一底座。 | class Throttle: |
| `is_paging_label@93` | def | L93-96 | 锚文本是不是分页控件（去空白 + 小写后判定；含纯数字 / 空文本）。 | def is_paging_label(text: str) -> bool: |
| `item_key@102` | def | L102-127 | 条目 → 可比较的键。dict 依次取 url/href/link/id/title；对象取 url/id/title。 | def item_key(item: Any) -> str: |
| `find_next_page@342` | def | L342-372 | 找下一页。返回 (next_url, "") 或 ("", reason)，reason ∈ REASONS。 | def find_next_page( |
| `iter_pages@375` | def | L375-414 | 逐页 yield (page_url, items)，遇到 soft_404 就停。 | def iter_pages( |
| `connect@25` | def | L25-37 | 打开（必要时创建）一个 sqlite 库，固定姿势一次做齐。 | def connect(path: str \ |
| `user_version@40` | def | L40-42 |  | def user_version(conn: sqlite3.Connection) -> int: |
| `migrate@45` | def | L45-77 | 按版本号升序执行尚未跑过的 SQL，返回本次实际执行的版本号列表。 | def migrate(conn: sqlite3.Connection, migrations: Iterable[t… |
| `ensure_columns@80` | def | L80-100 | 给已有表补列（只加不删、不改类型），返回真正补上的列名。 | def ensure_columns(conn: sqlite3.Connection, table: str, |

> 本模块共 **118** 个语义块，本页只列核心部件；完整清单见各 `symbols/` 页。

## 下沉指引
```
选中部件 → 打开第4层 symbols 文件 → read_block(path="collector/kit/blob.py", key="Blob@141")
选中部件 → 打开第4层 symbols 文件 → read_block(path="collector/kit/html.py", key="parse_html@75")
选中部件 → 打开第4层 symbols 文件 → read_block(path="collector/kit/http.py", key="normalize_charset@74")
```
