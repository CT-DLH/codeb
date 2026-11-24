---
covers:
  - src/core/ingest.ts
updated: 2026-11-17
---

# Identity matching and field merging

`matchIdentity()` 的三步顺序是**结构性约束**而不是优化：第一步返回「有强标识就只走强标识」，第二步被 `!hasStrong` 门禁锁住。改这个顺序，「同名不同学号」会立刻被误并——这是实测过的 1872 行导入事故。

## identityKey: five normalization steps in fixed order

`identityKey()`（`src/core/ingest.ts:695-699`）是「同一实体」的唯一判据，`normalize.ts` 里的三个函数串联：

```text
asText(value).trim()          // 非字符串走 String(value)
  → toHalfWidth()             // [\uFF01-\uFF5E] 减 0xfee0；\u3000 → 空格
  → stripParenthetical()      // /[(（\[【][^)）\]】]*[)）\]】]/g 整体删除
  → normalizeText()           // 内部再 toHalfWidth + toLowerCase + 删标点
```

标点表原文：`/[\s，。；：、,.;:!?！？"'“”‘’（）()【】\[\]《》<>·—\-_/\\]+/g`。

效果：`张三（已毕业）` == `张三`；`2023***071` 的星号**不在**标点表里，所以遮蔽学号原样参与比较——这正是遮蔽学号不能当强标识的原因（`pitfalls` 里有对应条目）。对象值走 `normalizeText(JSON.stringify(value))`，数组则在 `sameListItem` 里逐项递归。

`sameIdentityValue(a,b)`（701-705）额外要求两侧归一化结果**都非空**：空值永不等于空值，否则所有缺字段的行会互相匹配。

## Step one: strong short-circuits per path

`matchIdentity`（721-747）先算 `hasStrong = identity.strong.some(path => !isBlankValue(readPath(fields, path)))`——注意这是「本行有没有强标识值」，不是「有没有命中」。

然后按 `identity.strong` 的**数组顺序**逐个试：某路径有值就筛 `usable` 里同路径归一化相等者，**命中即 return**。所以：

- 强标识数组的书写顺序 = 匹配优先级，第一个命中的路径决定 `match.path`（进而决定 `sameKey` 与 `strongMatch` 判定）。
- 某强标识有值但零命中时**继续试下一个**强标识，不会中止。

## Step two: weak only when the row has no strong value at all

门禁是 `if (!hasStrong && identity.weak.length > 0)`（737）。再叠加一层：`identity.weak.every(path => !isBlankValue(...))`——弱标识必须**全部齐全**才参与整体相等比较，缺一列就完全不试。

于是带强标识的行**永远不落到弱标识分支**，即使弱标识全等也不合并。这正是「姓名相同但学号不同」的安全边界：同名的那张卡会在建卡后由 `findClaimableCards` 并入新卡，而不是反过来把新材料并进旧卡。

## Step three: create

两个分支都 miss 才新建。此时 `prepared.prepared.card_id` 进 `taken`（1933），并把计划卡 push 进 `index.entries` 且带 `planned_row`（1946-1951），让同一文件后面的行能看见它——文件内重复靠这条实现。

## Why candidates[0] and what it costs

`matchIdentity` 返回**全部命中**（`candidates` 是数组），调用方在 1757 取 `candidates[0]`。候选顺序来自 `loadDomainIndex` → `listCardFiles` 的目录枚举顺序。

- 强标识命中多张：不静默合并，除非显式 `on_duplicate: 'merge'`，否则 `ambiguous` 进 review（1760-1775）。
- 弱标识命中多张：记 `ambiguous`，且 `duplicatePolicy !== 'keep_both'` 时进 review（1849-1859）；默认 `keep_both` 下反而继续往下走——会**新建**一张卡。

## findClaimableCards: the claimable-card bridge

`findClaimableCards`（750-765）找「只有弱标识的待认领卡」，条件三层：

1. `identity.weak.length === 0` → 返回 `[]`（没有弱标识就没有认领概念）。
2. 本行任一弱标识为空 → 返回 `[]`（认领要求本行弱标识齐全）。
3. 遍历 `index.entries`：排除 `excludeCardIds`；**候选卡不能有任何强标识值**（`strong.some(non-blank)` 为真即出局）；弱标识逐项 `sameIdentityValue` 全等。

与 `matchIdentity` 的 weak 分支只差第 3 条的「候选卡无强标识」——这正是「待认领」的定义。

落地在 `absorbDonors`（2062-2098）：建卡/更新后调用，`on_claim !== 'merge'` 或无强标识则直接返回。每个 donor 用 `mergeFields(current, {...record.frontmatter, card_id: undefined, domain: undefined}, 'fill_empty', ...)` 合并、正文追加、`sources` 加一条「并入待认领卡 X」、写盘、`moveToTrash(donor.file, donor.card_id)`、从 `index.entries` 移除。donor 是**循环处理**的（每并一张都重算 `withDerives`），所以链式认领也收敛。

## dedup fallback: only when the domain declares no identity

