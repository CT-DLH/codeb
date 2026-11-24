---
covers:
  - src/core/ingest.ts
  - src/core/pdf.ts
  - src/core/parsers/
updated: 2026-11-17
---

# Input formats and type coercion

六种格式共用 `ParsedFile`（`src/core/ingest.ts:79-87`）出口，但解析器在细节上分歧很大。`row_numbers` 的语义是**文件里的展示行号**，不是数组下标——resume、`row_overrides`、`provenance`、`sources[].row` 全部按它对齐。

## detectFormat: extension table

`detectFormat`（89-99）只认扩展名，不嗅探内容：

```text
.xlsx → xlsx    .xls → xls     .csv → csv
.tsv / .tab → tsv    .jsonl / .ndjson → jsonl
.md / .markdown → md    .pdf → pdf
```

不认的一律 `null`，由 `parseTableFile`（440-454）抛出带引导的错：`不支持的文件类型: .docx（支持 xlsx/... ；截图、邮件正文请先由 AI 拆解成 jsonl）`。`.xls` 走 `parseXlsx` 同一分支（SheetJS 自己识别 BIFF）。

## row_numbers: four different conventions

| 格式 | 语义 | 公式 |
| :-- | :-- | :-- |
| xlsx/xls | 表头算第 1 行，数据从 2 起 | `headerIndex + offset + 2`（`matrixToRows:172`） |
| csv/tsv | 同上，且**已被 `splitDelimited` 丢掉空行** | 同上 |
| md | Markdown 文件里的**物理行号** | `lineNumbers.slice(1)`（260） |
| jsonl | **物理行号**（1 起），空行不占号 | `i + 1`（233） |
| pdf | 拍平全部非空行后的**序号** | `i + 1`（433） |

两条容易踩的后果：

- csv/tsv 的行号是**在丢掉全空行之后**重算的，与文本编辑器里的行号可能差几行。
- pdf 的「行号」是跨页拍平后的计数，**不含页边界信息**，没法反查是第几页。

`headerRow` 参数（`header_row` 选项，默认 1）只对 xlsx/csv/tsv/pdf 生效；jsonl 与 md **忽略它**——jsonl 无表头概念，md 自己跳过 `|---|` 分隔行。

## Empty-column dropping happens before headering

`matrixToRows`（149-175）先算 `width = max(row.length)`，再保留「至少一行非空」的列：

```text
keep = [0..width) 里 matrix.some(row => !isBlankValue(row[i])) 的下标
```

注释点明动机：名单常带整列为空的格式列（xls 的 `!ref` 撑到 J/K），不丢就会在报告里冒出「列5/列6」噪声。

**关键顺序**：先丢列，**再** `headerize(keep.map(i => matrix[headerIndex][i]))`。所以 `headerize` 看到的列数已经是压缩后的，重名列的 `#2` 后缀也按压缩后的原始名生成。

`isBlankValue` 用的是 `normalize.ts` 的统一口径：`null`/`undefined`/`''`/`[]`/`{}` 全算空。这也意味着**某列只有 0 或 false** 不算空（数字与布尔不是 blank），不会误删。

## headerize: duplicate columns get #2, #3

`headerize`（139-147）：

- 空表头 → `列${i+1}`（**注意 `i` 是压缩后的下标**，即 `列1` 是按可见顺序重新编号的）。
- 重复名第 n 次出现（n ≥ 1）→ `${raw}#${n+1}`。第一次保持原名，第二次是 `name#2`，第三次 `name#3`。

`parseMarkdownTable`（239-261）与 `pdfTableFromPages`（398）直接复用 `headerize`，所以三种格式的重名规则一致。

## csv/tsv: hand-written splitter, not a library

`splitDelimited`（101-137）是逐字符状态机，不是引号库：

- `"` 进入引用态；引用态里遇 `""` 输出一个 `"` 并跳过下一字符；单独的 `"` 退出引用态。
- 引用态里**所有字符原样保留**，包括 `\n` 与分隔符。
- 非引用态：`\n` 收行，`\r` **丢弃**（`else if (ch !== '\r') field += ch`，130），其他字符直接进 field。
- 收行时 `if (row.some(cell => cell.trim() !== ''))` — **全空行丢弃**。
- 文件尾若 `field !== '' || row.length > 0` 也收一次。

`readFileSync(filePath,'utf-8').replace(/^﻿/,'')` 先剥 BOM（206）。csv 的分隔符是 `,`，tsv 是 `\t`。

