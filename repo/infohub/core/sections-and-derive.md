---
covers:
  - src/core/sections.ts
  - src/core/derive.ts
  - src/core/normalize.ts
updated: 2026-11-17
---

# Body sections and derived fields

`src/core/sections.ts` 只做 H2 小节的读改写，`src/core/derive.ts` 只做正则取值。两者共用的前提是 `normalize.ts` 的路径读写与归一化——`readPath`/`writePath` 走点分路径，中间节点自动建对象，遇到数组会覆盖成 `{}`。

## sectionRange: H2 exact match, H1 or H2 ends it

`sectionRange(lines, section)`（13-25）是全部小节操作的地基，两条判据都很硬：

- **起点**：`lines.findIndex(line => line.trim() === heading)`，`heading = '## ' + section`。**精确全等**——`## AI 摘要 ` 后的行尾空格能过（`trim()`），但 `### AI 摘要`、`## AI 摘要 补充`、`##  AI 摘要`（两个空格）**都匹配不上**。
- **终点**：从 `start + 1` 向后找第一个匹配 `/^#{1,2}\s+/` 的行。**H1 和 H2 都会截断**，H3 及以下不会。

第 2 条常被误解为「H2 截断」：一个 `# 附录` 会把前面所有小节截断在它之前。所以卡片正文里混进 H1 会让后面所有 `appendToSection` 都追加到 H1 之前——生成顺序看起来「反了」。

找不到起点返回 `null`，`end` 默认 `lines.length`（末尾无标题时延到文末）。

## appendToSection appends at the end of that section

`appendToSection(body, section, text)`（27-39）：

- **无该小节**：`tail = body.trimEnd()`，返回 `${tail}${tail ? '\n\n' : ''}## <section>\n\n<text>\n`。空正文时不会留下开头空行。
- **有该小节**：切 `before = lines.slice(0, end)`、`after = lines.slice(end)`，把 before 拼回去 `replace(/\s+$/,'')`，再 `\n\n<text>\n`，然后 `after.length > 0 ? '\n' + after.join('\n') : ''`。

所以文本永远落在**该小节末尾、下一个标题之前**，且前后各留一个空行。若 `text` 自带尾部换行会被保留（`${text}\n`），可能产生双空行——`appendToSection` 不清理正文内部的空白。

**幂等性**：`appendToSection` **本身不幂等**——同一段 text 追加两次就得两份。幂等靠调用方：

- `importTable` 用 `body_repeat` 标记（`sources` 里已有同 file+row 就不追加，1891-1899）；
- `attach.ts` 用 `alreadyAttached` + `hasHeading` 双重拦截（见 attachments 页）。

## replaceSection overwrites or falls back to append

`replaceSection(body, section, text)`（54-63）：

- 没该小节 → **退回 `appendToSection`**（不是报错，也不是新建空节）。
- 有该小节 → `head = lines.slice(0, start + 1)`（**含标题行**）`replace(/\s+$/,'')`，`tail = lines.slice(end).join('\n').replace(/^\s+/,'')`，正文替换为 `text.trim()`，结果 `${head}\n\n${text}\n\n${tail}`；无 tail 则 `${block}\n`。

保留标题行原样（不改写 `## X`），只换内容。`tail` 的前导空白被吃掉，所以不会因为原节尾有空行而堆叠。

## extractSection returns undefined, not empty string

`extractSection(body, section)`（42-48）返回 `lines.slice(start+1, end).join('\n').trim()`；**没有该小节时返回 `undefined`**。这个区分是 `applySectionUpdates` 全部分支的依据：

- `undefined` = 上游这份材料没给这一节 → **保持旧值不动**；
- `''` = 上游给了这一节但内容为空 → 会 `replaceSection` 成空节。

`applySectionUpdates`（`ingest.ts:1174-1189`）的另两条判据：`text === extractSection(body, section)` 时跳过（内容相同则幂等）；`current.trim()` 为空时**整段直接返回 incoming**（空正文没有「保留」可言）。

## The _lead pseudo-section

`_lead` 不是 H2 小节，是正文开头那段 `> 一句话结论：…` 引用块。`applySectionUpdates` 里单独分支（1178-1181）：

```text
lead = extractLead(incoming)
if (lead && lead !== extractLead(body)) body = replaceLead(body, lead)
```

**上游没有 lead 时保持旧值**（`lead` 为空串不动作）；`_lead` 走 `replaceLead` 而非 `appendToSection`，因为引用块没有标题行可供 `sectionRange` 定位。

