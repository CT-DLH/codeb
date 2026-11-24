---
title: Distill gates and their silent failure modes
covers:
  - distill/sessions.py
  - distill/distill.py
  - distill/
updated: 2026-11-18
---

# 会话蒸馏器的六道闸门与它们的失败模式

`distill/` 把 DSH 原始会话读成素材再产出知识候选。它的价值不在 LLM，
而在六道会把候选**拦下来**的闸门；每道闸门都对应一个已实测过的静默故障或造假模式。
证据不足时它诚实地产出 0 条可落库候选，而不是硬凑一页。

## 结论先行

- 素材层 `sessions.py`：会话 → 结构化素材（探索成本、纠正、失败、已落库记录）。纯 stdlib，不写库。
- 候选层 `distill.py`：素材 → 候选 → 预填好的 `kb upsert` 命令；`--apply` 才落库。
- 任何一道闸门失效时，故障表现都是**静默产出大量重复页或噪音页**，而不是报错。
  所以这个工具的正确性完全取决于"查询失败必须响亮失败"。

## 为什么探索成本必须剔除知识库自己的页

最初把「读过某文件 ≥3 次」当成"这块知识已付费、该沉淀"，实测 8 条候选里 **4 条是读
`repo/` 下的知识页**，3 条路径已在磁盘上消失，真正的源码发现是 0 条。

读知识库的页是**在用库**，不是在**产出库**——把它算进成本会让每次正常的库查询都变成
一条"建议新建重复页"的候选。现在单独计 `kb_page_reads` 并跳过，`kb where` 的闸门才第一次
真正生效。

副产品：`kb_page_reads` 本身是个有用的指标，它量化了"这个会话到底有没有在消费知识库"。

## 为什么探索成本只看次数，不看跨回合数

曾加过 `turns >= 2`（同文件被多个回合碰过才算深度探索），结果 **S1 直接清空**。
现实是几乎所有付费探索都发生在一个回合内：一次连续读 5 个文件把它们读懂。
深度不由时间跨度定义。这条门槛已删除。

## 查询失败绝不能被当成"没有页面覆盖"

`covered()` 走子进程调 `kb.py where`。它的失败模式是**返回空列表**，而空列表的语义正是
"没有任何页覆盖这个路径" → 闸门判定为新知识 → 落库 → 重复页。

所以 `kb_alive()` 会先探一次 `kb tree`，不通就直接退出码 2 报错，不继续跑。
这不是防御性编程，是这个工具唯一的正确性依赖。

## 骨架不许落库

`draft_ready` 是硬门槛：没有 LLM、或 LLM 写不出 `why_not_obvious` /
`rejected_alternative` 的候选，一律只有骨架正文，`--apply` 会跳过它。

唯一逃生口 `--force` 也不许 `--append` 进真实页：它把候选转到 `--topic pending` 下新建，
于是 `[待补]` 清单自成一个折叠子节点，一眼能清、不会污染已有页面。
判据是「噪音页比缺页更糟」：缺页只是没信息，噪音页让读者不知道信哪个，而且之后没人会去合并。

## 已知问题

- 一次跑完 13 个会话约 53 秒，瓶颈是 `kb where` 反复起子进程；
  `_COVER_CACHE` 已缓存（一次蒸馏里库不变），但仍偏慢。真要提速得给内核加批量查询。
- `kb.py --json tree` 返回扁平 `items[]`，不是 `dirs/pages` 嵌套树；
  `where` 返回 `hits[]`。按直觉写解析会静默拿到空结果——正好撞上上面那条故障。
- 信号只给"候选位置"（哪条消息、哪个文件），**不给判断**。
  S2/S4 依赖中文句式正则（`CORRECTION_RE` / `TRADEOFF_RE`），漏报是常态，
  别把它当覆盖率指标用。
- 中文标题会让内核退化成 `page-<hash>` 文件名（见 `codeb/defects`），
  所以候选的 `title_en` 一律用英文。

## 怎么跑

```bash
# 1) 素材：把 DSH 历史会话读成结构化 JSONL（只读，不碰库）
python distill/sessions.py material --cwd codeb -o _kbwork/materials.jsonl
python distill/sessions.py report   --cwd codeb -o _kbwork/report.md    # 人读版
python distill/sessions.py list                                         # 便宜清单，不解码

# 2) 候选：素材 → 闸门 → 预填好的 kb upsert 命令（默认 dry-run，不落库）
python distill/distill.py --materials _kbwork/materials.jsonl \
  --report _kbwork/candidates.md -o _kbwork/candidates.jsonl

# 3) 落库：只对 draft_ready 的候选生效；--id 选编号
python distill/distill.py --materials _kbwork/materials.jsonl --id 1,3 --apply
```

会话存储位置由 `~/.dsh/sessions/<cwd-slug>/<session-id>/session.v4.jsonl.zstd` 决定，
`--cwd` 是对 slug 的子串过滤（`--cwd codeb` 命中 `--D-work-project-codeb--`）。

`--llm` 四挡，**默认 `nvidia`**（读 infohub 的 `.env`，见下节「LLM 配置」）：
`nvidia` / `openai`（同一实现）/ `none`（只出骨架线索）/ `cmd`（外部命令，`KB_DISTILL_CMD`，
用临时文件传参，避免 Windows 沙箱下 piped stdio 永久阻塞）。
`--verbose` 打印 LLM 失败原因。

