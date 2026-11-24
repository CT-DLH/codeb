---
covers:
  - src/core/ingest.ts
updated: 2026-11-17
---

# Ingest pipeline: parse to write

`importTable()`（`src/core/ingest.ts:1514-2231`）是唯一的批量导入入口，整条流水线是**单函数内的两阶段**：阶段 A（1587-1952）只分析、绝不写盘；阶段 B（2022-2230）先过安全阀再落盘。`card_create` 走 `prepareCard` + `commitCard`（1102-1193），与 `card_import` 共用同一份校验与 card_id 生成，两条通道不可能分叉。

策略取值与报告的**用法判读**见 `infohub/core/import-report`；本页只写实现层的阶段、分支与边界。

## Stage map with line ranges

| 阶段 | 行号 | 关键函数 | 产出 |
| :-- | --: | :-- | :-- |
| 解析 | 1525 | `parseTableFile` | `ParsedFile {format, columns, rows, row_numbers, sheets?, active_sheet?}` |
| 行窗口 | 1526-1541 | 内联 resume/limit 过滤 | `rows[]` + `rowNumbers[]` |
| 映射 | 1587-1634 | `mapRow` → `coerceValue` / `writePath` | `RowMapping {fields, body?, src?, review?, clear[], replaceSections[], overwriteFields[], unmapped[], filled[], blank}` |
| 校验+card_id | 1706-1727 | `prepareCard` → `loadDomainSchema().safeParse` | `PreparedCard {card_id, file, frontmatter, duplicate_warning?}` |
| 匹配 | 1735 | `matchIdentity` 或 `dedupMatch` | `IdentityMatch {via, path?, candidates[]}` |
| 策略 | 1748-1949 | 内联分支 | `PlannedRow` |
| 报告 | 1954-2018 | `countOf` + 三个 slice | `ImportReport` |
| 安全阀+写盘 | 2023-2230 | `mergeFields` / `commitCard` / `applySectionUpdates` / `absorbDonors` / `withDerives` | 计数 + `ids` |

`plan` 是 `PlannedRow[]`，六种 action：`create | update | skip | quarantine | reject | review`。`skip`/`reject`/`review` **从不写盘**（2102-2117 只 `continue` 并推进 `lastCompletedRow`）；只有 `create` 与 `update` 落盘。

## Stage A never touches disk, and why the split matters

阶段 A 对每行做完全部判断，然后 `if (options.dry_run !== false) return report`（2020）。`dry_run` **默认 true**（1958），所以不带 `dry_run: false` 永远是预演。这条分界的价值：整批中止时（`max_updates` 超限、或写盘抛错）报告仍完整可用，且「预演计数」与「落盘计数」出自同一份 `plan`。

## Report field semantics

字段的用法判读见 `infohub/core/import-report`。这里只记四个容易数错的实现细节：

- `parsed` 是**处理行数**（`rows.length`，1963），不是文件总行数——`resume_from_row` 与 `limit` 都会让它小于文件行数。
- `would_update` 与 `would_merge_in_file` 是**同一 action=update 的两种归属**（2009-2010 按 `item.in_file` 切开），两者之和才是 update 总数。
- `sample` 只有 3 条（1987 `plan.slice(0, 3)`），fields 用 `flatten` 摊平、去掉 `SERVER_FIELDS` 根（`card_id`/`domain`/`collected_at`/`created_at`/`edited_at`）再遮蔽敏感值。
- `derived`（路径 → 填了几张卡）只在实盘报告出现，预演不跑写盘。

## Anomaly type enum, all eight

`AnomalyType`（1252-1260）：`empty_title`、`empty_row`、`duplicate`、`invalid_field`、`review`、`ambiguous`、`claim`、`override`。各类型该怎么办见 `infohub/core/import-report`；这里记**生产者**，因为改动时常要判断「这个 type 有没有人 push」：

| type | 生产位置（行号） |
| :-- | :-- |
| `override` | 1607 行级覆盖生效 |
| `invalid_field` | 1630 `_clear` 越权、1652 `_overwrite_fields` 越权、1714 schema 校验失败 |
| `review` | 1668 `_review` 列、1738 有 `_clear` 却无匹配卡 |
| `empty_row` | 1673 `mapping.blank` |
| `empty_title` | 1680 非 placeholder 策略、1698 placeholder 生成成功 |
| `duplicate` | 1830 幂等跳过、1861 命中合并、1892 正文不重复追加 |
| `ambiguous` | 1765 强标识多命中、1850 弱标识多命中、1786 遮蔽伪强标识 |

**`claim` 枚举值存在但全库无生产者**——认领合并只体现在 `report.claimed` 计数与 `sources` 里那条「并入待认领卡 X」，不进 anomalies。想加这个异常得自己 push。

