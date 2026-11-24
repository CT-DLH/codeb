"""上下文缓存淘汰器（虚拟内存的换页层）。

设计：
  - 每次模型调用前，call_model_input_filter 拿到 ModelInputData
  - 扫 input 里的 function_call_output：过老且没在最近被使用的，
    把 output 换成墓碑（正文存入 sidecar，可按 key 取回）
  - 「使用」的定义：模型又引用了它的 call_id（很少发生），
    或者它是最近 K 条里的——用 LRU 近似：只看位置，越靠前越老。
  - 关键约束：**不能改 function_call / function_call_output 的配对结构**，
    否则 API 会报错。只替换 output 的字符串内容。

这层与 loop.py 的 Ledger 互补：Ledger 是手写循环的折叠，
这里是 openai-agents 循环里的折叠，通过官方 filter 钩子实现。
"""
from __future__ import annotations

import time


class ContextCache:
    """把老工具结果的正文换出上下文（保留墓碑 + sidecar 可取回）。

    keep_recent: 最近 N 条工具结果始终留在上下文（热区 / cache）
    max_chars:   单条 output 超过这个长度才值得换出（短的不折腾）
    """

    TOMB = "[已换出：{key}。完整内容在 sidecar，用 cache_get(\"{key}\") 取回]"

    def __init__(self, keep_recent: int = 2, max_chars: int = 200):
        self.keep_recent = keep_recent
        self.max_chars = max_chars
        self.sidecar: dict[str, str] = {}
        self.evicted: list[str] = []
        self._counter = 0

    def _key(self, msg: dict) -> str:
        cid = msg.get("call_id", "")
        return f"call#{cid[:12]}" if cid else f"block#{self._counter}"

    def filter(self, data) -> "ModelInputData":
        """CallModelInputFilter：就地改写 ModelInputData.input。

        注意签名：filter 收到的是 **CallModelData**，真正的
        ModelInputData 在 `data.model_data`（不是 data.input）。
        探针里直接打印的是 model_data，接线时踩过这个坑：
        写成 data.input 会在真实调用里报 `no attribute 'input'`。
        返回的必须是 ModelInputData（不是 CallModelData）。
        """
        md = getattr(data, "model_data", data)   # 兼容直接传 ModelInputData 的测试
        msgs = getattr(md, "input", None)
        if not isinstance(msgs, list):
            return md
        self._msgs = msgs
        # 找到所有 function_call_output 的下标（按出现顺序 = 由老到新）
        out_idx = [i for i, m in enumerate(msgs)
                   if isinstance(m, dict) and m.get("type") == "function_call_output"]
        self._counter = len(out_idx)
        keep_from = max(0, len(out_idx) - self.keep_recent)
        for n, i in enumerate(out_idx):
            m = msgs[i]
            out = m.get("output", "")
            if not isinstance(out, str) or len(out) <= self.max_chars:
                continue
            if n >= keep_from:
                continue  # 热区，保留
            key = self._key(m)
            if key in self.sidecar:
                continue  # 已经换出过
            self.sidecar[key] = out
            self.evicted.append(key)
            # 只替换 output 字符串，不动 call_id / type ——配对结构保持完整
            m["output"] = self.TOMB.format(key=key)
        return md

    def get(self, key: str) -> str | None:
        return self.sidecar.get(key)

    def stats(self) -> dict:
        saved = sum(len(v) for v in self.sidecar.values())
        return {"evicted": len(self.evicted), "keys": self.evicted,
                "sidecar_chars": saved}
