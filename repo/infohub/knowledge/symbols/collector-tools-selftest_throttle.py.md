---
covers:
  - collector/tools/selftest_throttle.py
title: Semantic block index: selftest_throttle.py (layer 4)
updated: 2026-11-24
---

# 语义块索引：selftest_throttle.py（第4层）

**源码文件**：`collector/tools/selftest_throttle.py`  
**解析器**：`ast`  
**第5层完整正文**：`read_block(path="collector/tools/selftest_throttle.py", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| check@44 | def | L44-51 |  | def check(cond: bool, msg: str) -> None: |
| Clock@61 | class | L61-79 |  | class Clock: |
| Clock.__init__@62 | def | L62-65 |  | def __init__(self, start: float = 1000.0): |
| Clock.monotonic@67 | def | L67-68 |  | def monotonic(self) -> float: |
| Clock.time@70 | def | L70-71 |  | def time(self) -> float: |
| Clock.sleep@73 | def | L73-75 |  | def sleep(self, x: float) -> None: |
| Clock.reset@77 | def | L77-79 |  | def reset(self) -> None: |
| install@85 | def | L85-91 |  | def install(clock: Clock) -> None: |
| restore@94 | def | L94-95 |  | def restore() -> None: |
| compare@98 | def | L98-112 | 同一串假时钟下分别驱动原实现与新实现，比对 sleep 序列。 | def compare(label: str, base_fn, new_fn, clock: Clock, n: int) -> None… |
| BHttp@120 | class | L120-132 | kit/http.py Http._throttle 原实现（host + jitter）。 | class BHttp: |
| BHttp.__init__@123 | def | L123-125 |  | def __init__(self, delay: float): |
| BHttp._throttle@127 | def | L127-132 |  | def _throttle(self, url: str) -> None: |
| BFetch@135 | class | L135-147 | zhihu_pipe/fetch.py _throttle 原实现（global，_MIN_INTERVAL 可 0）。 | class BFetch: |
| BFetch.__init__@138 | def | L138-140 |  | def __init__(self, interval: float): |
| BFetch._throttle@142 | def | L142-147 |  | def _throttle(self) -> None: |
| BAcademic@150 | class | L150-161 | sources/academic.py _throttle 原实现（global）。 | class BAcademic: |
| BAcademic.__init__@153 | def | L153-155 |  | def __init__(self, interval: float): |
| BAcademic._throttle@157 | def | L157-161 |  | def _throttle(self) -> None: |
| BWeb@164 | class | L164-175 | sources/web.py _throttle 原实现（global，用 time.time 记时）。 | class BWeb: |
| BWeb.__init__@167 | def | L167-169 |  | def __init__(self, interval: float): |
| BWeb._throttle@171 | def | L171-175 |  | def _throttle(self) -> None: |
| BBucket@178 | class | L178-191 | sources/bilibili.py / github.py _throttle 原实现（bucket 两档）。 | class BBucket: |
| BBucket.__init__@181 | def | L181-184 |  | def __init__(self, search: float, core: float): |
| BBucket._throttle@186 | def | L186-191 |  | def _throttle(self, bucket: str) -> None: |
| BSliding@194 | class | L194-216 | sources/xiaohongshu.py _throttle 原实现（sliding 窗口 + 递归重算）。 | class BSliding: |
| BSliding.__init__@197 | def | L197-200 |  | def __init__(self, interval: float, max_per_minute: int): |
| BSliding._throttle@202 | def | L202-216 |  | def _throttle(self) -> None: |
| BHost@219 | class | L219-232 | sources/browser.py BrowserSession._throttle 原实现（host）。 | class BHost: |
| BHost.__init__@222 | def | L222-224 |  | def __init__(self, interval: float): |
| BHost._throttle@226 | def | L226-232 |  | def _throttle(self, url: str) -> None: |
| main@240 | def | L240-403 |  | def main() -> int: |
| b_bili@310 | def | L310-311 |  | def b_bili(): |
| n_bili@313 | def | L313-314 |  | def n_bili(): |
| b_gh@321 | def | L321-322 |  | def b_gh(): |
| n_gh@324 | def | L324-325 |  | def n_gh(): |
| b_bili2@354 | def | L354-355 |  | def b_bili2(): |
| n_bili2@357 | def | L357-358 |  | def n_bili2(): |
| b_gh2@370 | def | L370-371 |  | def b_gh2(): |
| n_gh2@373 | def | L373-374 |  | def n_gh2(): |
