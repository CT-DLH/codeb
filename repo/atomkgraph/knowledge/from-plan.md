---
covers:
  - scripts/know-ingest.ts
  - scripts/group-ingest.ts
  - packages/core/src/ingest/unified.ts
  - packages/core/src/ingest/apply.ts
  - packages/core/src/ingest/paper-plan.ts
  - packages/core/src/repositories/paper-repo.ts
  - scripts/test-paper-ingest.ts
updated: 2026-11-20
title: Question and point ingests: two field namings and the from-plan traps
---

# 题目/知识点导入流水线：两套字段命名与 from-plan 三坑

把题目/知识点从文档导进库的流水线。两条入口脚本 + `packages/core/src/ingest/` 里的计划器/应用器。

## 文件地图

- `scripts/know-ingest.ts`：单文档入口，`--from-plan` 走「先出计划、审阅后再应用」。
- `scripts/group-ingest.ts`：多文件试卷组入口。**它不传 `paper` → 不能创建试卷**（见末尾待办）。
- `packages/core/src/ingest/unified.ts`：`planUnifiedIngest` 出计划、`applyUnifiedPlan` 落库。**必须同时把 `opts.chat` 和 `opts.cfg` 传给 `cutSheetWithLlm`**，漏传会静默退回正则。
- `packages/core/src/ingest/sheet-llm.ts`：`cutSheetWithLlm`——题目/答案的 LLM 切分与配对（锚点协议，见下文）。
- `packages/core/src/ingest/exercise-sheet.ts`：正则切分路径，现作对照与兜底；`bindAnswers` 按题号绑定。
- `packages/core/src/ingest/outline.ts`：`buildOutline`——**按编号算层级**，不数井号。
- `packages/core/src/ingest/apply.ts`：`applyQuestions`。
- `packages/core/src/ingest/paper-plan.ts`：`PaperPlanner`——决定一道题落在哪张卷、哪个 part。
- `packages/core/src/repositories/paper-repo.ts`：paper/paper_part 表访问。
- `packages/core/src/services/relink-service.ts`：`relinkQuestions`——给孤儿题按向量检索重建知识点关联。

## 两套字段命名（历史上是真 bug 的根源）

`BuiltQuestion` 用 `group` / `no`；`ExtractedQuestion` 用 `paper_part` / `question_no`。同一个概念两套名字，导致字段映射出错（见下）。

## `--from-plan` 路径修掉的三个真 bug

1. **`--from-plan --apply` 崩溃**：`sourceNameOf(args, doc!)` 解引用了 `null`（`doc` 在 `fromPlan` 分支是 null）。**dry-run 提前返回所以从没暴露**——崩的正是脚本自己推荐的使用路径。修法：签名放宽到 `ParsedDocument | null` + fallback 链（`--source` → plan 文件名 → 「未命名材料」）。
2. **`--from-plan` 下试卷没创建**：`sourceHash` 之前只在 `--token`/文档路径算，`--from-plan` 下是 `undefined` → `identityKey` 永远不转发 → `PaperPlanner.plan` 返回 null → 静默不建卷。修法：`--from-plan` 时把 plan JSON 也算进 `sha256`。
3. **`paper_part_id`/`paper_no` 静默为空**：只有「出计划」路径做了 `group→paper_part`、`no→question_no` 映射，`applyUnifiedPlan` 的 fall-through 分支**没做**。静默是因为 `placeInPaper` 故意把没匹配上的 part 降级成 `paper_part_id=''`（不报错）。修法：抽出共享的 `attachPaperFields()`，出计划和应用两条路都调。

> **这三个 bug 的共性**：都藏在「推荐使用路径」上，且都被某种降级/提前返回机制掩盖（dry-run 提前返回、undefined key 静默 miss、故意降级不报错）。**只在 dry-run 测过的功能等于没测 apply。**

## 变异测试证明映射真的生效

把 `attachPaperFields` 注掉 → `5-3`/`5-4` 断言变红（`[null,null]` / `["",""]`）；还原后绿。

## 待办

`scripts/group-ingest.ts` 仍不传 `paper` → 多文件试卷组路径**不能创建试卷**。这是 R61 卷功能的一个缺口，未修。

## 题目/答案配对：锚点协议（不要让模型输出正文或偏移量）

LLM 切题切答案走 `packages/core/src/ingest/sheet-llm.ts` 的 `cutSheetWithLlm`。协议演进过两版，第一版是错的，教训值得记住。

### 错误版：让模型输出字符区间

一开始让模型返回每道题的 `[start, end]`。结果：**数量对得上（90/90），区间全错**——第 2 题的题干从选项 D 中间开始（`"RP\nC. IP, ICMP, ARP, RARPD. UDP...`）。

原因很简单：**模型不会数字符**。让它报 offset 等于让它做精确计数，必错，而且错得毫无规律。

### 正确版：只让模型返还原样锚点字符串

模型只输出 `stem_anchor` / `answer_anchor`——**从原文里原样抄一段字符串**。程序用 `indexOf` 自己定位，**正文永远由程序从源文本切**。

```
模型：{ stem_anchor: "以下可能导致一个进程从运行态变为就绪态的事件是", answer_anchor: "43. D" }
程序：source.indexOf(anchor) → 切片 → 得到题干正文
```

模型擅长"挑一段文字"，不擅长"数位置"。**摘录比测量可靠**。

锚点找不到就丢弃并计数（`dropped`），不猜。丢弃量大说明该页 OCR 已损坏——模型会据语义补写一个原文里不存在的句子，那种文本**不能采信**。

### 两个定位函数的区别（都必须有）

