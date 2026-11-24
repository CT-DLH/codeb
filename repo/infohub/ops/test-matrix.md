---
covers:
  - scripts/mcp-smoke-test.ts
  - scripts/ingest-test.ts
  - scripts/taxonomy-test.ts
  - scripts/sensitive-test.ts
  - scripts/derive-test.ts
  - scripts/list-index-test.ts
  - scripts/markdown-test.ts
  - scripts/attach-check.ts
  - scripts/collector-python-test.ts
  - scripts/python-selftest.ts
updated: 2026-11-17
---

# Test matrix: what each suite proves, and which to run after a change

这一页不记断言条数（那会随提交漂移）。要精确数字，跑一次看末尾输出的「全部通过：N 条断言」——
每个套件自己会报。这里记的是**每个套件证明什么、以及改完什么必须跑哪条**。

## 判据：这个测试能不能发现我改坏的东西

有几个是**端到端**的（真起进程、走真协议），其余是**对照**的（拿两条独立实现互相校验）。
后者更有价值，因为它证明的是「两套口径一致」，而不是「一条路径能跑通」。

## 两个大件

### mcp-smoke-test.ts — 全仓最重的测试

用真实 stdio 起 `src/mcp/server.ts`（`StdioClientTransport` + `node_modules/tsx/dist/cli.mjs`），
然后逐项调工具。它是**端到端**的：断言的是 MCP 协议的返回值，不是内部函数。

覆盖：工具清单全排列（**这条断言就是工具集的真源**，加减少一个工具必须同步改它）、Schema 发现、`dry_run`、领域与对象类型白名单、`card_create` 正常写入、
`card_read` / `card_list` / `card_search`、`card_update` + `card_commit` 两阶段、
`card_import` 预演与落盘、`card_attach`、`domain_create` / `domain_update`、
未知工具走协议级错误、通知不回复。

**单次工具调用给 120s 超时**。理由写在注释里：三卡制后全库上万张卡，`card_search` 不带 domain
时要扫全库（实测秒级），SDK 默认 60s 在慢机器上会偶发 `-32001`。

**为什么不用 mock**：本项目构建期发现的缺陷（根路径算错、小节拼接破坏结构、位置参数被忽略、
`bodyFile` 重复标题）全部只在真实进程下暴露。mock 边界等于把最该测的东西测掉。

### ingest-test.ts — 导入内核的单元测试

覆盖解析（xlsx / csv / tsv / jsonl / md / pdf）、列映射、类型还原、identity 三步匹配、
`card_id` 模板、字段合并冲突、策略分支、隔离区。

它是**唯一**覆盖 `mergeFields` 九级判定与 `import_conflicts` 回收的地方。改合并逻辑必跑。

## 按类型分的对照套件

| 套件 | 证明什么 | 改完什么要跑 |
| :-- | :-- | :-- |
| `taxonomy-test.ts` | 祖先关系沿 `parent` 链上溯，**与 ID 字符串前缀无关**；生产 loader 与内核口径一致 | 动 `tree-core.ts` / `loader.ts` / `_taxonomy/` |
| `sensitive-test.ts` | 领域包标记后，详情页 / 列表页 / 分片 JSON 三条出口都拿不到值；`__BUILD_STATIC__` 与 `INFOHUB_SENSITIVE` 组合行为 | 动 `sensitive.ts` / 任何 marshal 出口 |
| `derive-test.ts` | 规则只声明在领域包；值只来自原文匹配片段；链式规则靠不动点一次跑完；重跑不产生变更；已有值默认不覆盖；**提不出/没原文/正则写错三种原因分得开** | 动 `derive.ts` / 加 derive 规则 |
| `list-index-test.ts` | 索引给出的行序 / 筛选 / 分面 / 计数，与「全表 + 前端那套排序」逐项一致 | 动 `card-store.ts` 的分页索引或排序 |
| `markdown-test.ts` | 采集来的 markdown 里相对链接/图片指向**原文那页**，不是本站 | 动 `markdown.ts` / 预渲染爬链 |

`markdown-test` 值得单独说：预渲染器会跟着 `<a href>` 爬，一条 404 就能把整场构建炸掉。
这个测试就是那条链路的护栏——**它不是「渲染对不对」的测试，是「构建会不会崩」的测试**。

## 采集器侧的套件

### collector-python-test.ts

测试**解释器选择**。踩过的坑：本机 PATH 上的 `python` 启动得了，但装的是另一套依赖，
知乎源要 `import` 的模块在它那儿不存在——原先 `collect_run` 只看文件在不在就选中了它。

所以这个测试证明的是「选出来的解释器真的能 import 到采集器需要的模块」，
不是「python 命令存在」。

### python-selftest.ts

跑 `collector/tools/selftest_*.py`。为什么要这一层：那些自检是纯 Python 的，
但解释器得按「能不能真的 `import` 到依赖」来选——和上一条同源。
它把「跑哪些 selftest、用哪个解释器」这件事收进一条命令。

### attach-check.ts

**只读**的附件解析体检：拿真实任务书语料验证解析器与匹配口径，不改任何卡片。

基线是「全部解析成功、唯一命中 / 多命中 / 无卡各若干」——具体条数由脚本自己报。
解析器改坏了这里会红。这是唯一用**真实语料**而不是构造 fixture 的检查。

## 改完什么跑哪条

| 改动位置 | 必跑 |
| :-- | :-- |
| `src/core/ingest.ts`（合并、identity、card_id） | `test:ingest` |
| `src/core/derive.ts` 或领域包加 `derive` | `test:derive` |
| `src/core/attach.ts` / `parsers/` | `attach:check` |
| `src/lib/sensitive.ts` | `test:sensitive` |
| `src/lib/server/card-store.ts`（索引/排序/分页） | `test:list` |
| `src/lib/markdown.ts` | `test:markdown` |
| `src/lib/taxonomy/` 或 `_taxonomy/` | `test:taxonomy` |
| 任何 `src/mcp/` | `test:mcp` |
| 任何 `collector/` | `test:collector` + `test:research` |

## The one that is not a test

`npm run validate`（`scripts/validate.ts`）不是测试，是**构建前置校验**：
它检查领域包能否加载、卡片能否通过 Schema。`export:static` 第一步就是它。

区别：测试证明「行为符合预期」，`validate` 只证明「数据能加载」。
字段写错时 `validate` 会红，但逻辑写错它看不出来。

## 一个常被忽略的事实

**没有单元测试框架。** 这些脚本各自 `throw` / `process.exit(1)`，没有 describe/it，
也没有覆盖率统计。这是刻意的选择：每个套件要证明的事情是**一组具体口径**，
不是「函数被调用了」。加断言靠往现有脚本里加一段，不需要引入依赖。

代价是失败时只能看打印的那一行，不能按用例筛选。所以每条断言都写成
**能独立读出「哪里错了」的句子**（「kb_where 目录级 covers 前缀命中」而不是「test 4」）。
