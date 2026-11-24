---
covers:
  - distill/agent/loop.py
  - _kbwork/probe_frameworks.py
  - _kbwork/probe_agents_e2e.py
  - _kbwork/probe_subagent_dispatch.py
  - kb.py
  - distill/agent/codeb_agent.py
  - distill/agent/tools_fs.py
  - distill/agent/spawn.py
  - mcp/server.ts
  - _kbwork/plan-sidebar-split.json
  - distill/agent/context_cache.py
title: Surveying agent bases: what each one actually costs
updated: 2026-11-22
---

# Surveying agent bases: what each one actually costs

上一页 `subagent-base` 只对比了 pi 与自己写，那是**没先盘点就二选一**。
这一页把候选全量实测一遍，全部数字都来自本机安装后的真实测量，不用印象。

## 结论

| 用途 | 选什么 |
| :-- | :-- |
| 只做只读工具调用、自己控流程 | **自己的 `loop.py`**（319 行，0 依赖） |
| **要派子 agent、要 handoff、要 session 持久化** | **`openai-agents`**（唯一完整满足） |
| 想要「极简但成熟」 | 没有真正极简的成熟选项，见下 |

## 全量实测（`_kbwork/probe_frameworks.py`）

依赖数取 `requires_dist` 里不带 extra 标记的条目；行数取 wheel 内 `.py` 实测。

| 包 | 版本 | 核心依赖 | 实测行数 | 能派子 agent |
| :-- | :-- | --: | --: | :-- |
| **`openai-agents`** | 0.25.0 | 13 | 装后 40 个分发包 / 96.3 MB | **✓ `as_tool` + `handoff`** |
| `claude-agent-sdk` | 0.2.187 | 5 | — | 只驱动 Claude Code，绑死 |
| `pydantic-ai` | 2.71.0 | 1（+slim） | — | ✓ |
| `smolagents` | 1.26.0 | 6 | — | ✓ 但主打「模型写 Python」 |
| `langgraph` | 1.2.24 | 6 | — | ✓ 图式，重 |
| `agno` | 3.2.1 | 10 | — | ✓ |
| `thinharness` | 0.8.0 | 2 | **12,278 行** | 有 subagent 但明确「不做 compaction」 |
| `nextloop` | 1.1.0 | 2 | **10,068 行** | 有，且内置 compaction |
| `looplet` | 0.4.1 | **0** | **56,893 行** | 有 |

## 「minimal」这个词不能信

三个自称轻量的候选，实测行数：

```text
looplet      56,893 行   核心依赖 0     ← 最大，是 loop.py 的 178 倍
thinharness  12,278 行   核心依赖 2
nextloop     10,068 行   核心依赖 2
loop.py         319 行   核心依赖 0
```

`looplet` 的 PyPI summary 是「A Python loop for agents that call tools」，
核心依赖确实是 0——但它的 0 依赖是靠**把什么都自己写一遍**换来的：
自带 `evals.py` 3,660 行、两套完整的 coder cartridge（含 bash/grep/edit/glob/subagent）、
`cartridge/_serialise.py` 1,470 行、`provenance.py` 1,440 行、`cli/` 两个命令文件。

`loop.py` 同一个文件的规模对比：looplet 的 `loop.py` **4,201 行**，我们的 **319 行**。

这不是说 looplet 写得差。**它解决的是别的问题**：可发布的 agent cartridge、评测、
溯源、热重载。我们要的只是「多轮工具调用 + 折叠」，多出来的 5.6 万行不会因为我们
不用而不存在——它会在升级、排查、读懂行为时逐笔收账。

**教训：选基座要看 wheel 里的行数，不看 summary 里的形容词。**

## openai-agents：唯一完整满足的

四条硬约束逐条实测（`_kbwork/probe_agents_e2e.py`）：

| 约束 | 结果 |
| :-- | :-- |
| C1 接自定义端点 + extra_body | ✓ `OpenAIChatCompletionsModel(model=..., openai_client=AsyncOpenAI(base_url=...))`，源码里 `extra_body` 出现 2 次 |
| C2 工具是进程内函数 | ✓ `@function_tool` → `FunctionTool`，有 `.on_invoke_tool`，直接调 `kb.main()` |
| C3 逐条折叠 | ✓ **`agents.extensions.ToolOutputTrimmer`** |
| C4 依赖可数 | ✗ 40 个分发包 / 96.3 MB |

代价是 C4 不满足。但这是唯一一个把「派子 agent」做成一行 API 的：

```python
worker.as_tool(tool_name="assign_kit", tool_description="派给负责 kit 的执行者")
```

## 意外收获：ToolOutputTrimmer 就是我手算的那个设计

`agents.extensions.ToolOutputTrimmer` 的构造参数：

```python
ToolOutputTrimmer(
    recent_turns: int = 2,           # 最近几轮不折
    max_output_chars: int = 500,     # 超过这个长度才考虑折
    preview_chars: int = 200,        # 折叠后留多少预览（0 = 纯墓碑）
    trimmable_tools: str | Iterable[str] | None = None,   # 按工具名区分！
)
```

**四个参数与我上一轮独立算出的四个维度一一对应。** 尤其 `trimmable_tools`——
它证明「按工具区分折叠策略」不是我一个人的怪想法，是一个被独立实现过的正确设计。

`preview_chars=0` 就是我说的「墓碑」。

这改变了上一轮的判断：**折叠参数不该挂在每次调用上，这件事有第三方实现背书**。

## 派子 agent 实测：42–74 秒，三份上下文各自独立

`_kbwork/probe_subagent_dispatch.py` 用真实的 codeb 工具跑：

```text
步骤 1  leader 用 kb_dispatch 切范围
  范围 3 个 · 冲突 0 个
  共享页: 6 个
  全局串行点: collector/capabilities.json
  → 可以并行: True

步骤 2  leader 派活
  耗时 50117ms   调用子 agent: [assign_collector_kit, assign_collector_refs, assign_collector_sites]
```

回答质量是对的，例如 kit 的执行者报出了：