**没有模型、或模型给不出可核对事实时，这套东西产出的是线索，不是知识**——这是设计，不是缺陷。
六道闸门会让它诚实地返回 0 条可落库候选，而不是硬凑一页。

## 为什么它不算第二个写入路径

`kb_upsert` 仍是唯一写入口：`distill.py` 落库时 spawn `kb.py upsert`，
不自己写 md。它加的只是**上游的闸门**（值不值得写、该并进哪页），不是新的写入规则。

## 已知缺口

- `--covers` 用的是文件路径，而 `kb where distill/`（目录级反查）只有 `covers` 以 `/` 结尾
  才做前缀匹配。所以本目录的页应声明 `distill/` 而不是逐个文件。
- 慢点在 `kb where` 反复起子进程（`covered()` 已缓存，仍偏慢）；
  真提速要给内核加批量查询。
- 中文标题会让内核退化成 `page-<hash>` 文件名，所以候选标题一律走英文（见 `codeb/defects`）。

## LLM 配置（NVIDIA，与 infohub 共用一套）

`--llm` 默认就是 `nvidia`，不需要额外参数。配置**不复制、不新增**，直接复用
infohub 那份已被验证可用的 `.env`：

- 真源：`D:\work\project\infohub\collector\.env`（已被 infohub 的 `.gitignore` 排除）
- 键名：`ZHIHU_LLM_API_KEY`、`ZHIHU_LLM_BASE_URL`、`ZHIHU_LLM_MODEL`、`ZHIHU_LLM_MAX_TOKENS`
- 默认值（`load_env()` 读不到时的兜底，与 infohub 一致）：
  - base_url `https://integrate.api.nvidia.com/v1`
  - model `nvidia/nemotron-3.5-lightning-30b-a3b`
  - max_tokens `4096`
- 查找顺序：真实环境变量 → `ENV_CANDIDATES` 里的 `.env`。**只取 `ZHIHU_LLM_*` 与
  `LLM_DISABLE_THINKING`**，因为那个 `.env` 里还有 BILI_COOKIE / XHS_COOKIE /
  OPENALEX_API_KEY，整文件加载会把无关凭据带进本进程。
- 用 `utf-8-sig` 读 `.env`：Windows 上手工编辑的文件常带 BOM，不 strip 掉认不出键名。

### 必须关 thinking，否则必然拿到空正文

推理型 Nemotron 会先吐 `reasoning_content` 把 `max_tokens` 吃光，`content` 变成空串。
所以当 base_url 含 `nvidia.com` 且未设 `LLM_DISABLE_THINKING` 时，要在 **payload 顶层**
带 `{"chat_template_kwargs": {"enable_thinking": false}}`。
这是拿得到结果的硬前提，不是可选优化。`_content_of()` 会区分这种情形并报出
`reasoning 吃满了 max_tokens`，而不是笼统说"空返回"。

### 降级与重试

三级降级 `json_schema → json_object → 纯文本抠 JSON`，因为 NVIDIA 端点对
`json_schema` 支持不稳定。只在 HTTP 400/404/422 且错误文本提及
`response_format` / `json_schema` / `unsupported` 时才降级；超时与网络错误
**不降级**，那是重试该解决的事。每级内部对 429 做 5s/10s 退避，`temperature=0`。

## 六道闸门（全部经真实数据验证）

一条候选要落库必须依次通过：

| # | 闸门 | 拦什么 | 实测证据 |
| :-- | :-- | :-- | :-- |
| 1 | `kb_alive()` 自检 | kb 查询失败被当成"没有页覆盖" | 不通即 rc=2 退出 |
| 2 | `kb where` 去重 | 已覆盖路径重复建页 | S1 从 4 条降到 0 |
| 3 | 路径存在性 | 已删除/临时文件进 covers | `kb_page_reads` / `stale_reads` 单列 |
| 4 | `draft_ready` + `kind` | 骨架正文、审计线索落库 | S7 恒 `draft_ready=False` |
| 5 | `verify_facts()` | **正文里编造的文件路径** | 抓住 9 个不存在的模块 |
| 6 | `substance_ok()` | 占位符与模板空壳 | 抓住 `[工具文件名 5..24]` 整页 |

第 5、6 道是这轮新增的，起因是实测：一个采集子系统的描述写出了
`collector/entry.py::start_collection()`、`states.py`、`retry.py`、`circuit_breaker.py`、
`plugin_manager.py::load_plugins()` 等**九个模块，仓库里一个都不存在**。
它写的是"这类项目通常怎么实现"，不是"这个项目就是这样"。
第 6 道拦的是另一种失败：没编造任何路径，但整页是 `[工具文件名 N]` 这类占位填充——
事实闸门会放行，因为确实没有假路径可核。

## 无模型时的结论（重要）

跑 13 个真实会话、6 条候选，六道闸门后**可落库 0 条**。这不是工具坏了，是它诚实：
S2（用户纠正）的证据是**用户原话，不含源码**，模型拿不到可核对的事实就只能填模板或编造。

所以 S2 当前的正确定位是**"提示人去读哪段"的线索**，不是可直接落库的知识。
要让它产出知识，得先把该会话真实读过的源码片段塞进 `PROMPT` 的 `{context}`
（现在只塞了 corrections/claims/failures 的 380 字摘录）。在那之前，
**把 S2 的结果当待办清单用，不要当草稿用**。
