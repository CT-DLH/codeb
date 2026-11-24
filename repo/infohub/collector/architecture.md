---
covers:
  - collector/
  - src/mcp/tools/collect_run.ts
  - src/mcp/tools/collect_site.ts
  - src/mcp/tools/collect_guide.ts
  - docs/架构-采集三层.md
  - docs/通用网页采集.md
---

# Collector: three-layer architecture

`collector/` 有上百个 Python 文件、11 个平台插件、5 份站点 YAML。
不用先记住文件，先记住**一个判据**，所有「这段代码该放哪」的问题都由它回答。

## The single criterion

> **把这段代码搬到另一个站点，还成立吗？**
> 成立 → L1（`kit/`）。换站就要改 → L2（`sources/` 或站点 YAML）。只说「我要什么」→ L3。

这条判据写在 `collector/kit/__init__.py` 的 docstring 里，是这一层唯一被反复强调的规则。

## Layers and file boundaries

```text
L3 取用层     上层只说「我要什么」，不认识任何站点
   src/mcp/tools/collect_run.ts     MCP：登记腿
   src/mcp/tools/collect_site.ts    MCP：站点类
   collector/tools/run_*.py         命令行入口（run_nightly / run_site / run_source）
   产物永远走同一条落卡通道：inbox/*.jsonl → card_import 预演 → 落盘

L2 站点工具层  一个工具 = 一份 spec（声明）+ 必要时一个 adapter（动作）
   collector/sites/<family>/<kind>.yaml     站点 spec：选择器 / 接口 / 限速 / 输出映射
   collector/site_crawl/adapters/<kind>.py  只在「这个站形态特殊」时才需要
   collector/zhihu_pipe/sources/*.py        11 个平台插件

L1 原语层      不认任何站点的通用件
   collector/kit/http.py     限速(按 host)/重试/编码嗅探/UA/cookie/robots 硬闸
   collector/kit/html.py     解码 / 密度打分抽正文 / 链接与日期抽取
   collector/kit/blob.py     非 HTML 字节：下载 / 类型嗅探 / 四级降级抽文
   collector/kit/paging.py   翻页探测：软 404 铁律 + 候选形状
   collector/kit/store.py    sqlite 底座（WAL + busy_timeout=5000 + user_version 迁移）
```

## L1 status versus the target state

`kit/` 目前六个文件全在：`http` / `html` / `blob` / `paging` / `store` 五件已落地。
`extract.py` / `llm.py` / `registry.py` **仍是目标态，文件不存在**。

`site_crawl/http.py`、`site_crawl/text.py`、`zhihu_pipe/html_text.py` 三处已改为
re-export 或别名，实现只在 `kit/` 一份——所以「同名两套」的问题已经解决过一轮。

## L1 must not depend upward

`kit/` 内任何模块都不许 `import sources` / `import zhihu_pipe` / `import site_crawl`。

理由不是架构美观：**L1 一旦反向依赖，`kit` 就成了 L2 的附庸，「换站不改 L1」这条判据立刻失效**。
更糟的是依赖环——某个站点包坏了，会变成整个 `kit` import 不了。

落地手法是 **duck typing**：`kit.blob.fetch_blob()` 拿到的 `http` 参数只在运行时要求有 `fetch(url)`。
`site_crawl.http.Http` 可以当实参传进去，但 `kit` 里一行 `import` 都没有。

## Why L2 is YAML, not Python

一个工具 = 一份 spec（声明）+ 必要时一个 adapter（动作）。

**新增一个同 kind 的站点，diff 只包含一份 YAML**，L1 与 L3 零改动。
这是 `site_crawl/specs.py` 刻意设计的结果：

- 按 `kind` 显式分派（`_VALIDATORS` 表），不再用 `else` 把所有非 `teacher_home` 的当作列表型；
- 新增站点只要用已有的 kind，分派表不用动；
- 未来加第四个列表型 kind，也不必再改判据——判据统一是 `kind == "teacher_home"`。

## Three kinds, three required sets

| kind | 是什么 | 必填 | 为什么 |
| :-- | :-- | :-- | :-- |
| `teacher_home` | 教师主页，固定版式抠字段 | `selectors` + `output` | 靠选择器取值，必须逐项校验 |
| `column_list` | 栏目通知页 | 只要 `family/kind/site/base` | 正文靠 L1 密度打分抽，**没有选择器可填** |
| `announcement_list` | 公告列表页 | 加 `output` | 与栏目型同族复用组合层，但输出是结构化列表 |

## The cost of a typo in a spec

`specs.py` 对未知键**直接报错**，而不是忽略。

原因：拼错选择器最危险的不是报错，而是**解析静默返回 0 条**——看起来像「站点改版」，
实际是自己写错了键名。所以把故障挡在发请求之前。

## How collector output becomes cards

三层的出口是同一个，不允许各层自己写卡：

```text
采集器 → collector/data/pipeline.db（sqlite）
       → inbox/*.jsonl（导出）
       → card_import 预演
       → 落盘 cards/
```

`npm run collect:export` 做第一步到第二步。**采集层不认识卡片格式**，它只产 JSONL。
