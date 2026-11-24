---
title: Spawning subagents from codeb: openai-agents as a shell only
covers:
  - distill/agent/spawn.py
  - _kbwork/probe_context_inject.py
  - _kbwork/probe_inject_vs_tool.py
  - _kbwork/probe_inject_budget.py
  - _kbwork/probe_parallel.py
updated: 2026-11-21
---

# Spawning subagents from codeb: openai-agents as a shell only

问题不是「openai-agents 能不能用」，而是「**它能不能吃 codeb 已经组装好的上下文**」。
能吃，就只是换了个执行壳；不能吃，就得把组装逻辑在框架里重写一遍——那才是走回头路。

结论：**能吃，而且实测比「让子 agent 自己调工具」快一倍。**

## 四条注入通路，全部实测

`Runner.run` 的真实签名（`inspect.signature`）：

```python
Runner.run(
    starting_agent: Agent[TContext],
    input: str | list[TResponseInputItem] | RunState[TContext],
    *, context=None, max_turns=10, hooks=None, run_config=None,
    error_handlers=None, previous_response_id=None,
    auto_previous_response_id=False, conversation_id=None, session=None,
)
```

`input` 接受 `list[TResponseInputItem]`，而 `TResponseInputItem` 是 33 个成员的
Union，第一个就是 `EasyInputMessageParam`（即 `{"role": "user", "content": "..."}`）。

所以四条通路里最直接的那条成立：

| 通路 | 实测 | 用途 |
| :-- | :-- | :-- |
| **`input=` 注入消息列表** | ✓ | **主用**：codeb 装订完直接交 |
| `instructions=` 收 Callable | ✓ | 每个范围不同的角色说明 |
| `Agent(tools=[...])` 逐 agent 独立 | ✓ | 子 agent 只拿到自己该用的工具 |
| `Session` 预置历史 | ✓ 有 `add_items` | 跨任务续跑（暂不用） |

## 一条重要发现：让子 agent 自己调工具，会慢一倍

同一个范围、同一个问题，两种交付方式：

| 方式 | codeb 组装 | LLM 运行 | 子 agent 工具调用 | 答案 |
| :-- | --: | --: | --: | --: |
| **A 注入 input** | 228ms | **7.4s** | 2（都是 read_file） | 1,366 字 |
| B 作为工具让它自己调 `kb_pack` | — | 14.8s | 1（kb_pack） | 3,088 字 |

A 快一倍，因为**省掉了一整次 LLM 往返**：模型不用先决定「我该调什么工具拿上下文」。
在 B 里，那个决定本身就要一次完整的模型调用。

B 的答案更长（3,088 vs 1,366），但原因不是「工具更好」，而是**它装得更多**
（12,772 tok vs 7,491 tok）。把装订量对齐之后，差别就没了：

| 预算 | no_source | 装订 tok | 组装 | LLM | 调用 | 答案 |
| --: | :-- | --: | --: | --: | --: | --: |
| 4000 | True | 4,152 | 112ms | 8.6s | **0** | 1,617 字 |
| 8000 | True | 7,264 | 113ms | 8.3s | **0** | 2,000 字 |
| 8000 | False | 8,306 | 117ms | 8.4s | **0** | 2,056 字 |
| 13000 | False | 13,437 | 131ms | 11.9s | **0** | 2,602 字 |

**注入模式下工具调用数是 0。** 子 agent 一次往返就答完，因为它拿到上下文时
任务信息已经齐了。这是它比「工具模式」快的根本原因。

`4000 → 8000` 答案从 1,617 涨到 2,000 字（+24%），`8000 → 13000` 只涨到 2,602（+27%）
但耗时从 8.4s 涨到 11.9s（+42%）。**8,000 是拐点。**

## 落地：`distill/agent/spawn.py`

约 200 行，其中**没有一行业务逻辑是重复实现的**：

```python
def assemble(scope, budget=8000, with_source=False) -> Context:
    """复用 kb dispatch + kb pack，不重写任何组装逻辑。"""
    ctx.dispatch   = _kb(["dispatch", scope])          # 互斥 / 共享知识 / 接口面 / 串行点
    ctx.knowledge  = _kb(["pack", scope, "--no-source"])  # 源码 + 相关节 + 计划
```

`openai-agents` 在里面只做三件事：建 `Agent`、`Runner.run`、`asyncio.gather`。

### 一条硬约束写进了代码

```python
if info["conflicts"]:
    raise RuntimeError(f"写范围冲突，拒绝并行派发：{...}")
```

派发前必查互斥。**这条不能靠 instructions 提醒模型**——两个 agent 同时写一个文件
是数据损坏，不是风格问题。`kb_dispatch` 已经算好了，直接当闸门用。

全局串行点（如 `collector/capabilities.json`）不拦，但会拼进上下文：
每个子 agent 都知道「这个别自己重生成」。

### 工具集按角色裁剪

子 agent 只拿 `read_file` / `grep_text`，**不拿** `kb_pack` / `kb_dispatch`。
理由就是上面那条实测：上下文已经注入了，再给它找上下文的工具只会诱发多余往返。

对应到分页设计：**组装是 leader 的活，执行是 worker 的活**，两边的工具集不重叠。

## 并行收益是真的，但有前提

| 方案 | 3 个子 agent | 说明 |
| :-- | --: | :-- |
| openai-agents 常驻进程内并行 | **5.4s** | import 只付一次 3.2s |
| openai-agents 同进程串行 | 19.4s | |
| 3 个独立进程各跑一个 | 12.5s | 各付 3.3s import，合计 9.9s |
| loop.py 同步串行 | 8.8s | 无 import 开销，但不能并行 |

**并行省 72%**（19.4s → 5.4s），这是 `asyncio.gather` 的真实收益。

前提是**常驻进程**。`import agents` 实测 3.2–3.6s，而 `import kb` 只要 **0.019s**
（168 倍）。如果 codeb 每次新起进程，3.3s 的 import 会吃掉大部分并行收益
（12.5s 反而比 loop.py 的 8.8s 慢）。

所以这一层要么常驻，要么别用。

## 分页决定

| 场景 | 用什么 |
| :-- | :-- |
| 单个子 agent、同步等结果 | `loop.py`（319 行，0 依赖） |
| **≥2 个子 agent 并行、要错误隔离** | **`spawn.py`（openai-agents）** |
| 跨进程恢复、handoff | 暂不需要 |

选 `spawn.py` 的理由不是它功能多，而是**并行 + 错误隔离**这两件自己写容易错：
`asyncio.gather(..., return_exceptions=True)` 让一个子 agent 挂掉不拖垮整批，
手写这个要处理 cancel、异常聚合、部分结果。

## 已知缺口

1. **`import agents` 3.2s** 是硬成本。要摊薄必须常驻。
2. **探针 venv 在 `_kbwork/agvenv/`**（96 MB），还没进项目依赖。
   正式启用前要决定：是接受 `pip install openai-agents`，还是把 96 MB vendor 进来。
3. **DSH 里的 codeb MCP server 是旧进程**，只暴露 6 个工具（缺 `kb_pack` / `kb_dispatch`）。
   源码和 smoke 都是 8 个，所以是没重新加载。这挡在「DSH 调 codeb 派子 agent」前面。
