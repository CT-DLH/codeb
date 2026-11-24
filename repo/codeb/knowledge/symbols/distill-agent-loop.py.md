---
covers:
  - distill/agent/loop.py
title: Semantic block index: loop.py (layer 4)
updated: 2026-11-24
---

# 语义块索引：loop.py（第4层）

**源码文件**：`distill/agent/loop.py`  
**解析器**：`ast`  
**第5层完整正文**：`read_block(path="distill/agent/loop.py", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| load_env@23 | def | L23-37 | 与 distill.py 同一真源：infohub/collector/.env 里的 ZHIHU_LLM_*。 | def load_env() -> dict: |
| Tool@42 | class | L42-52 | 工具 = 名字 + schema + 一个 Python 函数。 | class Tool: |
| Block@56 | class | L56-65 | 一条工具结果在上下文里的样子。折叠后就地换成墓碑。 | class Block: |
| Block.tokens@64 | def | L64-65 |  | def tokens(self) -> int: |
| Ledger@68 | class | L68-117 | 上下文账本。折叠在这里发生，不在工具里。 | class Ledger: |
| Ledger.__init__@77 | def | L77-80 |  | def __init__(self): |
| Ledger.add@82 | def | L82-86 |  | def add(self, tool: str, text: str) -> Block: |
| Ledger.sweep@88 | def | L88-106 | 轮末折叠。返回这一轮被折叠的 key。 | def sweep(self, policy: dict[str, int], default: int = 2) -> list[str]… |
| Ledger.recall@108 | def | L108-110 |  | def recall(self, key: str) -> str \| None: |
| Ledger.messages@112 | def | L112-114 |  | def messages(self) -> list[dict]: |
| Ledger.total_tokens@116 | def | L116-117 |  | def total_tokens(self) -> int: |
| _kb@121 | def | L121-140 | 进程内调用 kb.py，不起子进程。54ms vs 261ms。 | def _kb(args: list[str]) -> str: |
| _s@143 | def | L143-148 | 模型常把可选参数写成字符串 "None" / "null"，得吃掉。 | def _s(v): |
| chat@195 | def | L195-227 | ----------------------------------------------------------------- LLM | def chat(messages: list[dict], tools: list[Tool], env: dict, *, |
| run@231 | def | L231-306 | ----------------------------------------------------------------- loop | def run(task: str, *, max_turns: int = 6, verbose: bool = True) -> dic… |
