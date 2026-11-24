---
covers:
  - collector/llm/
  - collector/refs/llm_parse.py
  - collector/tools/llm_compare.py
  - collector/tools/selftest_llm.py
  - docs/LLM抽取层.md
---

# Collector: LLM extraction

把「从非结构化文本里取字段」这类正则换成 LLM。**不是全面替换**——换哪一类、不换哪一类有明确边界。

## Boundary: three task classes

- **A 真提取**（从散文里找字段）→ 换 LLM。
- **B 格式**（`2024-03-05` 这种固定形状）→ 留正则，LLM 反而更贵更不稳。
- **C 项目保证**（我们自己写入的字段）→ 不需要抽取。

**新增抽取需求一律走这一层，不再写文法。** 这是 2026-10-29 定下的规则。
「科研项目抽取」就是按这个套路加的：同一套 `llm_json` + 分块 + 缓存 + 逐字溯源，只换 schema 与提示，没写任何正则。

## No LLM on the synchronous path

`card_import` / `card_create` 是 MCP 同步工具，客户端默认 **60s 超时**。

所以抽取只在 `inbox/*.jsonl` **生成阶段**发生，`ingest.ts` 一行不改。
这条约束决定了整个架构：LLM 永远是「离线预处理」，不在写入路径上。

## Four rules and their measured consequences

1. **JSON Schema 约束**：先 `response_format=json_schema` → 被拒用 `json_object` → 再「从文本抠 JSON」，每层过本地校验。
   **回退只发生在「400/404/422 且原因与 response_format 有关」**——超时/网络错误换格式没用，
   实测按旧写法一次慢 provider 能把整批挂死 12 分钟。

2. **逐字复制**：prompt 明写「不改写/不补全/不翻译/不纠错」。校验用 `check_fields()`：
   值必须在原文里找得到，**找不到只计数不丢数据**。

3. **溯源**：`line` 是整卡序号（分块时带 offset）。
   **`quote` 由命中的那一行自己派生，不再信模型给的原句**——实测模型给的 quote 有一半对不上（截断、改标点），
   而派生出来的必然逐字。模型那句只当一致性校验，对不上记 `quote_mismatch`（这是它指错行的信号），仍不丢条目。

4. **缓存是硬要求**：key = `sha256(prompt_version + model + schema 名 + system + 输入)`，存 `collector/data/llm_cache.db`。
   **system 也进 key**——改 prompt 忘了 bump 版本时才不会静默复用旧结果。

## Two provider traps

### Reasoning models eat the whole budget

本机的 `nvidia/nemotron-3.5-lightning-30b-a3b` 带思考：`max_tokens=400` 时
**100% 花在 `reasoning_content`**，`finish_reason=length`、`content` 为空。
三种 `response_format` 表现完全一样，**换格式救不回来**。

解法：`extra_body={"chat_template_kwargs": {"enable_thinking": false}}`，1.1–1.5s 直接出 JSON。
判定「空输出 + finish=length + 有 reasoning」时**直接报错让人调**，不要静默重试。

### Throughput sets the chunk size

| 输入 | 耗时 |
| :-- | --: |
| 5 行 | 24s |
| 10 行 | 26.5s |
| 12 行 | 32.5s |
| 30 行 | **180s 超时**（重试 3 次全废） |

所以默认 **12 行一块**（`LLM_CHUNK_LINES` 可调），每块独立缓存：跑到一半失败不白跑，重跑只补缺的块。
135 行的卡 = 12 块 ≈ 5 分钟。

## Chunk robustness: one bad chunk must not kill the card

原来的写法是：任何一块返回非法 JSON → 整卡抛 `LlmUnavailable` → 回退文法 → **800 多行白跑**。
mentor-116 有 809 行（占语料 15%），一次就废掉。

改成：单块失败只记 `failed_chunks` 并继续，**只有全部块失败才抛**。
重抽该卡 475 条、68 块、0 失败。

## Measured: where LLM and grammar each win

3 张卡并排对照（176 行）：

**LLM 明确更好**：

- 恢复短名前缀：`TDeLTA: A Light-Weight…`、`MMDIR: Multimodal…`——文法把前缀当作者/刊名切掉了。
- 丢掉藏进列表的垃圾行：纯人名 `Baotian Hu and Yang Xiang`、页码 `2154-2167` 被文法当成论文。
- 剥掉出处尾巴：`…Object Tracking，Knowledge-Based Systems，2017 通讯作者` → `…Object Tracking`。

**LLM 更差的地方**（密集编号列表 v1）：27/103 的标题带着行首序号，23 条超过 120 字（整行抄进标题）。
v2 prompt 加了「序号不是标题」「作者/出处不进标题」两条规则，并在清洗层确定性剥掉 `12.` 前缀：

| 指标 | v1 | v2 |
| :-- | --: | --: |
| 带行首序号的标题 | 27 | **0** |
| 超过 120 字的标题 | 23 | **1** |
| 抽出条数 | 103 | 87 |

## When one parser per card is not enough

- **单行一条的引用列表**（多数导师卡）：LLM 严格更好，可换成主解析器，文法留作回退。
- **135 行这种密集编号列表**：两边各有缺陷，**差异集占一半以上**（仅文法 108 / 仅 LLM 65）。
  这类卡不能整卡二选一，要**逐行仲裁**：两边都抽到 → 取更短、不带序号/作者前缀的那个；
  只有一边抽到 → 保留并标来源，人工看前 100 条再定规则。

成本参考：176 行用 16 块 ≈ 8 分钟；5404 行 ≈ 450 块 ≈ **3 小时**、约 1M token。

## Key numbers from the full run

111 张 mentor 卡里 **81 张有「科研论文」节**，共 5404 行 → **3878 条**题录。

- 逐字率 **98.1%**（3806/3878）。非逐字的 72 条里 45 条只是引号/破折号写法差异，真偏差 27 条（0.7%）。
- 与文法并排：仅文法 2583 / 仅 LLM 2141。**差异大头不是谁漏了，而是文法把期刊名、作者行、
  分隔线（`——————`）当成了论文**——这再一次说明密集列表不能整卡二选一。
- 幂等：同一输入跑两次，输出 jsonl 的 sha256 **逐字节相同**，第二次 0 次模型调用。

## Self-test

`tools/selftest_llm.py` 离线自检 34 条，**不联网**。
文法回退侧的 `selftest_refs.py` 22 条不受影响——两条路都要保持可跑，否则回退就是假的。
