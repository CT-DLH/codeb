---
covers:
  - src/core/attach.ts
  - src/core/parsers/
updated: 2026-11-17
---

# Attachments: matching files onto existing cards

`attachDirectory()`（`src/core/attach.ts:110-340`）处理「一份文件挂一张卡」的补充正文，与 `card_import` 的分工是**实体清单 vs 附件**：附件**永远不新建卡**。挂不上说明主表缺行，新建只会造出孤儿卡（文件头注释）。

## Pipeline and the six outcome statuses

```text
walk(source_dir)  → SUPPORTED_EXT 过滤 → parseAttachment → matchIdentity
  → 单命中：读卡 → alreadyAttached 判重 → 算 appended/kept → 进 plans
  → 多命中：ambiguous（onAmbiguous=review 才进 quarantine）
  → 零命中：missing（onMissing=quarantine 才进 quarantine）
  → 解析抛错：parse_error    → 扩展名不支持：unsupported
```

`AttachStatus`（34）：`match | ambiguous | missing | duplicate | parse_error | unsupported`。报告里六个计数一一对应（`scanned/parsed/matched/ambiguous/missing/duplicate/parse_error/unsupported`，48-61）。

`walk`（73-80）递归整棵目录，不排序——**文件处理顺序取决于 `readdirSync` 的返回序**，同题多卡的 `candidates[0]` 也吃这个序。

## declared_index never participates in matching

`declaredIndexOf`（83-87）取相对路径的第一段目录名（如 `15至19`）。它只进报告供人工核对，**不参与匹配**。注释写明：目录编号只是压缩包顺序号。

## match_by resolution: three-level fallback

`matchBy`（121-125）优先级：`options.match_by` → `cfg.matchBy`（领域包 `attachments.match_by`）→ `spec.identity?.weak`。三者都空直接抛错。

`on_missing`：`options.on_missing` → `cfg.onMissing` → `'quarantine'`。`on_ambiguous`：`options.on_ambiguous` → `cfg.onAmbiguous` → `'review'`。`max_updates` 默认 **20**（130），与 `card_import` 同值。

`cfg.enabled === false` 时**直接抛错**，不是静默跳过（119）。没有 `attachments` 声明时只加一条 hint 并按内置默认执行（118）。

`extFields` 的 label 反查告警（132-136）：`match_by` 里既不是 `title` 也不是合法 `ext.*` 路径的，加 hint「附件提供不了这个字段」——不阻断。

## fieldsFromAttachment: only title and meta

`fieldsFromAttachment`（94-103）只产出两类字段：

- `title` = 解析器自报的题目；
- `ext.*` = 通过 `labelToPath` 把 `ParsedAttachment.meta` 的 **label** 反查成 `spec.extFields` 的路径（`fields[path].label ?? path` → `ext.${path}`）。

所以附件能参与 identity 匹配的只有「题目 + 表头 meta（姓名/学号）」。卡片已有的 `aliases` **不参与**匹配——措辞变体只能靠补主表题面回收（hint 310）。

## Why match_by is rebuilt into an identity config with no strong

138-139 行：

```text
identityCfg = { strong: [], weak: matchBy, disambiguator: [] }
```

把 `match_by` 整体塞进 `weak`，于是复用 `matchIdentity` 的弱标识分支——**要求 matchBy 每一项都齐全且整体相等**，且多命中返回全部候选。这样附件匹配与主表匹配用同一套归一化（`identityKey`），不引入相似度阈值。

代价：`match_by` 里任何一项缺失，该附件直接 `missing`（`matchIdentity` 的 `every(non-blank)` 门禁）。目录编号之所以被明确排除在匹配外，也是因为它是压缩包噪声。

## Why existing sections are kept

这是附件的核心语义（文件头第 10 条注释）：**正文可能是手工改过的，附件只是原始模板，覆盖会丢掉人工修订**。

落地在 232-236：

```text
for (const s of att.sections) {
  heading = sectionMap[s.name] ?? s.name
  if (hasHeading(body, heading)) kept.push(s.name)
  else appended.push(s.name)
}
```

`hasHeading`（89-91）与 `sections.sectionRange` **同口径**：`line.trim() === '## ' + heading`，精确全等。所以 `### X` 或 `## X 补充` 不算已有。

- `sections`（`AttachDetail.sections`）= 解析器给出的**全部**小节名（原始名，不是映射后）。
- `kept_sections` = 因正文已有同名小节而**被保留**的（原始名）。
- `appended`（不进 `AttachDetail`，只进 `sources`）= 实际追加的（**映射后**的名字，284 行 `plan.appended.map(n => sectionMap[n] ?? n)`）。

同一个名字在不同字段里出现时，`sections`/`kept_sections` 是原始名、`sources.sections`/`sources.kept_sections` 是映射后名。改报告口径时要留意这个不一致。

