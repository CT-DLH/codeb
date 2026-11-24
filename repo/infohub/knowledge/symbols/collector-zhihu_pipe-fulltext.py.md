---
covers:
  - collector/zhihu_pipe/fulltext.py
title: Semantic block index: fulltext.py (layer 4)
updated: 2026-11-24
---

# 语义块索引：fulltext.py（第4层）

**源码文件**：`collector/zhihu_pipe/fulltext.py`  
**解析器**：`ast`  
**第5层完整正文**：`read_block(path="collector/zhihu_pipe/fulltext.py", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| load_cfg@38 | def | L38-45 |  | def load_cfg() -> dict: |
| _limits@48 | def | L48-56 |  | def _limits(cfg: dict) -> dict: |
| host_of@59 | def | L59-60 |  | def host_of(url: str) -> str: |
| allowed@63 | def | L63-72 | 域名后缀匹配：arxiv.org 也放行 export.arxiv.org。 | def allowed(url: str, cfg: dict \| None = None) -> bool: |
| _throttle@75 | def | L75-81 |  | def _throttle(lim: dict) -> None: |
| _download_in_thread@84 | def | L84-113 | 真正的下载体；结果/异常塞进 box，由调用方在主线程里重抛。 | def _download_in_thread(url: str, lim: dict, box: dict) -> None: |
| download@116 | def | L116-156 | 带大小上限的下载；不是 PDF 就直接拒绝（不顺手去爬 HTML 正文页）。 | def download(url: str, cfg: dict \| None = None) -> bytes: |
| pdf_to_text@159 | def | L159-182 | PDF → 文本。走 kit/blob.py 的四档降级链，不自带一套。 | def pdf_to_text(data: bytes) -> str: |
| clean_text@186 | def | L186-214 | PDF 抽出来的文本要处理成可读段落： | def clean_text(raw: str, max_chars: int) -> str: |
| harvest@217 | def | L217-256 | 按顺序试可用的 OA 链接，抽到足够长的正文就返回。 | def harvest(urls: list[str] \| str, cfg: dict \| None = None) -> dict: |
