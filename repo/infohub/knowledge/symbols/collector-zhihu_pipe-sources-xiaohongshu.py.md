---
covers:
  - collector/zhihu_pipe/sources/xiaohongshu.py
title: Semantic block index: xiaohongshu.py (layer 4)
updated: 2026-11-24
---

# 语义块索引：xiaohongshu.py（第4层）

**源码文件**：`collector/zhihu_pipe/sources/xiaohongshu.py`  
**解析器**：`ast`  
**第5层完整正文**：`read_block(path="collector/zhihu_pipe/sources/xiaohongshu.py", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| NeedsLogin@132 | class | L132-137 | 页面回来了但没有笔记本体——登录态缺失或已过期。 | class NeedsLogin(QuotaExceeded): |
| NoSearchAvailable@140 | class | L140-141 |  | class NoSearchAvailable(NoSearch): |
| _note_id@144 | def | L144-160 | URL → 笔记 ID。 | def _note_id(url: str, *, loose: bool = False) -> str: |
| _canon_note_url@163 | def | L163-178 | 笔记 ID + 原 URL 里的 xsec 参数 → 规范 URL（身份是 ID，token 只是访问参数）。 | def _canon_note_url(nid: str, url: str) -> str: |
| _count@181 | def | L181-196 | 小红书把互动数写成 "1.2万" / "999" / "赞"，统一成整数。 | def _count(v: Any) -> int: |
| _ts@199 | def | L199-204 | XHS 的时间是毫秒；2000 年之前的值说明单位不是毫秒。 | def _ts(v: Any) -> int: |
| _img_url@207 | def | L207-218 | 图片直链。urlDefault 经常不存在，只有 infoList（按尺寸给的一组 URL）。 | def _img_url(img: dict) -> str: |
| _balanced_json@221 | def | L221-245 | 从首个 '{' 起做括号配平截取，正确跳过字符串里的花括号。 | def _balanced_json(s: str) -> str \| None: |
| initial_state@248 | def | L248-263 |  | def initial_state(html: str) -> dict \| None: |
| find_note@266 | def | L266-291 | 定位笔记本体。state 结构随版本/端变化，先走已知路径再递归兜底。 | def find_note(state: dict) -> dict \| None: |
| walk@277 | def | L277-288 |  | def walk(o): |
| XhsSource@294 | class | L294-647 |  | class XhsSource(BrowserSource): |
| XhsSource.__init__@321 | def | L321-339 |  | def __init__(self) -> None: |
| XhsSource.set_min_interval@341 | def | L341-344 |  | def set_min_interval(self, seconds: float) -> None: |
| XhsSource._throttle@348 | def | L348-351 | ---------------------------------------------------------------- 底层请求 | def _throttle(self) -> None: |
| XhsSource._get_html@353 | def | L353-372 | 返回 (HTML, 最终 URL)——最终 URL 负责把 xhslink 短链展开。 | def _get_html(self, url: str) -> tuple[str, str]: |
| XhsSource._load_note@374 | def | L374-385 |  | def _load_note(self, url: str) -> tuple[dict, str]: |
| XhsSource._note_item@389 | def | L389-414 | ---------------------------------------------------------------- 翻译层 | def _note_item(self, url: str, note: dict) -> Item: |
| XhsSource._kind@417 | def | L417-418 |  | def _kind(note: dict) -> str: |
| XhsSource._token@421 | def | L421-423 |  | def _token(url: str) -> str: |
| XhsSource.search@427 | def | L427-484 | 浏览器搜索：打开 search_result 页，读渲染后的卡片。 | def search(self, query: str, *, limit: int = 30, cursor: str \| None =… |
| XhsSource._search_item@486 | def | L486-504 |  | def _search_item(self, row: dict) -> Item \| None: |
| XhsSource.parse_url@506 | def | L506-518 | 导入器入口：粘贴的链接（含 xhslink 短链、微信分享文案里的 URL）→ Item。 | def parse_url(self, url: str) -> Item \| None: |
| XhsSource.list_author@520 | def | L520-552 | 作者主页笔记列表。 | def list_author(self, author_id: str, *, kinds: Iterable[str] \| None … |
| XhsSource.fetch@554 | def | L554-595 |  | def fetch(self, ref: ContentRef) -> Document: |
| XhsSource.canonicalize@597 | def | L597-615 | 笔记 ID 是身份，xsec_token 是访问参数：留在 URL 里但不进 uid。 | def canonicalize(self, url: str) -> str: |
| XhsSource.health@617 | def | L617-647 |  | def health(self) -> Health: |
