---
covers:
  - src/mcp/tools/card_update.ts
  - src/mcp/tools/card_commit.ts
  - src/mcp/tools/card_batch.ts
  - src/mcp/tools/card_append.ts
  - src/mcp/tools/card_create.ts
  - src/mcp/tools/card_import.ts
  - src/mcp/tools/card_attach.ts
  - src/mcp/tools/card_delete.ts
updated: 2026-11-17
---

# Write tools: layering and the two-phase update

八个写工具里只有一个会「先暂存再提交」，其余七个都是**一次调用直接落盘**。
默认值也不统一：`card_create`/`card_batch` 默认真写，`card_import`/`card_attach`/`card_derive` 默认预演。
搞错这两件事的后果是相反的——前者会意外落盘，后者会以为已经写了。

## Who calls whom

```text
card_create ──┐
card_batch  ──┼─→ core/ingest.prepareCard()  → 校验 + 生成 card_id + findSimilarCards(查重)
              │        ↓
              └─→ core/ingest.commitCard()    → writeCardFile(file, matter.stringify(body, fm))
card_import ─────→ core/ingest.importTable()  → 内部同样走 prepareCard/mergeFields → writeCardFile
card_attach ─────→ core/attach.attachDirectory() → 直接 readCardFile + writeCardFile（不校验 Schema、不动 frontmatter 字段）
card_append ─────→ findCardFile + readCardFile + appendToSection + writeCardFile
card_delete ─────→ readCard + moveToTrash（rename 进 .trash/）
card_update ─────→ readCard + validatePartial + stageUpdate（写 .staging/，不碰卡片）
card_commit ─────→ readStaging + readCard + detectRevisionDrift → writeCardFile 或 createConflictRecord
```

`card_create` 与 `card_batch` 的 `create` 走的是**同一个** `prepareCard`，所以两条通道的校验、对象类型白名单、
`card_id` 生成口径不可能分叉。`card_import` 走 `importTable`，内部复用同一批函数但仍是一条独立路径——
「逐条 `card_create`」和「`card_import`」在判重策略上不同（前者只警告，后者会真的合并）。

## Which writes actually hit disk

| 工具 | 默认 | 落盘目标 | 落盘条件 |
| :-- | :-- | :-- | :-- |
| `card_create` | **写** | `cards/**/<card_id>.md` | 校验通过；`dry_run:true` 时不写 |
| `card_import` | 预演 | 同上（多张） | `dry_run:false` 且 `would_update ≤ max_updates` |
| `card_append` | **写** | 一张卡的正文 | 总是写（无 dry_run 参数） |
| `card_update` | 写暂存 | `.staging/<card_id>/<pending_id>.json` | 总是写暂存，**永不写卡片** |
| `card_commit` | **写** | 一张卡 / `.conflicts/<card_id>/*.json` | 版本一致写卡，不一致写冲突 |
| `card_attach` | 预演 | 多张卡的正文 + `sources` | `dry_run:false` 且 `cards_to_write ≤ max_updates` |
| `card_batch` | **写** | 按 op 决定 | `dry_run:true` 时不写；**没有 max_updates 安全阀** |
| `card_delete` | **写** | `.trash/<card_id>/<ts>-<file>` | 总是移动 |
| `card_derive` | 预演 | 多张卡的 frontmatter | `dry_run:false` 且计划改动 ≤ `max_updates`（默认 20） |

`card_batch` 是唯一没有任何张数上限的写工具——它的安全性靠 `stop_on_error` 与逐条 schema 校验，
不靠数量阀。批量落地超过几十条的场景应该走 `card_import`。

## The two-phase update and why it is not really optimistic locking

`card_update` 收 `_base_revision`，**但它不比对**。它只做三件事：`expandDotPaths`、`validatePartial`、`stageUpdate(cardId, baseRevision, changes)`。
比对发生在 `card_commit`：重新 `readCard()`，把 `card.revision`（当前文件的 sha256 前 16 位）与
`staging._base_revision`（调用方给的那个）比。

一致 → `writeCardFile(card.file, buildDraftContent(card, staging.changes))`，返回 `revision`。
不一致 → `createConflictRecord({_base_revision, current_revision, current_content: card.raw, draft_content})`，
源文件**一个字节都不动**，返回 `conflict_id`。两条路径都会 `deleteStaging(pending_id)`，
所以冲突一旦产生，暂存记录就没了——**你手上只剩 `.conflicts/` 里那份草稿**。

三个由此派生的行为要记住：

- **`draft_content` 是「当前卡片 + changes」，不是「基线卡片 + changes」**。`buildDraftContent` 用的是
  commit 那一刻读到的 `card`，而不是 `_base_revision` 对应的旧版本。所以冲突里那份草稿已经套用了别人的改动，
  三方合并时它既不是 base 也不是 theirs。
- **`card_update` 阶段产生的暂存永远不会过期**。`readStaging` 按 `pending_id` 线性扫 `.staging/` 下所有子目录，
  没有 TTL、没有清理。跑过几次没 commit 的会话会在 `.staging/` 里留下永久垃圾，且没人会提醒。