> **A.** *No upward (L2/L3) dependencies* – the module must not import `sources`,
> `zhihu_pipe`, or `site_crawl`.
> **B.** *Portability / "single criterion"* – code must stay site-agnostic.

这两条正是 `kb_pack` 装进去的 `infohub/collector/architecture` 里的内容。
**子 agent 没有读源码，只读了册子，答对了约束。**

## 但它漏派过，而且原因不是框架

第一版跑 3 个范围只派了 2 个（漏 `sites`），且答案变成英文。
我一度怀疑是框架吞任务——**这是会一票否决的问题**，所以专门复测。

复测三次，全派全，全中文：

| 配置 | 耗时 | 派了几个 |
| :-- | --: | :-- |
| `max_turns=8` | 50.1s | 3 / 3 |
| `max_turns=12` | 73.9s | 3 / 3 |
| 显式「一次只派一个」 | 64.3s | 3 / 3 |

差别只在 instructions 的写法：第一版写「各挂了一个执行者」，
复测改成「**必须三个都派，一个都不能漏**」「最后用中文汇总」。

**结论：leader 级别的任务分发，指令里必须显式点名数量与语种。**
这是 LLM 的措辞敏感，不是框架缺陷。但代价是——你没法靠框架保证派全，
只能靠指令 + 事后校验。所以真正需要的是**派完检查**：

```python
missing = [s for s in scopes if f"assign_{slug(s)}" not in called_names]
```

这一段必须自己写，任何框架都不给。

## 选型建议

**如果只要「agent 能查知识库」** → 继续用自己的 `loop.py`。
319 行、0 依赖、工具调用 54ms（进程内），比 openai-agents 的 96 MB 划算得多。

**如果要「派多个子 agent 并行干活」** → 用 `openai-agents`。
理由不是它功能多，而是这三件事自写代价高且容易错：

1. `as_tool` 的输入输出契约（子 agent 的返回值要变成父 agent 能读的字符串）
2. 并行的 turn 计数与错误隔离（一个子 agent 挂了不能拖垮整批）
3. session / tracing（排查「为什么这个子 agent 拿错了上下文」时没有它几乎不可能）

**不要选的**：
- `claude-agent-sdk` — 绑死 Claude Code 的运行时，我们的 NVIDIA 端点用不了
- `langgraph` — 图式编排，为了「派三个任务」引入整套状态机
- `thinharness` / `nextloop` — 规模不小（1 万行）但生态薄，遇到问题没人答
- `looplet` — 5.7 万行，它的复杂度服务于「可发布 cartridge」，不是我们的问题

## 落地

- `distill/agent/loop.py` — 319 行，零依赖，单 agent 够用
- `_kbwork/probe_agents_e2e.py` — openai-agents + NVIDIA + 三个 kb 工具，端到端
- `_kbwork/probe_subagent_dispatch.py` — leader + 三个子 agent，各自 `kb_pack`
- `_kbwork/probe_alternatives.py` — 全量体量与依赖测量，可重跑
- 探针用的 venv 在 `_kbwork/agvenv/`（96 MB，只做实验，不进项目依赖）

## codeb 子 agent 体系（2026-11-21 补齐，正式路径）

`spawn.py` 的**硬伤**：只有 `read_file` / `grep_text`，**只能读不能改**。
任何「在范围内改代码」的任务它都派不动——不是配置问题，是能力缺失。
真实派发（补 docstring、改字段、改路由）全都需要写权限，所以它一直没承接过真实任务。

现在补齐，`spawn.py` 保留为「只读问答」的轻量入口。

**文件**

| 文件 | 职责 |
| :-- | :-- |
| `distill/agent/tools_fs.py` | 文件与命令工具：`read_file` / `read_file_range` / `list_dir` / `grep_text` / `edit_file` / `write_file` / `append_file` / `run_cmd` / `diff_summary` |
| `distill/agent/codeb_agent.py` | 执行入口：`Task` 规格 → Agent → `kb dispatch` + `kb pack` 组装 → 注入执行 → 收结果 |

**组装仍然 100% 来自 `kb.py`**。这两个模块不产生业务逻辑，只做「规格 → Agent → 注入 → 收结果」。

**权限模型：三道防线，越界在工具层就被拦**

1. **全局永久禁止清单**（`DENY_PATTERNS`）。`node_modules/`、`dist/`、`.git/`、`package-lock.json`、`pnpm-lock.yaml`、`*.db`、`*.sqlite`、`*.pb`，**无论白名单怎么写都不能改**。防 agent 顺手改构建产物或依赖锁。
2. **派发时的白名单/禁止清单**（`Task.allowed` / `Task.denied`）。`allowed` 为空 = 不限制，否则必须命中。`denied` 优先级高于 `allowed`。**这是 leader 必须写清楚的东西**——白名单不是文档约束，是工具层的硬检查。
3. **路径解析**。`resolve()` 把相对路径锚定到 `ROOTS` 里声明的仓库根，`../` 逃逸、指向别的仓库的绝对路径一律拒绝。

三道防线**返回文本错误而非抛异常**：抛异常会被 openai-agents 记成 tool error，
模型看不到可读错误，只会重试同一次调用，烧掉整轮预算。

**拒绝信息必须告诉模型「别重试」**。早期版本只写「不要动其他文件」，实测 agent
连续 8 轮反复尝试越界写入直到 `MaxTurnsExceeded`。改进后明确写「**不要重试、
不要绕过、不要间接改**，在报告里说明未改动」，agent 立刻照做，轮次从 8 降到 1。

**实测：越界确实被拦住**。任务故意要求「顺手在 `kb.py` 开头加注释」，白名单只有目标文件。

```
拒绝写入（不在本次白名单内）：kb.py
  白名单：['_kbwork/agent_e2e_a.py']
  **不要重试、不要改用其他写法绕过、不要用 read_file 或其他工具间接改这个文件。**
  白名单之外你无权改动。请跳过这一步，在报告里明确写出「X 文件不在白名单内，未改动」…
```

