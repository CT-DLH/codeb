import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import loop

CASES = [
    ("只看坑（应触发 no_source）",
     "改 collector/kit/paging.py 有哪些坑？只告诉我必须知道的，不要贴源码。", 5),
    ("要照着写（应装源码）",
     "我要给 collector/kit/paging.py 加一种新的翻页判断，先给我看这个文件的结构。", 4),
]

for label, task, mt in CASES:
    print("=" * 74)
    print(f"[{label}]")
    print(task)
    print()
    s = loop.run(task, max_turns=mt)
    print()
    print(f"  轮数 {s['turns']} · 调用 {s['calls']} · 最终 {s['ctx_tokens']} tok"
          f" · 累计 {s['cumulative_ctx']} tok · 重复 {s['dups']}")
    print(f"  调用: {s['seen']}")
    if s["errors"]:
        print(f"  错误: {s['errors'][0][:150]}")
    print()
