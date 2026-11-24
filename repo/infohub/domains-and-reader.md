---
covers:
  - src/lib/schemas.ts
  - src/lib/server/card-store.ts
  - src/routes/
  - domains/
---

# Domain packs and the reader

领域包是 **Schema 唯一真源**，也是「建议清单」。改字段不改代码——这是整个项目最重要的一条架构决定。

## Why fields live in YAML, not code

前端不认识任何具体字段名。列表页的列与顺序 = `domains/<domain>.yaml` 的 `summary_columns`
（支持 `ext.doc_type` 这类嵌套路径）；表头中文名、详情页排序、`url`/`date`/`markdown` 的渲染方式，
全部来自字段的 `label` / `order` / `format`。

后果：加一个字段只需要 `domain_update`，不需要改 Svelte、不需要重新构建前端。
代价：`src/lib/schemas.ts` 把 YAML 递归转成 Zod，未声明字段一律放行。

## Three abstract parent packs

`extends` 只接受**单父包**，这个限制直接决定了一次结构搬迁：

| 父包 | 放什么 | 谁继承 |
| :-- | :-- | :-- |
| `_base` | 必填 `title`/`domain`/`collected_at`，加 `sources` 溯源 | 全部 |
| `_collect` | 所有采集器 100% 填充的字段：`url`/`fidelity`/`word_count`/`author`/`published_at` | `collect_*` |
| `_info` | 来源与冲突语汇 + 原属 `person` 的人物字段 | `info_*` |

**为什么人物字段搬进了 `_info`**：`info_student` 既需要人物字段又需要来源语汇，
但 `extends` 只能单父包，没法同时继承 `person` 与 `_info`。
所以把 `person` 的字段并入 `_info`，原 `person` 抽象包保留不删（避免断掉其它引用）。

抽象父包**不落卡、不进导航、不出现在 API 与列表页**。

## Why _collect holds only shared fields

实测 100% 填充的才放进父包，平台特有字段留在子包（知乎的 `voteup`/`comments`、论文的 `doi`/`venue`）。
这样列表列能按采集器定，**不会出现「论文卡显示空赞数」这种并集列**。

## The card reader is the hot path

`src/lib/server/card-store.ts` 是全仓最重的一个文件。它做两件事：

- 实时读 `cards/` 源文件（不使用模式的核心）；
- `mtime` 缓存，避免每次请求都重新解析全部 Markdown 文件。

**不要在它之外自己遍历 `cards/`**——那会绕过缓存，也会让「使用模式刷新即见」这个性质失效。

## Paged index

列表读取层走**分页索引**，不要下发全表。首页检索在静态模式下走 Pagefind，使用模式下走服务端实时检索。

## Changing a domain pack the right way

用 `domain_create` / `domain_update`（PATCH 语义），**不要手改 YAML**——会绕过元 Schema 校验与往返验证。

`domain_update` 支持：增删 `object_types`、加/改/删字段、重设 `summary_columns`、
设置 `dedup_key` / `identity` / `attachments`

删 `object_types` 时：仍被卡片使用的类型会**警告并给出占用卡数**，删空会报错。