### extractLead: consecutive '>' lines, blank lines allowed inside

`extractLead`（66-79）：`body.trimStart()` 后若首行不以 `>` 开头 → `undefined`。否则从第 0 行起扫：

- 以 `>` 开头 → `end = i + 1`，`continue`；
- 空行 → `continue`（**允许引用块内部有空行**，不终止扫描）；
- 其他任何行 → `break`。

返回 `lines.slice(0, end).join('\n').trim()`。注意 `end` 只在遇到 `>` 行时推进，所以「引用块 + 空行 + 引用块」之间夹的空行会包含在结果里，但尾部的空行不会（`end` 停在最后一个 `>` 行之后）。

### replaceLead: creates the lead if absent

`replaceLead`（82-101）：`trimStart()` 后不以 `>` 开头 → 返回 `${text.trim()}\n\n${rest}\n`（rest 为原文 `trimEnd()`，空则不接）。以 `>` 开头 → 用与 `extractLead` **完全相同**的扫描逻辑找 `end`，`tail = lines.slice(end).join('\n').replace(/^\s+/,'')`，返回 `${text.trim()}\n\n${tail}` 或 `${text.trim()}\n`。

两处扫描逻辑各写一遍而不是抽公共函数——改动时必须同步，否则 `extractLead` 判「有 lead」而 `replaceLead` 找不到边界。

**幂等性**：`replaceLead` 幂等（同样 text 替换同样位置，结果逐字节相同），前提是 `text` 已 `trim()`。而 `appendToSection` 不幂等。这条不对称是 `_replace_sections` 机制存在的原因之一。

## _replace_sections is the projection channel

`RowMapping.replaceSections`（`ingest.ts:477-482`）来自表格列 `_replace_sections`。语义：

- **只有显式点名的小节**才用上游内容替换；未点名的正文（人工修订）原样保留。
- 这是「上游派生内容跟着采集库变」与「人工修订不许被冲掉」两条纪律的**边界**。默认口径是只追加不覆盖（`sections.ts:4`）。

落地在 `importTable:2173-2176`：

```text
replaced = item.body && item.replace_sections?.length
  ? applySectionUpdates(record.body ?? '', item.body, item.replace_sections)
  : undefined
```

三个「不」必须记牢：

1. **用未降级的 `item.body`**，不是 `demoted`。`demoted`（2167，`replace(/^(#{1,5})\s+/gm, '#$1 ')`）是为「嵌进导入补充」准备的，会把 `##` 降成 `###`；拿它去找 `## AI 摘要` 永远找不到（注释 2171-2172 明写）。
2. `replaced !== undefined` 时**跳过 `appendToSection` 分支**，且**不受 `body_repeat` 拦截**——摘要重算后同一来源行再来一次，正是要借这次把新摘要写进卡片。
3. 只做了 `_replace_sections` 的行，正文路径不进「导入补充」，不产生来源标注。

## _overwrite_fields is the same discipline for fields

`_overwrite_fields`（`ingest.ts:484-488`）声明「归上游投影所有的字段路径」，合并时随源覆盖、不受 `fill_empty` 约束。与 `_replace_sections` 同一套纪律：只给采集库投影出来的派生字段（`fidelity`/`word_count`）用，人工填的字段不要放进来。

落地在 `mergeFields` 第 4 阶梯（`ownedSet.has(path)`，1021-1028）。禁区比 `_clear` 宽一档——disambiguator 允许覆盖（见 identity 页）。

## derive: rules come from the domain pack, never from cards

`deriveRules(spec)`（31-44）递归收集 `derive` 声明，先 `walk(spec.extFields, 'ext')` 再 `walk(spec.baseFields, '')`。**遍历顺序决定规则顺序**，进而影响不动点迭代的收敛速度（不影响结果）。递归到 `field.fields`（object 子字段）与 `field.item.fields`（数组 item，路径加 `[]` 后缀）。

三条约束（文件头注释）：值只能来自原文匹配片段（规则不产生内容）；规则声明在领域包（卡片与导入配方不携带正则）；派生字段标 `sensitive` 后由部署边界按同一口径剥离。

## Why fixed-point iteration

规则可以互相依赖：正文 → 提示字段 → 参保地。`applyDerives`（90-136）用 `for (let pass = 0; pass < rules.length + 1; pass++)`。

