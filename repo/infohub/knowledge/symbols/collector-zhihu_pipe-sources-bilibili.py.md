---
covers:
  - collector/zhihu_pipe/sources/bilibili.py
title: Semantic block index: bilibili.py (layer 4)
updated: 2026-11-24
---

# 语义块索引：bilibili.py（第4层）

**源码文件**：`collector/zhihu_pipe/sources/bilibili.py`  
**解析器**：`ast`  
**第5层完整正文**：`read_block(path="collector/zhihu_pipe/sources/bilibili.py", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| RiskControl@70 | class | L70-74 | -352 / 412 / 429：B 站风控，属于「本源临时不可用」，不是某篇内容抓取失败。 | class RiskControl(QuotaExceeded): |
| _clean@77 | def | L77-85 | B 站的 tag/description 有时是字符串、有时是列表，标题里还带 HTML 实体。 | def _clean(text: Any) -> str: |
| _int@88 | def | L88-105 | B 站同一字段在不同接口里可能是 int、数字字符串、甚至 450:7 这种时长。 | def _int(v: Any) -> int: |
| _key_from_url@108 | def | L108-110 |  | def _key_from_url(url: str \| None) -> str: |
| _mixin_key@113 | def | L113-117 |  | def _mixin_key(img_key: str, sub_key: str) -> str: |
| _query_string@120 | def | L120-125 |  | def _query_string(params: dict) -> str: |
| _signed_query@128 | def | L128-134 | WBI 签名：参数按 key 排序 -> 拼 wts -> md5(query + mixin_key) = w_rid。 | def _signed_query(params: dict, img_key: str, sub_key: str) -> str: |
| _read_varint@137 | def | L137-146 | 读一个 protobuf varint，返回 (值, 新下标)。 | def _read_varint(buf: bytes, i: int) -> tuple[int, int]: |
| _parse_dm_seg@149 | def | L149-208 | 解 DmSegMobileReply：repeated DanmakuElem = field 1 (tag 0x0A)。 | def _parse_dm_seg(raw: bytes) -> list[dict]: |
| _is_bvid@211 | def | L211-212 |  | def _is_bvid(s: str) -> bool: |
| BiliSource@215 | class | L215-691 |  | class BiliSource: |
| BiliSource.__init__@244 | def | L244-263 |  | def __init__(self) -> None: |
| BiliSource.set_min_interval@265 | def | L265-272 | CLI 的 --delay：两档一起覆盖（0 = 不限速，风控环境下不建议）。 | def set_min_interval(self, seconds: float) -> None: |
| BiliSource._headers@276 | def | L276-293 | ---------------------------------------------------------------- 底层请求 | def _headers(self, referer: str = "") -> dict[str, str]: |
| BiliSource._throttle@295 | def | L295-296 |  | def _throttle(self, bucket: str) -> None: |
| BiliSource._raw@298 | def | L298-316 |  | def _raw(self, url: str, *, bucket: str = "core", retries: int = 1) ->… |
| BiliSource._call@318 | def | L318-338 | 发一次请求并按 B 站的业务 code 翻译成内核听得懂的异常。 | def _call(self, path: str, params: dict \| None = None, *, bucket: str… |
| BiliSource._wbi_keys@340 | def | L340-350 | nav 接口的 wbi_img/sub_img 文件名，缓存 1 小时。 | def _wbi_keys(self) -> tuple[str, str]: |
| BiliSource._ensure_buvid@352 | def | L352-360 | 匿名也要有 buvid3，否则 search 极易 -412。只取一次，失败不阻断。 | def _ensure_buvid(self) -> None: |
| BiliSource._video_item@364 | def | L364-401 | ---------------------------------------------------------------- 翻译层 | def _video_item(self, v: dict, part: int = 1) -> Item: |
| BiliSource.search@405 | def | L405-420 | 关键词搜视频。kind 除 video 外本插件没有别的可给（不做专栏/用户搜索）。 | def search(self, query: str, *, limit: int = 30, cursor: str \| None =… |
| BiliSource.list_author@422 | def | L422-451 | 按 UP 主 mid 铺开其稿件。 | def list_author(self, author_id: str, *, kinds: Iterable[str] \| None … |
| BiliSource.fetch@453 | def | L453-474 |  | def fetch(self, ref: ContentRef) -> Document: |
| BiliSource.fetch_audience@476 | def | L476-574 | 观众反馈：评论（按热度分页）+ 弹幕（按 6 分钟分片）。 | def fetch_audience(self, ref: ContentRef, *, max_comment_pages: int = … |
| BiliSource._pick_cid@577 | def | L577-581 |  | def _pick_cid(info: dict, part: int) -> int: |
| BiliSource._header_md@583 | def | L583-605 |  | def _header_md(self, info: dict, part: int) -> str: |
| BiliSource._subtitles@607 | def | L607-652 | player/wbi/v2 的字幕轨 -> 纯文本。优先级：人工中文 > AI 中文 > 任意。 | def _subtitles(self, bvid: str, cid: int) -> str: |
| BiliSource.is_zh@623 | def | L623-625 |  | def is_zh(t: dict) -> bool: |
| BiliSource.is_ai@627 | def | L627-631 |  | def is_ai(t: dict) -> bool: |
| BiliSource._clip@655 | def | L655-656 |  | def _clip(body: str) -> str: |
| BiliSource.canonicalize@658 | def | L658-676 | BV 号 + 分 P 号才算身份；?p= 必须保留，其余参数（vd_source 等）丢弃。 | def canonicalize(self, url: str) -> str: |
| BiliSource.health@678 | def | L678-691 |  | def health(self) -> Health: |
