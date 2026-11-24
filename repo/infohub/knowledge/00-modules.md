---
covers:
  - infohub/**
title: infohub module navigation (layer 2)
updated: 2026-11-23
---

# infohub 项目模块导航（第2层页表）

> 进入 infohub 项目后先读本页：列出该项目内部的模块。
> 每个模块指向第3层部件细页表，部件页再指向第4层语义块索引。
>
> **范围口径**由 [`repo/.kbignore`](../../.kbignore) 决定（gitignore 语法）：
> 排除第三方 `参考项目/`（1856 个文件）、`.svelte-kit/` 构建产物、`.cache/` 一次性探针、
> `scripts/` 与 `collector/tools/` 里的 `backfill_*`/`fix_*`/`migrate_*`/`probe_*` 维护脚本。
> 判决后核心源码 **196 个**，已索引 **182 个（92.9%）**，余下 14 个是无语义块的空文件/入口。

## 模块列表

| 模块 | 源码范围 | 第3层部件细页表 | 文件数 | 语义块 | 状态 |
|:--|:--|:--|--:|--:|:--|
| 采集核心工具 | `collector/kit/**` | [collector-kit](modules/collector-kit.md) | 5 | 118 | 有效 |
| 站点爬取 | `collector/site_crawl/**` | [site-crawl](modules/site-crawl.md) | 6 | 71 | 有效 |
| 知乎管道 | `collector/zhihu_pipe/**` | [zhihu-pipe](modules/zhihu-pipe.md) | 24 | 409 | 有效 |
| 引用解析 | `collector/refs/**` | [refs](modules/refs.md) | 6 | 70 | 有效 |
| LLM 抽取 | `collector/llm/**` | [llm](modules/llm.md) | 4 | 53 | 有效 |
| 采集 CLI 工具 | `collector/tools/**` | [collector-tools](modules/collector-tools.md) | 59 | 446 | 有效 |
| 采集根级模块 | `collector/*.py` | [collector-root](modules/collector-root.md) | 2 | 25 | 有效 |
| MCP 服务 | `src/mcp/**` | [mcp](modules/mcp.md) | 31 | 130 | 有效 |
| 核心领域逻辑 | `src/core/**` | [core](modules/core.md) | 15 | 152 | 有效 |
| 前端库 | `src/lib/**` | [lib](modules/lib.md) | 11 | 184 | 有效 |
| 路由 | `src/routes/**` | [routes](modules/routes.md) | 10 | 22 | 有效 |
| 控制台 | `console/**` | [console](modules/console.md) | 6 | 148 | 有效 |
| 根级文件 | `*.py`、`src/*.ts` | [root-files](modules/root-files.md) | 3 | 9 | 有效 |
| 根级配置 | `*.ts`、`*.js`、`vite.config.ts` | （配置入口，无块） | 3 | 0 | 空 |

**合计**：13 个有内容模块，**182** 个源文件、**1837** 个语义块。

## 第4层语义块索引

`symbols/` 下共 **182** 个符号索引页、**1837** 个语义块，全部由
`distill/agent/semantic_blocks.py` 解析生成（Python 用 `ast`，TS/JS 用 TypeScript
compiler API），key 与行号精确到源码真实位置。

**为什么不用 LLM 写**：行号和块名是可机械获取的事实。此前让 LLM 生成 atomkgraph
的符号页，造出 29 个错行号和假方法名（如 `CommentService.createComment`），
最终只能全部回炉用脚本重建。

**`*.svelte` 有意不索引**：解析器对 svelte 只有 regex-fallback，抓出的行号不可信，
宁可留空也不写假精度。

## 已知空文件（14 个，无块可索引）

`collector/*/__init__.py`（5 个）、`site_crawl/http.py`（纯转发层，只 re-export）、
`site_crawl/text.py`、`src/mcp/server.ts`（只调 `registerXxx` 的入口）、
`src/routes/+layout.ts`、`src/mcp/lib/field-spec.ts`、`svelte.config.js`、
`vite.config.ts`、`inbox/launch_cmc_7h.py`、`inbox/run-imports.mjs`。

## 查找流程

```
本页 → 选中模块 → 第3层部件细页表（modules/*.md）
    → 选中部件/文件 → 第4层语义块索引（symbols/*.md）
    → 选中语义块 key → read_block(path, key) 调入第5层完整正文
```

## 操作

- **重建符号索引**：`python -X utf8 _kbwork/gen_symbols.py --repo infohub`
- **重建 sqlite 索引**：`python -X utf8 kb.py reindex`
- **查覆盖缺口**：`python -X utf8 _kbwork/check_covers.py`
- **回归**：`powershell -NoProfile -ExecutionPolicy Bypass -File _kbwork/run_regression.ps1`
- **写范围**：默认 `infohub/**`