已知将就：没有转义多行之外的容错——某行引号不闭合会让后面所有内容并进同一个字段，且**不报错**。

## jsonl: passthrough mode, no column_map needed

`parseJsonl`（214-237）逐行 `JSON.parse`，错误信息带行号（`第 ${i+1} 行不是合法 JSON`）。非对象或数组直接抛。`columns` 是**所有行 key 的并集**（`Set`，插入序）。全空行跳过，不占 `row_numbers`。

特殊之处在 `importTable:1542`：

```text
passthrough = parsed.format === 'jsonl' && !options.column_map
```

此时 `mapRow` 的 `raw = options.passthrough ? column : (columnMap[column] ?? '')`（580）——**列名直接当字段路径用**。所以 jsonl 不写 `column_map` 也能导，前提是 key 就是 `ext.student_id` 这种路径。一旦传了 `column_map`，就退回普通映射，未映射的列进 `unmapped_columns`。

## md: pipe table, separator rows skipped

`parseMarkdownTable`（239-261）只认以 `|` 开头的行，去掉首尾 `|` 后 `split('|')` 并逐格 `trim()`。分隔行判据是**每一格**都匹配 `/^:?-{2,}:?$/`（至少两个短横，允许两侧冒号），整行跳过。少于 2 行（表头+数据）抛错。

已知将就：单元格里不能有 `|`，没有转义处理；也没有多行单元格。

## pdf: -table, per-page cluster-then-align

链路是 `parsePdfTable` → `pdfPages(file,'table')` → `pdftotext -enc UTF-8 -table <file> -`（`src/core/pdf.ts:11-21`），按 `\f` 分页。

**为什么不用 `-layout`**（356-367 注释）：`-layout` 按视觉间距拼行，把一条记录拆成「密集行 + 稀疏行」交替出现，稀疏行丢一半字段——实测 607 条记录变 1194 行。`-table` 按列补空格，一行一条记录，且列内数值自洽（智育分最高的人智育排名就是 1）。

**为什么用字符串下标而不是显示宽度**：`-table` 按**字符数**补空格，一个中文字也只占一格。`tokenizeLine`（269-275）用 `/\S+/g` 取 token 并记 `match.index` 作为 `start`。

每条注释都对应一条实测：

1. 同一份 PDF **每页的补空格基准不同**（同一列首页 45、后续页 36、尾页再差 1）→ 必须逐页定列。
2. 表头只在第一页出现，且表头起点与数据起点差几格 → 列名靠**单调对齐**而非相等匹配。

### Header detection when header_row is absent

`pdfTableFromPages`（373-438）里 `headerIndex = headerRow > 1 ? headerRow - 1 : -1`。`headerRow === 1`（默认）时不预设，改为在**前 12 个非空行**里取 token 数最多的一行（389-395）；`bestCount < 2` 则抛错 `没能在前 12 行里找到表头（至少两列），可用 header_row 指定`。空文本抛 `PDF 里没有可读文本（扫描件？需要先 OCR）`。

### Per-page column fixing: mergeClusters → alignClusters → nearestIndex

每页三步（402-435）：

**① 挑出「参与定列」的行**（405-410）：`tokens.length >= 2` 且**不是页码行**且**不是表头重复行**。页码行正则 `PAGE_NUMBER_LINE = /^[-–—\s]*\d{1,4}[-–—\s]*$/`（354）；表头重复行判据是把 token 用 `|` 拼起来与 `headerJoined` 全等。标题行（「2024-2025 年度…公示」）靠「token 数 ≥ 2」自然出局。

**② `mergeClusters(positions, wanted)`（281-296）**：把本页实测起点去重排序，若数量多于表头列数，**反复合并间距最小的一对**（`out.splice(best, 2, out[best])` 保留左边界），直到数量 ≤ `wanted`。用途：一个单元格内含空格被拆成两个 token 时，把它们并回一列。并完仍按左边界归属，后面的 `nearestIndex` 会把右侧 token 落回同一列。

**③ `alignClusters(clusters, headerStarts)`（305-339）**：把本页实际起点**单调对齐**到表头列。这是一个 DP：

