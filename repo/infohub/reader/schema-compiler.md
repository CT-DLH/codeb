---
covers:
  - src/lib/schemas.ts
updated: 2026-11-17
---

# Schema compiler: YAML packs to Zod

`src/lib/schemas.ts` 把 `domains/*.yaml` 递归编译成 Zod schema，并负责 `extends` 继承链的合并与缓存——它是「加字段不改前端代码」这条架构决定在代码上的全部实现。

## The inheritance chain resolves leaf to root

`domainInheritanceIds(domainId)` 返回**根在前、叶在后**的完整链（`['_base','_info','info_student']`），实现是一个不带递归的 `while`：

```ts
let current = domainId;
while (current && current !== '_base') {
  if (seen.has(current)) throw new Error(`extends 成环: ${...}`);
  seen.add(current); ids.push(current);
  current = readYaml(`<DOMAINS_DIR>/${current}.yaml`).extends || '_base';
}
ids.push('_base'); ids.reverse();
```

四个刻意的取舍：

- **单父包**。`extends` 只读一个字符串，不做数组归一化——`extends: [person, _info]` 会直接失效（`pitfalls` 里记着这条）。项目的应对是把 `person` 的字段并入 `_info`，原 `person` 包保留不删以免断引用。
- **`_base` 永远是根**，且可以被重复写到任意层（`extends: _base` 与写空等价）。
- **环当场抛错**，不是返回部分结果——构建期就会炸，代价是这个包整个不可用。
- **深度不设上限**，靠 `seen` 保证有限终止；链深天然被 `domains/` 下包数封顶。

## mergeChain: two merge policies, deliberately different

字段与整体口径不能用同一条规则合并，这是全文件最重要的一条判断：

| 键 | 策略 |
| :-- | :-- |
| `base_fields` / `ext_fields` | **逐键 Object.assign**，子类同名覆盖父类（复用字段就是这个用途） |
| `identity` / `dedup_key` / `summary_columns` / `object_types` / `attachments` / `imports` | **整体口径**：叶子没写（`== null` 或空数组）才逐层往父找，第一个非空的整段继承 |

理由写在注释里：`identity.strong` 一个来自父、一个来自子，拼出来的是**第三种判定规则**，比没有继承更危险。`merged.domain_id` 强制取叶子的 `domain_id ?? domainId`。

`chainSignature(ids)` = 每个包 `${id}:${statSync(mtimeMs)}` 或 `${id}:missing`，拼成串。**缓存键是整条链的 mtime**：改父包（`_info.yaml`）时子包文件没变，只看叶子 mtime 会拿到脏数据。

`clearSchemaCache(domainId?)` 是给「领域包写盘之后」用的，注释直说：漏一处就会「改完 YAML 刷新没反应」。而 `card-store` 的表缓存另有 `signature` 兜底，所以手工改 YAML 也能生效——只是慢一拍。

## The recursive conversion is 30 lines

`buildZodFromSpec(spec)` 是纯递归，**不硬编码任何字段名**：

```
string    → z.string()
number    → z.number()
boolean   → z.boolean()
array     → z.array(buildZodFromSpec(spec.item ?? {type:'string'}))
object    → z.object(buildShape(spec.fields ?? {}))
其他      → throw new Error(`[schemas] 未知字段类型: ${spec.type}`)
```

三条后处理，顺序固定：

1. `spec.enum?.length > 0` → **整个结果被替换**成 `z.enum(spec.enum)`。注意这是替换而非收窄：`type: number` + `enum` 会得到 `z.enum`（值必须是字符串），`array` + `enum` 也一样。这是个真实存在的边界，领域包里没这么写过才没暴露。
2. `spec.required === false` → `.optional()`。
3. `required` 缺省或 `true` → **必填**。这是容易踩的一条：`{type: string}` 不带 `required: false` 就是必填。

`buildShape(fields)` 就是 `Object.fromEntries` 逐键调 `buildZodFromSpec`。

`z.object(spec.fields)` 默认 strip 未声明键——`object` 类型的嵌套子字段**没有 passthrough**。所以「未声明字段放行」只在顶层与 `ext` 成立，嵌套 object 里多写一个键会被静默删掉。

## Why undeclared fields pass through

`loadDomainSchema(domainId)` 的组装方式：

```ts
z.object({ ...baseShape, ext: extSchema.optional() }).passthrough()
```

其中 `extSchema` 是 `z.object(extShape).catchall(z.unknown())`；`extFields` 为空时退回 `z.record(z.string(), z.unknown())`。

三层放行各有各的位置：

