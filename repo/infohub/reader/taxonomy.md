---
covers:
  - src/lib/taxonomy/
updated: 2026-11-17
---

# Taxonomy: pure tree core and its loader

`src/lib/taxonomy/` 是两套树里**不影响字段的那一套**：`tree-core.ts`（零依赖纯函数）管「卡片讲什么」，`domains/*.yaml` 的 `extends` 管「卡片有哪些字段」。两边互不引用，`domain_id` 不许当分类标签用。

## Nodes are single-segment IDs, hierarchy lives in parent

`_taxonomy/<namespace>.yaml` 的格式只有一条硬约束：

```yaml
namespace: discipline      # 必须是三选一
label: 学科
nodes:
  - id: discipline:cs      # <namespace>:<单段 slug>
    label: 计算机科学
    legacy_id: discipline:cs   # 旧点分 ID，仅迁移映射
    kind: tree                 # tree | enum，缺省按 tree
    order: 10                  # 只影响同级展示顺序
  - id: discipline:ai
    label: 人工智能
    parent: discipline:cs      # 完整新 ID，不是相对名
    kind: tree
    order: 10
```

`parseTagId(id)` 是唯一的解析入口，非法的返回 `null` 而不是抛错。五条拒绝条件：`typeof !== 'string'`、`trim()` 后为空、没有冒号、`colon <= 0`、head 不在 `NAMESPACES = ['discipline','org','topic']` 里、slug 为空 / 含首尾空白 / **含点** / **含第二个冒号**。

「slug 不含点」这条是去层级化改造留下的硬边界：`discipline:cs.ai` 这种旧式 ID 一律判非法，层级完全靠 `parent` 表达。所以把 `nlp` 从 `ai` 挪到 `cs` 下只改一行 `parent`，卡片里一个字都不用动。

## Three data shapes, one direction of derivation

| 类型 | 字段 | 谁用 |
| :-- | :-- | :-- |
| `TaxonomyNodeInput` | `id` / `label` / `parent?` / `legacy_id?` / `order?` / `kind?` | YAML → 索引 |
| `TaxonomyIndex` | `nodes` + `byId` + `parentOf` + `childrenOf` + `legacyToId` | 匹配与筛选 |
| `TaxonomyTree` | `roots` + `orphans` + `byId` | 只用于展示 |

`TaxonomyTree` 与 `TaxonomyIndex` 是**两份产物**，不是一个对象的两种视图——索引做匹配（需要 `parentOf` 上溯、`childrenOf` 下展），树做渲染。`loadTaxonomy()` 只建索引，全仓没有任何地方调 `buildTree()`。

## createIndex: two passes, orphans recorded but not linked

```ts
// 第一遍：去重 + 建空 childrenOf
for (const node of nodes) { if (byId.has(node.id)) continue; ... childrenOf.set(node.id, []); }
// 第二遍：只在父存在时回填
for (const node of byId.values()) { const p = node.parent; if (p && byId.has(p)) childrenOf.get(p)!.push(node.id); }
```

三个刻意的行为：

- **重复 ID 只保留第一条**，第二条静默丢弃（由 `validateNodes` 报 `duplicate_id`）。
- **`parent` 指向不存在的节点时仍然记进 `parentOf`**，但不回填 `childrenOf` —— 上溯/下展会在那里自然终止，保证「坏数据不抛异常」。
- **`legacyToId` 也去重**，第一个登记的赢。它是迁移脚本的幂等映射真源，二义就会把卡迁到两处。

## isAncestor walks parent, never compares strings

`isAncestor(ancestorId, tagId, index)` 的三条前置检查：两个 ID 都必须能 `parseTagId`、`namespace` 必须相同、**相等不算祖先**。然后从 `tagId` 沿 `parentOf` 上溯，带 `visited` 防环：

```ts
let cur = index.parentOf.get(tag.id) ?? null;
while (cur && !visited.has(cur)) { if (cur === ancestor.id) return true; visited.add(cur); cur = index.parentOf.get(cur) ?? null; }
```

