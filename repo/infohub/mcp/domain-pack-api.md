---
covers:
  - src/mcp/tools/domain_create.ts
  - src/mcp/tools/domain_update.ts
  - src/mcp/lib/schema-loader.ts
  - src/mcp/lib/field-spec.ts
updated: 2026-11-17
---

# Domain pack API: create vs patch

`domain_create` 是**整份 YAML 重写**（PUT），`domain_update` 是**只动传入子键的 PATCH**。
两者的校验深度也不同：create 只查「新包自己能不能被加载」，update 还要查「这次改动引用的路径在不在」。
手改 YAML 会同时绕过这两层，这是唯一被禁止的路径（`_base.yaml` 除外，它没有工具入口）。

## domain_create writes a whole file, then proves it loads

写入 `domains/<domain_id>.yaml`，键序固定：`domain_id / name / extends / abstract? / object_types / identity? / dedup_key? / ext_fields / summary_columns`。

五道前置检查，全部 `isError` 且不写盘：

1. `DOMAIN_ID_RE = /^[a-z0-9][a-z0-9_-]{0,63}$/` 且不能等于 `base`。下划线合法（`info_student` 这类三卡制前缀要用它）。
2. `abstract !== true` 时 `object_types` 不能为空——**只有抽象父包允许空**（它不落卡）。
3. `extends`（默认 `_base`）必须存在于 `listAllDomainIds()`（不含 `_base` 自身，所以 `_base` 单独放行）。
4. 文件已存在且没传 `overwrite:true` → 拒绝。
5. `ext_fields` 过 `fieldSpecSchema` 元 Schema（见下节）。

`identity` 另有两条硬校验：

- `strong` 与 `weak` 至少一个非空（只有 `disambiguator` 或只有 `card_id_pattern` 不算）。
- 每个引用路径必须能解析：`ext.x` 查「父包继承的 ext + 本包刚声明的 ext」，非 `ext.` 前缀查 `_base.base_fields`。
  取路径的**首段**（`ext.guardian.phone` → `guardian`），所以只要顶层字段声明了，子路径就不再逐级校验。

写完立刻 `clearSchemaCache()` + `loadDomainSchema(domain_id)` 做**往返验证**：能构造出 Zod schema 才算成功。
抛错时 `rmSync(file, { force: true })` 清理现场，**不留半成品**。这是 create 与 update 最大的行为差别——
create 失败是「文件不存在」，update 失败是「文件被还原」。

`summary_columns` 默认 `['title','summary','last_verified']`，`object_types` / `dedup_key` / `identity` 不传就不写这几个键。
返回 `{created, domain_id, name, extends, abstract, object_types, dedup_key, identity, inherited_ext_fields, ext_field_count, file}`。

## domain_update patches nodes, keeps comments

用 `parseDocument` 读 → `doc.setIn`/`doc.deleteIn`/`doc.set`/`doc.delete` 改 → `doc.toString()` 写回。
**注释和未改动节点的排版都保留**，这是选 `parseDocument` 而不是 `parse` + `stringify` 的原因。

十二个可选键，全为 `undefined` 时直接 `isError: '没有要修改的内容：至少传 … 之一'`：

| 参数 | 语义 | 空值行为 |
| :-- | :-- | :-- |
| `extends` | 改父包 | `'_base'` → `doc.delete('extends')`（退回通用根） |
| `add_object_types` | 追加类型 | 已存在的只警告并忽略 |
| `remove_object_types` | 删除类型 | 不存在的只警告并忽略；**删空 → isError** |
| `add_ext_fields` | 新增字段 | 字段已存在 / 继承自父包 → 都是 error（不是警告） |
| `update_ext_fields` | 改字段子键 | 字段必须存在（本包或继承）；空 patch → error |
| `remove_ext_fields` | 删字段 | 不存在 / 继承自父包 → error |
| `summary_columns` | 重设列 | `[]` → isError |
| `dedup_key` | 重设去重键 | `[]` → `doc.delete('dedup_key')` |
| `identity` | 重设标识位 | `{}` 或全空 → `doc.delete('identity')` |
| `attachments` | 附件能力 | `{}` → `doc.delete('attachments')` |
| `imports` | 导入默认策略 | `{}` → `doc.delete('imports')`；`strategies: {}` 单独删掉 strategies |
| `domain_id` | 必填，须已存在 | 不存在 → isError |

### Extend cycles are checked before writing

`extends` 指向自己 → 立即拒绝。父包文件不存在 → 拒绝。环检测沿 `domainExtendsMap()`（子→父的现存映射）
从**新父包**往上走，`seen` 里预置了 `domain_id` 自身，遇到重复节点报 `extends 会成环: a → b → a`。
已有坏链（父包本身指向一个不存在的 id）用 `if (!up) break` 兜住，不会把这次修改卡死。

父包不是抽象包时给警告但**照写**：`extends: <可落卡领域>` 会让两张表共享同一套字段。

### Field operations refuse ambiguity rather than guess

`add_ext_fields` 对「已存在」和「继承自父包」都是 error，指向 `update_ext_fields`；`remove_ext_fields` 对继承字段
报 `字段继承自父包 X，不能在本包删除（要改请改父包）`。这是刻意的：继承字段的子域覆盖必须写成**完整定义**，
而不是一个补丁子键。

