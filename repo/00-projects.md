---
covers: []
title: Projects index (layer 1)
updated: 2026-11-22
---

# 项目索引（第1层页表）

> 本页是**最顶层页表**：只列项目，每个项目指向自己的**第2层模块导航**。
> 不列源码细节、不列知识页正文——那是更下层的事。
> agent 先读此页决定进入哪个项目，再跳转到该项目的模块导航。

| 项目 | 知识根目录 | 第2层模块导航路径 | 默认写范围 | 状态 |
|:--|:--|:--|:--|:--|
| codeb | `repo/codeb/` | [`repo/codeb/knowledge/00-modules.md`](codeb/knowledge/00-modules.md) | `kb.py`、`distill/agent/*.py` | 有效 |
| atomkgraph | `repo/atomkgraph/` | [`repo/atomkgraph/knowledge/00-modules.md`](atomkgraph/knowledge/00-modules.md) | `packages/**`、`apps/**` | 有效 |
| infohub | `repo/infohub/` | [`repo/infohub/knowledge/00-modules.md`](infohub/knowledge/00-modules.md) | `infohub/`、`mcp/` | 有效 |
| _shared | `repo/_shared/` | [`repo/_shared/knowledge/00-modules.md`](_shared/knowledge/00-modules.md) | `_shared/` | 有效 |

## 页表层级关系

```
第1层（本页）  项目索引            1 个文件，列全部项目
    │
    ├─ 第2层  模块导航             每个项目 1 个文件，列该项目的模块
    │
    ├─ 第3层  部件细页表           每个模块 1 个文件，列模块内的功能部件
    │
    ├─ 第4层  语义块索引           每个源码文件 1 个文件，列文件内所有语义块（元信息）
    │
    └─ 第5层  完整源码页帧         不落盘，read_block(path, key) 运行时调入
```

**查找路径**：项目 → 模块 → 部件 → 语义块 → 完整正文。越往下页表文件越多、粒度越细。

**执行操作**（`edit_file` / `write_file` / `run_cmd`）**不属于页表**，单独落在 `tasks/` 任务清单，由 leader 派发。
