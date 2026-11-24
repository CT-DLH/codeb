---
covers:
  - collector/tools/grab_cookie.py
title: Semantic block index: grab_cookie.py (layer 4)
updated: 2026-11-24
---

# 语义块索引：grab_cookie.py（第4层）

**源码文件**：`collector/tools/grab_cookie.py`  
**解析器**：`ast`  
**第5层完整正文**：`read_block(path="collector/tools/grab_cookie.py", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| Platform@67 | class | L67-73 |  | class Platform: |
| _extract@114 | def | L114-127 | 把上下文里属于该平台的 cookie 挑出来；同名取「值非空」的那条。 | def _extract(sess, plat: Platform) -> list[dict]: |
| _cookie_string@130 | def | L130-131 |  | def _cookie_string(cookies: list[dict]) -> str: |
| _login_confirmed@149 | def | L149-162 | 真登录了吗？只看「登录专属 cookie 有没有出现」，不发请求。 | def _login_confirmed(plat: Platform, cookies: list[dict]) -> tuple[boo… |
| _write_env@165 | def | L165-203 | 在 .env 里就地改 KEY=，没有就追加。返回 replaced/appended。 | def _write_env(key: str, value: str) -> str: |
| _write_zhihu@206 | def | L206-212 | 写进 zhihu-cli 的 profile（与 ingest_curl.py 同一落点，只是不用再复制 cURL）。 | def _write_zhihu(cookies: list[dict]) -> str: |
| _fresh_source@215 | def | L215-221 | 绕过 get_source 的实例缓存，按最新写入的登录态新建一个源（好拿去 health()）。 | def _fresh_source(name: str): |
| _print_platforms@224 | def | L224-234 |  | def _print_platforms() -> None: |
| _wait_login@239 | def | L239-311 | 盯到登录态出现为止。返回 (cookies, ok, 未完成的理由)。 | def _wait_login(sess, page, plat: Platform, wait_s: int) -> tuple[list… |
| _run_one@316 | def | L316-358 | --------------------------------------------------------------------- 主流程 | def _run_one(sess, plat: Platform, wait_s: int) -> int: |
| main@361 | def | L361-400 |  | def main(argv: list[str] \| None = None) -> int: |