- `k = clusters.length`、`n = headerStarts.length`。
- `k === 0` → `[]`；`k >= n` → 直接顺序一一对应（`Math.min(i, n-1)`，末列挤压）。
- 否则建 `(k+1) × (n+1)` 的 `dp`/`prev`，`dp[0].fill(0)`，`dp[i][j] = min_p(dp[i-1][p] + |clusters[i-1] - headerStarts[j-1]|)`，`p` 从 `i-1` 到 `j-1`（**单调约束**：列只能从左到右，允许某些列在本页整列没有值）。
- 终点取 `dp[k][j]` 最小者（`j` 从 `n` 递减到 `k`，`<=` 比较故**取最小的 j**，倾向左侧对齐）。
- 回溯出 assignment；长度不等于 `k` 则退回顺序映射兜底。

**为什么不能按「起点相等」直接匹配**：表头是中文（占格不同），且每页基准会变。起点数恰好等于列数时，单调约束自然退化成按顺序一一对应；少于列数时取差值最小的对齐，**尾列整列为空也能对上**。

**④ 归位**：每个 token 用 `nearestIndex(clusters, token.start)`（341-352，`<` 比较故**并列取左**）找到 cluster 下标，再 `columnOf[cluster]` 得到列；同一列内多个 token 用空格 join（`cells[col] = cells[col] ? `${cells[col]} ${token.text}` : token.text`）。整行全空则丢弃。

## coerceValue: the full restoration ruleset

`coerceValue`（510-561）先 `fieldSpecFor(spec, path)` 取字段声明；**取不到声明**就只做 `typeof string ? trim() : 原值`——未声明字段不做任何类型还原。`fieldSpecFor`（494-503）支持 `ext.` 前缀与嵌套（`node.fields[key] ?? node.item.fields[key]`，array item 也能下钻）。

**string**：字符串 `trim()`；数字/布尔转 `String(value)`；其他原样。

**number**：

```text
Number( toHalfWidth(asText(value)).replace(/[,\s%]/g, '') )
```

即先全角转半角、再去逗号/所有空白/百分号。**保留负号与小数点**，不处理「万」「元」。`Number.isFinite(num)` 为真返回数字，否则**返回原始字符串**（不是 null）——让 schema 校验去报 `invalid_field`，而不是静默丢值。

**boolean**：`toHalfWidth(asText(value)).toLowerCase()` 后查表：

```text
TRUE_WORDS  = {'true','yes','y','是','有','1'}
FALSE_WORDS = {'false','no','n','否','无','0'}
```

两个词表都不命中则**返回原值**（同样交给 schema 报错）。

**array**：

1. 已是数组 → 原样返回。
2. `asText(value)` 为空 → `null`。
3. 以 `[` 开头 → 试 `JSON.parse`，成功且是数组则用，失败**吞掉异常**继续走分隔符。
4. `field.split === false` → `[text.trim()].filter(Boolean)`，**整值为一项**。这是「中国茶、酒文化与健康」不被顿号拆成两门课的开关。
5. 否则 `text.split(ARRAY_SPLIT)` → 每项 `trim()` → `filter(Boolean)`。

`ARRAY_SPLIT = /[,，;；、\n]+/`（505）：半角逗号、全角逗号、半角分号、全角分号、顿号、换行。**不含空格**、不含竖线、不含斜杠。

**object**：仅当值是字符串且以 `{` 开头时试 `JSON.parse`，失败返回原字符串（不再 trim 后的继续处理）。非字符串的 object 直接返回原值。

**null/undefined**：直接返回 `null`（第一行短路）。

## Where coercion is applied, and where it is not

`coerceValue` 在四处被调用，口径必须一致：

- `mapRow:629`（列值 → 字段）
- `importTable:1595`（`defaults`）
- `importTable:1604`（`row_overrides`）
- `withDerives:2051`（派生值，通过 `applyDerives` 的 `coerce` 注入）

**不经 `coerceValue` 的**：`mapRow` 里的 `_body`（原样或 `JSON.stringify(value, null, 2)`）、`_review`（`asText`）、`_src`（手工拼 `SourceRef`）、`_clear`/`_replace_sections`/`_overwrite_fields`（按 `[,，;；\s]+` 或 `[,，;；]+` 拆成路径列表，**注意 `_clear` 用的是更宽的分隔符集，含空格**）。

`_clear` 的分隔符是 `/[,，;；\s]+/`，而 `_replace_sections`/`_overwrite_fields` 是 `/[,，;；]+/`。差别在空格：字段路径不含空格，但小节名**可能含空格**，所以后者不敢按空格拆。
