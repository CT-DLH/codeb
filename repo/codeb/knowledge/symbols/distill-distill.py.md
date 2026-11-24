---
covers:
  - distill/distill.py
title: Semantic block index: distill.py (layer 4)
updated: 2026-11-24
---

# 语义块索引：distill.py（第4层）

**源码文件**：`distill/distill.py`  
**解析器**：`ast`  
**第5层完整正文**：`read_block(path="distill/distill.py", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| _tmpout@62 | def | L62-64 |  | def _tmpout() -> Path: |
| run_kb@67 | def | L67-85 | 跑 kb.py 并拿到 (返回码, stdout, stderr)。 | def run_kb(argv: list[str], timeout: int = 60) -> tuple[int, str, str]… |
| kb_json@88 | def | L88-95 |  | def kb_json(argv: list[str], timeout: int = 60) -> dict \| None: |
| kb_alive@98 | def | L98-106 | 自检：kb 调用到底通不通。 | def kb_alive(repo: str) -> bool: |
| covered@109 | def | L109-119 | kb where：这个路径已经被哪些页覆盖。 | def covered(repo: str, rel_path: str) -> list[dict]: |
| merge_target@122 | def | L122-134 | 出现频次最高的页作为并入对象：同一条候选的证据若已散落在某页，就不该另起一页。 | def merge_target(hits_by_path: dict[str, list[dict]]) -> str \| None: |
| page_titles@137 | def | L137-140 | repo 下已有页：rel -> title。kb tree --json 返回扁平 items（不是目录树对象）。 | def page_titles(repo: str) -> dict[str, str]: |
| suggest_page@143 | def | L143-167 | 用 kb search 找"这条知识最该并进哪一页"。 | def suggest_page(repo: str, texts: list[str]) -> str \| None: |
| load_materials@172 | def | L172-185 | ---------------------------------------------------------------- 素材 | def load_materials(p: Path) -> list[dict]: |
| short_id@191 | def | L191-193 |  | def short_id(sid: str) -> str: |
| title_from@196 | def | L196-204 | 英文标题：内核 slugify 对中文会退化成 page-<hash>，所以标题必须给英文。 | def title_from(paths: list[str], limit: int = 3) -> str: |
| cand_s1@209 | def | L209-254 | S1 已付费的探索且 kb where miss：本工具的核心信号。 | def cand_s1(mats: list[dict]) -> list[dict]: |
| cand_s3@257 | def | L257-289 | S3 死路：失败过且不是瞬时抖动的，值得记"别这么干"。 | def cand_s3(mats: list[dict]) -> list[dict]: |
| cand_s2@292 | def | L292-328 | S2 用户纠正：代码里永远读不出来的那类知识。 | def cand_s2(mats: list[dict]) -> list[dict]: |
| cand_s7@331 | def | L331-364 | S7 未落库的高投入会话：审计线索，不是可落库的候选。 | def cand_s7(mats: list[dict]) -> list[dict]: |
| repo_root@380 | def | L380-384 |  | def repo_root(repo: str) -> Path \| None: |
| verify_facts@387 | def | L387-420 | 核对正文里提到的每个文件路径是否真实存在。 | def verify_facts(c: dict, max_missing: int = 0) -> list[str]: |
| substance_ok@439 | def | L439-466 | 返回"空壳"证据列表；空列表 = 通过。 | def substance_ok(c: dict) -> list[str]: |
| skeleton@486 | def | L486-505 | 无 LLM 时的正文骨架：把证据摆到位，让在场 agent 只需补判断。 | def skeleton(c: dict) -> str: |
| call_llm@530 | def | L530-535 |  | def call_llm(prompt: str, mode: str, verbose: bool = False) -> dict \|… |
| _llm_cmd@538 | def | L538-553 | 外部命令后端：用临时文件传 stdin/stdout，绕开沙箱对 piped stdio 的限制。 | def _llm_cmd(prompt: str) -> dict \| None: |
| load_env@577 | def | L577-611 | 读 env：先看真实环境变量，再补 infohub 的 .env。 | def load_env(verbose: bool = False) -> dict[str, str]: |
| _extra_body@614 | def | L614-621 | 推理型模型要关掉 thinking，否则 content 为空。 | def _extra_body(base: str, env: dict) -> dict: |
| _post@624 | def | L624-644 | 裸 HTTP POST，返回 (status, json)。4xx 不抛，交给调用方决定是否降级。 | def _post(url: str, payload: dict, key: str, timeout: int) -> tuple[in… |
| _content_of@647 | def | L647-661 | 取出正文，并说明为什么是空的（reasoning 吃满 token 是最常见的坑）。 | def _content_of(data: dict) -> tuple[str, str]: |
| _format_rejected@664 | def | L664-670 | 只有"服务端不认识 response_format"才降级；超时/网络错误应当重试。 | def _format_rejected(status: int, err: str) -> bool: |
| _llm_openai@673 | def | L673-740 |  | def _llm_openai(prompt: str, verbose: bool = False) -> dict \| None: |
| enrich@743 | def | L743-802 | 有 LLM 时补正文；没有就保留骨架。丢弃不合格草案。 | def enrich(c: dict, mats_by_id: dict[str, dict], mode: str, verbose: b… |
| upsert_argv@807 | def | L807-820 | 预填好的 kb upsert。标题必须英文（中文会让内核退化成 page-<hash> 文件名）。 | def upsert_argv(c: dict) -> list[str]: |
| write_bodies@823 | def | L823-828 |  | def write_bodies(cands: list[dict], outdir: Path) -> None: |
| render_md@831 | def | L831-864 |  | def render_md(cands: list[dict], mode: str) -> str: |
| apply_one@869 | def | L869-890 | 落盘：只走 kb upsert 这个唯一写入口，绝不直接写 md。 | def apply_one(c: dict, force: bool = False) -> dict: |
| main@895 | def | L895-989 | ---------------------------------------------------------------- CLI | def main(argv=None) -> int: |
