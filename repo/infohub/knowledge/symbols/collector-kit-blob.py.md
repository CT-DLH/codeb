---
covers:
  - collector/kit/blob.py
title: Semantic block index: blob.py (layer 4)
updated: 2026-11-24
---

# 语义块索引：blob.py（第4层）

**源码文件**：`collector/kit/blob.py`  
**解析器**：`ast`  
**第5层完整正文**：`read_block(path="collector/kit/blob.py", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| Blob@141 | class | L141-163 | 一个附件（或任何非 HTML 响应）的原始字节及其元信息。 | class Blob: |
| Blob.size@161 | def | L161-163 | 字节数。语义上等价于旧 FetchResult.bytes，但不等于传输职责。 | def size(self) -> int: |
| Unparsed@166 | class | L166-183 | 抽文失败。reason 是机器可判定码，detail 说清是哪个后端/哪一步。 | class Unparsed(RuntimeError): |
| Unparsed.__init__@180 | def | L180-183 |  | def __init__(self, reason: str, detail: str = ""): |
| _kind_from_url@189 | def | L189-194 |  | def _kind_from_url(url: str) -> str: |
| _kind_from_ctype@197 | def | L197-204 |  | def _kind_from_ctype(content_type: str) -> str: |
| _sniff_zip@207 | def | L207-232 | 看 zip 内部条目判断是哪种 OOXML；看不出来就是普通 zip。 | def _sniff_zip(data: bytes) -> str: |
| _sniff_ole2@235 | def | L235-250 | OLE2 复合文档：只能靠 ctype / 扩展名区分 doc\|xls\|ppt，判不出就 unknown。 | def _sniff_ole2(content_type: str, url: str) -> str: |
| sniff_kind@253 | def | L253-284 | 判断字节是什么。内容优先，Content-Type 次之，扩展名最后。 | def sniff_kind(data: bytes, content_type: str = "", url: str = "") -> … |
| _decode_text@290 | def | L290-309 | 字节 → 文本。顺序：BOM/声明 → utf-8 → gb18030 → 替换。 | def _decode_text(data: bytes, content_type: str = "") -> str: |
| _http_fetch@315 | def | L315-330 | 按 duck-typing 调 http 层的 fetch（或 get）。缺了就抛 ValueError。 | def _http_fetch(http: Any, url: str) -> Any: |
| _payload_reason@333 | def | L333-346 | 把 http 层的失败原因收敛到 REASON_CODES 里的码，原始串留在 note 里。 | def _payload_reason(raw_reason: str, status: int) -> tuple[str, str]: |
| fetch_blob@349 | def | L349-449 | 取一个 URL 的原始字节，装进 Blob.data。 | def fetch_blob( |
| _find_pdftotext@458 | def | L458-460 | pdftotext 的绝对路径；找不到返回 ""。 | def _find_pdftotext() -> str: |
| _find_pandoc@463 | def | L463-465 | pandoc 的绝对路径；找不到返回 ""。 | def _find_pandoc() -> str: |
| _find_powershell@468 | def | L468-476 | powershell 的绝对路径；找不到返回 ""（非 Windows 一定为空）。 | def _find_powershell() -> str: |
| _run@479 | def | L479-498 | 跑一个子进程，返回 (returncode, stdout, stderr)。不抛异常（超时也算返回码 -1）。 | def _run(cmd: list[str], *, data: bytes \| None = None, timeout: float… |
| _err_text@501 | def | L501-502 |  | def _err_text(raw: bytes, limit: int = 200) -> str: |
| _pdf_via_pypdf@512 | def | L512-526 |  | def _pdf_via_pypdf(data: bytes) -> str: |
| _pdf_via_pymupdf@529 | def | L529-541 |  | def _pdf_via_pymupdf(data: bytes) -> str: |
| _pdf_via_pdftotext@544 | def | L544-560 | pdftotext -layout -enc UTF-8 - -：stdin 喂字节，stdout 取文本。 | def _pdf_via_pdftotext(data: bytes) -> str: |
| _pdf_via_pandoc@563 | def | L563-579 | pandoc 兜底。 | def _pdf_via_pandoc(data: bytes) -> str: |
| _pdf_backends@582 | def | L582-589 | 降级链。每次调用时重新取模块属性，自检替换 _pdf_via_* 就能整体关掉某档。 | def _pdf_backends() -> list[tuple[str, Any]]: |
| _docx_via_builtin@595 | def | L595-630 | 标准库抽 docx：zipfile + ElementTree 读 word/document.xml。 | def _docx_via_builtin(data: bytes) -> str: |
| _docx_via_pandoc@633 | def | L633-640 |  | def _docx_via_pandoc(data: bytes) -> str: |
| _docx_backends@643 | def | L643-644 |  | def _docx_backends() -> list[tuple[str, Any]]: |
| _doc_via_word_com@679 | def | L679-720 | .doc（OLE2 二进制）唯一可用后端：Word COM。 | def _doc_via_word_com(data: bytes) -> str: |
| _xlsx_via_builtin@726 | def | L726-778 | 标准库粗抽 xlsx：sharedStrings.xml + 每个 worksheet 的单元格，每行用 \t 连。 | def _xlsx_via_builtin(data: bytes) -> str: |
| _html_via_builtin@790 | def | L790-805 | HTML → 纯文本，纯 re 实现。 | def _html_via_builtin(data: bytes, content_type: str = "") -> str: |
| _chain@811 | def | L811-843 | 跑完一条降级链：返回 (文本, 后端名)，全失败抛 Unparsed。 | def _chain( |
| to_text@846 | def | L846-887 | Blob → (文本, 后端名)。抽不出抛 Unparsed，绝不返回空串。 | def to_text(blob: Blob) -> tuple[str, str]: |
| fetch_and_text@890 | def | L890-906 | 一行完成「取附件 → 抽文」，返回 (文本, blob, 后端名)。 | def fetch_and_text(http: Any, url: str, **kw) -> tuple[str, Blob, str]… |
