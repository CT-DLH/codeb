---
covers:
  - kb.py
  - distill/agent/semantic_blocks.py
  - distill/agent/tools_fs.py
  - distill/agent/codeb_agent.py
  - distill/agent/context_cache.py
  - mcp/server.ts
  - distill/distill.py
  - distill/sessions.py
title: codeb module navigation (layer 2)
updated: 2026-11-22
---

# codeb 项目模块导航（第2层页表）

> 进入 codeb 项目后先读本页：列出 codeb 内部的所有**模块**。
> 每个模块指向**第3层部件细页表**。不列源码正文、不列语义块细节。

## 模块列表

| 模块 | 源码范围 | 知识页 | 第3层部件细页表 | 状态 |
|:--|:--|:--|:--|:--|
| KB 工具链 | `kb.py` | [agent-base-survey](agent-base-survey.md)、[kb-usage](kb-usage.md) | [kb-tools](knowledge/modules/kb-tools.md) | 有效 |
| 语义块解析器 | `distill/agent/semantic_blocks.py` | [agent-base-survey](agent-base-survey.md) | [semantic-parser](knowledge/modules/semantic-parser.md) | 有效 |
| 文件系统工具层 | `distill/agent/tools_fs.py` | [agent-base-survey](agent-base-survey.md) | [fs-tools](knowledge/modules/fs-tools.md) | 有效 |
| 代理执行层 | `distill/agent/codeb_agent.py` | [agent-base-survey](agent-base-survey.md)、[dispatch-and-context-cache](dispatch-and-context-cache.md) | [agent-exec](knowledge/modules/agent-exec.md) | 有效 |
| 上下文缓存 | `distill/agent/context_cache.py` | [dispatch-and-context-cache](dispatch-and-context-cache.md) | [context-cache](knowledge/modules/context-cache.md) | 有效 |
| MCP 服务层 | `mcp/server.ts` | [agent-base-survey](agent-base-survey.md) | [mcp-server](knowledge/modules/mcp-server.md) | 有效 |

## 查找流程

```
本页 → 选中模块 → 打开对应第3层部件细页表
    → 选中部件 → 打开第4层语义块索引
    → 选中语义块 → read_block 调入第5层完整正文
```

**写范围**：默认 `kb.py`、`distill/agent/*.py`、`mcp/server.ts`。改任何模块前先看其第3层页表的写范围白名单。
**验证命令**：`powershell -NoProfile -ExecutionPolicy Bypass -File _kbwork/run_regression.ps1`（见各模块第3层页表）。
