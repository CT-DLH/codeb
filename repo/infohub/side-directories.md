---
covers:
  - src/mcp/lib/storage.ts
  - .trash/
  - .staging/
  - inbox/
updated: 2026-11-17
---

# The side directories and what fills them

仓库根下有一堆点开头的目录，它们不在 `cards/` 里，但**改写入逻辑、排查数据丢失时必须知道**。
这些目录都被 git 忽略——所以它们也是「本地状态」，不会出现在别人的机器上。

## 实测体量（2026-11-17）

| 目录 | 文件数 | 体量 | 谁写 | 能不能删 |
| :-- | --: | --: | :-- | :-- |
| `.trash/` | **46715** | 102.2 MB | `moveToTrash()` | 能，是删除缓冲区 |
| `.backup/` | 1136 | — | 迁移脚本 | 能，历史快照 |
| `.staging/` | 394 | — | `card_update` 暂存队列 | **不能**，有未提交的修改 |
| `.cache/` | 100 | — | 构建 / 检索缓存 | 能，会重建 |
| `.quarantine/` | 1 | — | 校验失败隔离 | 看内容，可能是待补数据 |
| `.conflicts/` | 0 | — | 冲突收敛 | 当前为空 |

`.trash` 有 4.6 万个文件这件事本身就是一条知识：**这个项目的删除量远大于它的卡数增量**，
因为批量导入的错误合并、重复卡清理都走「移入 trash」而不是物理删除。

## .trash is a real safety net, not a graveyard

`moveToTrash()` 的实现（`src/mcp/lib/storage.ts`）只有五行，但两个细节决定了它可恢复：

```ts
const stamp = new Date().toISOString().replace(/[:.]/g, '-');
const dest = join(TRASH_DIR, cardId, `${stamp}-${basename(file)}`);
mkdirSync(dirname(dest), { recursive: true });
renameSync(file, dest);
```

1. **按 `cardId` 分目录**，不是平铺。所以「这张卡历史上被删过几次」一眼可见——
   `.trash/51f9afec`、`.trash/51f9afec-2`、`.trash/51f9afec-3`、`.trash/51f9afec-4` 是同一实体被删了四次。
2. **时间戳前缀**，所以同名文件不会互相覆盖，且能按时间找回。

**删除 = 移动，不是抹除。** 注释写明「可恢复、Git 忽略，不做物理抹除」，
`card_delete` / `card_batch` / 导入并卡三处共用这一个函数。

这条设计消解了 `infohub/invariants` 里「并卡合掉的找不回来」那个风险——
不是完全找不回，是**没有工具帮你找**。真要恢复就手动从 `.trash/<card_id>/` 里挑时间戳。

注意 `.trash` 里还有非卡片文件（`list-index-test.ts.bak`、`m2-manifest.json`），
那是迁移脚本顺手丢进去的，说明这个目录也是「不想直接 rm 的临时弃置区」。

## .staging holds uncommitted two-phase writes

`card_update` + `card_commit` 是两阶段写入：`card_update` 把改动写进 `.staging/`，
`card_commit` 才真正落盘。`StagingRecord` 的结构：

```ts
interface StagingRecord {
  pending_id: string;
  card_id: string;
  _base_revision: string;      // 乐观锁基准：读取时的内容指纹
  changes: Record<string, any>;
}
```

`_base_revision` 是乐观锁的核心：`card_commit` 时会重新算当前文件的内容指纹，
**和 `_base_revision` 不一致就拒绝**（说明期间有人改过这张卡）。

`.staging/` 里堆积的文件说明有大量未提交的改动。这些不是垃圾——
直接清空等于丢掉别人做到一半的工作。但也没有工具会自动清理它们（`infohub/design-tradeoffs`
里说的「没有并发写保护」的另一面）。

排查「为什么我改的字段没生效」时，先看 `.staging/` 里有没有这张卡的 pending 记录。

## .quarantine collects what failed validation

两个不同来源都叫 quarantine，别混：

| 来源 | 产物 | 内容 |
| :-- | :-- | :-- |
| `card_import` 的 `on_invalid: quarantine` | 报告里的 `quarantine_file` | 校验失败的行 |
| `card_attach` 的 `on_missing: quarantine` | `inbox/attachments-quarantine.jsonl` | 匹配不到卡的附件 |

注意第二个写的是 **`inbox/` 而不是 `.quarantine/`**，且预演时文件名带 `.preview` 后缀：

```ts
quarantineFile = join('inbox', dryRun ? 'attachments-quarantine.preview.jsonl' : 'attachments-quarantine.jsonl');
```

**预演和真跑写不同文件**，这样预演的产物不会覆盖上一次真跑的结果。
`.quarantine/` 目录本身是更早的机制残留。

## .conflicts is a queue, not a log

当前为空——这不是没配过，而是**冲突都收敛完了**。

`migrate:conflicts` 用来回收已收敛的冲突记录。清空后 `status` 会从「冲突」退回「待核实」：

> 冲突清零不等于「有效」——值对不对只能由人确认，机器只把它退回待核实。

这句话是这一页最该记住的：**工具不会替你判断哪个值是对的**，它只负责让「还有未决冲突」
和「已经没有未决冲突」可区分。

## .cache and .backup are the only safe ones to delete

- `.cache/`（100 文件）：构建与检索的中间产物，删了会重建，只是慢一次。
- `.backup/`（1136 文件）：迁移脚本在动 `cards/` 之前做的快照，删了就失去回滚点。

其余四个目录删之前必须确认：`.staging/` 有未提交改动、`.trash/` 是唯一恢复源、
`.quarantine/` 可能是待补数据、`.conflicts/` 记录未收敛的冲突。

## The rule these directories encode

`cards/` 是**唯一真源**，但这六个目录说明真源之外必须有缓冲区：

```text
.staging/     写入前     两阶段提交
.quarantine/  校验后     不合格但不能丢
.conflicts/   合并后     需要人决定的
.trash/       删除后     可恢复
.backup/      迁移前     可回滚
.cache/       派生       可重建
```

它们全部在 git 忽略列表里，且**全部不是 Schema 的一部分**——
没有任何领域包字段指向它们。这是「派生结构不落盘」那条不变量的例外处理：
真正需要在写入路径上暂存的东西，放在卡片文件之外，而不是加字段进 frontmatter。