**上限是 `rules.length + 1` 而不是常数**：每轮至少成功填一个路径才会 `progressed = true`，路径总数是 `rules.length`，所以最多 `rules.length` 轮就能全部填完，`+1` 是给「最后一轮无进展」确认收敛。注释写明意图：不会出现两条规则互相等对方（那会死循环，用上限兜住）。

`if (changed.includes(path)) continue;`（106）——**已填过的规则不再参与后续轮次**，这是收敛的实质保证：每轮只处理未填的，`changed` 单调增长。

## Four skipped reasons, and why the distinction matters

`DeriveSkipped['reason']`（19）：

| reason | 触发条件 | 含义 |
| :-- | :-- | :-- |
| `no_source` | `sourceText(card, rule.from)` 为空串 | 来源字段/正文没有内容 |
| `no_match` | `text.match(re)` 返回 null，**或** `captured()` 结果是空串（74） | 有原文但没匹配上 |
| `kept_existing` | 目标已有值且 mode 是 `fill_empty`（不是 `overwrite`），且新旧值**不相等** | 有匹配但按 mode 保留旧值 |
| `invalid_pattern` | `new RegExp(rule.pattern)` 抛错（67-70），`detail` 带 `err.message` | 领域包里的正则本身写错 |

「提取不到」和「提取错了」必须能区分——这是文件头注释的原话。`skipped` 每路径最多一条（`if (!skipped.some(s => s.path === path))`），且最终 `skipped.filter(s => !changed.includes(s.path))`（135）——最终改成过了的路径不再出现在 skipped 里。

注意 `kept_existing` 的判定顺序：先比 `String(current) === String(value)`（123，**相等就 `continue`，不记 skipped**），再判 mode。所以「同原文提出同值」既不算 changed 也不算 skipped，只静默跳过——这是幂等路径。

## captured: named group wins over group 1

`captured(match)`（57-62），严格三级：

1. `match.groups?.value` 是字符串且 `trim()` 非空 → 用它。
2. `match.length > 1` 且 `match[1]` 是字符串且 `trim()` 非空 → 用它。
3. 否则 `match[0].trim()`（**整个匹配**，包含正则锚定的上下文文字）。

所以领域包写 `pattern: '学号[:：]\\s*(\\d+)'` 拿到纯数字；写 `pattern: '学号[:：]\\s*\\d+'`（无捕获组）拿到 `学号：2023001` 整段——**这是最容易写错的地方**。命名组必须叫 `value`，叫 `id`/`num` 会被忽略并退到第 2 级。

第 3 级也解释了为什么「有捕获组但捕获为空」（如 `(\d*)`）会退到整段匹配而不是返回空。

## mode semantics

判定式（124）：

```text
if (!blank && (options.mode ?? rule.mode ?? 'fill_empty') !== 'overwrite') → kept_existing
```

优先级：**调用方 `options.mode` > 规则 `rule.mode` > 默认 `fill_empty`**。

- `fill_empty`：只在目标为空时写。`blank` 的判据是 `current === null || current === undefined || current === ''`（121）——**注意 `[]` 和 `{}` 不算 blank**，空数组/空对象会被当成「已有值」挡住。
- `overwrite`：值不同就覆盖。这是「重算已有值时用 overwrite，不改领域包」的通道（`DeriveOptions.mode` 注释）。

## coerce is injected, not imported

`DeriveOptions.coerce?: (path, value) => unknown`（79）。`derive.ts` **不 import `coerceValue`**——那样会形成 `derive → ingest` 的循环依赖，而且工具层若走另一份实现就会口径分叉。

调用方注入（`ingest.ts:2050-2052`）：

```text
applyDerives(spec, card, { coerce: (path, value) => coerceValue(spec, path, value) })
```

注入点只有两处使用：`withDerives`（导入写盘前最后一步）与 `absorbDonors` 内部的 `withDerives` 调用。所以派生「落在写盘前的最后一步」，保证「先导入原始列、再补提取」与「一次性导完」结果一致。

`only` 选项（81）按 `want === path || path.startsWith(want + '.')` 过滤，可只跑某棵子树。

## withDerives hides the body key

`withDerives`（2048-2056）把正文挂在 `card.body` 上让 `from: body` 的规则能读，跑完 `delete card['body']`。副作用：卡片 frontmatter 里**不能有名为 `body` 的字段**，否则会被删掉。这是隐含约束，领域包不要声明 `body` 字段。

`changed` 里每个路径累加计数到 `derivedCount`，最终进 `report.derived`（路径 → 填了几张卡）。预演看不到这个数字——预演不跑写盘，`derived` 只在 `dry_run:false` 的报告里出现。