`sections` 与 `kept_sections` 的差集就是实际写入的东西，但报告只给了 `kept_sections`——要看追加了哪些得算差集或看 `sources`。

## Write phase: append once, then source line

`if (!dryRun && !aborted)`（266-294）按 `plans`（`Map<卡文件, 计划[]>`）逐卡写：

```text
for (const s of plan.parsed.sections)
  if (!hasHeading(body, heading)) body = appendToSection(body, heading, s.content)
body = appendToSection(body, '来源', `- 附件 ${plan.file}`)
sources.push({kind:'attachment', file, parser, title, sections, kept_sections, attached_at})
```

`hasHeading` 在写循环里**再查一次**（276）——因为前一个 plan 可能刚追加了同名小节。这是「一张卡挂多份附件」时的去重。

`appendToSection(body,'来源', ...)` 每份附件都调一次，所以「来源」小节里会累积 `- 附件 a.docx`、`- 附件 b.pdf`。这一行**没有判重**，但 `alreadyAttached` 在更早拦住了同一文件的重复挂载。

`attached_at` 是 `new Date().toISOString().slice(0,10)`——**日期而非时间戳**，同一天重跑看不出来。

## Idempotency: alreadyAttached by kind + file

`alreadyAttached`（105-108）判据：`sources` 里存在 `s.kind === 'attachment' && asText(s.file) === sourceFile`。命中直接 `duplicate++` 并跳过，**不重复追加正文也不重复记 sources**。

`sourceFile` 是 `relative(process.cwd(), file).replace(/\\/g,'/')`（154）——**相对 cwd 的路径，正斜杠归一化**。所以：换 cwd 跑同一批附件，`alreadyAttached` 会全部失效并重复挂载；不同目录下的同名文件不会互相干扰。

这是最容易踩的幂等陷阱，注释只在 `duplicate` 的 warning 里写「重复跑不会重复追加」，没写「前提是 cwd 不变」。

## Safety valve: cards, not files

`aborted = !dryRun && cardsToWrite > maxUpdates`（259），`cardsToWrite = plans.size`（卡文件数）。与 `card_import` 的 `would_update` 口径一致但**计数对象不同**：这里数的是**目标卡片数**，不是行数。20 份附件挂到 3 张卡不会中止。

中止时 `aborted` 带文案、`dry_run: true`（320 `dryRun || aborted`）、**一份都不写**。报告仍是预演口径——`attached` 保持 0，`hints` 首条是中止说明。

`dry_run` 默认 **true**（129 `options.dry_run !== false`）。

## Quarantine file path differs by mode

296-301 行：`inbox/attachments-quarantine.preview.jsonl`（预演）vs `inbox/attachments-quarantine.jsonl`（实盘）。**相对路径，不带仓库根**——与 `card_import` 的 `.quarantine/<domain>/<stamp>.jsonl`（绝对路径 + 时间戳）不一致，预演与实盘也**不同名**，所以预演产物不会被实盘覆盖。

内容是一行一个 JSON：`missing` 写 `{file, declared_index, title, sections, reason}`，`ambiguous` 写 `{file, declared_index, title, candidates, reason:'ambiguous'}`。每次写都是 `writeFileSync` **整文件覆盖**，不是追加。

## Report truncation

`DETAIL_LIMIT = 40`（71）。`details.slice(0, 40)` + `details_truncated: boolean`（335-336）。与 `card_import` 的 `MAX_ANOMALIES = 50` + 计数（而非布尔）不同——这里是布尔，所以「截断了多少」看不到。

## Hints are the operational instructions

`hints`（117、303-317）是可执行建议，按严重度排序，`unshift` 的排最前：

- 领域无 `attachments` 声明 / `match_by` 路径不合法；
- 中止说明；
- `unsupported > 0` → 列出支持的扩展名（**不静默跳过**是解析器注册表的明确纪律）；
- `missing > 0` → 「主表缺行就先补主表，card_attach 不会替它新建卡」+「匹配只比对 title，aliases 不参与」；
- `ambiguous > 0` → 「需要人工指定 card_id 后再单独挂」；
- 最终：`没有需要写入的卡片` / `会改 N 张卡（预演，未落盘）` / `已改 N 张卡、挂上 M 份附件：<前 8 个>`。

## Parsers: the shared contract

`ParsedAttachment`（`parsers/types.ts:12-21`）：`{title?, meta?, sections[], source_file, parser, warnings?}`。`title` 取不到留 `undefined`，由调用方决定隔离——**解析器不做任何判断**（文件头注释）。

`AttachmentParser`（23-29）：`id`、`extensions?`（缺省不限）、`parse(file, sourceFile)`，**返回 null = 不归我解析**，交给下一个候选。

