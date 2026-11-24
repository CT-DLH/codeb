---
covers:
  - collector/tools/selftest_grab_cookie.py
title: Semantic block index: selftest_grab_cookie.py (layer 4)
updated: 2026-11-24
---

# 语义块索引：selftest_grab_cookie.py（第4层）

**源码文件**：`collector/tools/selftest_grab_cookie.py`  
**解析器**：`ast`  
**第5层完整正文**：`read_block(path="collector/tools/selftest_grab_cookie.py", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| check@26 | def | L26-33 |  | def check(name: str, cond: bool, extra: str = "") -> None: |
| FakeSession@36 | class | L36-43 | 只实现 grab_cookie 用到的那一个方法（鸭子类型，不启浏览器）。 | class FakeSession: |
| FakeSession.__init__@39 | def | L39-40 |  | def __init__(self, cookies: list[dict]) -> None: |
| FakeSession.cookies@42 | def | L42-43 |  | def cookies(self, domain: str = "") -> list[dict]: |
| c@46 | def | L46-47 |  | def c(name: str, value: str, domain: str) -> dict: |
| test_cookie_string@51 | def | L51-57 | ------------------------------------------------------------------ 1. 拼串 | def test_cookie_string() -> None: |
| test_extract@61 | def | L61-90 | ------------------------------------------------------------------ 2. 抽取 | def test_extract() -> None: |
| test_write_env@94 | def | L94-126 | ------------------------------------------------------------------ 3. 写 .env | def test_write_env() -> None: |
| test_registry@134 | def | L134-149 |  | def test_registry() -> None: |
| test_wait_login_success@153 | def | L153-194 | ------------------------------------------------------------------ 5. 等待判定 | def test_wait_login_success() -> None: |
| Page@156 | class | L156-161 |  | class Page: |
| Page.wait_for_timeout@157 | def | L157-158 |  | def wait_for_timeout(self, ms: int) -> None: |
| Page.inner_text@160 | def | L160-161 |  | def inner_text(self, sel: str) -> str: |
| test_login_confirmed@197 | def | L197-217 |  | def test_login_confirmed() -> None: |
| main@220 | def | L220-233 |  | def main() -> int: |