agent 回应：`**kb.py** 不在本次白名单内，故未对其作任何修改（已按规范在报告中说明）。`
`kb.py` 头两行确认无改动。**边界是实测守住的，不是「agent 应该自觉」。**

**异常处理：失败必须返回「部分结果」，不能抛裸异常**

`MaxTurnsExceeded` / 429 / 超时都让 `Runner.run` 抛异常。**关键设计**：`run_task` 不抛，
调用 `_collect()` 返回结构化 dict，带 `ok: false` + `error` + 已完成的 `steps`。

原因：烧满轮次时模型**可能已经改了一部分文件**。抛裸异常，leader 只知道「失败了」，
拿不到「改了什么」，只能整块重跑，浪费已花的 token 和时间。带 `steps` 才能判断
「哪些已做、哪些要补」。

区分两个阶段：

- **`dispatch` 失败（范围无效）** → `run_many` **主动抛错快速失败**，不把无效任务丢给 agent 白烧轮次。这是正确行为。
- **`Runner.run` 失败** → 收敛为结构化结果，保留已完成的步骤。

**并行：白名单隔离 + 写范围互斥**

`run_many` 先跑一次全局 `dispatch` 验互斥，**有冲突直接拒绝派发**，不并行改同一个文件。

实测两个 agent 各改一个文件：总 21.0s vs 串行和 34.7s（**节省 39%**）。
隔离验证：A 的文件里没有 B 的内容，B 的文件里没有 A 的内容，函数没有被重复复制。

**并行会放大限流**。同一个模型 key 并发调，实测出现过 worker-b 烧满 8 轮
`MaxTurnsExceeded`（单跑同一任务 8.9s 成功）。这是 NVIDIA 端 429 的已知约束
（见 `client.ts` 注释：N 个 key = N 并发是唯一有效加速手段），不是本层缺陷——
但**失败时现在能拿到部分结果了**，这一点比以前强。

**CLI**

```bash
_kbwork/agvenv/Scripts/python.exe -X utf8 distill/agent/codeb_agent.py run \
    --scope "_kbwork/agent_e2e_target.py" --repo codeb \
    --task "给这个文件里每个函数补上中文 docstring…" \
    --allow "_kbwork/agent_e2e_target.py" --budget 4000
```

## 正式入口：`kb agent`

之前它只是 `distill/agent/` 里的脚本，不算体系。现在接成 `kb.py` 的正式子命令。

```bash
python -X utf8 kb.py agent "_kbwork/agent_e2e_target.py" \
    --task "给每个函数补中文 docstring" \
    --allow "_kbwork/agent_e2e_target.py" \
    --budget 4000 --max-turns 8
```

`--repo` 可省略（从 scope 推导）。`--allow`/`--deny` 可重复。`--no-source` 关掉源码装订。
`--json` 输出结构化结果（含 `steps`）。

**依赖方向**：`kb.py` 必须保持 stdlib 零依赖，所以 `cmd_agent` **不 import agents**，
而是 `subprocess` 转发给 `distill/agent/codeb_agent.py`，由那边的 venv 提供 openai-agents。
组装依然是 kb 自己做的（子进程里调 `kb pack` / `kb dispatch`），
**方向永远是 agent → kb，不能反过来**。

`--python` 可指定解释器；默认找 `_kbwork/agvenv/Scripts/python.exe`，没有则用当前解释器。

## 一个真 bug：`with_source` 默认值写错了

`Task.with_source` 最初默认 `False` → 传给 `kb pack --no-source` → 对**没有被知识页
认领的代码范围**装出 **0 块 0 tok**：

```
# 上下文包：_kbwork/agent_e2e_target.py
仓库 `codeb` · 精度 **none** · 预算 13000 · 实装 0 tok · 0 块
> 没有任何知识页认领这个范围，下面只有源码。
## 有意省略
装进 0 块 / 0 tok（预算 13000）。
```

**agent 拿到的是一片空白**，然后靠 `read_file` 自己把源码读回来——这等于绕过了
codeb 的组装，还白花了装订的 token。而我之前的端到端测试「跑通了」（12.9s，
4 次调用 read→edit→edit→run_cmd），**恰恰是因为它自己 read 了**，所以没暴露。

默认改成 `True` 后，同样的范围装进 192 tok（目标文件 29 行全文）。

**这条的教训**：端到端「跑通」不能证明组装正确。必须单独断言
**上下文 tok > 0**，否则 agent 靠工具自给自足也能跑通，管道坏了看不出来。
`_kbwork/test_kb_agent_cmd.py` 的 K2/K3 就是专门断言这件事的：

- `context_tokens >= 150`（装进了源码本身）
- `pack` 输出含 `def add_numbers`（真的装了源码文本）
- 对照 `--no-source` 确实是 `实装 0 tok`（证明默认值必须 True）

## 验证矩阵（全部通过）

| 脚本 | 断言 | 覆盖 |
| :-- | :-- | :-- |
| `mcp/smoke.ts` | 75 | MCP 层全部工具，确认 `kb.py` 改动没破坏现有功能 |
| `_kbwork/test_tools_fs.py` | 25 | 三道权限防线、精确匹配、多次匹配中止 |
| `_kbwork/test_agent_parallel.py` | 9 | 并行节省 39%、白名单隔离、编辑质量、互斥拦冲突 |
| `_kbwork/test_exception_handling.py` | 17 | 异常返回部分结果、长参数截断、范围无效快速失败 |
| `_kbwork/test_kb_agent_cmd.py` | 11 | `kb agent` 跑通、上下文非空、repo 推导、白名单生效 |

前四个不联网；`test_agent_parallel` / `test_kb_agent_cmd` 要真调 LLM。

**验证脚本**（不联网、不调 LLM）

| 脚本 | 覆盖 |
| :-- | :-- |
| `_kbwork/test_tools_fs.py` | 25 断言：三道权限防线、精确匹配、多次匹配中止、正常编辑路径 |
| `_kbwork/test_agent_parallel.py` | 9 断言：并行节省、白名单隔离、编辑质量、互斥拦冲突 |
| `_kbwork/test_exception_handling.py` | 17 断言：异常返回部分结果、成功路径不受影响、长参数截断、范围无效快速失败 |

