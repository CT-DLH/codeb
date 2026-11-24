---
covers:
  - scripts/
updated: 2026-11-21
---

# Script atlas: what lives in scripts/

按「跑它会发生什么」分组，不按文件名。每组给一句职责、关键参数、以及**是否会破坏性写盘**——后者是这一页最该先看的列。

scripts/ 里文件不少，但真正构成日常链路的只有少数几个（见 npm scripts 页）。其余是：**一次性任务入口**、**历史留档的调试脚本**、**测试集**。

## 测试类（多数自清理，一个例外）

| 脚本 | 职责 | 关键参数 | 破坏性 |
| :-- | :-- | :-- | :-- |
| `mcp-smoke-test.ts` | MCP server 端到端冒烟，起真实 stdio server | 无 | **会写卡又还原**：改示例卡、建测试域、删自己造的东西；退出钩子里还原 |
| `ingest-test.ts` | `src/core/ingest.ts` 单测：解析/映射/identity/合并/策略 | 无 | 建 `domains/_probe.yaml` + `cards/_probe/`，结束时清理 |
| `taxonomy-test.ts` | 分类树内核 vs 生产 loader 的对照 | 无 | 只读（纯内存 + 读真实 YAML） |
| `sensitive-test.ts` | 敏感字段三条出口 + 运行时形态 | 无 | 建 `_sens` 夹具，清理 |
| `derive-test.ts` | 派生字段规则链、幂等、覆盖语义 | 无 | 建 `_derive` 夹具，清理 |
| `list-index-test.ts` | 分页索引 vs 全表逐页对照 | 无 | **会往真实领域写探针卡** `zz-list-index-probe`，`finally` 删 |
| `markdown-test.ts` | 正文渲染的链接口径 | 无 | 只读 |
| `attach-check.ts` | 附件解析器与匹配口径的基线回归 | 无 | 只读，但要求 `raw/综合毕设指导书` 语料在 |
| `collector-python-test.ts` | 采集器解释器探测逻辑 | 无 | 只读；会 spawn python 多次 |
| `python-selftest.ts` | 跑 `collector/tools/selftest_*.py` | 位置参数：脚本名，可多个 | 取决于被跑的自检 |

`mcp-smoke-test` 与 `list-index-test` 是唯一两个碰真实数据的。前者用 `SMOKE_ARTIFACTS` 正则限定「只删自己造的东西」——`.staging/` 里可能躺着别人待审的草稿，`.trash/` 是合并/删除卡片的唯一回收站，整棵树 `rm -rf` 会把这些一起抹掉。

## 迁移与回填（默认全是 dry-run）

| 脚本 | 语义 | 默认 | 落盘开关 | 幂等 |
| :-- | :-- | :-- | :-- | :-- |
| `migrate-card-ids.ts` | 按领域包 `card_id_pattern` 重算 id 并重命名文件 | dry-run | `--apply` | 是（已是目标 id 的不动） |
| `migrate-conflicts.ts` | 回收已收敛的 `import_conflicts`，`status: 冲突` 退回 `待核实` | dry-run | `--apply` | 是（再跑 `would_change` 为 0） |
| `migrate-award-to-student.ts` | 获奖名单并入学生名册 | dry-run | `--apply` | 是（重复记录不追加） |
| `migrate-tag-ids.ts` | 旧式点分 tag ID → 新单段 ID | dry-run | `--write`（注意不是 `--apply`） | 是（新 id 不是映射键） |
| `migrate-collected-at.mjs` | 给缺 `collected_at` 的卡补值 | **直接写盘，没有 dry-run** | 无 | 是（已有该字段跳过） |
| `backfill-source-body.ts` | 给空正文卡生成最小「来源」小节 | dry-run | `--apply` | 是（只填空正文） |
| `backfill_timestamps.ts` | 从 git 历史回填 `created_at` / `edited_at` | dry-run | `--apply` | 是（只补缺失字段） |
| `optimize-mentor.ts` | 把 `ext.research` 拆进 `tags`、截断过长 summary | **直接写盘，没有 dry-run** | 无 | 部分（tags 去重，但 summary 截断累加 `...`） |
| `optimize_mentor.py` | 同上，Python 版 | 直接写盘 | 无 | 同上 |
| `llm_clean_tags.py` | 用 LLM 清洗导师 tags，直接写卡 | 直接写盘 | 无 | 否（每次重新请求） |
| `apply-paper-summaries.ts` | 读 `inbox/paper-summaries.jsonl` 的 `op=update` 行改卡 | 直接写盘 | 无 | 是（值相同跳过） |

