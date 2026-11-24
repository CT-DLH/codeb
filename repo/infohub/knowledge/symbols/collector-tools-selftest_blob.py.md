---
covers:
  - collector/tools/selftest_blob.py
title: Semantic block index: selftest_blob.py (layer 4)
updated: 2026-11-24
---

# 语义块索引：selftest_blob.py（第4层）

**源码文件**：`collector/tools/selftest_blob.py`  
**解析器**：`ast`  
**第5层完整正文**：`read_block(path="collector/tools/selftest_blob.py", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| ok@36 | def | L36-44 | 一条断言。cond 为真即通过；detail 在不通过时打出来。 | def ok(name: str, cond, detail: str = "") -> None: |
| ok_raises_unparsed@47 | def | L47-65 | 断言抛 Unparsed（且可选断言 reason），并且绝不返回空串。 | def ok_raises_unparsed(name: str, fn, want_reason: str = "") -> None: |
| ok_raises_value_error@68 | def | L68-80 |  | def ok_raises_value_error(name: str, fn) -> None: |
| make_pdf@88 | def | L88-115 | 现场写一份最小合法 PDF（xref 偏移按实际位置算，poppler 才肯好好读）。 | def make_pdf(body_text: str) -> bytes: |
| make_docx@128 | def | L128-133 |  | def make_docx() -> bytes: |
| make_xlsx@148 | def | L148-156 |  | def make_xlsx() -> bytes: |
| Res@165 | class | L165-175 | 模拟 http 层返回值（site_crawl.http.FetchResult 的字段面）。 | class Res: |
| Res.__init__@168 | def | L168-175 |  | def __init__(self, ok: bool = True, status: int = 200, final_url: str … |
| FakeHttp@178 | class | L178-189 |  | class FakeHttp: |
| FakeHttp.__init__@179 | def | L179-182 |  | def __init__(self, res: Res \| None = None, exc: Exception \| None = N… |
| FakeHttp.fetch@184 | def | L184-189 |  | def fetch(self, url: str, **kw): |
| GetOnlyHttp@192 | class | L192-201 | 只有 get() 的实现（site_crawl.http.Http 两者都有，但 duck-typed 不能假设）。 | class GetOnlyHttp: |
| GetOnlyHttp.__init__@195 | def | L195-197 |  | def __init__(self, res: Res): |
| GetOnlyHttp.get@199 | def | L199-201 |  | def get(self, url: str, referer: str = "", allow_redirects: bool = Tru… |
| test_sniff@207 | def | L207-255 |  | def test_sniff() -> None: |
| test_fetch@261 | def | L261-336 |  | def test_fetch() -> None: |
| NoFetch@268 | class | L268-269 |  | class NoFetch: |
| _all_pdf_backends_off@342 | def | L342-356 | 把四档 PDF 后端全部伪造为不可用，返回原值以便还原。 | def _all_pdf_backends_off() -> dict: |
| _restore@359 | def | L359-364 |  | def _restore(saved: dict) -> None: |
| test_pdf@367 | def | L367-436 |  | def test_pdf() -> None: |
| spy@383 | def | L383-386 |  | def spy(cmd, **kw): |
| test_docx@442 | def | L442-463 |  | def test_docx() -> None: |
| test_xlsx_html@469 | def | L469-491 |  | def test_xlsx_html() -> None: |
| test_doc@497 | def | L497-524 |  | def test_doc() -> None: |
| test_fetch_and_text@530 | def | L530-543 |  | def test_fetch_and_text() -> None: |
| test_redlines@549 | def | L549-571 |  | def test_redlines() -> None: |
| main@574 | def | L574-594 |  | def main() -> int: |
