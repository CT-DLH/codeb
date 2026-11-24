---
covers:
  - src/mcp/tools/card_import.ts
  - src/core/ingest.ts
updated: 2026-11-17
---

# Import strategies and the report contract

`card_import` 的结果是一个 `ImportReport`。**这张报告本身就是 API**——
模型根据它决定「下一步改 strategies 还是改数据」，所以字段语义必须精确，不能靠猜。

## The five strategies and their real defaults

`ImportStrategies` 五个键（`src/core/ingest.ts:1215-1226`），默认值在 `DEFAULT_STRATEGIES`：

| 键 | 取值 | 默认 | 作用 |
| :-- | :-- | :-- | :-- |
| `empty_title` | `placeholder` / `quarantine` / `reject` | **`placeholder`** | 标题为空怎么办 |
| `on_duplicate` | `merge` / `skip` / `keep_both` | **`keep_both`** | 命中已有卡怎么办 |
| `merge_rule` | `fill_empty` / `overwrite` / `union` | **`fill_empty`** | 合并时字段规则 |
| `on_claim` | `merge` / `review` | **`merge`** | 强标识命中后是否自动并入待认领卡 |
| `on_invalid` | `quarantine` / `reject` | **`quarantine`** | 校验失败怎么办 |

### Why the default is keep_both, not merge

注释原文：

> 批量导入默认非破坏：并卡合掉的找不回来，多出来的可以事后合。
> 未显式指定 `on_duplicate` 时强标识命中仍合并——同一学号/DOI 是定义性同一实体，且 `fill_empty` 不覆盖原值。

这是一个**不对称的风险判断**：多建一张卡是可见、可修的；错误合并会静默丢信息且不可逆。
所以默认偏向「宁可多」。

但强标识命中是例外：同一个学号就是同一个人，这不是判断问题而是定义问题。
**这个例外只在未显式传 `on_duplicate` 时生效。**

## Why placeholder, not reject

`empty_title` 默认 `placeholder`：标题空就生成占位标题（`isPlaceholderTitle` 认得出的那种，
以「未命名」开头或以「-待定题目」结尾）。

理由：一条信息没有标题仍然可能有价值，直接丢掉等于替用户做决定。
而占位标题**在合并时按空值对待**，所以后续带真名的材料会覆盖它，不会产生假冲突。

## The report fields that decide your next action

`ImportReport`（`ingest.ts:1310-1366`）有 30 多个字段，其中**八个**真正影响下一步：

| 字段 | 含义 | 什么时候看它 |
| :-- | :-- | :-- |
| `would_create` | 将新建几张 | 预演时判断规模是否符合预期 |
| `would_update` | 将改动**仓库里已有卡**的行数 | **这是 `max_updates` 唯一管的数** |
| `would_merge_in_file` | 并入本次导入自己新建的卡 | 不占额度，所以它大不是问题 |
| `anomalies` | 异常清单（最多 50 条） | 有 `invalid_field` 就是映射错了 |
| `anomalies_truncated` | 被截掉的异常条数 | **非 0 说明问题比看到的多** |
| `risks` | 合并风险线索（最多 20 条） | 有 `disambiguator_asymmetry` 要考虑 `keep_both` |
| `unmapped_columns` | 没被 `column_map` 映射的列 | 通常意味着漏了字段 |
| `aborted` | 中止原因 | 非空表示**一张都没写** |

### would_update is not "how many rows matched"

这是最容易误解的一处：

> 只统计「改动仓库里已有卡片」的合并——它才是 `max_updates` 安全阀管的东西。

一次导入 500 行全新数据，`would_update` 是 0，不会触发安全阀；
同样 500 行如果都在更新已有卡，`would_update` 是 500，直接中止。
`would_merge_in_file` 单独计数就是为了让这两件事不混在一起。

## The three truncation constants

```ts
const MAX_ANOMALIES = 50;
const MAX_RISKS = 20;
const MAX_CLEARS = 100;
const RAW_CELL_LIMIT = 60;
```

`anomalies_truncated` / `risks_truncated` / `clears_truncated` 分别报告被截掉的条数。
**看到 `truncated > 0` 必须降低 `limit` 或分段跑**，否则你看到的是问题的前 50 条，
而真问题可能在第 200 条。

`RAW_CELL_LIMIT = 60`：异常里附带的原始行，每个单元格超 60 字符就截断加 `…`。
这是为了防止整表内容灌进对话上下文——**报告里永远只出现定位信息，不出现全量数据**。

## Anomaly types and what each one means

八个类型（`AnomalyType`）：