三者是纯函数层。真机端到端另跑 `codeb_agent.py run` 单条验证（12.9s，
4 次调用 read→edit→edit→run_cmd）。

**与 DSH subagent 的关系**

**这就是用户要求的方向**：子 agent 跑在 codeb 里，上下文由 `kb.py` 组装，
工具由 codeb 提供，DSH 只做顶层编排。之前用 DSH 的 `subagent` 派发是偏离，
现在这套才是正式路径。

分工上仍要遵守：**契约由 leader 定稿、范围由 leader 划、风险由 leader 核实、
结果由 leader 验证**。这套工具保证「子 agent 不会越界」，但不保证「子 agent
会选对方案」——那仍然是 leader 的职责。

## 调度层：并发上限 + 依赖 DAG + 任务边界折叠（2026-11-21 晚）

方案来自一个类比：**主 agent 派多个任务，并发有上限就像 CPU 核数，超出的排队**。
落地时发现原实现有两个真缺陷。

### 缺陷 1：`asyncio.gather` 一次全发，没有并发上限

```python
asyncio.gather(*[run_task(t, env) for t in enriched], return_exceptions=True)
```

全部任务同时发出。实测**同 key 并发 2 个就撞 429**，导致 worker-b 烧满 8 轮
`MaxTurnsExceeded`（单跑同一任务 8.9s 成功）。

改成 `Scheduler` + `asyncio.Semaphore`，默认 `DEFAULT_CONCURRENCY = 2`。

### 缺陷 2：cache 布局是反的

缓存按**最长公共前缀**命中（不需要端点报告，是协议行为）。原实现两处失误：

**a. `instructions` 里插了 `t.scope`**

```python
instructions=f"你只负责写范围 `{t.scope}`，不要碰白名单之外的任何文件…"
```

每个 agent 系统提示词都不同，**从第 20 字节就分叉，所有 agent 之间零 cache 共享**。
改成 `_shared_instructions()`：**不含任何 per-task 内容**，差异约束移到 user 消息末尾。

**b. 知识层排在最前，而它最容易分叉**

`render()` 原本是 scope → dispatch → knowledge。知识层与范围强相关，
换范围整段不同，**放最前面等于后面什么都共享不了**。

改成从稳定到易变：`COMMON_WORLD` → `dispatch` → `knowledge` → 上游结论 → 差异约束 → 任务。

**实测收益**（`_kbwork/test_cache_and_scheduler.py`）：

| 场景 | 公共前缀 |
| :-- | :-- |
| 改前（scope 在 instructions 里） | 0 字节（system 就分叉） |
| 改后·异范围 | **325 字符**（越过 COMMON_WORLD 250 字，进到 dispatch） |
| 改后·**同范围** | **859 / 861 字符（99.8%）** |

**同范围任务的 cache 收益接近满分**——这恰好是最常见的场景（同一批文件派多个任务）。

### 新增：依赖 DAG 与任务边界折叠

`Task` 新增两个字段：

```python
depends_on: list[str] = []   # 必须先成功的上游任务名
persist: bool = False        # 是否把完整轨迹落盘
```

`Scheduler` 的四个行为：

1. **并发上限 = 队列**。信号量压到 N，超出的排队等（不是全放）。
2. **依赖失败 → 下游跳过**，标记 `skipped: true` 而不是「跑了但失败」。
   上游失败时下游拿到的是噪音，宁可跳过也不要让它基于错误前提改文件。
3. **任务边界折叠**：下游只拿上游的 **`conclusion`**（即 `answer`），不拿 `steps`。
   这是最彻底的折叠——不需要裁剪历史，因为**历史根本没进下游的上下文**。
4. **`persist` 决定轨迹是否写盘**。默认只传结论；需要追查时 leader 显式开。

环检测和悬空依赖在 `Scheduler._validate()` 里，构造时即报错。

### 真机验证（`_kbwork/test_chain_real.py`，5/0）

三任务链 step1 → step2 → step3，串行跑：

```
[step1] ok=True  2.5s  该文件包含一个名为 helper_a 的函数。
[step2] ok=True 14.1s  该文件中的函数名为 helper_b。
                       如果引用上游结论，上一步（step1）的结论是：
                       "该文件包含一个名为 helper_a 的函数。"
[step3] ok=True  4.0s  该文件一共包含 2 个函数：add_numbers 与 add_three。
                       （上游结论均涉及其他文件，并未对本文件的函数数量做出描述。）
```

**step2 明确复述了上游结论**；**step3 还正确判断出上游内容与自己的文件无关**——
说明「只传结论」不仅省 token，也没让下游丢失必要信息。
另外 4 个无依赖任务用 concurrency=2 跑，9.1s 全部成功。

### 一个噪音 bug

`asyncio.run` 关闭事件循环后，httpx 连接池的清理协程仍会触发，
打出 `RuntimeError: Event loop is closed`。结果是对的，但**噪音会盖住真正的错误**。
修法是在 `run_task` 的 `finally` 里显式 `await client.close()`，而不是指望 gc。

### 与 `loop.py` 折叠的关系

两套机制**互补，不是替代**：

| | `loop.py`（Ledger） | `Scheduler`（本次） |
| :-- | :-- | :-- |
| 折叠粒度 | 单条工具结果 | **整个任务的过程** |
| 可逆 | 是（`recall(key)` 取回） | 否（过程丢弃，但可 `persist` 留盘） |
| 依据 | 时间（几轮前） | **任务边界**（做完了就没用） |

按任务边界折叠比按时间折叠更强：它有明确语义，知道「这个子任务结束了，
中间所有 read_file / grep 都可以扔」。按时间只知道「旧了」，不知道「还有没有用」。

## CLI 接入：`kb agent` 现在能跑多任务计划

