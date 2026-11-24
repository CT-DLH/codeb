---
covers:
  - distill/agent/spawn.py
title: Semantic block index: spawn.py (layer 4)
updated: 2026-11-24
---

# 语义块索引：spawn.py（第4层）

**源码文件**：`distill/agent/spawn.py`  
**解析器**：`ast`  
**第5层完整正文**：`read_block(path="distill/agent/spawn.py", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| load_env@22 | def | L22-33 | ---------------------------------------------------------------- 凭据 | def load_env() -> dict: |
| _kb@37 | def | L37-41 | ---------------------------------------------------------------- codeb 调用 | def _kb(argv: list[str]) -> tuple[int, str]: |
| read_file@48 | def | L48-59 | 读仓库里的一个文件（相对仓库根），返回前 max_lines 行。 | def read_file(path: str, max_lines: int = 150) -> str: |
| grep_text@63 | def | L63-83 | 在目录里搜字符串，返回 路径:行号:内容（最多 20 条）。 | def grep_text(pattern: str, path: str = ".") -> str: |
| Context@88 | class | L88-95 | codeb 组装出来的一份上下文。这就是「子 agent 看到的世界」。 | class Context: |
| assemble@98 | def | L98-113 | 复用 kb dispatch + kb pack，不重写任何组装逻辑。 | def assemble(scope: str, budget: int = 8000, with_source: bool = False… |
| render@116 | def | L116-129 | 把上下文变成注入用的消息。 | def render(ctx: Context, task: str) -> list[dict]: |
| _client@133 | def | L133-134 | ---------------------------------------------------------------- 执行 | def _client(env): |
| spawn_one@137 | async def | L137-154 |  | async def spawn_one(ctx: Context, task: str, env: dict, max_turns: int… |
| spawn_many@157 | async def | L157-183 | 并行跑 N 个子 agent。先 dispatch 验互斥，冲突就拒绝派发。 | async def spawn_many(scopes: list[str], task: str, *, |
| run_sync@186 | def | L186-188 | 同步入口：codeb 的 cmd_* 可以直接调这个。 | def run_sync(scopes: list[str], task: str, **kw) -> list[dict]: |