`migrate-collected-at.mjs`、`optimize-mentor.ts`、`optimize_mentor.py`、`llm_clean_tags.py`、`apply-paper-summaries.ts` 是这条流水线上**没有 dry-run 的几个例外**，跑之前先 commit。它们都是早期一次性任务留下的，没有 `--apply` 保护。

`migrate-tag-ids` 的开关叫 `--write` 而不是 `--apply`，与系列里其他脚本不一致，照抄命令时最容易混。

## 采集导出（只写 inbox/）

| 脚本 | 职责 | 关键参数 | 输出 |
| :-- | :-- | :-- | :-- |
| `collect-export.ts` | `pipeline.db` → 文章卡投影行 | `--mode enrich\|index`、`--out`、`--urls-file` | `inbox/collect-articles.jsonl` 或 `inbox/collect-index.jsonl` |
| `crawl-export.ts` | `crawl.db` → 教师卡投影行 | `--config`、`--db`、`--out` | `inbox/crawl-<family>-teachers.jsonl` |
| `paper-summary-export.ts` | `pipeline.db` 的论文摘要 → paper 卡投影行 | 无 | `inbox/paper-summaries.jsonl` |
| `collect-enrich.ts` | 以卡片为队列补正文 | `--limit` / `--source` / `--backend` / `--delay` / `--retry` / `--dry-run` / `--max-updates` / `--domain` | **会写卡** |
| `zhihu-enrich-loop.ts` | 长跑版：按时间窗口反复补正文落卡 | `--minutes` / `--gap-min` / `--batch` / `--drain-batch` / `--window-hours` / `--platform` / `--backend` | **会写卡** |
| `import-jsonl.ts` | 通过 MCP 调 `card_import` 的本地 runner | `<jsonl> <domain>` + `--write` / `--merge` / `--max-updates N` | 默认 dry-run |
| `mcp-tool.ts` | 通用 MCP 工具 CLI，入参写成 JSON 文件 | `<toolName> <args.json>` | 取决于工具 |
| `prepare-courses.ts` | 课程大纲目录 → `inbox/courses.jsonl` | `[src] [out]` | 写 `inbox/`，`.doc` 走 Word COM |
| `scan-collector-pii.ts` | 落卡前扫采集正文的 PII 形状 | 无 | 只读 |
| `attach-check.ts` | 附件解析基线 | 无 | 只读 |

前三个是纯投影器，一条铁律：**不参与写入决策**。判重、合并、冲突、来源登记全归 `importTable`，它们只做「换一种说法」。

`collect-enrich` / `zhihu-enrich-loop` / `paper-cnki-summary` / `mentor-papers-summary` 是四个会真的写卡的采集侧脚本，它们都不经 `--write` 开关——只要不是 `--dry-run` 就直接落。这是与迁移类相反的默认值，别混。

## LLM 加工

| 脚本 | 职责 | 关键参数 | 破坏性 |
| :-- | :-- | :-- | :-- |
| `batch_llm.ts` | 通用流水线引擎，配置即任务 | `--config <json>`、`--limit N`、`--only id1,id2`、`--dry-run` | 取决于配置的 `save_mode`：`jsonl` 只产行，`direct` **直接改卡** |
| `mentor-papers-summary.ts` | 反向聚合论文 → 写导师卡「论文总结」小节 | `--dry-run` / `--limit` / `--only` / `--force` / `--max-writes` | **直接写卡** |
| `paper-cnki-summary.ts` | 知网 paper 卡补摘要（四段串起来） | `--limit` / `--dry-run` / `--write` / `--backend` | 默认只预演 |
| `paper-title-fix.ts` | 用本地 DOI 查找缓存校准论文标题 | `--apply` / `--only` | 默认 dry-run |
| `test-llm.ts` | 调一次 `callLLM` 验证凭据与端点 | 无 | 只读（消耗配额） |
| `test-filter.ts` | 手工验证 `ext.mentors` 过滤口径 | 无（硬编码 `mentor-001`） | 只读 |