```bash
# 单任务
python -X utf8 kb.py agent "_kbwork/a.py" --task "改 X" --allow "_kbwork/a.py"

# 多任务（依赖 + 并发上限）
python -X utf8 kb.py agent --plan _kbwork/plan.json --concurrency 1
```

计划文件格式（只有 `name`/`scope`/`task` 必填，其余同 `Task` 字段）：

```json
[
  {"name": "s1", "scope": "_kbwork/agent_par_a.py", "repo": "codeb",
   "task": "说明这个文件有几个函数", "max_turns": 3},
  {"name": "s2", "scope": "_kbwork/agent_par_b.py", "repo": "codeb",
   "task": "说明函数名；拿到上游结论请复述", "depends_on": ["s1"]}
]
```

真机跑通（2 任务 1 依赖，concurrency=1）：s1 2.6s / s2 5.0s，合计成功 2。

## 又一个真 bug：CLI 把 dataclass 的默认值废掉了

`Task.with_source` 改成默认 `True` 之后，**CLI 仍然传 `False`**：

```python
r.add_argument("--with-source", action="store_true")   # 默认 False
...
with_source=args.with_source,                          # 显式传 False，覆盖 dataclass 默认
```

于是 `kb agent` 走 CLI 时**永远只装知识层**，对没有知识页认领的范围装出
「0 块 0 tok」，agent 拿到空白上下文。我上一轮以为已经修好，实际只改了 dataclass。

修法：参数语义反转成 `--no-source`，构造时 `with_source=not args.no_source`。
**凡是有 dataclass 默认值的字段，CLI 都不能用 `store_true` 直接传**——
store_true 的 False 会静默压掉 dataclass 的 True。

### 教训：宽松断言会让 bug 蒙混过关

上一轮 `test_kb_agent_cmd.py` 断言 `context_tokens >= 150` 就通过了，
因为**包头部的 dispatch 文字本身就有 71 tok**，加上知识层壳子很容易凑到 150。
真正该断言的是「**源码文本在包里**」：

```python
ok("def add_numbers" in pack_out)                    # 硬证据：源码文本
ok(tok_pack > tok_disp * 1.5)                        # 相对判据，不用魔法数字
```

改成这两条后实测 `pack=342 tok / dispatch=71 tok`，关系清晰。
**端到端「跑通」不能证明组装正确**——agent 靠 `read_file` 自给自足也能跑通。

## 依赖注入已验证正确（一次误判的记录）

`kb agent --plan` 实跑时 s2 报告「目前没有针对本范围的上游结论」，看起来像
依赖没注入。单独验证后确认**注入是正常的**：

- `_kbwork/test_deps_injection.py` 12/0：上游小节确实在消息里（第 785 字符），
  内容、来源名都在，且排在差异约束之前（cache 友好）。
- 单跑 s2 带 deps，模型明确复述：「上游结论（来自「s1」）：该文件里有 1 个函数：
  helper_a(x)…（此结论原指代的可能是 agent_par_a.py，但按要求复述如上。）」

所以那次是**模型行为波动**，不是代码缺陷。任务措辞「如果拿到上游结论请复述」
容易被理解成「只复述与本范围相关的」。要稳定复述，任务里应直接写
「必须复述上游结论原文」，而不是给条件句。

**方法上的收获**：怀疑注入没生效时，先做一次**不调 LLM 的纯 render 检查**
（消息里有那几段吗、位置对不对），把「代码 bug」和「模型行为」分开，
否则很容易去改本来正确的代码。

## 一个并发相关的收尾问题

`asyncio.run` 关闭事件循环后，httpx 连接池的清理协程仍会触发，
打出 `RuntimeError: Event loop is closed`。**不能靠 `await asyncio.sleep(0)` 补**——
清理必须在循环关闭之前跑完。正确修法是在 `run_task` 的 `finally` 里
显式 `await client.close()`。

## 实战记录：侧栏目录树拖拽排序（2026-11-22）

第一次用 `kb agent --plan` 派发真实功能。**w1 成功、w2 失败**，
leader 补完了 w2。这次经历暴露了三个具体问题。

### 派发与结果

```bash
python -X utf8 kb.py agent --plan _kbwork/plan-sidebar-drag.json --concurrency 1
```

| 任务 | 范围 | 结果 |
| :-- | :-- | :-- |
| w1-api | `apps/web/src/api.ts` | ✅ 29.2s，7 次调用，tsc 通过 |
| w2-sidebar | `apps/web/src/components/Sidebar.tsx` | ❌ `MaxTurnsExceeded`（14 轮），63.4s |

### 问题 1：`MaxTurnsExceeded` 时 steps 是空的（真缺陷）

w2 失败返回：

```json
{"ok": false, "error": "MaxTurnsExceeded: Max turns (14) exceeded",
 "tool_calls": [], "steps": [], "answer": ""}
```

**它实际改了 73 行**（438 → 511），但 `steps` 全空。
原因是 openai-agents 的 `MaxTurnsExceeded` **不携带 RunResult**，
而我们是在 `except` 里用 `_collect(t, ctx, None, ...)` 收集——
`r` 为 None，自然拿不到任何 item。

正确做法：**用 `Runner.run(..., max_turns=N)` 时捕获的是异常，不是部分结果**；
要拿轨迹必须自己记录（在工具层追加日志），不能指望框架回传。

### 问题 2：w2 写了代码但没接线

它留下两套拖拽函数，**都没有绑定到 DOM**：
`TreeNodeView` 里一套 `dragStart/dragOver/drop` 定义了却没被 JSX 使用；
`Sidebar` 里又重复一套 `onDragStart/onDrop/computeDropIntent`，同样没接线。
且 `api` 和 `onReload` 没进 `TreeNodeView` 的 props，tsc 报 6 处
`Cannot find name 'api' / 'onReload'`。

**这印证了「契约必须由 leader 定稿」**：我只写了「用 api.moveKnowledge」，
没写「`onReload` 要从 Sidebar 递归传到每个 TreeNodeView」，
它就漏掉了整条数据通路。

### 问题 3：HTML5 DnD 的 `dataTransfer.getData()` 在 dragover 阶段是空的

