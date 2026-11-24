---
covers:
  - collector/kit/http.py
title: Semantic block index: http.py (layer 4)
updated: 2026-11-24
---

# 语义块索引：http.py（第4层）

**源码文件**：`collector/kit/http.py`  
**解析器**：`ast`  
**第5层完整正文**：`read_block(path="collector/kit/http.py", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| normalize_charset@74 | def | L74-76 |  | def normalize_charset(name: str) -> str: |
| decode_body_ex@83 | def | L83-113 | 按声明解码，返回 (文本, 原因)。 | def decode_body_ex(content: bytes, header_charset: str = "") -> tuple[… |
| decode_body@116 | def | L116-118 | 优先按 meta/响应头声明的编码解码，最后回退 UTF-8 → gb18030 → 替换。 | def decode_body(content: bytes, header_charset: str = "") -> str: |
| decode_html@121 | def | L121-123 | 与 zhihu_pipe/html_text.py 同名的入口，便于两边以后收敛到 L1。 | def decode_html(raw: bytes, content_type: str = "") -> str: |
| json_loads_ignore@126 | def | L126-134 |  | def json_loads_ignore(raw: str) -> Any: |
| _load_robots@144 | def | L144-164 | 取并解析 robots.txt；返回 (parser\|None, 说明)。拿不到就返回 None（视为允许）。 | def _load_robots(root: str, timeout: float, ua: str) -> tuple[Any, str… |
| _robots_for@167 | def | L167-180 |  | def _robots_for( |
| robots_allowed@183 | def | L183-205 | 这个 URL 允许我们抓吗？返回 (allowed, 说明)。说明永远进报告。 | def robots_allowed( |
| clear_robots_cache@208 | def | L208-209 |  | def clear_robots_cache() -> None: |
| FetchResult@216 | class | L216-231 |  | class FetchResult: |
| FetchResult.raise_for_status@228 | def | L228-231 |  | def raise_for_status(self) -> "FetchResult": |
| FetchError@234 | class | L234-240 | 抓取失败。reason 是机器可判定码，detail 是完整结果。 | class FetchError(RuntimeError): |
| FetchError.__init__@237 | def | L237-240 |  | def __init__(self, reason: str, result: FetchResult \| None = None): |
| Http@246 | class | L246-439 | 带「按 host 节流」与 robots 闸的 urllib 封装。 | class Http: |
| Http.__init__@255 | def | L255-285 |  | def __init__( |
| Http._throttle@289 | def | L289-294 | ------------------------------------------------------------ 节流 | def _throttle(self, url: str) -> None: |
| Http.robots@298 | def | L298-305 | ------------------------------------------------------------ 入口 | def robots(self, url: str) -> tuple[bool, str]: |
| Http.fetch@307 | def | L307-403 | 取一个 URL，永远返回 FetchResult（不抛传输层异常）。 | def fetch( |
| Http.request@405 | def | L405-415 | fetch() 的抛异常版本：失败时 reason 就是异常消息。 | def request(self, method: str, url: str, **kw) -> FetchResult: |
| Http.get@417 | def | L417-419 |  | def get(self, url: str, referer: str = "", allow_redirects: bool = Tru… |
| Http.text@421 | def | L421-425 |  | def text(self, url: str, referer: str = "") -> str: |
| Http.json@427 | def | L427-428 |  | def json(self, url: str, referer: str = "") -> Any: |
| Http.post_json@430 | def | L430-439 |  | def post_json(self, url: str, data: dict, referer: str = "") -> Any: |
| Throttle@445 | class | L445-564 | 四种限速策略的统一底座。 | class Throttle: |
| Throttle.__init__@465 | def | L465-482 |  | def __init__(self, delay: float = 1.5, *, scope: str = "host", |
| Throttle._key@484 | def | L484-494 |  | def _key(self, key: str) -> str: |
| Throttle.set_delay@497 | def | L497-499 | 运行时覆盖最小间隔（CLI --delay）。只改参数，不动已记录的时序。 | def set_delay(self, seconds: float) -> None: |
| Throttle.set_bucket@501 | def | L501-503 | 运行时覆盖某个桶的间隔（search / core 两档分别可改）。 | def set_bucket(self, name: str, seconds: float) -> None: |
| Throttle.set_max_per_minute@505 | def | L505-507 | 运行时覆盖每分钟上限（sliding 档）。 | def set_max_per_minute(self, n: int) -> None: |
| Throttle._wait_window_compat@509 | def | L509-535 | 逐源对齐「滑动窗口 + 每分钟上限 + 最小间隔」的原始节奏（第四档）。 | def _wait_window_compat(self) -> float: |
| Throttle.wait@537 | def | L537-560 | 按当前策略阻塞到可以发下一次请求，返回实际等了多少秒。 | def wait(self, key: str = "") -> float: |
| Throttle.reset@562 | def | L562-564 |  | def reset(self) -> None: |