`const match = identity ? matchIdentity(...) : dedupMatch(...)`（1735）。`identity` 来自 `parseIdentity`，而该函数在 strong/weak/disambiguator/card_id_pattern/card_id_fallback **全空时返回 null**（`src/lib/schemas.ts:396-404`）——所以「只写了 `attachments`」的领域也算未声明。

`dedupMatch`（768-785）调 `findSimilarCards`，参数带 `title`/`aliases`/`source_ref`/`fields`，取前 **5** 个候选、过滤 `score >= 0.8`，再映射回 `IndexEntry`。`path` 记 `hits[0].matched_by ?? 'source_ref/title/alias'`。

扣分点：`dedupMatch` 只保留 `hits[0].matched_by` 作为整组的 `path`，却把多个候选都塞进 `candidates`——所以 `via==='dedup'` 且多候选时，`strongMatch` 判定用的是**第一个**候选的命中原因。

## applyPattern: every supported token

`applyPattern`（803-845）用 `/\{([^{}]+)\}/g` 逐个替换，token 先 `trim()`：

| token 形态 | 取值 | 缺值行为 |
| :-- | :-- | :-- |
| `{year}` | `year` 参数（= `collected_at` 前 4 位，`prepareCard:1137`） | 不会缺 |
| `{domain}` | 领域 id 原值（**不 sanitize**） | 不会缺 |
| `{hash:weak}` | `identity.weak` 上所有值的 `hashIdentityValues` | 值全空 → `missing` |
| `{hash:strong}` | `identity.strong` 同上 | 值全空 → `missing` |
| `{hash:<路径>}` | 任意单字段路径（`/^hash:(.+)$/` 兜底分支） | 值空 → `missing` |
| `{slug(<路径>)}` | `slugify(readPath(fields, 路径))` | 空 → `missing` |
| `{<字段路径>}` | `sanitizeSegment(readPath(fields, token))` | 空 → `missing` |

`slug()` 内层路径同样支持 `ext.xxx` 这类点分路径（走 `readPath`）。`token === 'hash:'` 这种空后缀由 `if (!source) { missing = true }` 拦住。

收尾（843-844）：`rendered.replace(/-{2,}/g,'-').replace(/^-+|-+$/g,'')`，然后 **`cleaned.length >= 3` 才返回**，否则 `null`。三字下限是防止 `{domain}` 单独渲染成过短、在文件系统里难辨认的 id。

`sanitizeSegment`（789-793）与 `slugify` 的差别值得记牢：前者只把 `/[\ /:*?"<>|\s]+/`（含反斜杠、正斜杠、Windows 非法字符）换成 `-`，**保留中文与大小写**；后者 `toHalfWidth().toLowerCase()` + `/[^\p{L}\p{N}]+/gu → '-'`，**保留中文但小写**，且默认 `maxLength = 32`（超长先截断再去尾 `-`）。

## hashIdentityValues: sha1, 8 hex chars

```text
sha1( values.map(identityKey).join('|') ).digest('hex').slice(0, 8)
```

八个十六进制字符，用 `identityKey` 归一化后再拼——所以 id 对「全角/半角、括号注释、空白标点、大小写」不敏感，对**值本身**敏感。绝不能用随机数或时间戳：那会让幂等失效，重复导入重复建卡。

## buildCardId: pattern → fallback → hash → slug

顺序（847-875）：`[cardIdPattern, cardIdFallback]` 过滤空串后**依次尝试**，任一 `applyPattern` 返回非 null 即用。

三条兜底分支，按 `identity` 是否为 null 分叉：

- **未声明 identity**（`!identity`，860-864）→ 历史口径：`slugify(title || object_type || 'card')`，拼 `${domain}-${year}-${slug}`；连 slug 都空则 `${domain}-${year}-${Date.now().toString(36)}`。
- **声明了 identity 但两个模板都没成**（865-874）：先取 `[strong, weak]` 里第一组有值的（**strong 优先**）；这组也空则退到 `[title]`；有值就 `${domain}-${year}-${hashIdentityValues(...)}`；仍无值则 slug → 再退到时间戳。

注意「`object_type` 参与历史 slug」这条：同一领域里两份没有 title 的材料，只要 `object_type` 相同就会撞 id，靠 `uniqueCardId` 拆开。

## uniqueCardId: -2, -3, never -1

`uniqueCardId`（877-888）`busy = existsSync(domainDir/<id>.md) || taken?.has(id)`，`taken` 是本批已分配的 id 集合。冲突时从 **`n = 2`** 起试 `${baseId}-2`、`-3`……**没有 `-1`**。所以第一次重名是 `student-x-2`，不是 `-1`。

## mergeFields: the decision ladder

`mergeFields`（985-1080）返回 `{frontmatter, changed, conflicts}`，逐条按 `flatten(incoming)` 的**叶子路径**处理，判定阶梯严格按此顺序：