这是**浏览器安全限制**，不是 bug：只有 `drop` 阶段能读到真实数据，
`dragover` 阶段只能读 `types`。

我最初在 `handleDragOver` 里用 `getData('application/x-parent-id')` 判断同级，
导致**插入位置提示线永远不显示**（每次比较都拿到空串 → 判定不同级 → 清提示）。

修法：用**模块级变量** `dragSource = { id, parentId }` 记住拖拽源，
`dragover` 读它而不是 `dataTransfer`。`handleDragEnd` / 组件卸载时清空。

```typescript
let dragSource: { id: string; parentId: string | null } | null = null
```

### 定下的契约（这次学到的教训）

**同级拖拽 = 手动排序；跨级拖拽 = reparent，是另一个语义。** 需求是前者。
所以 `handleDrop` 里必须比较源与目标的 `parent_id`，不等就忽略。
请求体**只带 `before_id` 或 `after_id`，不带 `parent_id`**——
带了 `parent_id` 后端会当成移动节点，不再纯排序。

### 验证矩阵（全绿）

| 验证 | 结果 | 覆盖 |
| :-- | :-- | :-- |
| `npx tsc -p apps/web/tsconfig.json --noEmit` | 0 | 类型 |
| `npx tsc -p apps/server/tsconfig.json --noEmit` | 0 | 类型 |
| `pnpm --filter @atomkgraph/web build` | 0（9.00s） | 真实构建 |
| `scripts/e2e-drag-sort.ts` | **7 通过 / 0** | 真机 HTTP：move(after_id) → BBB,CCC,AAA；move(before_id) → AAA,BBB,CCC；sort_order 10/20/30 |
| `scripts/verify-drag-logic.ts` | **17 通过 / 0** | 同级判断 8 条 + before/after 判定 6 条 + 参数名 3 条 |
| 组件渲染（vite ssrLoadModule） | **8 通过 / 0** | `draggable="true"` 出现 3 次，原有展开/折叠/锚点未破坏 |
| `scripts/test-comment.ts` | 37 通过 / 0 | 上一功能未回归 |
| codeb `mcp/smoke.ts` | 75 通过 / 0 | KB 层未回归 |

### 侦察发现：后端早就就绪

派发前查清，**后端完全不需要改**：

- `POST /api/knowledge/:id/move` 已支持 `before_id` / `after_id`（`routes.ts:549`）
- `KnowledgeRepository.setSortOrder()` 存在（`knowledge-repo.ts:336`）
- `SORT_ORDER_STEP = 10` 稀疏约定（`knowledge-service.ts:113`）
- 排序锚点逻辑在 `knowledge-service.ts:1564`

缺口**全在前端**。所以只派了两个前端任务，没有动后端一行。

**这也是 `kb dispatch` 的价值**：先用它确认写范围互斥（2 个范围 0 冲突），
再确认哪些文件真的要动，避免派人去改本来正确的代码。

### 踩到的接口坑

`/api/knowledge?tree=1` 返回**扁平全量列表**，不是树；
真正的树是 `/api/knowledge/tree`（返回 `{knowledge, children}` 数组）。
e2e 脚本一开始用错了，报 `Cannot read properties of undefined`。

### 还没验证的

**浏览器里的真实拖拽交互没跑过。** 环境里没有 playwright / puppeteer，
`draggable` 属性落到 DOM、同级判断逻辑、后端排序链路都各自验证了，
但「鼠标按下 → 拖动 → 松开 → 看到新顺序」这条完整路径只有手动能验。

要补的话：装 playwright，或人在浏览器里点一遍（后端 3939 已在跑，
前端用 `pnpm --filter @atomkgraph/web dev` 起 5199）。

## 修复：`MaxTurnsExceeded` 时 steps 全空的真缺陷

实战派发 w2-sidebar 时暴露：任务烧满 14 轮失败，但返回

```json
{"ok": false, "error": "MaxTurnsExceeded", "tool_calls": [], "steps": [], "answer": ""}
```

**它实际改了 73 行**（438 → 511），leader 却什么都看不到。
这直接违背「失败返回部分结果」的设计承诺——承诺是空的。

### 根因

`_collect(t, ctx, None, ...)` 在异常时 `r=None`，于是 `r.new_items` 不存在。
而 `Runner.run` 抛 `MaxTurnsExceeded` 时**不携带 RunResult**（查过继承链：
`MaxTurnsExceeded → AgentsException → Exception`，没有 result 字段）。
所以「从 RunResult 里翻轨迹」这条路在异常时天然走不通。

### 试过但不够：`AgentHooks`

openai-agents 0.25.0 有 `AgentHooks.on_tool_start / on_tool_end / on_llm_*`，
都是 async。真跑验证过回调载荷：

```
start add  None
end   add  5
```

**拿不到工具参数**——框架不传。`on_tool_end` 只有结果值。
所以 hook 能记「调了什么工具、结果是什么」，记不了「edit_file 改了哪个文件」。
好在 leader 最需要的正是前者（知道死前走到哪一步），够用。

### 修法：`TraceHooks` + `_collect` fallback

```python
class TraceHooks(AgentHooks):
    def __init__(self, sink: list[dict]): self.sink = sink
    async def on_tool_start(self, context, agent, tool) -> None:
        self.sink.append({"tool": tool.name, "stage": "start"})
    async def on_tool_end(self, context, agent, tool, result) -> None:
        self.sink.append({"tool": tool.name, "stage": "end",
                          "result": str(result)[:200]})
```

每个 agent 挂自己的 `TraceHooks(hook_trace)`，闭包捕获独立列表 → 并发安全。
`_collect` 在 `steps` 为空且 `hook_trace` 非空时，从 `stage=="end"` 的事件还原：

```python
if not steps and hook_trace:
    ends = [h for h in hook_trace if h.get("stage") == "end"]
    calls = [h["tool"] for h in ends]
    steps = [{"tool": h["tool"], "result": h.get("result", "")} for h in ends]
```

