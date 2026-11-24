---
covers:
  - collector/zhihu_pipe/sources/browser.py
title: Semantic block index: browser.py (layer 4)
updated: 2026-11-24
---

# 语义块索引：browser.py（第4层）

**源码文件**：`collector/zhihu_pipe/sources/browser.py`  
**解析器**：`ast`  
**第5层完整正文**：`read_block(path="collector/zhihu_pipe/sources/browser.py", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| BrowserUnavailable@90 | class | L90-91 | 没装 playwright / 机器上没有可用的 Chrome。属于环境问题，不是站点问题。 | class BrowserUnavailable(RuntimeError): |
| NeedManualAction@94 | class | L94-99 | 需要人工过滑块/扫码登录。 | class NeedManualAction(QuotaExceeded): |
| BrowserBlocked@102 | class | L102-107 | 站点直接返回 4xx/5xx（反爬），且没落到能识别的验证页。 | class BrowserBlocked(QuotaExceeded): |
| browser_available@110 | def | L110-115 | playwright 装没装。只查包，不启动浏览器。 | def browser_available() -> bool: |
| challenge_reason@118 | def | L118-127 | 返回非空字符串 = 这张页面需要人工。空字符串 = 正常页面。 | def challenge_reason(url: str = "", text: str = "") -> str: |
| challenge_present@130 | def | L130-135 | 视口里是不是真有一个验证控件（而不是被停在屏幕外的模板）。读不到就按「没有」算。 | def challenge_present(page) -> bool: |
| challenge_reason_page@138 | def | L138-150 | challenge_reason 的带页面版：文案命中时，还要验证控件真的在视口里才算要人工。 | def challenge_reason_page(page, text: str = "") -> str: |
| risk_reason@153 | def | L153-166 | 平台直接拒绝当前访问环境（不是让你验证，验证也没用）。 | def risk_reason(url: str = "", text: str = "") -> str: |
| parse_cookie_string@169 | def | L169-176 | k=v; k2=v2 → Playwright 的 cookie 列表。域必须写成 .example.com 才匹配子域。 | def parse_cookie_string(cookie_str: str, domain: str) -> list[dict]: |
| last_login@179 | def | L179-188 | 读取 browser_login.py 写下的最近一次人工验证记录（没有就返回空 dict）。 | def last_login(source: str = "") -> dict: |
| mark_login@191 | def | L191-199 | 人工验证通过后落一个标记，health() 据此报告「已验证」。 | def mark_login(source: str, url: str = "") -> Path: |
| BrowserConfig@203 | class | L203-220 |  | class BrowserConfig: |
| BrowserConfig.from_env@211 | def | L211-220 |  | def from_env(cls) -> "BrowserConfig": |
| BrowserSession@223 | class | L223-445 | 一只 Chrome，多个源共用。同步 API（流水线是单线程的）。 | class BrowserSession: |
| BrowserSession.__init__@226 | def | L226-239 |  | def __init__(self, config: BrowserConfig \| None = None) -> None: |
| BrowserSession.started@244 | def | L244-245 | -------------------------------------------------------------- 生命周期 | def started(self) -> bool: |
| BrowserSession.set_min_interval@247 | def | L247-249 |  | def set_min_interval(self, seconds: float) -> None: |
| BrowserSession.start@251 | def | L251-286 |  | def start(self) -> None: |
| BrowserSession.close@288 | def | L288-299 |  | def close(self) -> None: |
| BrowserSession.channel@302 | def | L302-303 |  | def channel(self) -> str: |
| BrowserSession.page@308 | def | L308-313 | -------------------------------------------------------------- 页面操作 | def page(self): |
| BrowserSession.new_page@315 | def | L315-317 |  | def new_page(self): |
| BrowserSession._throttle@319 | def | L319-320 |  | def _throttle(self, url: str) -> None: |
| BrowserSession._visible_text@323 | def | L323-327 |  | def _visible_text(page) -> str: |
| BrowserSession.raw_goto@329 | def | L329-346 | 不做验证码判定地打开页面。登录引导用，业务代码别用。 | def raw_goto(self, url: str, *, page=None, timeout_ms: int = 0): |
| BrowserSession.guard@348 | def | L348-358 | 当前页面是验证页/风控页吗？是就按「临时不可用」抛出。JS 操作后也要调一次。 | def guard(self, page=None) -> None: |
| BrowserSession._manual@360 | def | L360-364 |  | def _manual(self, reason: str) -> NeedManualAction: |
| BrowserSession.goto@366 | def | L366-404 | 打开页面并返回 (HTML, 最终 URL)；遇到验证页直接抛 NeedManualAction。 | def goto(self, url: str, *, page=None, wait_selector: str = "", |
| BrowserSession.eval@406 | def | L406-412 | 执行一段 async 函数体；入参叫 A，返回值原样带回 Python。 | def eval(self, script_body: str, arg: Any = None, *, page=None) -> Any… |
| BrowserSession.add_cookies@414 | def | L414-423 | 把 .env 里的整串 Cookie 灌进浏览器上下文（已有 profile 的补充）。 | def add_cookies(self, domain: str, cookie_str: str) -> int: |
| BrowserSession.seed_cookies_once@425 | def | L425-429 |  | def seed_cookies_once(self, domain: str, cookie_str: str) -> None: |
| BrowserSession.cookies@431 | def | L431-445 | 把上下文里的 cookie 原样带出来（给了域后缀就只回匹配的那些）。 | def cookies(self, domain: str = "") -> list[dict]: |
| get_session@451 | def | L451-455 |  | def get_session(config: BrowserConfig \| None = None) -> BrowserSessio… |
| close_session@458 | def | L458-462 |  | def close_session() -> None: |
| BrowserSource@468 | class | L468-500 | 给浏览器型源共用的基类：验证码口径、限速、Cookie 注入、人工引导文案。 | class BrowserSource: |
| BrowserSource.__init__@477 | def | L477-478 |  | def __init__(self) -> None: |
| BrowserSource.browser@481 | def | L481-485 |  | def browser(self) -> BrowserSession: |
| BrowserSource.browser_available@487 | def | L487-488 |  | def browser_available(self) -> bool: |
| BrowserSource.set_min_interval@490 | def | L490-493 |  | def set_min_interval(self, seconds: float) -> None: |
| BrowserSource.manual_hint@495 | def | L495-497 |  | def manual_hint(self) -> str: |
| BrowserSource.need_manual@499 | def | L499-500 |  | def need_manual(self, reason: str) -> NeedManualAction: |
