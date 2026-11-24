---
covers:
  - collector/sites/
  - collector/site_crawl/
  - collector/zhihu_pipe/sources/
  - collector/zhihu_pipe/store.py
  - collector/zhihu_pipe/pipeline.py
---

# Collector: L2 sites and platform plugins

L2 有**两个不同的东西**，它们经常被混为一谈：

| | 站点层（site_crawl + sites/） | 平台插件（zhihu_pipe/sources/） |
| :-- | :-- | :-- |
| 对象 | 具体学校的某个栏目 / 教师主页 | 一个内容平台（知乎、B站、GitHub…） |
| 形态 | YAML 声明为主，adapter 为例外 | Python 插件，一个平台一个文件 |
| 新增成本 | 一份 YAML | 一个 `.py` |
| 数量 | 5 份 YAML、1 个 adapter | 11 个插件 |

判断该写哪种：**内容形态由学校版式决定 → 站点层；由平台接口决定 → 平台插件。**

## Site layer: what a spec holds

以 `sites/hitsz/teachers.yaml`（教师主页）为例，四组键：

- `http`：`delay` / `timeout` / `retries`。**限速在 L1 按 host 兜底**，这里只是站点的额外声明。
- `apis`：直接调接口而不是驱动浏览器。
- `selectors`：`profile`（单值字段）与 `sections`（列表型字段）。
- `output`：选择器抽出来的东西怎么映射成卡片字段。

### Why call the API instead of driving a browser

教师主页左侧的「个人介绍 / 科研论文 / 科研项目」是**前端页签**，但数据由主页 JS
一次 `POST TeacherHome/teacherBody.do` 取回，响应里已包含**全部页签的 HTML**。

所以不需要驱动浏览器点按钮。驱动浏览器慢、脆、还要处理等待与超时；
直接调同一个接口，一次请求拿到全部内容。

### Site knowledge lives in spec comments

`teachers.yaml` 里这类注释很多，它们是最有价值的站点知识：

```yaml
  # 站点路径就是 hompage（少一个 e），不是笔误，不要"修正"
  name_search: hompage/findTeachersByName.do

  # 主页把邮箱倒着写（nc.ude.tih@…），页面上由 JS 反转显示
  email_reverse: true
```

第一条防的是「好心修正 bug 反而弄坏」。第二条说明为什么需要 `email_reverse` 这个键——
没有注释的话，下一个人会以为它是冗余配置。

### Section-name aliasing

`sections.aliases` 解决的是：**同一含义有十几种写法**。

```yaml
aliases:
  个人简介:
    - "个人简介"
    - "个人介绍"
```

键是卡片里的**稳定小节名**，值是主页上出现过的写法（包含匹配，大小写不敏感）。
不归并的话，同一份简历会散成五六个小节，前端没法展示。

## Platform plugins: 11 platforms from 10 files

`zhihu_pipe/sources/` 下 10 个 `.py`，但注册出 **11 个平台**——
`academic.py` 一个文件注册了多个学术源（`arxiv` / `openalex` / `pubmed` / `s2` 等），
因为它们的接口形状相同，共用一份实现。

平台清单：`zhihu` / `bilibili` / `xiaohongshu` / `github` / `cnki` /
`arxiv` / `openalex` / `pubmed` / `s2` / `crossref` / `web`。

另有 `site` / `browser` 两个文件，属于基础设施（按站点 YAML 驱动、浏览器兜底），不注册成搜索平台。

注册方式 = 在 `_FACTORIES` 加一行 + 写一个实现类（见 `sources/__init__.py`）。

**`web` 是独立采集器而不是「按站点拆」**，因为它是**通用网页抽取器**——
不针对任何具体站点。`site` 才是「按站点 YAML 驱动」的那一个。

能力声明写在插件里，由 `tools/capabilities.py` 汇总到 `capabilities.json`：

- `platforms`（11 个）= 声明了 `SEARCH` 的源（TS SOURCES / 下拉来源）；
- `sites`（3 个）= 只声明 `BODY` 的站点源：`hit_yzb` 公告、`hitsz` 栏目、`hitsz` 教师主页；
- `body_capable`（14 个）= 能取正文的源，平台与站点合起来算。

`capabilities.json` **不要手改**，用 `tools/capabilities.py --write` 生成。

## query_guide: teaching the caller how to search

这是 `capabilities.json` 里最容易被忽略、但价值最高的一块。每个平台的
`query_guide` 有六个字段：`lang` / `searchable` / `pattern` / `examples` / `avoid` / `capacity`。

它解决的问题：**同一个搜索词，在不同平台的检索效果差一个数量级**，而调用方（LLM）不知道。

几条实测结论：

| 平台 | 关键约束 |
| :-- | :-- |
| `zhihu` | 自然语言短语最有效；写 `AND`/`OR` 会被当成普通字符 |
| `arxiv` | 全英文；**别把多个词拼成一个短语**（`all:"..."` 精确匹配，拼长了直接 0 结果） |
| `github` | 支持限定符 `in:name` / `stars:>N` / `language:X` / `topic:Y` |
| `cnki` | 中文库；英文检索命中差；需登录态 |
| `web` | 关键词堆叠比长句好；已登记站点会被 `_OWNED` 拦掉 |

`avoid` 字段专门记**反例**（如「arXiv 里搜中文」「把疑问句当自然语言搜」），
`capacity` 记**容量上限与配额**（未配 key 时 GitHub 30 次/分、S2 会 429）。

这份 guide 会随 `capabilities.json` 一起暴露给 MCP 调用方，
所以它实际上是**给 LLM 的检索说明书**，不是给人看的文档。

## Two state machines coexist

`collector/` 里有**两套采集状态机**：旧的 `zhihu_pipe` 与新的 `site_crawl`。
迁移原则是 **只接不改写、凭据不入库**：

- 旧管道（`zhihu_pipe/store.py`）继续管平台类采集的状态与去重；
- 新框架（`site_crawl/store.py`）管站点类；
- 二者共用 `kit/store.py` 的 sqlite 底座，但**表结构与状态语义不同**。

**不要试图统一它们**——统一意味着重写已经跑通的平台去重逻辑，代价远大于收益。
迁移的边界写在 `docs/采集迁移.md`。

## Credential handling

知乎这类需要登录态的源，Cookie 存在 `zhihu-toolkit` 的 default profile
(`~/.zhihu-cli/cache`)，**不在项目目录、不进 git**。

项目里的 `collector/.env` 存其它凭据，同样在 `.gitignore` 里。

`tools/ingest_curl.py` 从浏览器复制的 cURL 里提取 Cookie：
因为 `zhihu auth paste` 只解析 `-H` 头、**抓不到 `-b` 里的 Cookie**，所以要自己写这个脚本。

签名相关的 `x-zse-93/96` 由 toolkit 用 `d_c0` 自动生成，
**脚本会自动剔除 cURL 里手写的签名**——避免用过期的签名导致 403。

## Boundary of long-run tasks

`tools/run_*.py` 有十几种入口（`run_target` / `run_keyword` / `run_nightly` /
`run_source` / `run_site` / `run_research` / `run_survey`），最长的是 `run_research.py`。

它们都属于 **L3 取用层**：只负责编排，不包含站点知识。加一个新入口不应该改 L1 或 L2。

`run_nightly` 是最常用的一个：主题搜索 → 顺着命中作者铺开 → 查重 → 主题筛选 →
抓正文（**读过的自动复用，不重复联网**）→ LLM 总结 → 生成清单。