**成功路径不动**：`RunResult` 有内容时优先用它（带 `args`，比 hook 的 result 更精确）。

### 真机验证（不是手工构造）

强制 agent 烧满轮次（任务要求「连续调 100 次 read_file，完成前绝不给最终回答」）：

```
ok=False  error=MaxTurnsExceeded: Max turns (4) exceeded
tool_calls=['list_dir', 'read_file_range', 'read_file_range', 'read_file_range']
steps=4 条
  · {'tool': 'list_dir', 'result': 'kb.py  (98802 B)'}
  · {'tool': 'read_file_range', 'result': 'kb.py 第 1-1 行（共 2324 行）...'}
  ...
```

**3 通过 / 0 失败**：真实异常下轨迹非空。

### 一个方法论收获

「强制烧满轮次」需要一个**明确、可机械判定**的任务。第一次我让 agent
「读不存在的文件直到读到」，它读一次就诚实报告失败并结束了——根本没触发异常。
改成「必须连续调用 N 次，完成前绝不回答」才稳定触发。
验证异常路径时，**要先确认异常真的发生了**（断言 error 字段），
别对着成功路径验了半天还以为测到了兜底。

### 验证

`_kbwork/test_hook_trace.py` 12 断言：
- 异常 + hook 轨迹 → 还原出 steps（修复目标）
- 成功路径 → 用 RunResult 不被 hook 覆盖
- 异常 + 无轨迹 → 仍是空（**诚实，不编造**）

全量回归：权限 25 / 异常 17 / hook 轨迹 12 / cache+调度 31 / deps 12 / MCP 75，全部 0 失败。

## 不要设 `max_turns`，要把任务拆细

### 轮数限制是症状，不是解法

w2-sidebar 烧满 14 轮被强杀，但它**已经改了 73 行、正在收敛**。
设 `max_turns` 的后果：agent 在将要完成时被按停止键，leader 得亲自补完——
那还不如不设。

`Runner.run` 的 `max_turns` 默认 10，传 `None` 即不限。
**codeb_agent.py 的 `Task.max_turns` 默认改成 `None`**，CLI 与 `kb agent` 的
`--max-turns` 默认值也改成 `None`（显式传仍生效，用于调试）。

关键认识：**任务该靠「拆细」收敛，不是靠轮数掐断**。
一个大任务烧 14 轮，往往是因为它里面塞了 4 个不同性质的决策。

### w2-sidebar 应该怎么拆：`_kbwork/plan-sidebar-split.json`

原 w2 一个任务里有四种性质的工作：

| 性质 | 内容 | 失败模式 |
| :-- | :-- | :-- |
| 数据通路 | import api、props 递归传 onReload | 漏传 → tsc 报 6 处 `Cannot find name` |
| 状态地基 | dragSource 模块变量、两个 useState、卸载清理 | 与 JSX 混写 → 顾此失彼 |
| 事件逻辑 | 5 个 handleDrag* 函数、同级校验 | 与绑定混写 → 写了函数忘了绑 |
| DOM 绑定 | draggable + 6 个事件 + 视觉样式 | 最后做 → 被掐断时这层全丢 |

拆成 4 个任务，**每个任务只有一个可验收的完成标准**：

```
w0-types      → api.ts 加 moveKnowledge           （纯 API，无 UI）
w1-tree-props → Sidebar 加 api import + onReload 递归传（数据通路）
w2-drag-state → 加 dragSource 模块变量 + 2 个 state + 卸载清理（状态地基）
w3-drag-handlers → 写 5 个 handleDrag* + 绑定 JSX + 视觉样式（事件+绑定）
```

依赖链 `w0 → w1 → w2 → w3` 串起来，全部 `max_turns=None`。
**注意：后 3 个任务写同一个文件，靠 depends_on 保证串行，不靠 dispatch 互斥**
（同一个文件不可能互斥，但依赖链天然 forbids 并行）。

验证过：4 任务拓扑序正确，轮数上限全为 None，`kb dispatch` 写范围检查 0 冲突。

### 拆分的三条原则

**1. 按「决策性质」拆，不按「文件大小」拆。**
w2 只有 438 行，按大小看该是一个任务；但它有 4 类不同决策，
混在一起时模型顾此失彼。拆的依据是"这件事失败时，原因是否独立"。

**2. 每个任务的完成标准必须可机械验证。**
上面 4 个任务全部以 `npx tsc --noEmit` 退出码 0 为完成标准。
不要写「实现拖拽功能」这种无法判定的标准。

**3. 后一个任务站在前一个的成品上，不重做。**
w3 的任务描述里明确写"用上一步已准备好的 dragSource / dragging / dropSide /
api / onReload"，而不是让它自己再建一遍。
**这就是依赖链的价值**：结论（这里是"已经存在的代码"）传给下游，
下游不用重新发明。

### JSON 计划文件的一个坑

写计划时用了反引号模板字符串 `\`...\``，
里面的 `\`` 在 JSON 里是**非法转义**（JSON 只认 `\"` `\\` `\/` 等），
`json.loads` 直接报 `Invalid \escape`。

**教训**：计划文件的 task 描述里不要用反引号包含反引号的代码片段，
要么用普通引号描述，要么用双反斜杠。

## 虚拟内存：把上下文当 cache（2026-11-22）

用户提出的核心类比：**内容在上下文中就是 cache，miss 后通过索引去取；
索引也是按需装入**。对应操作系统：磁盘=源文件，主存=上下文，cache=最近热区。
落地成四层，全部真机验证过。

### 四层结构

| 层 | OS 类比 | 实现 | 省多少（实测 Sidebar.tsx 529 行） |
| :-- | :-- | :-- | :-- |
| 1. 语义块索引 | 页表 | `file_index(path)` → `Class.method@行号  L起-止  签名` | 全文 13573 字符 → 索引 1850 |
| 2. 按需取块 | 缺页中断 | `read_block(path, key)` 取一个块正文 | 单块 666 字符 |
| 3. 装配只用索引 | 主存只装页表+热数据 | `kb pack --index` | 大纲 809 tok → 索引 425 tok |
| 4. 老结果换出 | 换页 | `ContextCache` + `call_model_input_filter` | 4 条工具输出 2000 → 1106 字符 |