注册表 `PARSERS = [taskBook, courseSyllabus, pdfText, genericDocx]`（`index.ts:16`），**顺序即优先级**：先模板、后通用兜底。`SUPPORTED_EXT = ['.docx', '.pdf']`（17）。`parseAttachment`（30-48）先按扩展名筛，再按 `options.parser` 精确筛，然后**逐个试到第一个非 null**；全试完仍 null 抛 `结构无法识别：<file>（换 parser 或人工处理）`。指定了不存在的 parser 会抛错并列出该扩展名可用解析器。

`.doc` 不在这层处理：先用 `scripts/word-to-docx.ps1`（Word COM）转成 docx——**本层不碰二进制**（index.ts 注释）。

### docx.ts: regex XML, no docx library

`readDocxText`（43-64）用 `adm-zip` 读 `word/document.xml`，正则拆 `<w:tbl>/<w:tr>/<w:tc>/<w:p>/<w:t>`。产出三样：

- `tables`：每张表 → 行 → 单元格文本（**按「张」保留边界**，因为课程大纲一张表对应一个栏目，拍平后数据行认不出自己属哪张表）；
- `rows = tables.flat()`（任务书只认「第一张表」的形态，保留旧口径）；
- `paragraphs`：先把 `<w:tbl>` 整块**剪掉**再取 `<w:p>`，否则表头（毕业要求/教学内容）会混进章节正文。

`collectText`（22-41）：一个片段内按 `<w:p>` 分组，组内拼全部 `<w:t>`；**组内无 `<w:p>` 时**兜底直接拼 `<w:t>`。最后 `unescapeXml`（`&lt;/&gt;/&amp;/&quot;/&apos;` 五种）。同一单元格多段落用 `\n` 连接。

`stripSpace`（67-69）只删空白，用来做「题目对账」。

不引 docx 库的理由：任务书是固定模板，只需要「表格单元格文本」和「段落文本」两件事，正则版本已在 54 份真实任务书上跑通。

### task-book.ts: two templates, table first

`rows.length >= 2` 才试 `fromTable`（113）——注释说明门槛故意低：行数门槛会把模板精简过的任务书挡在外面。

`fromTable`（29-74）：

- 找题目行：`bare(cell0)` 去空白去冒号后**恰好在 `TITLE_KEYS`** 里，且第二格非空。`TITLE_KEYS = ['题目','设计（论文）题目','设计(论文)题目','毕业设计（论文）题目','综合设计（论文）题目']`——半角/全角括号各列一条，漏一条就认不出。
- meta：只取题目行**之前**的行，每行按**两格一组**（`i += 2`）配对 `label/value`，要求 `label.length <= 12` 且 value 非空。空栏（姓名没填）不进 meta。
- sections：题目行之后逐行，`cell0` 为空或含 `SKIP_LABELS`（`签字`/`意见`/`领导小组`）则跳过。用 `/^([^:：\n]{2,20})[:：]\s*/` 拆「标签：正文」，无冒号则整格当名字、正文取第二格。
- 空内容进 `blank`；名字形如 `（1）xxx` 进 `markers`——注释解释：这是条目编号不是栏目名（该文件整组缺了「主要内容」栏），**按原文保留 + 加警告**，不硬扯到上一栏、不改名叫「主要内容」。

`fromParagraphs`（77-96）：`TITLE_KEYS` 里某个 key 单独成行，下一行是题目；之后按 `PARA_HEADINGS` 六项匹配章节名（`bare(p).startsWith(bare(h))`），标题行内冒号后的剩余部分作为首段内容。

`buildWarnings`（99-105）三条：没识别出章节 / `blank` 非空 / `markers` 非空。

### course-syllabus.ts: alias table, longest-first

`LABELS`（16-30）13 组标签、每组一个 `key` 与 `aliases` 数组。构建时 `ALIAS_TO_KEY` 按**小写别名**建映射，`ALL_ALIASES` 按**长度倒序**排序（37）——注释解释：否则「学分」会抢先吃掉「总学分」。

`LABEL_RE`（40-43）动态拼：

```text
(别名1|别名2|…)\s*(?:[A-Za-z][A-Za-z ()()\/&.]*)?\s*[:：]\s*
```

中间那段可选组吃掉 `课程编码Course Code：` 这类中英混排的英文部分（以字母开头、允许字母/空格/括号/斜杠/&/点）。`gi` 标志，`readLabels` 每次先 `lastIndex = 0`。

`readLabels`（61-84）：一行可含多个标签（`课程学时：32 讲课学时：24 实验学时：8`），每段值取「本匹配结束 → 下一匹配开始」。处理后：

