import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import loop

# 这个问题需要「文件清单 + 已知坑」两块信息，单靠 dispatch 答不全。
# 看模型会不会自己去装订。
task = ("改 collector/kit/paging.py 有哪些坑？只告诉我必须知道的，"
        "不要贴源码。")
print("=" * 74)
print(task)
print()
s = loop.run(task, max_turns=5)
print()
print(f"轮数 {s['turns']} · 调用 {s['calls']} · 最终 {s['ctx_tokens']} tok · "
      f"累计 {s['cumulative_ctx']} tok · 折叠 {s['folded_total']} · 重复 {s['dups']}")
print("调用:", s["seen"])
if s["errors"]:
    print("错误:", s["errors"][0][:200])
