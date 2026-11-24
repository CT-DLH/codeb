---
covers:
  - distill/agent/codeb_agent.py
title: Agent execution - component table (layer 3)
updated: 2026-11-22
---

# 模块：代理执行层（codeb_agent.py）——部件细页表（第3层）

**项目**：codeb
**源码文件**：`distill/agent/codeb_agent.py`（解析器=ast，40 个语义块）
**第4层语义块索引**：[codeb_agent.py](../symbols/codeb_agent.py.md)
**写范围**：`distill/agent/codeb_agent.py`（不得碰 `packages/**`、`apps/**`）
**验证命令**：`powershell -NoProfile -ExecutionPolicy Bypass -File _kbwork/run_regression.ps1`

## 职责
实现 codeb 的代理执行核心：把上下文组装成 openai-agents 的注入消息，创建 AsyncOpenAI 客户端，跑 `Runner.run`，通过 `TraceHooks` 管理工具轨迹（异常时作为 RunResult fallback）、通过 `Scheduler` 做依赖 DAG + 并发调度、通过 `ContextCache` 做上下文换页。

## 适用场景
- 改消息序列拼接逻辑（`render`）——顺序即 cache 布局，勿随意调换稳定→易变段。
- 改任务执行主体（`run_task`）、并发调度（`Scheduler`）、hook 轨迹（`TraceHooks`）。
- 确认 `ContextCache.filter` 只替换 `function_call_output.output`，不动 `call_id`/`type`。
- 不适用：纯前端 UI、AtomKGraph 后端路由、采集器采集。

## 功能部件

| 部件 key | 类型 | 行号 | 作用 |
|:--|:--|:--|:--|
| `Task@113` | class | L113-158 | 任务模型（budget/max_turns/depends_on/persist 等） |
| `make_tools@164` | def | L164-256 | 组装子 agent 工具集（read_block/edit_file/run_cmd/cache_get…） |
| `Context@261` | class | L261-265 | 上下文容器（dispatch/knowledge/tokens） |
| `assemble@268` | def | L268-289 | kb dispatch + kb pack 组装 Context |
| `_shared_instructions@292` | def | L292-307 | 共用系统指令（**零 per-task 内容**，保 cache 前缀） |
| `render@310` | def | L310-362 | 消息序列：COMMON_WORLD→dispatch→知识层→上游结论→差异约束→任务 |
| `run_task@379` | async def | L379-422 | 执行主体：AsyncOpenAI 客户端 + Runner.run |
| `_collect@425` | def | L425-463 | 收集结果，异常时用 hook_trace fallback |
| `TraceHooks@60` | class | L60-84 | hook 轨迹沉槽 |
| `TraceHooks.__init__@75` | def | L75-76 | hook 沉槽初始化 |
| `TraceHooks.on_tool_start@78` | async def | L78-79 | 工具开始钩子 |
| `TraceHooks.on_tool_end@81` | async def | L81-84 | 工具结束钩子 |
| `Scheduler@489` | class | L489-587 | 依赖 DAG + 并发调度器（99 行） |
| `Scheduler.__init__@503` | def | L503-512 | 初始化（信号量） |
| `Scheduler._validate@514` | def | L514-522 | 校验 DAG 冲突与串行瓶颈 |
| `Scheduler._topo@524` | def | L524-540 | 拓扑排序 |
| `Scheduler._run_one@542` | async def | L542-564 | 单任务执行（精确 23 行，非整个类） |
| `Scheduler._persist@566` | def | L566-572 | 持久化任务结果 |
| `Scheduler.run@574` | async def | L574-587 | 并发执行全部任务 |
| `run_many@590` | async def | L590-608 | 多任务入口 |
| `run_sync@611` | def | L611-618 | 同步入口 |
| `build_parser@622` | def | L622-655 | CLI 解析 |
| `plan_from_json@658` | def | L658-687 | 从 plan.json 建任务 |
| `main@707` | def | L707-759 | 入口 |

## 测试文件
- `_kbwork/test_cache_and_scheduler.py`（31/0）
- `_kbwork/test_deps_injection.py`（12/0）
- `_kbwork/test_index_mode_e2e.py`（5/0，真实 LLM）
- `_kbwork/test_cache_e2e.py`（4/0，真实 LLM）
- `_kbwork/test_cache_get_e2e.py`（4/0，真实 LLM）
- `_kbwork/test_hook_trace.py`（12/0）

## 下沉指引
```
选中部件 → 打开第4层 codeb_agent.py.md → read_block(path="distill/agent/codeb_agent.py", key="render@310")
```
