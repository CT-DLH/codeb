---
covers:
  - pipelines/
updated: 2026-11-21
---

# Pipelines: LLM tasks as JSON config

`pipelines/` 里全是 JSON，没有代码。每一份都是 `scripts/batch_llm.ts` 的任务配置——**加一份配置就多一个任务，改提示词不动代码**。唯一的例外是 `mentor-papers-summary.json`，它被 `scripts/mentor-papers-summary.ts` 读（那个脚本需要 map/reduce 两阶段，`batch_llm` 的「一卡一字段」模型表达不了）。

## 跑法

```
npx tsx scripts/batch_llm.ts --config pipelines/<name>.json [--limit N] [--only id1,id2] [--dry-run]
```

`--config` 必填，缺了 `exit 1` 打用法。`--limit` 数的是「过滤之后真正要处理的那几张」，不是目录里的前 N 个文件——先 filter 再截断，这个顺序影响可复现性。`--only` 收 card_id 或文件名（逗号分隔），用来重跑人工审过的那一批。

`--dry-run` 不只是「不写盘」：它把 `save_mode` 强制改成 `jsonl`，所以预演看到的是「将要通过 `card_import` 写入什么」，而不是「将要直接改哪个字段」。

## 配置的骨架

一份配置最少要有 `domain` + `target` + `prompt`，以及 `source` / `source_sections` / `join` 三者之一。缺了会在启动时 `exit 1`，错误信息直接说缺什么：

```
配置需要 source（当前卡字段）/ source_sections（正文小节）/ join（跨卡上下文）之一
```

`source` 与 `source_sections` **互斥**（前者取一个字段，后者取正文小节），同时给也 `exit 1`。

| 键 | 语义 |
| :-- | :-- |
| `domain` | 领域名。经 `domainDir()` 映射到 `cards/<collect\|info\|report>/<子类型>/`。目录不存在时 `exit 2` 并列出可用领域 |
| `source` | 材料来源。特值：`body`（正文前 3000 字）、`title+body`（标题 + 正文前 2000 字）；其余按字段路径取值 |
| `source_sections` | 从正文里取这几个 `## 小节` 拼成材料。小节名不存在时跳过并计数 |
| `source_min_chars` | 材料厚度闸。**低于这个字数不发请求**，直接跳过 |
| `target` | 写回目标字段路径（`title` / `summary` / `ext.title_zh` / `tags`…） |
| `prompt` | 系统提示。支持 `{{title}}` / `{{ext.venue}}` 这类本卡标量插值，以及 `{{joined_text}}` |
| `schema` | JSON Schema。给了就强制 `response_format: json_object`，并把 schema 追加进系统提示 |
| `filter.missing` | 列出的字段**全部**为空才处理（把范围压在脏数据上） |
| `save_mode` | `jsonl`（默认，只产 `card_import` 吃的行）/ `direct`（直接改 frontmatter） |
| `out` | `jsonl` 模式的输出文件，落在 `inbox/` |
| `concurrency` | 并发 worker 数，默认 1 |
| `batch_size` | 一次请求处理 N 条，默认 1。> 1 时禁 `join` / `source_sections` / `{{...}}` 插值 |
| `skip_source_cjk` | 原文已是中文就跳过（翻译任务用） |
| `provenance` | 写盘时往 `sources` 补的来源条目 `{file, kind, fields}` |

## join：跨卡取原文

`join` 是 `batch_llm` 最重要的一个能力：当前卡的某个字段里存着**别的卡的 id**，引擎把那些卡的指定小节拼成 `{{joined_text}}`。

```json
"join": {
  "domain": "info_mentor",
  "on": "ext.mentors",
  "select_section": "科研论文",
  "hint_field": "title",
  "max_chars": 8000
}
```

`on` 指向当前卡上的字段，值可以是单个 id 或数组；id 可写 `mentor/mentor-031` 也可只写 `mentor-031`（自动补 `join.domain` 前缀）。缺卡、小节不存在都会进 `notes` 并跳过那张。

**`max_chars` 的默认 8000 是有依据的**，注释里记了实测：导师主页的论文小节中位数 2.8 万字、最长的 16 万字。从头截 2 万字只保住 63% 的关键行，按相关性挑块 8 千字就是 100%——预算小反而准。