`ImportRisk.type`（1304）三种：`disambiguator_asymmetry`、`field_conflict`、`identity_collision`，全部由 `assessMergeRisk`（1461-1512）产生，且**只在 `strongMatch` 为假时才调用**（1847）——强标识命中不是「可能不该合并」而是定义性同一实体。

`assessMergeRisk` 两级判据：先查 `disambiguator` 单边缺失（`!incoming || !existing`，两边都缺则 `continue`）；再找前 **3** 个字段值冲突（跳过 `RISK_IGNORED_FIELDS` 八项、`UNION_ROOTS`、数组、对象，1444-1455 与 1491-1502）。

## DEFAULT_STRATEGIES and the four-layer override

`DEFAULT_STRATEGIES`（1368-1376）：`empty_title:'placeholder'`、`on_duplicate:'keep_both'`、`merge_rule:'fill_empty'`、`on_claim:'merge'`、`on_invalid:'quarantine'`。

合并顺序（1517-1524）：`DEFAULT_STRATEGIES` → `spec.importStrategies`（领域包 `imports.strategies`）→ `options.strategies`，其中**值为 undefined 的键被过滤掉**（1517-1519）→ 生效。过滤是关键：传 `{on_duplicate: undefined}` 等同于没传，不会把领域包的值抹掉。

`on_duplicate` 有两处**绕过 strategies 的旁路**，改策略时最容易漏：

1. `strongMatch` 且 `options.strategies?.on_duplicate === undefined` 且 `spec.importStrategies?.on_duplicate === undefined` → 强制 `merge`（1839-1846）。`strongMatch` = `via === 'strong'`，或 `via === 'dedup'` 且 `path` 是 `source_ref`/`dedup_key`（1754-1756）。
2. `clears.length > 0` → 强制 `merge`（1840），修正行必须能落到卡上撤回字段。

## Three safety valves, exact semantics

**`max_updates`（默认 20，2023）**：判定式 `report.would_update > maxUpdates`（2024），**严格大于**才中止——计划正好 20 张放行，21 张中止。`would_update` 只数 `action === 'update' && !item.in_file`（2009），所以**并入本文件自己新建的卡（`item.in_file`）不占额度**。`in_file` 来自 `target.planned_row`（1926），而 `planned_row` 只有本轮 `create` 时才写进 `index.entries`（1946-1951）。超阈值时 `ok:false`、`aborted` 带文案、**一个文件都不写**；若带 `resume_from_row` 还回填 `last_completed_row: resumeFrom - 1`（2029），让续跑停在原地而不是跳过。

**`limit`（1246）**：`options.limit > 0` 才生效（1528），在 `if (limitCount && rows.length >= limitCount) return;`（1538）处截断。它在 `resume_from_row` 过滤**之后**（1534-1540），所以数的是「resume 之后要处理的行数」，**不是文件行号**。

**`resume_from_row`（1248）**：`> 1` 才生效（1527）。过滤条件 `rowNumber < resumeFrom`（1534），即**包含** `resume_from_row` 这一行；`skipped_before_resume` 计被跳过的行数。按**展示行号**（`row_numbers`）比较，不是数组下标。

写盘阶段另有一个隐式保护：`quarantine` 行写 `.quarantine/<domain>/<stamp>.jsonl`（2033-2034），每行 `{row, provenance, reason}`；`update` 时目标卡文件不存在也转 quarantine 并写 `reason: 目标卡片不存在: <card_id>`（2146-2156），不静默丢。

## Truncation constants and what truncation costs

```text
MAX_ANOMALIES = 50    // anomalies.slice(0,50) + anomalies_truncated = len-50
MAX_RISKS     = 20
MAX_CLEARS    = 100
RAW_CELL_LIMIT = 60   // 异常 raw 里单格文本截到 60 字符 + '…'
```

截断只作用于**报告**，不影响 plan 与写盘。三个 `*_truncated` 都是 `Math.max(0, len - LIMIT)`（1984-2017），所以「truncated=0」等价于「全量都在」。`compactRow`（1384-1392）先丢空值再截断，`RAW_CELL_LIMIT` 只对字符串生效，数字/布尔原样保留。

`clears` 与 `ClearRecord {row, card_id, path, old}`（1295-1300）记的是「被真正抹掉的旧值」，在阶段 A 就于 1900-1909 采集，所以预演也能看到——这是唯一会丢信息的操作，因此单独计数、单独截断、单独回传。

## Sensitive values never echo back

`HIDDEN = '（敏感值，不回显）'`（1399）。两条遮蔽路径，缺一不可：

