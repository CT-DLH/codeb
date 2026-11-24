---
covers:
  - kb.py
updated: 2026-11-18
---

# Codeb plan

这个页面收拢还没有归属到具体知识页的待办。已经有知识页的功能，待办就写在那页的 `## 计划` 小节里，不要集中到这里。

## 约定

条目只写意图，不写状态：`- [ ] P-<slug> 一句话说清改什么 — done: <锚点>`。
**不要写 [x]**——「已实现」由 done: 锚点在查询时现场核对代码，写进文件就会在代码被回退后静默骗人。
锚点三种：`path a.py, b/`、`` grep kb.py `正则` ``、`none`（进 manual 交人判断）。
关闭用 `kb plan close P-xxx --into <页> --section <节> --body-file f.md`：先写知识，再删条目。

## 计划
- [ ] P-lock-stress 把写锁的并发回归测试固定进 mcp/smoke.ts，而不是留在 _kbwork — done: grep mcp/smoke.ts `write_lock`
- [ ] P-git-init 给 codeb 建 git 仓库：现在 59 页是单份无版本历史 — done: path .git
- [ ] P-distill-source 把会话真实读过的源码片段喂进 S2 提示词，否则它只能填模板 — done: path distill/prompt.py
- [ ] P-claim 多会话施工范围租约（scope 声明 + 过期心跳） — done: path .kbwork/claims/
- [ ] P-uplift-tree 把超过 400 行的知识页按 parent 拆成子页（pitfalls 度数最高） — done: none
- [ ] P-cleanup 清掉 _tmp/capture-loop.md 与 _kbwork 探针（把结论折进冒烟测试） — done: none

## 落地记录

### 背景

T2 引入 parent 字段时，把折叠与悬空报警的实现写进了 kb.py，但没有对应的回归测试。

### 结论

`mcp/smoke.ts` 已覆盖 parent 折叠与悬空报警（grep 命中）。这块行为由冒烟测试守住。

### 放弃了什么

没有为 `--flat` 单独写测试：它只是跳过折叠，与折叠共用同一路径，重复测试没有增量价值。