| type | 含义 | 该怎么办 |
| :-- | :-- | :-- |
| `empty_title` | 标题为空 | 看 `empty_title` 策略是否符合预期 |
| `empty_row` | 整行空 | 通常无害，文件本身有多余空行 |
| `duplicate` | 命中已有卡 | 看 `same_key` 判断靠什么命中的 |
| `invalid_field` | 字段校验失败 | **映射错了**，改 `column_map` 重跑 |
| `review` | 需要人工决定 | 通常是弱标识多命中 |
| `ambiguous` | 匹配到多张卡 | 不要强行合并 |
| `claim` | 发生了待认领卡并入 | 正常，但要知道哪些卡被并了 |
| `override` | 用了 `row_overrides` | 正常，人工指定值优先 |

`invalid_field` 带 `issues: Issue[]`（结构化，不是文本拼接），能直接定位到字段路径。

## Risks are advice, not decisions

`ImportRisk` 三个类型：

| type | 含义 | 建议 |
| :-- | :-- | :-- |
| `disambiguator_asymmetry` | 消歧字段单边缺失 | 通常是名额分配差异 → `keep_both` |
| `field_conflict` | 同一字段两个来源值不同 | 保留双方，人工收敛 |
| `identity_collision` | 标识撞车 | 强标识冲突交给工具拦进 review |

**工具只给依据，不替人决定。** `risks` 里每条都带 `suggestion` 字段，但那是建议不是结论。
这是项目一贯的立场：判断留给人（或调用方的模型），工具只负责让判断有依据。

## Clears: the audit trail of erased values

`would_clear` / `clears`（最多 100 条，`ClearRecord` 是 `{row, card_id, path, old}`）。

它记录**被真正抹掉的旧值**。什么情况下会抹值？`merge_rule: overwrite`
或 `owned` 字段被上游覆盖时，旧值就没了。`clears` 是唯一能事后知道「原来是什么」的地方。

**这是唯一一类会丢信息的操作**，所以它单独计数、单独截断、单独回传。

## resume_from_row: the only safe way to split a big file

导入 5000 行超时或中断后，不要重跑整个文件。用：

```jsonc
{
  "resume_from_row": 1201,   // 从这一展示行号开始，小于它的直接跳过
  "limit": 1000              // 只处理 1000 行
}
```

`skipped_before_resume` 告诉你跳过了多少行，`last_completed_row` 告诉你处理到哪——
**下次的 `resume_from_row` 就填 `last_completed_row + 1`**。

行号是**展示行号**（表头算第 1 行，数据行从 2 起；jsonl 是物理行号），
和 Excel 里看到的行号一致，不需要自己换算。

## The whitelist check that lives in the kernel, not the tool

`prepareCard` 里有一段容易被忽略的校验（`ingest.ts:1131-1135`）：

```ts
const declaredType = asText(base.object_type);
if (declaredType && spec.objectTypes.length > 0 && !spec.objectTypes.includes(declaredType)) {
  return { ok: false, issues: [{ path: 'object_type', ... }] };
}
```

注释解释了为什么放在内核而不是工具层：

> `card_create` 挡得住，`card_import` 会绕过去，而混合材料一批导入时行里带类型是常态
> （不挡就会写出一堆领域包没声明过的类型，列表页按类型筛选直接落空）。

**这是「校验必须在唯一内核里」的一个具体实例**：任何只在某一个通道做的校验，
另一个通道就一定能绕过去。

## Reading a real report

```jsonc
{
  "ok": true,
  "dry_run": true,
  "parsed": 348,
  "would_create": 330,
  "would_update": 12,          // 只有 12 行会改动已有卡，远低于 max_updates=20
  "would_merge_in_file": 6,    // 文件内重复，不占额度
  "anomalies": [
    { "row": 57, "type": "invalid_field", "detail": "...", "issues": [...] }
  ],
  "anomalies_truncated": 0,
  "risks": [
    { "row": 88, "type": "disambiguator_asymmetry", "suggestion": "keep_both" }
  ],
  "unmapped_columns": ["备注"],
  "aborted": null
}
```

读法：这份可以真跑——`would_update` 12 < 20，且 `anomalies_truncated` 与 `risks_truncated` 都是 0。

反例：如果同一份文件 `would_update` 是 336，报告会直接带 `aborted`，**一张卡都不写**。
那时要么分批（`resume_from_row` + `limit` 把「更新已有卡」的行切到 20 以内），
要么确认这确实是要批量更新的场景（比如全量回填）再显式调高 `max_updates`。

`aborted` 非空 = 整体中止，不是部分成功。这一点决定了「重跑」永远安全。