`selectBlocks` 的算法：按条目切块（空行或 `- ` / `1. ` 开头断块），拿 `hint_field`（默认 `title`）的值切成线索词（英文取 3 字符以上非停用词，中文按二元组），每块数命中数，**按密度排**（`hits / sqrt(block.length / 200 + 1)`）。按密度而非绝对命中数是关键：几千字的摘要块会把一行标题挤出去（实测绝对分值只排到第 18 位，密度排进前三）。命中数为 0 就停，不硬塞——留给模型自己判断「找不到」。

## 输出闸：一串否决式检查

`applyResult` 是所有结果写盘前的唯一入口，单卡与批量两条路径共用。它是一串**串联的否决检查**，任一命中就 `stats.same++` 并 `return`（不是抛错）。顺序有讲究：

| 顺序 | 检查 | 挡什么 |
| :-- | :-- | :-- |
| 1 | 空值保护 | 模型返回 `null`/空串 → 保留原值，绝不把原值清空 |
| 2 | `strip_leading_title` | 输出开头重复了卡片标题时去掉它。**必须排在「本来就是对的」比较之前**——落盘后存的是去掉姓名的版本，后比较会每次判成有改动，幂等判断失真 |
| 3 | 与原值完全相同 | 无改动 |
| 4 | `normalizeSkeleton` 相同 | 只差标点/空白/大小写的假修改 |
| 5 | `join.reject` 正则 | 返回形状不可能是目标值（链接、DOI） |
| 6 | `join.reject_name_list` | 返回像作者名单（3 段以上、八成是短段的引文行） |
| 7 | `max_output_chars` | 模型把摘要塞进 title |
| 8 | `allow_superset`（默认关） | 返回里套着原标题。默认关是因为「修标题」不该把标题换成整条引文；**重写型**字段（新简介包含旧摘要）才开 |
| 9 | `allow_language_change`（默认关） | 中文标题被换成英文名 |
| 10 | `require_cjk` | 翻译任务返回英文原题 |
| 11 | `min_output_chars` | 「教授，博导」这种职称串当简介 |
| 12 | `join.verbatim` | 答案必须能在关联原文里逐字找到（归一化忽略空白/大小写/项目符号/序号） |
| 13 | `grounding.terms` | 输出里的术语要逐字出现在材料里 |
| 14 | `grounding.min_cjk_coverage` | 输出里的中文二元组要有多大比例能在语料里找到 |

第 13 条有个精细的例外：材料本身是英文时**不启用中文词表**——模型会把 Associate Professor 译成「副教授」，按中文词表核对必然误伤（实测误伤 002）。判据只看小节**正文**：`readSectionsWithSize` 拼上去的 `### 个人简介` 是中文标题行，带着它判断会让英文材料被当成中文材料。

第 14 条的实现是 `cjkCoverage`：把输出切成中文二元组，数多少能在语料里找到，低于阈值就拒。这是拦「整段虚构」的手段（材料 794 字全英文，模型写出一串中文研究方向）。

## 各份配置在做什么

| 文件 | 领域 | 输入 → 输出 | 写回方式 |
| :-- | :-- | :-- | :-- |
| `mentor-summary-unify.json` | `info_mentor` | 正文「个人简介 / 研究方向」两节 → `summary` | `jsonl`（默认） |
| `fix-paper-titles.json` | `collect_paper` | 导师主页「科研论文」小节（join 到 `info_mentor`）→ `title` | `direct` |
| `paper-title-zh.json` | `collect_paper` | `title` → `ext.title_zh` | `direct` |
| `clean-mentor-tags.json` | `info_mentor` | `ext.research` → `tags` | `jsonl`（默认） |
| `curate-competition.json` | `info_competition` | join `collect_web` 的「AI 摘要」→ `ext.curated_note` | `jsonl` |
| `summarize-papers.json` | `collect_paper` | `title+body` → `summary` | `jsonl` |
| `mentor-papers-summary.json` | `info_mentor` | 反向聚合 + map/reduce → 正文「论文总结」小节 | 由 `mentor-papers-summary.ts` 写 |

几份配置里值得注意的口径：

**`mentor-summary-unify.json`** 是最简单的一份（23 行）。`source_sections: ["个人简介", "研究方向"]` 只取两节小品——`source: "body"` 会把「科研论文」小节一起塞进去，中位数 2.8 万字，既超预算又让模型拿论文列表编简介。厚度闸 `source_min_chars: 30`、`min_output_chars: 20`、`allow_superset: true`（重写型，新简介包含旧摘要属正常）、`grounding.min_cjk_coverage: 0.45`。`grounding.terms` 12 项（教授/副教授/助理教授/讲师/博士生导师/硕士生导师/国家级/省部级/院士/特聘/长江学者/杰青/优青）——这些词**材料里没有就不许出现**。`corpus_fields` 只有 `["ext.dept"]`：`ext.research` **不在白名单**，只能经正文材料进入。