不用字符串前缀是因为去层级化后 ID 是单段：`ai` 与 `nlp` 前缀毫无关系，只有 `parent` 链才表达包含。`coversTag(selectedId, tagId, index)` 是它的门面（相等或祖先），`coversWithIndex` 是内部版本。

## matchesAny returns false on empty — filterCards decides

这是全文件最容易误用的语义：

```ts
matchesAny(cardTags, selectedTags, index)  // 空选中 → false
```

注释写得很明确：「没有选」不等于「全选」，**是否放行由 `filterCards` 决定**——这样 UI 与脚本对空数组的理解不会出现两种。`filterCards(cards, selectedTags, index, mode='or')` 的行为：

- `selectedTags` 为空 → `return [...cards]`（原样返回，浅拷贝）。
- 选中项全部非法 → `return []`。
- `'or'` 任一命中；`'and'` 每个所选都必须命中（**同一张卡的父子标签可以分别满足两个所选**）。
- 按 `card_id` 去重（一张卡同时挂 `ai` 和 `nlp`，筛 `cs` 只出一次）；**没有 `card_id` 的卡不参与去重**——宁可多一条，也不能因为缺 ID 被悄悄吞掉。
- 保持输入顺序（列表顺序是上游排好的，筛选不该顺手改序）。

## buildTree: cycles are flattened into orphans, not recursed

`buildTree(nodes)` 用三次线性扫描而不是递归：

1. 建 `byId`（重复 ID 只留第一条），`attached` 集合防止同一节点被挂到两个父下。
2. 挂接：`parent` 不存在 → 进 `orphans`；存在 → `parent.children.push(node)`。
3. **环检测不是在建树时做的**——对每个节点独立上溯，`seen` 保护，能走到「没有 parent 的节点」或「parent 不存在」就算到达根；走不到的就是环成员。

环的处理是**平铺**而不是移走：`poisoned` 集合里的节点 `children = []` 后全部进 `orphans`。理由写在注释里：只把环成员挪走、保留彼此的 `children` 指针，返回结构里仍然有环，调用方只要递归渲染就爆栈。平铺是唯一「一定能画出树」的形态。

`sortSiblings()` 递归按 `order` 排序，`orderKey()` 把缺失的 `order` 映射成 `Number.MAX_SAFE_INTEGER` —— **没写 order 的排在显式排序之后**，手写的节点顺序不该被「漏填字段」顶到最前面。

## validateNodes returns a list, never throws

七种 `TaxonomyProblem.code`，一次全报出来（注释：一份 taxonomy 有 5 处问题时调用方应当一次看到 5 条，而不是修一条跑一次）：

| code | 触发 |
| :-- | :-- |
| `invalid_namespace` | head 不在三选一里 |
| `invalid_id` | 缺冒号 / slug 为空或带空白 / parent 不是合法 ID |
| `id_has_dot` | ID 含点（层级该写在 parent 里） |
| `duplicate_id` | 重复定义，detail 带首次出现的序号 |
| `duplicate_legacy_id` | 两个节点声称来自同一个旧 ID |
| `orphan` | parent 不在全集里 |
| `cycle` | 按排序后的成员集合做键，同一个环只报一次 |
| `enum_has_children` | `kind: enum` 却有子节点（语义是「并列」，有下挂说明判据用错） |

`validateNodes` 先收集全量 ID 再逐条校验（`parent` 可能写在子节点之后），环检测用「按起点逐个上溯 + `chain.indexOf`」而不是建图——同一个环会被多个起点走到，靠 `reportedCycles` 去重。

## countByTag: total must dedupe per card

`countByTag(cards, nodes)` 给每个节点两个数：`self`（恰好挂这个标签）与 `total`（自身 + 全部后代覆盖的卡数）。

关键实现：**先把「这张卡覆盖到的节点」收成 `Set` 再计数**，而不是把每个标签的祖先链长度相加。后者在多层重复标注时会翻倍——一张卡同时挂 `ai` 和 `nlp`，`cs` 的子树合计只能是 1。上溯用 `visited` 防环（校验会报，但统计不能因此卡死）。

