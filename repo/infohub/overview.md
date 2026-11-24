---
covers:
  - src/
  - domains/
  - scripts/
  - package.json
root: D:/work/project/infohub
updated: 2026-11-17
---

# Overview

## Three things in one breath

- **卡片** 是唯一数据单位：`cards/<层>/<领域>/<card_id>.md`，Markdown + YAML frontmatter。
- **领域包** 是唯一 Schema 真源：`domains/*.yaml` 声明字段、列表列、判重规则。前端不认识具体字段名。
- **两条写入通道**：MCP（Agent 用）与 CLI 脚本（批量、运维），二者共用同一份内核 `src/core/ingest.ts`。

## Two runtime modes (the usual confusion)

| | `dev` / `preview` | `build` + export |
| :-- | :-- | :-- |
| 适配器 | `adapter-node` | `adapter-static` |
| 卡片来源 | 运行时读文件系统 | 构建时预渲染 |
| 改完卡要不要重跑 | 不用，刷新即可 | **要重新 build** |
| 适合 | 本地写作、Agent 写卡 | 发布静态站 |

搞错这一点的典型症状：改完卡刷新页面还是旧内容——因为你在 build 模式下，卡片在构建时已被烘进 HTML。

## Current data (differs from README)

**卡片数与工具数不要从这里抄。** 它们是会漂移的派生值，现查更可靠：

```bash
python sizes.py            # 目录规模
ls cards/info              # 有哪些信息卡领域
find cards -name '*.md' | wc -l   # 卡片总数
```

下面这份是**带日期的快照**（2026-11-16），只用来和 README 对照，不作为当前真值：

| 项 | README 写 | 当日实测 |
| :-- | --: | --: |
| 卡片总数 | 3479 | 14923 |
| student 卡 | 1179 | 3019 |
| MCP 工具数 | 21 | 24 |
| 领域命名 | `person` / `thesis` / `job` | `info_*` / `collect_*` |

当时的分领域分布：`collect/` 下 zhihu 4658、paper 4517、github 1894、web 320、bilibili 23；
`info/` 下 student 3019、course 149、mentor 115、thesis 84、academic 78、competition 64、gaokao 1、job 1。

这两张表的用处只有一个：**证明 README 的数字落后了一个数量级**。
真实数字请现查，不要引用这里。

另外两处 README 与代码不符（这两条是结构性的，不会漂移）：

- `cards/report/` 与 `report_*` 领域**并不存在**，尽管 `domainDir()` 支持三层结构；
- README 第 31 行把一段目录树混进了正文。

为什么页面里不写行数与文件数，见 `infohub/numbers-policy`。

## Directory map

```text
src/core/         ingest.ts（写入内核）
src/mcp/          MCP server 与全部工具
src/lib/server/   card-store.ts（读取层，性能关键）
src/routes/       SvelteKit 路由
domains/          领域包 YAML（Schema 真源）
cards/            卡片数据
collector/        Python 采集器（见 collector/ 子目录的页面）
scripts/          运维与门禁脚本
```

## Reading order

**先建立全局理解**

- 七条硬约束及其背后的理由，一次看懂大半个代码库 → `infohub/invariants`
- 卡片落到磁盘上是什么形状 → `infohub/card-file-shape`
- 为什么这样设计、否掉过哪些方案 → `infohub/design-tradeoffs`
- 常见误解与坑（按踩到频率排序） → `infohub/pitfalls`

**写入与字段**

- 四条写入通道怎么选、identity 怎么写 → `infohub/write-channel`
- 导入策略与报告字段的精确语义 → `infohub/core/import-report`
- 导入内核逐阶段（解析→映射→校验→写盘） → `infohub/core/ingest-pipeline`
- identity 三步匹配与字段合并语义 → `infohub/core/identity-and-merge`
- 六种输入格式与类型还原 → `infohub/core/input-parsers`
- 正文小节读写与派生字段 → `infohub/core/sections-and-derive`
- 附件挂载到已有卡 → `infohub/core/attachments`

**领域包（Schema 真源）**

- 16 份 YAML 逐包逐字段 → `infohub/domain-packs-atlas`
- 领域包怎么驱动前端 → `infohub/domains-and-reader`
- 用工具改包（不要手改 YAML） → `infohub/mcp/domain-pack-api`

**MCP 工具**

- 全部工具的完整契约 → `infohub/mcp/tools-reference`
- 写入工具之间的层级与两阶段提交 → `infohub/mcp/write-tool-relations`
- 错误分级与静默失败路径 → `infohub/mcp/error-taxonomy`
- storage / dedup / llm-client 内部 → `infohub/mcp/lib-internals`

**读取层与前端**

- 读取热路径与缓存 → `infohub/reader/card-store`
- YAML → Zod 编译 → `infohub/reader/schema-compiler`
- 路由与 API 契约 → `infohub/reader/routes-and-api`
- 敏感边界、渲染与排序 → `infohub/reader/sensitive-and-publish`
- 分类树 → `infohub/reader/taxonomy`
- 两种运行模式在代码级怎么分叉 → `infohub/build/config-and-modes`

**采集子系统（collector/）**

- 先看**架构与分层判据** → `infohub/collector/architecture`
- 要改抓取逻辑 → `infohub/collector/l1-primitives`（翻页/限速/抽正文的硬规则）
- 原语的函数级 API → `infohub/collector/kit-api`
- 要加一个站或平台 → `infohub/collector/l2-sites-and-plugins`
- 站点 YAML 逐份说明 → `infohub/collector/site-specs`
- 要改字段抽取 → `infohub/collector/llm-extraction`
- 工具脚本清单 → `infohub/collector/tools-atlas`

**运维与构建**

- npm script 逐条展开 → `infohub/ops/npm-scripts`
- 发布门禁 → `infohub/ops/publish-gate`
- 测试矩阵「改完该跑哪条」 → `infohub/ops/test-matrix`
- 迁移脚本与 dry-run → `infohub/ops/migrations`
- 点开头的辅助目录（.trash / .staging / .quarantine） → `infohub/side-directories`

**不确定从哪开始时**：`kb where <源码路径>` 反查归属，`kb search <关键词>` 全库搜词。
