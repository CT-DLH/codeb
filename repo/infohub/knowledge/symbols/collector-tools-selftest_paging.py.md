---
covers:
  - collector/tools/selftest_paging.py
title: Semantic block index: selftest_paging.py (layer 4)
updated: 2026-11-24
---

# 语义块索引：selftest_paging.py（第4层）

**源码文件**：`collector/tools/selftest_paging.py`  
**解析器**：`ast`  
**第5层完整正文**：`read_block(path="collector/tools/selftest_paging.py", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| ok@37 | def | L37-44 |  | def ok(name: str, cond, detail: str = "") -> None: |
| Res@50 | class | L50-58 | 模拟 http 层返回值（两种现成 FetchResult 的字段并集）。 | class Res: |
| Res.__init__@53 | def | L53-58 |  | def __init__(self, ok: bool = True, status: int = 200, text: str = "",… |
| FakeHttp@61 | class | L61-72 | 按 URL 查表返回页面的假 http。表里没有的一律 404——这正是最坏情况。 | class FakeHttp: |
| FakeHttp.__init__@64 | def | L64-66 |  | def __init__(self, pages: dict[str, str]): |
| FakeHttp.fetch@68 | def | L68-72 |  | def fetch(self, url: str, **kw): |
| GetOnlyFakeHttp@75 | class | L75-81 | 只有 get() 的实现，验证 duck-typing 不是只认 fetch。 | class GetOnlyFakeHttp(FakeHttp): |
| GetOnlyFakeHttp.get@78 | def | L78-79 |  | def get(self, url: str, referer: str = "", allow_redirects: bool = Tru… |
| make_page@84 | def | L84-91 | 搭一页假列表：items 是条目 id 列表，可选一个「下一页」控件。 | def make_page(items, *, next_href: str = "", rel_next: bool = False) -… |
| parse_items@94 | def | L94-99 | 调用方的条目解析器（L2 会传真的进来，这里是最小替身）。 | def parse_items(html: str, url: str) -> list: |
| test_soft_404@112 | def | L112-127 |  | def test_soft_404() -> None: |
| test_soft_404_everywhere@130 | def | L130-161 |  | def test_soft_404_everywhere() -> None: |
| test_order@167 | def | L167-198 |  | def test_order() -> None: |
| test_failures@204 | def | L204-253 |  | def test_failures() -> None: |
| boom@239 | def | L239-240 | 解析器抛错：按 0 条处理，不许把异常穿透给调用方 | def boom(_html, _url): |
| test_item_key@259 | def | L259-274 |  | def test_item_key() -> None: |
| OnlyId@269 | class | L269-270 |  | class OnlyId: |
| test_iter_pages@280 | def | L280-303 |  | def test_iter_pages() -> None: |
| test_iron_rule_in_code@309 | def | L309-321 |  | def test_iron_rule_in_code() -> None: |
| main@324 | def | L324-341 |  | def main() -> int: |