这个函数全仓只有测试脚本调用，页面上的分面计数走 `card-store` 的倒排索引，不走它。

## loader.ts: read three files, cache once, never invalidate

```ts
const TAXONOMY_FILES = ['discipline.yaml','org.yaml','topic.yaml'] as const;
let cached: Taxonomy | null = null;

export function loadTaxonomy(): Taxonomy {
  if (cached) return cached;
  const nodes = TAXONOMY_FILES.flatMap(readNodes);
  const index = createIndex(nodes);
  const problems = validateNodes(nodes);
  cached = { index, nodes, problems };
  return cached;
}
```

- **进程内缓存一份，永不失效**。注释的理由：`_taxonomy` 是静态文件，运行期不会变。所以改了 YAML **必须重启 dev server**——`domains/` 有 watcher 与 mtime 签名，`_taxonomy/` 没有。
- `readNodes()` 逐字段归一化，非法 `kind` 归成 `undefined`（等价 tree），非 number 的 `order` 也归 `undefined`。
- 加载器**不抛错**，`problems` 一并返回由调用方定严重程度——延续「坏数据不抛异常」的契约。`taxonomy-test.ts` 要求零问题，页面可以只告警。
- 三个便捷函数都接受可选 `tax` 参数（默认 `loadTaxonomy()`），方便测试传入夹具：`ancestorsOf(id)` 返回**从父到根**（不含自身，未知 ID 返回 `[]`）；`descendantsOf(id)` 用显式栈做 DFS（非递归，防深树爆栈）；`labelOf(id)` / `resolveLegacyId(legacyId)`。

`__PROJECT_ROOT__` 这里有一处单独的 `declare const`：`app.d.ts` 里的同名声明带 `export {}`，是模块级的、没暴露成全局，所以 loader 自己补一条让 `svelte-check` 不报错。运行时仍靠 `typeof ... !== 'undefined'` 安全回退。

## How the aggregate pages actually use it

只有**一处**生产代码消费 taxonomy：`card-store.ts` 的 `idsForValues()`。

```ts
for (const value of values) {
  const set = byCol.get(value); if (set) for (const id of set) out.add(id);
  for (const desc of descendantsOf(value)) { const dset = byCol.get(desc); if (dset) ... }
}
```

这是「选中父节点时把后代 ID 也展开」的全部实现——叶子 / 非树节点 `descendantsOf` 返回 `[]`，所以精确值筛选行为与改造前逐字一致。现有的中文自由词标签（`tags: ["机器学习"]`）全部走这条空路径，taxonomy 目前只是**可选增强**，不是必由之路。

值得记下的后果：分面选项本身来自倒排里的**字面值**，所以筛选器里看到的是 `discipline:cs` 这样的原始 ID，中文名要靠 `plan.valueLabels` 映射——而 `valueLabels` 来自领域包字段的 `value_labels`，**不是** taxonomy 的 `label`。两者没接上，这是当前 UI 上看不到「计算机科学」的原因。

## Current data

`_taxonomy/` 只有三个文件，总计 34 个节点：

| namespace | 文件 | 节点 | kind |
| :-- | :-- | --: | :-- |
| `discipline` | `discipline.yaml` | 19 | 全部 `tree`，5 个根（cs / math / physics / humanities） |
| `org` | `org.yaml` | 8 | 全部 `tree`，4 个根（hit / pku / thu / cas） |
| `topic` | `topic.yaml` | 7 | 全部 `enum`，**没有 parent、没有子节点** |

`topic` 全 enum 是刻意的：方法之间是并列关系（「LLM 包含强化学习」不成立），强行造子只会得到一棵每年都要重排的假树。`discipline` 里 `cv` 与 `ai` 平级而不是挂在 `ai` 下，也是同一条判据（CV 是平行分支）。

`legacy_id` 全部保留旧点分 ID（`discipline:cs.ai.nlp`），只给 `migrate-tag-ids.ts` 做幂等映射，不参与树结构。