⚠ 这份配置**没有 `max_output_chars` / `require_cjk` / `strip_leading_title` / `concurrency` / `save_mode`**（2026-11 核对）。长度上限只由提示词的「20~120 字」约束；产出落 `inbox/mentor-summary-unify.jsonl`，**落盘还要过 `card_import` 预演**，不是直接改卡。这些键 `batch_llm.ts` 都支持，只是没启用——别把本页别处描述当成已生效的约束。

**`fix-paper-titles.json`** 的 `join` 开了 `verbatim: true`（标题必须是原文的逐字片段）+ `reject_name_list: true` + 一长串 `reject` 正则（http / doi: / `10.xxxx/` / 期刊名开头 / 委员会头衔 / 纯会议缩写+年份）。这全部来自实测：模型会把「作者 + 原标题 + 期刊」整条抄回来（样本里 3/10）。

**`paper-title-zh.json`** 用 `batch_size: 8` + `skip_source_cjk: true` + `concurrency: 3`。批量模式下的那道保险在 `parseBatchResults`：返回条数或 id 对不上**整批作废**，宁可空着也不把 A 的结果挂到 B 上。提示词里还点了具体术语口径（nowcasting → 临近预报、token 保留英文、whole slide image → 全切片图像）。

**`curate-competition.json`** 的 `join.select_section` 是「AI 摘要」，`max_chars: 8000`。它守一条规矩：同一件事多份材料说法不一致时用「有资料称…」保留分歧，不替读者裁决——因为竞赛信息卡的读者要自己判断。

**`clean-mentor-tags.json`** 有一道特殊的断点续跑判据在代码里（不是配置）：目标数组已有值且不含分词碎片（`and`/`for`/`data`/`mining`/`learning`/`of`/`in`）就当洗过了，直接跳过。

## mentor-papers-summary.json 为什么不一样

`batch_llm` 的模型是「一卡一字段」，关联原文靠 `join.on` 指向的卡 id 存在**当前卡**上。导师论文是反过来的：论文指向导师，导师卡里没有论文 id 清单。而且一位导师最多几百篇，按相关性截块必然丢论文，剩下的清单就不再是「他的论文」。

所以这份配置的读法是：`scripts/mentor-papers-summary.ts` 读它，但只用它的 `map` / `reduce` 两段提示词与 schema、`chunk_size`、`target_section`、`reverse_join`、`out`、`provenance`。**反向索引、分块、合并的逻辑在脚本里，提示词与 schema 在配置里**——换提示词不动代码，重跑可复现。

它的 `reduce.prompt` 里有一条强约束：代表作标题必须是输入「逐篇要点」里 `标题` 字段**逐字**出现过的那串文字（保留英文、标点、大小写），且每篇论文只能归入一条主线。脚本侧对应三道闸：

1. map 返回条数或 id 与输入对不上 → 整批作废。
2. reduce 的主线代表作标题必须逐字来自输入（`norm` 后比对），对不上就丢掉；全丢光则跳过这位导师。
3. 已有「论文总结」小节且篇数与当前索引一致 → 不发请求（重跑只为补新论文或 `--force`）。

第 2 条的实现里有一处注释很值得读：不能用 `titleSet.has(...)` 写进 `find` 的谓词——它不依赖 `p`，任何认得的标题都会命中**第一篇**论文，主线会全并到同一篇上。

## 与 collector / llm-client 的关系

所有 LLM 调用都走 `src/mcp/lib/llm-client.ts` 的 `callLLM(prompt, text, schema)`。它做四件事：

1. **从 `collector/.env` 读凭据**（`ZHIHU_LLM_API_KEY` / `ZHIHU_LLM_BASE_URL` / `ZHIHU_LLM_MODEL`），并且**只在 `process.env` 里没有该键时才写**——环境变量优先于文件。
2. **结果缓存**在 `collector/data/llm_ts_cache.json`，键是 `sha256(model \0 prompt \0 text \0 schema)`。所以同一份材料跑两次只花一次配额，这也是「重跑幂等」在成本侧成立的原因。
3. 关闭推理模型的思考过程：`LLM_EXTRA_BODY` 可整体覆盖 body；否则 `LLM_DISABLE_THINKING=1` 或（默认且端点是 nvidia.com 时）设 `chat_template_kwargs.enable_thinking = false`。
4. 给了 schema 就设 `response_format: json_object`，并在系统提示尾部追加「必须严格按 JSON Schema 生成」+ schema 本体 + 「不要把 Schema 本身当成结果输出」——后者是针对一类真实坏输出的防御（`extractValue` 里也有对应的兼容：模型把 schema 对象吐回来时，从 `properties` 里取第一个键的值）。