- **`pending_id` 是 `${Date.now()}-${random6}`**，不是哈希。同一毫秒内两次 `card_update` 理论上不会撞（随机后缀），
  但 `readStaging` 找到第一个匹配就返回——不同卡上恰好同 id 时取到哪一份取决于 `readdirSync` 顺序。

`card_commit` 的 `revision` 是写盘后的**新**哈希，可以直接当作下一轮 `card_update` 的 `_base_revision`。

## card_append is the escape hatch, and it has a cost

`card_append` 不读版本、不检测漂移、不碰 frontmatter，只把 `text` 拼进正文指定小节。
这就是为什么采集场景优先用它：一次调用就完事，不需要「读 → 暂存 → 提交」三次往返。

代价是**并发追加会静默丢内容**：两个调用各自读到同一份 body，各自加一段，后写的直接覆盖前一个。
`writeCardFile` 的内容指纹只能判断「和磁盘上的比变没变」，判断不了「这中间别人改过」。
它也不维护 `sources`——追加的内容没有溯源记录，`card_attach` 才有。

`section` 省略时是 `body.trimEnd() + '\n\n' + text`，**不加任何标题**；给了 `section` 才走
`appendToSection`（小节不存在则新建 `## <section>`，已存在则插到该小节末尾、下一个 `#`/`##` 之前）。
`card_append` 不做 `sensitive` 处理：把敏感值粘进正文，它会绕过发布门禁对**字段**的剥离。

## card_batch: no transaction, and its conflict check can never fire

`card_batch` 逐条执行，**没有事务、没有回滚**。`stop_on_error` 默认 `true`，第一条失败就停；
`summary.hint` 明确写着「已写入的不回滚」。所以它是「一次性跑完一串」而不是「全成功或全失败」。

内部实现里有几处只在这个工具存在的语义：

- **别名系统**：`create` 成功后 `aliases.set('op<i>', card_id)`，op 里带 `as` 时额外注册 `aliases.set(op.as, card_id)`；
  后续 op 用 `ref: "$别名"` 引用。`resolveRef` 找不到别名时**退化成字面量**
  （`aliases.get(name) ?? name`），所以拼错的 `$foo` 会变成 card_id `foo` 去查卡，报 `not_found` 而不是「别名不存在」。
- **预演期的自指**：`dry_run:true` 时前面 `create` 的卡还没落盘，`append`/`update`/`delete` 引用它会 `not_found`。
  代码用 `taken` 集合兜住：`if (dry_run && taken.has(cardId))` → 记 `planned_target:true` 并算成功。
  真跑时没有这条豁免。
- **`update` 的乐观锁形同虚设**：`stageUpdate(cardId, card.revision, changes)` 里传的基线就是
  **刚刚读到的** `card.revision`，紧接着 `detectRevisionDrift(card, staged._base_revision)` 拿它和同一个
  `card.revision` 比——**恒为 false**。结果：`card_batch` 的 update 分支永远走写盘，`entry.error = 'conflict'`
  这条路径在生产上不可达。要真检测漂移必须走 `card_update` + `card_commit`（那条路径的基线来自调用方）。
- **`create` 的 `taken` 是跨 op 累积的**：同一批里两次 `create` 撞 `card_id` 时，第二次得到 `-2` 后缀（`uniqueCardId`）。
- **`response_mode: 'full'` 只在 `create` 的 dry_run 分支里生效**，返回 `entry.frontmatter`；
  其他 op 不管 `full` 与否都只回状态键。名字叫 full，实际只覆盖一种情况。
- **`ops_file` 支持两种形态**：整体 JSON 数组（首字符 `[`），或一行一条 JSONL（空行跳过）。
  解析失败直接 `isError`，第几条不合法会点名。文件开头的 BOM 用 `replace(/^﻿/, '')` 剥掉。

失败记录的形状统一：`entry.ok = false` 加上 `entry.error`，其中 `error` 可能是
字符串（`'create 需要 domain'` / `'not_found'` / `'text_file 不存在: x'`）或代码名（`'schema_invalid'` / `'conflict'`），
`schema_invalid` 额外带 `errors[]` 与 `issues[]`。**`error` 的类型不固定，封装时要两边都判。**

## card_delete leaves orphans behind

`moveToTrash` 只 `rename` 卡片文件。`card_id` 目录名保留，所以同一张卡删两次会在
`.trash/<card_id>/` 下留两份不同时间戳的文件（卡片不在原路径，第二次会先报 `未找到卡片`）。
`.staging/<card_id>/` 与 `.conflicts/<card_id>/` 里的记录**不会被清理**，删卡后它们变成永久孤儿。

## What each tool refuses to do

- `card_append` 不新建卡、不校验字段（`section` 名随意）。
- `card_attach` 永不新建卡：`missing` 就隔离、`ambiguous` 就进复核，都不猜。
- `card_update` 不能改未在领域包声明的字段（`validatePartial` 逐键拒绝），也不能靠它落盘。
- `card_commit` 不合并冲突，只把两份内容交出来（`card_conflicts` → `card_resolve`）。
- `card_batch` 的 `delete` 条目在 `dry_run` 下只回 `entry.dry_run = true`，不做存在性以外的检查。
- `card_create` 的 `duplicate_warning` 只是警告，**仍然会创建**——「看到警告就以为被挡下」是这条流程最常见的误读。