- `clean`（49-53）去 `\u00a0`、去首尾冒号逗号句号分号。
- `NUMBER_FIELDS = ['总学时','讲课学时','实验学时','上机学时','学分']` 走 `squeezeNumber`（`/\d+(?:\.\d+)?/` 取第一个数字，取不到返回 `''`）。
- **含 `周天月` 的数值字段跳过**（74-77）：实践课按周排课（`总学时：4周`），4 周不是 4 学时；`总学时` 这种情况把原文存进 `'周数'`。
- `审核人` **不写入**（80）——它只用来截断上一个标签的值（`撰写人：张三 审核人：李四`）。
- `if (value && !into[key])` — **先到先得，不覆盖**。

`buildSections`（117-177）：

- `NUM_HEADING = /^[一二三四五六七八九十]{1,2}\s*[、.．]\s*(.{1,30})$/`（一、二、… 最多 30 字）。
- `BARE_HEADING`（47）是 20 个固定词的枚举（课程简介/课程目标/教学安排/考核方式/教材/课程思政…），末尾可选冒号，`i` 标志。
- 标题行先剥排版说明：`/[（(][^）)]*(黑体|字号|行距|加粗|字体)[^）)]*[）)]/g`（137）。
- `课程基本信息|基本信息` 与 `对应关系|支撑关系` 命中时 `current = null` **且不建节**——前者值已进 meta，后者只是表格标题。
- 同名小节**续写同一节**（150-151），避免正文堆一串同名小节。
- 章节内的标签行（`学分：2`）`if (readLabels(line, metaOnly)) continue`——**不进正文**。
- 表格：一张表 = 一个栏目，`tableSectionName`（97-102）按表头关键词分三类：`考核|成绩` → 考核方式；`教学内容|教学安排|课程内容` → 课程内容；其余 → **支撑关系**。同一栏目名的多张表，若已有同表头（`row.join('|')` 全等）就丢掉重复表头再拼（168-170）。
- `tableToMarkdown`（87-95）：按最宽行补空列，`---` 分隔行，单元格内 `\n` 换成空格。

`parseCourseText`（179-223）：

- **两遍扫标签**：先扫 `paragraphs`，再扫 `tables.flat()` 的每个单元格（190-195）——因为信息常在表格里。
- 标题优先级：`meta['课程名称']` → `titleFromParagraph(首段)` → `options.fileTitle` → `titleFromParagraph(首行表格 join)`。每级都 `.replace(/^《|》$/g,'').trim()`。
- **`if (!title && labelHits === 0) return null`**（208）——这是「不归我解析」的唯一出口。只要有一个标签命中，哪怕没标题也认。
- 警告两条：没有章节；没有 `课程代码`（「只能用文件名兜底」——但代码兜底其实没实现，`codeFromFileName`（226-229）是导出的独立函数，`parseCourseText` 不调用它）。

`titleFromParagraph`（105-115）：先试 `《([^》]{2,40})》`，再去掉尾部 `(课程)?(中英文)?(教学大纲|课程大纲|课程简介|简介|大纲)`，长度 2-40 才返回，否则空串。

`titleFromFileName`（231-236）只认书名号，**不认裸文件名**——文件名是 `2023-数据结构-教学大纲.docx` 时返回空串，该级兜底失效。

### pdf-text.ts: reuse the course parser

`pdfTextParser`（13-23）调 `parseCourseText(pdfParagraphs(file), [], ...)`：**表格参数传空数组**，所以 PDF 永远没有表格小节（`pdfParagraphs` 已经 `trim()` 掉了缩进，列位置信息全丢）。`fileTitle` 走 `titleFromFileName`，同样只认书名号。

PDF 走的不是 `-table` 而是默认 `-layout`（`pdfParagraphs` → `pdfLines` → `pdfText(file,'layout')`）。**表格导入用 `-table`，附件用 `-layout`**——同一条 `pdftotext` 出口，两个模式，别混。

### generic-docx.ts: last resort, no invention

`isHeading`（11-16）四条全满足才算小标题：`0 < length <= 24`、不含 `\n`、**不以句读结尾**（`/[，。；、,.;:：!?！？)）】」”]$/`）、非空。注意它以 `：` 结尾也判为「正文」——冒号结尾的行不进标题。

`parse`（26-51）：标题行开新节（名字走 `stripSpace`），普通段落并进当前节；**当前没有节**时并进名为 `正文` 的节（38-41，且判 `sections[0].name !== '正文'` 防重复建）。最后 `sections.filter(s => s.content)` 丢掉空节。

标题兜底（43）：首段 `length <= 40` 就用它 `stripSpace`，否则用**文件名去扩展名**，并带 warning「没有可当标题的首段，用文件名兜底」。注释：「不补内容、不改写，原文没有的层级就不编出来」。

`basename`（18-21）是**自己实现的一份**，没有用 `node:path`——与 `attach.ts` 的 `relative` 口径独立，改路径归一化时两处都要看。
