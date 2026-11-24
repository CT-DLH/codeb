---
covers:
  - collector/survey_refs.py
title: Semantic block index: survey_refs.py (layer 4)
updated: 2026-11-24
---

# 语义块索引：survey_refs.py（第4层）

**源码文件**：`collector/survey_refs.py`  
**解析器**：`ast`  
**第5层完整正文**：`read_block(path="collector/survey_refs.py", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| url_key@71 | def | L71-87 | URL 的比较键：只保留 host + path，把「同一页面的不同写法」抹平。 | def url_key(url: str) -> str: |
| path_segments@90 | def | L90-93 | URL 的路径段（已 percent 解码），给 content_id 兜底档用。 | def path_segments(url: str) -> list[str]: |
| section_text@101 | def | L101-113 | 取 ## <name> 小节内容。按整行匹配标题，和 sections.ts 同一口径。 | def section_text(body: str, name: str) -> str: |
| RefTarget@119 | class | L119-137 | 一条引用解析到的采集卡。字段只放「解析与判定需要的」，不放整份 frontmatter。 | class RefTarget: |
| RefTarget.ref@132 | def | L132-134 | 写进信息卡 ext.refs 的形式：domain/card_id（与 resolveRefValue 的解析口径一致）。 | def ref(self) -> str: |
| RefTarget.score@136 | def | L136-137 |  | def score(self) -> tuple[int, int, int]: |
| CollectIndex@140 | class | L140-229 | cards/collect//*.md 的只读索引：URL/规范化键/content_id → 采集卡。 | class CollectIndex: |
| CollectIndex.__init__@151 | def | L151-157 |  | def __init__(self, cards_root: Path = CARDS_COLLECT): |
| CollectIndex._load@159 | def | L159-186 |  | def _load(self, root: Path) -> None: |
| CollectIndex._put@189 | def | L189-195 | 同一 URL 可能同时存在空壳卡与正文卡：留「更有材料」的那张。 | def _put(bucket: dict[str, RefTarget], key: str, target: RefTarget) ->… |
| CollectIndex.resolve@197 | def | L197-216 | 四档解析，档位与顺序固定（实测 ①+③ 就把本批 787/787 全解掉）。 | def resolve(self, url: str) -> RefTarget \| None: |
| CollectIndex.resolve_by_key@218 | def | L218-229 | ② 档：按采集库的合并键找卡。本批命中 0，但换批名单就会出现。 | def resolve_by_key(self, collector_key: str) -> RefTarget \| None: |
| load_db_rows@234 | def | L234-254 | 读采集库，返回 (URL → 行, canonical_key → 行)。 | def load_db_rows(db_path: Path = DB_PATH) -> tuple[dict[str, dict], di… |
| store_row@257 | def | L257-265 | 卡片 → 对应库行：先按 collector_key（合并键），再退回 URL。缺行返回空 dict。 | def store_row(target: RefTarget \| None, by_url: dict, by_key: dict) -… |
| classify@277 | def | L277-302 | 一条引用落到哪个材料桶。顺序即优先级，别按字典序重排。 | def classify(target: RefTarget \| None, row: dict, data_dir: Path = DA… |
| state_of@305 | def | L305-318 | 阶段机。有序规则：先命中先定，不能四条独立判完再抢值。 | def state_of(curated_note: str, refs_pending: int, refs_material: int)… |
| load_curated_notes@321 | def | L321-346 | competition_key → 卡上已有的 ext.curated_note（只读，毫秒级）。 | def load_curated_notes(info_root: Path \| None = None) -> dict[str, st… |
| SeqRefs@352 | class | L352-373 | 一个实体的索引投影结果——直接对应信息卡上的那几个字段。 | class SeqRefs: |
| SeqRefs.count@372 | def | L372-373 |  | def count(self) -> int: |
| build_seq_refs@376 | def | L376-417 | 一个实体：URL 清单 → 去重后的采集卡 + 五个计数。 | def build_seq_refs(seq: str, urls, index: CollectIndex, by_url: dict, … |
| _selftest@422 | def | L422-487 | 打印与方案文档一致的数字。数字变了说明实现或数据变了，两者都要能解释。 | def _selftest(name: str) -> int: |
| main@490 | def | L490-494 |  | def main(argv: list[str] \| None = None) -> int: |
