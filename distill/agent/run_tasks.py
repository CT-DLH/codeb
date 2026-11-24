import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import loop

TASKS = [
    ("导航类", "告诉我们知识库有哪些仓库", 3),
    ("装订类", "用 kb_pack 装订 collector/sites/ 的上下文，然后告诉我里面包含哪几份 YAML 文件。", 4),
    ("约束类", "collector/kit/ 下有哪些代码文件？改 paging.py 之前要注意什么？", 4),
    ("定位类", "哪些知识页在描述 collector/refs/llm_parse.py？我该读哪一节？", 4),
]

fail = 0
for label, task, mt in TASKS:
    print("=" * 74)
    print(f"[{label}] {task}")
    print()
    s = loop.run(task, max_turns=mt)
    print()
    print(f"  轮数 {s['turns']} · 调用 {s['calls']} · 最终上下文 {s['ctx_tokens']} tok"
          f" · 累计 {s['cumulative_ctx']} tok · 折叠 {s['folded_total']} 块"
          + (f" · 拦下重复 {s['dups']} 次" if s.get("dups") else ""))
    print(f"  调用序列: {s['seen']}")
    if s["errors"]:
        fail += 1
        print(f"  错误 {len(s['errors'])} 个：{s['errors'][0][:160]}")
    print()

print("=" * 74)
print(f"有错误的任务：{fail}/{len(TASKS)}")