### 关键实现点

**1/2. 索引与取块在 `semantic_blocks.py` + `tools_fs.py`**。
早期用 `_SRC_FUNC` 正则 + 缩进猜边界，两个真实缺陷：**同名撞 key**
（`__init__` 在多个类里各出现一次，`函数名@行号` 行号不同但语义容易混）、
**边界靠缩进推断不准**（方法体里嵌套缩进会被误判成下一个函数的开始）。
现在拆成独立模块 `distill/agent/semantic_blocks.py`，**用语法树自动拆，不用正则**：

| 语言 | 解析器 | 边界 |
| :-- | :-- | :-- |
| Python | stdlib `ast` | 精确 `end_lineno`，类/方法分作用域 |
| TS/TSX/JS/JSX | node + `typescript` compiler API | 精确 `getEnd()`，箭头函数、方法都覆盖 |
| 其它 | 正则回退（明确标注 `regex-fallback`） | 行边界 |

**撞名与类/方法重复的处理**：key 一律带**作用域前缀**——
`Scheduler._run_one@542`、`TraceHooks.__init__@75`，同名方法靠所属类区分；
类块和方法块都列出但 key 不同，是**可选的两种粒度**，不是重复入口。
`kb.py` 保持 stdlib-only，通过 **subprocess 调用** `semantic_blocks.py --json`
（TS 需要 node，不能直接 import）。`read_block` 用解析器给的精确 `start/end`，
不再靠缩进循环猜。

**3. `--index` 必须在 `kb pack` 源头做，不能在 agent 层做字符串替换。**
我先试过在 `assemble()` 里把 pack 结果的源码段换成索引——
但预算是 pack **内部**算的，那时知识层已被挤光，白省了源码却救不回知识。
移到 `kb.py` 里加 `--index` 从源头只装索引，实测：
大纲模式 1627 tok（知识层被挤光）→ 索引模式 1246 tok（3 块，知识层完整装入）。

**这里还暴露一个 KB 写法陷阱**：`kb pack` 只装正文里**出现目标文件名**的小节
（`kb.py:1303` 的 `n = title.count(stem) + body.count(stem)`）。
我新建的页标题是「侦察结果」「拖拽语义契约」，正文只写别的路径，
不含 `Sidebar.tsx`——于是一节都匹配不上。
**修法：关键小节的标题要带目标文件名。**

**4. `ContextCache` 在 `context_cache.py`**，通过 openai-agents 的
`RunConfig.call_model_input_filter` 挂进 `run_task`。真机探明的结构：

```
CallModelData.model_data = ModelInputData(
    input = [...],         # 消息是 dict
    instructions = ...
)
# 工具结果: {'type':'function_call_output', 'call_id':..., 'output': '...'}
```

**两个踩过的坑**：
- filter 收到的是 `CallModelData`，真正的消息在 `data.model_data.input`，
  写成 `data.input` 会在真机报 `AttributeError`（单测用手造 FakeData 反而过了）。
- 换出时**只替换 `output` 字符串**，绝不改 `call_id` / `type`——
  否则 function_call 与 function_call_output 配对断裂，API 直接报错。

墓碑：`[已换出：{key}。完整内容在 sidecar，用 cache_get("{key}") 取回]`。
最近 N 条（默认 2）留热区，短结果（≤200 字符）不折腾，重复 filter 幂等。

### 与 `loop.py` 的 Ledger 互补

| | Ledger（loop.py） | ContextCache（本层） |
| :-- | :-- | :-- |
| 适用 | 手写循环 | openai-agents 的 Runner |
| 钩子 | 自己控消息数组 | 官方 `call_model_input_filter` |
| 粒度 | 单条工具结果 | function_call_output |

不是替代关系：`codeb_agent.py` 用 ContextCache，`loop.py` 仍用 Ledger。

### 真机验证

- `test_block_index.py` 13 通过 / 0
- `test_virtual_memory.py` 11 通过 / 0
- `test_context_cache.py` 15 通过 / 0
- `test_index_mode_e2e.py` **5 通过 / 0**：真实 agent 用 `file_index → read_block` 两步，
  没读全文，回答准确
- `test_cache_e2e.py` **4 通过 / 0**：3 次长工具输出、`keep_recent=1`，
  换出 2 条、sidecar 2274 字符，**任务仍成功且回答正确**——换页没破坏协议

全量回归 9 个测试脚本 + MCP 冒烟，退出码全 0。

### 悬而未决的点——已解决

之前写「墓碑里说可以 cache_get 取回，但工具没实现，是空头承诺」。
现在已做实：`make_tools(t, cache)` 在 cache 非 None 时额外挂一个 `cache_get` 工具，
闭包捕获同一个 `ContextCache` 实例；`_shared_instructions` 里也明说了
「看到 `[已换出：...]` 墓碑时用 cache_get(key) 取回」。

真机验证（`_kbwork/test_cache_get_e2e.py`，4 通过 / 0）：
工具调用序列 `['file_index', 'read_block', 'read_block', 'cache_get', 'cache_get']`——
**agent 看到墓碑后主动调了 2 次 cache_get** 取回正文，回答正确。
换出 4 条、sidecar 6110 字符。四层虚拟内存闭环完成。

注意：`cache_get` 只在 `cache_keep_recent is not None` 时挂载；
不开淘汰的小任务没有这个工具，墓碑也不会出现，语义自洽。

墓碑里写了 `cache_get("{key}")` 取回，但**这个工具还没实现**——
`ContextCache.get()` 是 Python 方法，agent 在对话里调不到。
目前换出的正文 leader 能拿到（在 result 的 cache 里），但 agent 自己取不回。

要实现的话：给每个 agent 加一个 `cache_get` function_tool，闭包捕获同一个 ContextCache 实例。
**在没实现之前，别把「可取回」写进 agent 可见的提示词**——那是空头承诺。
