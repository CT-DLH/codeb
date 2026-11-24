---
covers:
  - src/core/
  - src/lib/schemas.ts
  - domains/_base.yaml
---

# Write channels

所有写入最终都会落到 `src/core/ingest.ts` 与 `src/core/attach.ts`。
**MCP 工具与 CLI 脚本共用同一份内核**，这是刻意的：保证「逐条写入」和「批量导入」的校验、判重、`card_id` 生成口径完全一致。

## Four channels, chosen by material shape

| 材料形态 | 通道 | 为什么不是别的 |
| :-- | :-- | :-- |
| 单条信息 | `card_create` / `card_append` | 采集场景优先 `card_append`，挂到已有卡的小节，不走「读版本→暂存→提交」 |
| 表格，一行一实体 | `card_import` | 逐行 `card_create` 在几十行材料上会失败（桥接层转义不可靠，实测失败 5 次） |
| 主表 + 附件补正文 | `card_attach` | `card_import` 没有「匹配已有卡并追加正文」的语义 |
| 目录里一文件一实体 | 脚本归并成 JSONL → `card_import` | 先由 `prepare:courses` 做程序能做的那部分（转码、去重、按课程归并） |

## Data by file path, never by argument

这是最硬的约束。批量通道把数据留在磁盘，对话里只出现**判断**（列映射、异常策略）和**报告**（异常与样本）：

```text
file_read({ file_path: 'inbox/x.csv' })                → 表头 + 每列填充数/类型/风险 + 样例
card_import({ ..., dry_run: true })                    → 预演报告
card_import({ ..., 同一参数, dry_run: false })          → 落盘 + 计数
```

`column_map` 的值可以是数组（一列喂多个字段）。保留目标：`_body`（正文）/ `_src`（溯源）/ `_review`（该行进人工）/ `_ignore`（丢弃）。
非结构化材料（PDF、截图、邮件）先由 AI 拆成 `inbox/x.jsonl`（原文没有的字段一律 `null`），再走同一条 `card_import`。

## Non-destructive defaults

`on_duplicate: keep_both`、`on_invalid: quarantine`、`merge_rule: fill_empty`。

例外：强标识（`identity.strong` 或 `source_ref` / `dedup_key`）在未显式传 `on_duplicate` 时**默认合并**。

`risks` 会主动说明「为什么可能不该合并」（如消歧字段单边缺失，通常是名额分配），并建议 `keep_both`。
**工具只给依据，不替人决定。**

## Three safety valves

- `max_updates`（默认 20）：只看「改动仓库里已有卡片」的行数。文件内重复合并到本文件新建的卡**不占额度**。超阈值整体中止，一个文件都不写。
- 计划更新数与 `anomalies` 对不上时，**先改 `strategies` 或个别行的 `row_overrides`，不要改数据文件**。
- 敏感字段：带 PII 的材料**先标记字段再导入**。先塞进普通字段再搬，等于已经公开过一次。

## identity: the single rule for same-entity

只在领域包声明，不在卡片里临时决定。

```yaml
identity:
  strong: [ext.student_id]        # 本身唯一，命中即合并
  weak: [ext.name]                # 整体相等且唯一命中才合并，多命中进 review
  disambiguator: [ext.class]      # 只用于人工区分
  card_id_pattern: student-{ext.student_id}
  card_id_fallback: student-name-{ext.name}
```

**匹配顺序固定 ① 强标识 → ② 弱标识 → ③ 新建，不可颠倒。** 颠倒会让「同名不同学号」被误合并。

- 只有姓名的材料先落成「待认领卡」，带学号的材料出现时自动并入，donor 原文件进 `.trash/`。
- 合并不静默覆盖：值不同就保留双方 + 记 `import_conflicts` + `status: 冲突`。
- `{hash:weak}` = `sha1(归一化标识值)` 前 8 位。**不能用随机数**，否则幂等失效。
- 没声明 identity 的领域退回 `dedup_key`；两者都没有时 `card_import` **直接拒绝**，避免批量灌重复卡。

## Deterministic dedup without embeddings

`source_ref` 归一化后相同（1.0）→ `title` 归一化后相同/包含（1.0 / 0.85）
→ `aliases`（0.9 / 0.85）→ `dedup_key` 组合键全等（1.0）。

`card_create` 命中 ≥0.8 时返回**非阻断**的 `duplicate_warning`，**仍会创建**。

## Mandatory dedup flow before writing

先 `card_find_similar` → 高相似先 `card_read` → 补充信息用 `card_append`、
字段变更用 `card_update` + `card_commit`、**确认不同实体才 `card_create`**。

同一事件多来源合并到一张卡，多个 URL 写进正文「来源」小节；表述变体加入 `aliases`。
