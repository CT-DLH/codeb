---
covers:
  - distill/agent/codeb_agent.py
title: codeb_agent.py semantic block index (layer 4)
updated: 2026-11-22
---

# 语义块索引：codeb_agent.py（第4层）

**源码文件**：`distill/agent/codeb_agent.py`（解析器=ast，40 个语义块）
**第5层完整正文**：`read_block(path="distill/agent/codeb_agent.py", key="<name>@<line>")`

| 语义块 key | 类型 | 行号 | 作用 |
|:--|:--|:--|:--|
| `TraceHooks@60` | class | L60-84 | hook 轨迹沉槽 |
| `TraceHooks.__init__@75` | def | L75-76 | hook 沉槽初始化 |
| `TraceHooks.on_tool_start@78` | async def | L78-79 | 工具开始钩子 |
| `TraceHooks.on_tool_end@81` | async def | L81-84 | 工具结束钩子 |
| `load_env@88` | def | L88-101 | 加载环境变量 |
| `_kb@104` | def | L104-108 | 调 kb.py 子进程 |
| `Task@113` | class | L113-158 | 任务模型 |
| `make_tools@164` | def | L164-256 | 组装工具集 |
| `_r@170` | def | L170-171 | 工具小工具 |
| `_rr@173` | def | L173-174 | 工具小工具 |
| `_ld@176` | def | L176-177 | 工具小工具 |
| `_g@179` | def | L179-180 | 工具小工具 |
| `_fi@182` | def | L182-184 | file_index 工具 |
| `_rb@186` | def | L186-188 | read_block 工具 |
| `_e@190` | def | L190-192 | edit_file 工具 |
| `_w@194` | def | L194-196 | write_file 工具 |
| `_a@198` | def | L198-200 | append_file 工具 |
| `_cmd@228` | def | L228-236 | run_cmd 工具 |
| `_cache_get@242` | def | L242-249 | cache_get 工具 |
| `Context@261` | class | L261-265 | 上下文容器 |
| `assemble@268` | def | L268-289 | kb dispatch + kb pack 组装 |
| `_shared_instructions@292` | def | L292-307 | 共用系统指令（零 per-task 内容） |
| `render@310` | def | L310-362 | 消息序列拼接（cache 布局） |
| `run_task@379` | async def | L379-422 | 执行主体 |
| `_collect@425` | def | L425-463 | 收集结果（hook_trace fallback） |
| `Trace@473` | class | L473-486 | 任务轨迹 |
| `Trace.to_dict@483` | def | L483-486 | 轨迹转 dict |
| `Scheduler@489` | class | L489-587 | 依赖 DAG + 并发调度器 |
| `Scheduler.__init__@503` | def | L503-512 | 初始化（信号量） |
| `Scheduler._validate@514` | def | L514-522 | 校验 DAG 冲突与串行瓶颈 |
| `Scheduler._topo@524` | def | L524-540 | 拓扑排序 |
| `Scheduler._run_one@542` | async def | L542-564 | 单任务执行（精确 23 行） |
| `Scheduler._persist@566` | def | L566-572 | 持久化任务结果 |
| `Scheduler.run@574` | async def | L574-587 | 并发执行全部任务 |
| `run_many@590` | async def | L590-608 | 多任务入口 |
| `run_sync@611` | def | L611-618 | 同步入口 |
| `build_parser@622` | def | L622-655 | CLI 解析 |
| `plan_from_json@658` | def | L658-687 | 从 plan.json 建任务 |
| `_print_result@690` | def | L690-704 | 打印结果 |
| `main@707` | def | L707-759 | 入口 |
