---
covers:
  - distill/sessions.py
title: Semantic block index: sessions.py (layer 4)
updated: 2026-11-24
---

# 语义块索引：sessions.py（第4层）

**源码文件**：`distill/sessions.py`  
**解析器**：`ast`  
**第5层完整正文**：`read_block(path="distill/sessions.py", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| decode_bytes@59 | def | L59-71 | zstd skippable-frame 会话文件 → 明文。 | def decode_bytes(raw: bytes) -> bytes: |
| _decode_cli@74 | def | L74-91 |  | def _decode_cli(raw: bytes) -> bytes: |
| session_file@94 | def | L94-99 |  | def session_file(dirpath: Path) -> Path \| None: |
| parse_ts@102 | def | L102-111 |  | def parse_ts(value) -> datetime \| None: |
| norm_slash@116 | def | L116-117 | ---------------------------------------------------------------- 路径归一 | def norm_slash(p: str) -> str: |
| to_posix@120 | def | L120-121 |  | def to_posix(p: Path) -> str: |
| abs_path@124 | def | L124-134 | 把会话里的路径参数变绝对（posix 斜杠），供分仓库与判文件用。 | def abs_path(target: str, cwd: str \| None) -> str: |
| repo_of@137 | def | L137-156 | 绝对路径 → (仓库名, 仓库内相对路径)。 | def repo_of(abs_posix: str, cwd: str \| None) -> tuple[str \| None, st… |
| basename_of@159 | def | L159-160 |  | def basename_of(p: str) -> str: |
| call_target@163 | def | L163-168 |  | def call_target(name: str, args: dict) -> str \| None: |
| text_of@173 | def | L173-181 | message.content[] → 纯文本。跳过 reasoning：它是草稿，不能当证据引用。 | def text_of(content) -> str: |
| parse_args_field@184 | def | L184-193 |  | def parse_args_field(raw): |
| excerpt@196 | def | L196-197 |  | def excerpt(s: str, limit: int = MAX_EXCERPT) -> str: |
| short_id@202 | def | L202-205 | 会话短名：去掉目录名里的 session- 前缀，只留 uuid 头 8 位。 | def short_id(sid: str) -> str: |
| fold_session@208 | def | L208-353 |  | def fold_session(path: Path, sid: str) -> dict: |
| discover@358 | def | L358-373 | ---------------------------------------------------------------- 发现 | def discover(home: Path, cwd_filter: str \| None) -> list[tuple[Path, … |
| material_index@376 | def | L376-384 | 便宜清单：不解码正文。 | def material_index(home: Path, cwd_filter: str \| None) -> list[dict]: |
| render_report@389 | def | L389-433 | ---------------------------------------------------------------- 报告 | def render_report(mats: list[dict], min_cost: int) -> str: |
| main@438 | def | L438-480 | ---------------------------------------------------------------- CLI | def main(argv=None) -> int: |