1. `SERVER_FIELDS`（`card_id`/`domain`/`collected_at`/`created_at`/`edited_at`）→ 跳过。判的是完整路径字符串，所以 `ext.card_id` 不会被误跳。
2. `isBlankValue(value)` → 跳过。**且此时还没进 `comparedPaths`**——空白值不构成「比过」，旧冲突不会被销案。
3. **`UNION_ROOTS`**（`sources`、`aliases`、`tags`、`import_conflicts`、`gaps`）→ 无论 `merge_rule` 是什么都取并集，只要新增了至少 1 项就写。判的是 `path.split('.')[0]`，所以 `sources.0.file` 这种摊平路径也会被并到 `sources` 根。
4. **`ownedSet.has(path)`**（来自 `_overwrite_fields`）→ 值真变了就覆盖，绕过 `fill_empty`。等价判据是 `normalizeRef(current) === normalizeRef(value) || identityKey(current) === identityKey(value)`，都没变就**逐字节不动**（保证重跑幂等）。
5. `isBlankValue(current)` 或 `path === 'title' && isPlaceholderTitle(current)` → 直接写。
6. 归一化后相等 → `continue`（不算 changed，也不记冲突）。
7. `rule === 'overwrite'` → 直接写。
8. **两侧都是数组** → 取并集，新增 0 项则 `continue`；否则写 + changed。
9. 其余（标量不相等）→ `conflicts.push(`${path}: 保留「${current}」，新值「${value}」（${provenance}）`)`。

第 8 条是「数组并集不是冲突」的全部理由：两份材料各给几项时**都保留**是可行解；标量做不到两全，只能交人工。

## Placeholder titles are treated as empty

`isPlaceholderTitle`（979-983）：空串、或以 `未命名` 开头、或以 `-待定题目` 结尾 → 视为空。

两个生产者：`placeholderTitle()`（1431-1442，格式 `${hints.join('-')}-待定题目`，hint 取 weak+disambiguator 前两个非 title 字段，都没有则 `第N行`），以及领域包模板拼出的 `未命名…`。

不这么做，后续带姓名的材料会被自己的旧占位标题挡住并记一条假冲突——实测覆盖掉 426 张已命名卡的反向事故（1880-1881）则是另一半：`titleDerived` 为真时 merge 前 `delete fields.title`，占位标题**只用于建卡**。

## conflict recycling overwrites by field path

`conflictFieldPath`（947-950）用 `/^(\S+?): 保留「/` 取冲突行的**路径前缀**，不解析「保留/新值」里的内容——值里带引号或花括号也不影响判键。解析不出来（历史手写格式）返回 `null`。

回收算法（1061-1078）：

```text
before = 现有 import_conflicts
kept   = before 里 path === null 或 !comparedPaths.has(path) 的行
next   = [...kept, ...本轮新冲突]
```

即**本轮真正比过的路径按新结果覆盖**，没比过的原样保留——「后一份材料不许替前一份销案」。

`comparedPaths` 只在第 2 步之后才 `add`，所以**这一行没该字段、或该字段是空值**时，旧冲突一定留到下一轮。

`status` 的状态机只有两条边：

- `next.length === 0` → `delete merged.import_conflicts`，且若 `status === '冲突'` 改成 **`待核实`**。注释写明理由：冲突清零不等于「有效」，值对不对只能由人确认，机器只退回待核实。
- `conflicts.length > 0` → `merged.status = '冲突'`。只在本轮**真的产生**新冲突时置位，清理不置位。

`changed.push('import_conflicts')` 只在列表内容实际变化时发生（长度或逐行比较），避免无意义的 `edited_at` 刷新。

## unionListSources dedupes by file + row

`sources` 的并集不能走普通数组语义：同一份材料同一行的多次写入必须合成**一条**，`fields` 取并集（921-938）。判等键是 `asText(item.file) === entry.file && asText(item.row) === entry.row`。不同行、不同文件各留一条，于是「谁写了哪个字段」可回溯。

## owned vs clear: two different forbidden sets

`_clear` 与 `_overwrite_fields` 的禁区**故意不同**（1552-1584）：

| | 禁区 |
| :-- | :-- |
| `_clear`（forbiddenClear） | title、domain、card_id、object_type、collected_at、created_at、edited_at、sources、status、confidence + strong + weak + **disambiguator** |
| `_overwrite_fields`（forbiddenOverwrite） | 同上但**不含 disambiguator** |

理由写在注释里：disambiguator 不参与判重，让上游刷新它不会并错卡（article 的 `ext.collector_key` 正是这种）。两者都额外拒绝 `_` 开头与含 `..` 的路径。

命中禁区时该行进 `invalid_field`，并按 `on_invalid` 转 `quarantine` 或 `reject`——注意是**整行**丢弃，不是只丢那个非法路径。

## deletePath runs before merge

`_clear` 在合并前作用于**旧卡片副本**（2159-2162）：`deletePath(base, path)` 返回被删的旧值，`!== undefined` 时 `clearedFields++`。所以修正行可以「清掉错误旧值 + 填入新值」一次完成。`deletePath`（960-973）遇到数组中间节点或不存在路径返回 `undefined`，不抛错。