- **顶层 `.passthrough()`** —— `ext_labels`、`body` 这些前端附加键不会被拒。
- **`ext` 的 `.catchall(z.unknown())`** —— Agent 随手加的 `ext.临时备注` 保留。
- **`ext` 整体 `.optional()`** —— 没有 ext 的卡也合法。

理由（`design-tradeoffs`）：领域包是「建议清单」不是「合同」。代价是结构完整性，这是有意识放弃的——它是检索系统，不是知识管理系统。

`collectUnknownFields(domainId, data)` 负责把「未声明」变成**警告而非错误**：`INTERNAL_KEYS = {'ext','body','ext_labels'}` 不算未声明，顶层报 `顶层.<key>`、ext 里报 `ext.<key>`。`loadDomainSpec` 抛错时返回 `[]`（宁可少一条警告，不让构建炸掉）。

## What loadDomain* actually returns

| 函数 | 返回 | 调用方 |
| :-- | :-- | :-- |
| `loadDomainMeta` | `{id, name, objectTypes, summaryColumns, dedupKey, identity, attachments, importStrategies}` | 导航、首页、`domain_update` |
| `loadDomainSpec` | 加上 `baseFields` / `extFields` 的原始 `FieldSpec` 字典 | `card-store` 的列规划、`sensitive` 的路径扫描 |
| `loadDomainBaseShape` / `loadDomainExtShape` | 两份 Zod shape | `loadDomainSchema`、MCP 校验 |
| `loadDomainSchema` | 完整卡片 schema | `build:data`、写入通道 |

`loadDomainExtShape` 特意包含从父包继承来的字段，注释写了原因：否则**继承来的字段会被校验拒写**。

## The three sub-parsers normalize to camelCase

领域包 YAML 用 `snake_case`，运行期配置用 `camelCase`，转换层是三个手写函数，都是「宽松取值 + 默认值」风格：

- `parseIdentity(raw)` —— `strong` / `weak` / `disambiguator` 全用同一个 `list()`（`Array.isArray` → `String` → `trim` → 过滤空串）。`card_id_pattern` / `card_id_fallback` 只有 `trim()` 后非空才带上。**五个字段全空则返回 `null`**（不是一个空对象）。
- `parseAttachments(raw)` —— `enabled: section.enabled !== false`（默认开）；`matchBy` 缺省时调用方回退到 `identity.weak`；`onMissing` / `onAmbiguous` 用白名单反选，非法值一律回落到安全侧（`quarantine` / `review`），注释说明理由：挂错一张卡比挂不上更难发现。`sectionMap` 来自 `body_section_map`。
- `parseImportStrategies(raw)` —— 读 `imports.strategies`，五个键各自用 `IMPORT_ENUMS` 白名单过滤，非法值**静默丢弃**（不报错），全空返回 `null`。

反向的 `attachmentsForApi` / `importsForApi` 把 camelCase 转回 `snake_case`，注释强调「照着抄就能写回 `domain_update`」——这是往返验证（写→读→写）能成立的前提。

## Enumeration: two functions, one line apart

- `listAllDomainIds()` —— `domains/*.yaml` 去掉 `_base.yaml`，排序。**包含 `_` 开头与 `abstract`**。
- `listDomainIds()` —— 再 `.filter(id => !isAbstractDomain(id))`。

`isAbstractDomain` 每次都 `readYaml` + 判断 `abstract === true`，**没有缓存**；`domainExtendsMap()` 同理，遍历全部包读 `extends`，跳过 `_base`。

注释里记了一次真实回归（2026-11-07 修）：早先 `listAllDomainIds` 一律按 `_` 前缀过滤，于是三卡制的父包 `_collect` / `_info` 看不见，首页 `parent` 全 null、13 个领域全落进「其他」组。**只排除 `_base`**，因为它不是可引用的父包。

## Errors: thrown early, formatted as one line

这个文件只有两种错误形态：

- `[schemas] 文件不存在: <绝对路径>` —— `readYaml` 里 `existsSync` 失败。
- `[schemas] extends 成环: a → b → a` —— 把已经走过的链和当前节点一起拼出来。
- `[schemas] 未知字段类型: <type>` —— `buildZodFromSpec` 的 default 分支。

全部是 `throw new Error(...)`，**没有 Zod issue 包装**。真正的字段级错误来自 `schema.safeParse()`，由调用方格式化：`build:data` 打 `result.error.flatten()` 的 JSON 并计入 `invalid`（见 `scripts/build-data.ts`）。所以「哪个字段错了、错在哪」由 Zod 决定，这个文件只负责「把 YAML 转成那份 Zod」。

`isAbstractDomain` / `domainExtendsMap` / `collectUnknownFields` / `mergeChain` 的调用方则各自 `try/catch` 成默认值——一个坏包不该让首页 500。
