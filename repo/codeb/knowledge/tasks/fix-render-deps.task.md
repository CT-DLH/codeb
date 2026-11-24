---
covers:
  - distill/agent/codeb_agent.py
title: Task: add deps validation to render (executable checklist)
updated: 2026-11-22
---

# 任务：给 render 函数加入 deps 校验

## 目标
在 `render` 里对 `deps` 做基础校验，防止上游结论缺失时静默产生空消息，改完 `run_regression.ps1` 全绿。

## 模块
代理执行层（`distill/agent/codeb_agent.py`）

## 前置（按页表路径读）
1. 第2层模块导航：[codeb/knowledge/00-modules.md](../00-modules.md) → 代理执行层
2. 第3层部件细页表：[agent-exec](agent-exec.md) → 部件 `render@310`
3. 第4层符号索引：[codeb_agent.py](../symbols/codeb_agent.py.md) → `render@310 L310-362`

## 步骤
1. `read_block(path="distill/agent/codeb_agent.py", key="render@310")` —— 第5层缺页调入完整正文，确认现有 deps 分支逻辑。
2. `edit_file(path="distill/agent/codeb_agent.py", old="<现有片段>", new="<加校验后的片段>")` —— `old` 逐字符匹配第1步读到的原文。
3. `run_cmd(cmd="powershell -NoProfile -ExecutionPolicy Bypass -File _kbwork/run_regression.ps1")` —— 验证。
4. 若 `render` 行号变化，同步更新第3层 [agent-exec](agent-exec.md) 与第4层 [codeb_agent.py](../symbols/codeb_agent.py.md) 中 `render@310` 的行号范围。

## 完成标准
- [ ] `run_regression.ps1` 所有测试 exit=0
- [ ] 改动未超出模块写范围白名单（仅 `distill/agent/codeb_agent.py`）
- [ ] 第3层与第4层页表中 `render` 行号与实际源码一致