`batch_llm` 与 collector 的关系只有一条：**共用同一个 `.env` 与同一个缓存文件**。采集侧的 Python 摘要走 `zhihu_pipe` 自己的 LLM 客户端，两边不共享缓存（一份 JSON 一份 Python）——所以同一段文本在两侧各算一次。这个重复没有优化，因为采集侧与加工侧的调用时机、模型、提示词都不同，强行共享反而会让缓存键的语义变得含糊。

`mentor-papers-summary.ts` 额外做了一件事：**给采集摘要让路**。它维护 `collector/data/llm_busy.json` 心跳（`{pid, kind, at, note}`），用 `renameSync` 原子写；调用前 `waitForQuiet` 等别人空闲，调用后 `busyTouch` 刷心跳。判定「持有者已退出」的口径是心跳超过 180 秒没更新，与 `zhihu_pipe/busy.py` 同一口径。心跳写不进去不影响本任务（try/catch 吞掉），只影响别人看不看得到我们在烧配额。

## 闸的盲区：它只防模型编，不防源数据脏

`grounding` 系列闸拦的是**模型自己加戏**（材料说在某校任教，模型补出「副教授」）。它拦不住另一种坏输出：**源数据本身就是错的，模型忠实抄了，而且抄得完全合规**。

实测（2026-11，`mentor-summary-unify` 全量预演）：某张导师卡的 `ext.research` 本身是论文标题的连写残片，尾部还带着拼写错误（`…Scanpath Prediction of the 360-degree Videso`）。模型把它逐字放进「研究方向：…」，接地闸一路放行——因为**每个字确实都在材料里**。

判据：**接地闸的语义是「输出 ⊆ 材料」，不是「材料是对的」**。所以遇到「输出荒谬但过闸」时，先查源字段而不是调阈值：

```
输出长度正常、过 terms、过 coverage、方向名却像一串句子的尾段
  → 去看 source 字段本身（ext.research / ext.dept）
  → 是连写残片 / 截断 / 拼写错误时，修源数据，不要加闸
```

反过来的坑也在同一处：曾有一批卡的 `ext.research` 是「连写的一串论文标题」，若在提示词里原样列出方向候选，模型会把整串抄进简介。**`corpus_fields` 允许照抄的字段必须先确认自己干净**，否则等于给模型发了一份它没有能力质疑的材料。

### 闸拦下之后：人工兜底，不改闸

`--only` 落盘时被闸拦下的卡，走人工核写而不是放宽阈值：

```
card_batch（ops_file 指向 jsonl，每条 {op:"update", card_id, changes, note})
  → dry_run 看报告 → dry_run:false 落盘
```

`note` 里写明「闸拦下的原因 + 人工依据」（如「闸拦下（凭印象补职称）；材料无职称，人工不写职称」）。这样复盘时能区分「模型写对的」与「人写的」，也是以后调阈值的依据。

**不要因为几张卡过不了闸就放宽全局阈值**——被拦下的样本恰好是闸的价值证明。实测那批里 010 是英文材料被编出中文研究方向、030/065 是材料无职称被补「教授/副教授」，放宽就全放出去了。

### 并发数与端点限流

`concurrency` 默认 1。部分端点（实测 NVIDIA 托管的推理模型）并发 3 会**成批超时 / `fetch failed`，几十条请求全废**，而并发 1 只废个别条。这不是重试能救的（整批都撞在同一个限流窗口上）。

判据：一次预演里 `[ERR] … fetch failed` 集中出现、且条数接近「未命中缓存的全部请求」，就是限流而不是内容问题。降 `concurrency` 重跑——缓存命中已成功的那部分，不重复花钱。

### 改提示词等于让缓存全部失效

缓存键含 `prompt`。改一个字的提示词，**所有卡都要重新请求**（实测改提示词后一次跑出 76 条新请求；而只改并发数是 0 成本）。所以：

- 调闸参数（`concurrency` / `min_output_chars` / 阈值）不影响缓存，可以反复试；
- 改提示词前先在 `--limit 5` 上看一眼输出形状，别在全量上迭代提示词。