`update_ext_fields` 在覆盖继承字段时，写的是 `{...inheritedExt[key], ...patch}` 的**合并结果**，
不是只写 patch（否则子包 YAML 里只剩一个孤零零的子键，看起来像缺 type）。

### Validation: meta-schema in, round-trip out

三层校验，全部在写盘前：

1. **`fieldSpecSchema`（`src/mcp/lib/field-spec.ts`）= 元 Schema**，校验「定义字段的字段」。
   `z.lazy` 递归，`.strict()` 拒绝任何未声明属性。`type` 是必填且只能是
   `string/number/boolean/array/object`；`derive` 是 `{from, pattern, mode?}` 且 `.strict()`，
   `pattern` 在**声明时**就 `new RegExp()` 试编译（写错正则当场拒绝，而不是让每条卡都「提取不到」）。
   `add_ext_fields` 走完整的 `fieldSpecSchema`；`update_ext_fields` 校验的是 `{原定义, ...patch}` 的合并结果。
2. **路径存在性**（只有警告，不阻断）：`dedup_key`、`summary_columns`、`identity.strong/weak/disambiguator`、
   `identity.card_id_pattern` 里的 `{…}` token、`attachments.match_by`。
   判定用 `isDeclaredPath()`：`ext.` 前缀查 `nextExt`（本次改完后的 ext）或父包继承集，其余查
   `loadDomainSpec(domain_id).baseFields`（含继承链）。
3. **往返验证**：写盘后 `clearSchemaCache()` + `loadDomainSchema(domain_id)`，抛错则把原始 `raw` 写回并
   `clearSchemaCache()`，返回 `领域包往返验证失败，已还原`。还原本身失败时只保留原始错误。

`card_id_pattern` 的 token 校验比 create 细：`{year}` / `{domain}` 放行；`{hash:weak}` / `{hash:strong}` 检查对应
列表非空；`{hash:<路径>}` 与 `{slug(<路径>)}` 检查路径已声明，否则警告
`生成的 ID 会走哈希兜底`。**注意这是警告不是错误**——写错模板不会拒绝，只会在生成 id 时静默走兜底。

## What deleting an object type actually does

```
nextTypes = own object_types（本包为空则用继承来的）
→ 逐个 remove：不存在就 warnings.push('不存在，忽略')
→ nextTypes 空 且 不是 abstract → fail('object_types 不能为空…')
→ 对每个真的删掉的类型，扫 listCardFiles(domain_id) 统计 frontmatter.object_type
   count > 0 → warnings.push('仍有 N 张卡片使用该类型（卡片不会删，但卡片校验会提示类型未声明）')
```

三条行为边界：

- **只警告，不阻断。** 卡片不会被改、不会被删，`object_type` 值原样留在卡上；只是此后 `prepareCard` 的
  白名单校验会拒绝**新写入**该类型。
- **占用统计走 `listCardFiles(domain_id)`**，也就是 `domainDir(domain)` 这一个目录。给抽象父包删类型时，
  卡片都在子域目录里，统计恒为 0——**抽象包上的占用警告永远不出现**。
- **子包没写 `object_types` 时沿用继承值**（`ownTypes.length > 0 ? ownTypes : loadDomainSpec().objectTypes`），
  否则「只删一个类型」会把父包整列覆盖成只剩一项。副作用：这个继承值是在**改父包之前**取的，
  同一次调用里既改 `extends` 又删类型时，基数来自旧父包。

`add_object_types` 的项会 trim + 去重 + 丢空串；删除同理。

## attachments: the shape card_attach depends on

`domain_update` 组装 `attachments` 时做了四处规范化，与 `parseAttachments`（读侧）严格对齐：

- `accept`：trim → 小写 → 补前导点（`docx` → `.docx`）→ 去重。不在 `SUPPORTED_EXT`（`.docx` / `.pdf`）里的只警告，
  提示这类文件会进报告的 `unsupported`。
- `parser` 必须在 `PARSERS` 的 id 里（`task-book` / `course-syllabus` / `pdf-text` / `generic-docx`），否则 `isError`。
- `body_section_map` **是合并而不是替换**：`{...currentMap, ...sectionMap}`，键或值为空的映射被丢掉并警告。
- `enabled` 只在显式 `false` 时警告：`card_attach 对该领域会直接报错而不是跳过`。
  实际链路是 `meta.attachments` 非 null 就过工具层检查，再在 `attachDirectory` 里抛 `enabled=false，不接受附件导入`。

`match_by` 为空且领域没有 `identity.weak` → 警告 `card_attach 会因为没有关联键而报错`。
`match_by` 里的路径除了 `title` 之外都要是已声明的 ext 路径（否则只警告，附件本来就提供不了这个字段）。

## PATCH merges, and where the merge is shallow

`imports.strategies` 是**逐键 patch**（`{...currentStrategies, ...只写非 undefined 的键}`），其余键整体替换。
`identity` 是**整体替换**：传了就整套重写，没传的列表变空数组（不是保留旧值），
所以只想改 `card_id_pattern` 时也得把 `strong`/`weak` 一起带上，否则它们会被清空并触发
`identity 至少要声明 strong 或 weak 之一`。

改父包会顺带算影响面：`collectChildren()` 递归收集所有后代，`impact[]` 每项 `{domain, cards}`（`cards` 是该域卡片数），
并追加一条警告 `继承者同步生效：…`。这条不受「改动是否真的影响字段」约束——改任何东西都会算一遍。