- **`maskSensitivePaths(spec, row)`（1401-1407）**：用于 `sample[].fields`。键是**字段路径**（`ext.id_card`），用 `fieldSpecFor(spec, path)?.sensitive === true` 直接判。
- **`sensitiveSourceColumns(spec, columnMap)`（1410-1420）**：用于 `anomalies[].raw`。raw 的键是**源列名**（Excel 表头），字段路径判不了，所以反向遍历 `column_map`，把「目标路径里有任一 sensitive」的列名收进 Set，再由 `maskSensitiveColumns`（1422-1429）替换。

两处都先判 `!isBlankValue(value)`——空值不遮蔽，否则报告里会出现一堆「（敏感值，不回显）」淹没真正的值。

卡片照常写敏感值，剥离只发生在报告。注释写的理由：判断「映射对不对」看列名、计数、异常类型就够，不需要把身份证原文搬进对话。

## prepareCard, commitCard, buildSourceBody

`prepareCard`（1102-1167）是 `card_create` 与 `card_import` 的共用校验节点，顺序严格：

1. `loadDomainSpec(input.domain)`。
2. 组装 `base`：`{...fields, domain, collected_at}`。`collected_at` 取 `fields.collected_at`，空则 `today`（`new Date().toISOString().slice(0,10)`，UTC 日期不是本地日期）。
3. `object_type` 只在 `input.object_type` 有值**且** `fields.object_type === undefined` 时注入（1120-1122）。注释：参数只是「这一批没写 object_type 时填什么」，行里自己声明了就按行的来（混合材料一批导入是常态），没声明的类型交给枚举校验拒绝，**不静默改写**。
4. `loadDomainSchema(input.domain).safeParse({...base, ext: base.ext ?? {}})` — 失败转 `toIssues`（61-73，`path` 数组 join('.')，空则 `(root)`）。
5. **`object_type` 白名单**（1131-1135）：`declaredType && spec.objectTypes.length > 0 && !spec.objectTypes.includes(declaredType)` → 返回 `ok:false` 且 `issues:[{path:'object_type', code:'custom'}]`。注意 `spec.objectTypes.length === 0` 时**不拦**（没声明类型清单的领域放行任何值）。
6. `year = collectedAt.slice(0,4)`，空则当前年份（1137）。
7. `cardId = input.card_id ?? uniqueCardId(domain, buildCardId(...), input.taken)` — 显式传入的 `card_id` **完全绕过** `buildCardId` 与 `uniqueCardId`（不查重不查重名）。
8. `frontmatter.card_id` 与 `frontmatter.domain` 在 parse **之后**覆盖写回（1140-1141），所以领域包里的 `card_id` 字段约束不会拦住它们。
9. `duplicate_check !== false` 时跑 `buildDuplicateWarning(findSimilarCards(..., 5))`。

第 5 步为什么放这一层（注释原文）：`card_create` 挡得住，`card_import` 会绕过去，而混合材料一批导入时行里带类型是常态——不挡就会写出一堆领域包没声明过的类型，**列表页按类型筛选直接落空**。这是「校验必须在唯一内核里」的具体实例。

`commitCard`（1191-1193）：`writeCardFile(file, matter.stringify(body.trim() || emptyBodyText, frontmatter))`。默认兜底文案 `'## 来源\n\n- 待补充'`；`importTable` 的 `create` 分支**显式传 `''`**（2133），因为那边已经用 `buildSourceBody` 兜了一层。

`buildSourceBody`（1196-1211）从 `sources` 生成最小正文：跳过 `file` 与 `row` 全空的条目；`kind === 'attachment'` 的行写成 `- 附件 <file>`，其余写 `- <file> · 第 <row> 行`（row 为空则省掉后半）。有行才返回 `## 来源\n\n<lines>`，否则空串——空串再交给 `commitCard` 的兜底文案。

`duplicate_warning` 是**非阻断**的：`prepareCard` 照样返回 `ok:true`，`card_create` 照样建卡。它与 `importTable` 里阻断的区别在于——`importTable` 的 `duplicate` 异常会改 action 为 `skip`/`update`，而 `duplicate_warning` 只是一条附带信息。且 `importTable` 传 `duplicate_check: !identity`（1710）：**声明了 identity 的领域不再跑 dedup 扫描**，因为已有一套精确匹配。

## Abort and resume bookkeeping

写盘循环外是 `try/catch`（2100-2213）。抛错时返回 `ok:false` + `aborted: 导入在第 N 行之后失败: <msg>；已写入的部分保留，可用 resume_from_row 续跑`，并带上已完成的 `created`/`updated`/`quarantined`/`claimed`/`cleared`/`derived`/`ids`。**已写的不回滚**——续跑靠 `resume_from_row`，幂等性由「同一来源行字段 merge + 正文 `body_repeat` 拦截」保证。

`lastCompletedRow` 初值 `resumeFrom ? resumeFrom - 1 : undefined`（2041），所以一开始就失败时仍然给出可续跑的起点。