`batch_llm` 是唯一「加一份配置就多一个任务」的引擎，`pipelines/*.json` 全是它的配置。`mentor-papers-summary` 特意不走它：那个引擎是「一卡一字段」，而论文→导师是反向索引，还需要 map/reduce 两阶段。

`test-llm.ts` 与 `test-filter.ts` 是调试留档：前者硬编码一段中文 prompt，后者硬编码 `domain='paper'` / `filter={'ext.mentors': 'mentor/mentor-001'}`——三卡制后 `domain='paper'` 已指向不存在的目录（`collect_paper` 才对），跑起来会得到空结果而不是报错。看到这张卡有没有被正确筛出，用列表页或 `card_list` 更可靠。

## 一次性历史脚本（Python / CJS / PS1）

这些是当初某个数据导入任务的一次性工具，路径与领域名都停在旧结构上，**不建议当参考实现读**：

| 文件 | 当初做什么 | 现状 |
| :-- | :-- | :-- |
| `parse-guidebooks.cjs` | 扫 `raw/综合毕设指导书` 的 docx，从表格提题目与行 | 读旧 `cards/thesis` 口径；有 `DEBUG_IDX` 单文件调试模式 |
| `analyze-guidebooks.cjs` | 同上 + 与主表比对、目录编号错位归因 | 输出 `inbox/guidebooks.jsonl` + `inbox/match-report.txt` |
| `build-guidebook-cards.cjs` | 从 guidebooks 生成待建卡正文与 plan | `rmSync` 并重建 `inbox/guidebook-bodies/` |
| `extract-archives.cjs` | 解压 rar/zip 到所在目录 | 幂等（同名跳过）；临时目录 `__rar_tmp__` 会删 |
| `import-edu-info.mjs` | 从 `../edu-info` 导入导师/时间线/任务书/公告 | 写 `cards/mentor`、`cards/academic`（旧单层目录） |
| `word-to-docx.ps1` | Word COM 批量 `.doc` → `.docx` | 被 `prepare-courses.ts` 调用；每次 `SaveAs` 后校验文件大小 ≥512 字节 |
| `optimize_mentor.py` / `llm_clean_tags.py` | 见迁移表 | 直接写盘 |

`word-to-docx.ps1` 值得单独看一眼：它的容错不是「重试三次」这么简单。每次失败都 `Quit` 并重启 Word（`Stop-Word` 直接 kill `winword` 进程），因为 Word 崩溃后会卡在僵死状态，同一个 COM 实例继续调只会继续失败。`SaveAs` 返回成功后还要 `Test-Path` + 长度检查——「返回了不代表落盘完成」，Word 崩溃时可能留下空文件或根本没写。

## 下划线开头的脚本

`_dep.cjs` / `_filter.cjs` / `_idstat.cjs` / `_scan.cjs` / `_patch.js` 是 `.scratch/` 里搬回来的临时排查片段：查依赖装没装、过滤 `match-report.txt` 的未匹配行、统计各目录中文 id 数量、扫原始材料目录、以及一个按段落切任务书的实验版解析器。全部硬编码路径，没有 dry-run 概念，只作为历史留档存在。

## 本地服务与状态判断

`serve-local.mjs` / `preview-server.mjs` / `needs-build.mjs` 三个小脚本，各自解决一个具体问题，见 local-server 页。

## 另见：crawl-export / import-jsonl 的端到端上下文

`crawl-export.ts` 与 `import-jsonl.ts` 在这页只有一行定位。它们所在的完整链路
（教师主页 spec → `collect_site.py` → `crawl.db` → `crawl:export` → `import:jsonl` → `batch_llm` 简介清洗）、
各自的 CLI 参数全集、以及 `crawl-export.ts` 里那四段实质逻辑（`buildBody` 的排序语义、
`buildRecord` 的 15 项映射、`summary` 兜底、`_clear` 的空值例外）记在
`infohub/collector/crawl-db-jsonl-llm`。