- `locate(text, anchor, from, minLen)`：允许**前缀截断**（28/20/14/9/6/5/4/3），逐步缩短找最长的可定位前缀。用于题干——题干长，尾部差一点不影响。
- `exactLocate(text, anchor, from, minLen=3)`：**不截断**，只做空白不敏感匹配。用于答案——答案锚点就是 `43. D` 这种短串，一旦截断成 `43. ` 就会匹配上任何一道题，**错答案被静默掩盖**。

`exactLocate` 最初写死 `if (a.length < 3) return -1`，把 `9.` 这种两字符探针也拦掉了。加 `minLen` 参数解决。

### 题号只做显示，绝不做身份

答案配不上时用题号兜底（`ansRecoveredByNo`）：拿 `^\s*(\d{1,3})\s*[.．、。]` 去原文探。但**题号本身不能当题的标识**——书里的题号有 `01.` 补零和不补零两种写法，同一本书前后不一致。题号只用于显示和兜底定位。

### 校验兜底：数据不合理就退回正则

`answerCount > questions.length`，或答案文本非空但 `answerCount === 0`，直接返回 `null` 走正则路径。**LLM 路径宁可放弃也不能产出错配**。

### 一个真实的静默失败

`unified.ts` 调 `cutSheetWithLlm` 时只传了 `opts.cfg`，没传 `opts.chat`；而 CLI 从不设 `cfg`。结果**全部 7 个节静默退回正则**，日志上看不出任何异常，只是"效果不如预期"。修好后 5/7 走 LLM。

**判据**：想确认 LLM 路径真的生效，看结果里的 `sheets[].via` 字段是 `llm` 还是 `regex`，别靠"感觉快了"。

## 三条不可让步的设计原则

### 2. 答案缺失永远是流水线的错，不是材料的问题

这是用户的明确要求，也是正确的工程立场。看到「这题没答案」，**按这个顺序查**：

1. **该页转录产物是否残缺** —— 用 `assertPageCoverage` 跑一遍。p207 那种「成品率 7%、但 `finish=stop` + HTTP 200」的页会静默通过，看起来像「这页本来就没答案」
2. **答案节是否被上一节边界吞掉** —— 见 `knowledge/l0-l3` 的 `maxLevel` 陷阱。`2.1.10 答案与解析` 作为二级标题被保留、前面的三级小节被丢掉，于是它一路吞到下一个二级标题
3. **答案锚点是否因 OCR 损坏而 `dropped`** —— 锚点搜不到说明该段原始文字已坏，模型据语义补写的不能采信
4. **该页是否根本没被转录** —— 缓存缺页不等于「书里没有」，是任务没跑完

实测案例（两个，成因完全不同）：

- 操作系统 `2.2.9 答案与解析` 只有 16 字符。**根因是那几页转录缺页**，答案成了空壳，模型只好把上一节的 `43. D` 配过来。查证过程：`2.1.9` 有 75 题、`2.1.10` 里有 01~73 连续答案，而 2.1 第 43 题问「进程从运行态变为就绪态」、答案 `43. D` 正是「时间片到时」——语义吻合，说明配对没错，是 2.2 的答案没被转录进来。
- 全书扫描时 p108 / p207 / p239 三页**断在半句**（p207 断在「逻辑地址结构为」、p108 断在「如下图所示」、p239 断在选项 B 中间）。这是模型写完一半就 `finish=stop`，**不是截断**（`finish_reason` 不是 `length`）。

**判据**：`finish=stop` 不代表内容完整。只有拿产物和原文比覆盖率才能发现。

## 重跑会造重复：content_hash 挡不住跨批次

### 现象

同一章跑两遍 → 题目从 182 变 304。`content_hash` 去重**没生效**。

### 原因

`content_hash` 是**内容派生**的。同一次重跑里，如果切分方式变了（正则 87 题 vs LLM 88 题），同一道题切出来的正文会有细微差异（多一个句号、少一个空格），`content_hash` 就不同 → 判定为"新题"。

**所以 `content_hash` 能挡"完全相同的文本重复导入"，挡不住"同一份材料用不同流水线跑两遍"。**

### 处理顺序（顺序错了会留下孤儿）

1. **先删旧批次**：`DELETE FROM questions WHERE ...` 只删目标批次的行
2. **再删它们的关联**：`question_knowledge` 里指向这些题的行（222 行）
3. **然后**才发现：删旧题把**新题的关联**也带走了——因为新题原本关联的是旧知识点节点，删旧批次时那批节点一起没了

第 3 步是实际踩到的：删完之后 124 道 LLM 题成了孤儿题（有题无知识点关联）。

### 修法是 relink 而不是重新入库

`packages/core/src/services/relink-service.ts` 的 `relinkQuestions({ db, chat, questionIds, scopeId, apply })`：拿每道题的内容去**向量检索**匹配知识点，再建 `question_knowledge` 边。

实测结果：`targets:124 linked:96 no_candidate:28 links:39`。

- `linked: 96` —— 96 道题找回关联
- `no_candidate: 28` —— 28 道找不到合适候选（不是失败，是这批知识点里确实没有对应内容）
- `links: 39` —— 实际建的边数（一题可关联多个知识点）

**先想 relink，再想重新入库**。重新入库会再造一批重复题，还要再删一遍。

### 入库后的三条自检

跑完必须查这三项，缺一项就说明流水线有问题：

1. **重复数 = 0**：按 `content_hash` 分组 `count > 1`
2. **孤儿数 = 0**：`questions` 里没有 `question_knowledge` 行的题
3. **缺答案数**：有题干但 `answer` 为空的题——**这个数不为 0 就是流水线的错**（见上文设计原则 2）
