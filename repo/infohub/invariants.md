---
covers:
  - AGENTS.md
  - README.md
updated: 2026-11-17
---

# The invariants that explain most of the codebase

七条硬约束写在 `AGENTS.md` 开头，但**真正解释代码形状的是它们背后的理由**。
记住这一页，很多看起来绕的实现就会变得显然——它们是这些约束的直接后果，而不是过度设计。

## 1. Long text never travels through an argument

**约束**：任何长文本写入必须走文件路径参数，不塞进 `content` 参数。

**理由**：桥接层对 raw 代码块和长字符串的转义不可靠，实测失败 5 次。
不是「不方便」，是「会丢数据」。

**代码后果**：`card_import` 收 `file_path` 而不是 `rows`；`card_attach` 收 `file`；
`kb` 系的 `--body-file` 同理。`file_read` 工具存在的唯一目的就是**先看表头再决定映射**，
而不是让模型把数据念一遍。

## 2. Dry run is not optional

**约束**：批量导入前必须 `dry_run`，看报告后再执行。

**理由**：映射错误一旦落盘，就是几十上百张卡被污染，而回滚没有工具支持
（没有删除命令，只能手工删文件）。

**代码后果**：`card_import` 的 `dry_run` 默认 `true`。预演与真跑**吃同一份参数**——
这是刻意的，两边参数不同就等于「预演的不是要做的事」。

## 3. AI never fills gaps in the source

**约束**：AI 拆解原文时不补内容，原文没有的字段一律 `null`。

**理由**：补出来的值看起来合理，但它是**编造的**，而且不再可区分。
一旦接受一次补全，整张卡的可信度都无法评估。

**代码后果**：`derive.ts` 的注释写着「值只能来自原文匹配到的片段，规则本身不产生内容」；
LLM 抽取的 prompt 明写「不改写/不补全/不翻译/不纠错」，校验用 `check_fields()`——
值必须在原文里找得到，**找不到只计数不丢数据**。

## 4. Twenty cards is the blast radius

**约束**：单次 update 超过 20 张卡时中止。

**理由**：防止映射错误批量污染。20 是「还能人工检查」的上限。

**代码后果**：`max_updates` 默认 20，但判定有个精确边界容易被误解——

> **它只看「改动仓库里已有卡片」的行数。文件内重复合并到本文件新建的卡不占额度。**
> 超阈值整体中止，一个文件都不写。

所以导入 500 行全新数据不会触发；导入 500 行去更新已有卡才会。
而且它是**整体中止**，不是「写前 20 张然后停」——部分写入比不写更糟。

## 5. identity lives in the domain pack, nowhere else

**约束**：identity 字段只在领域包声明，不在卡片里临时决定。

**理由**：如果每张卡能自己声明「我是谁」，同一实体就有了多种判定口径，
而「同一实体」的判定必须全局唯一，否则去重结果取决于处理顺序。

**代码后果**：`matchIdentity` 只读 `spec.identity`，从不读卡片上的字段来推断规则。
`card_id` 由 `buildCardId(domain, fields, identity, year)` 生成，identity 是入参而不是查询结果。

## 6. Mark PII before it enters, not after

**约束**：敏感字段只在领域包声明（`sensitive: true`），带 PII 的材料**先标记字段再导入**。

**理由**：**先塞进普通字段再搬，等于已经公开过一次。** 这句话是整个项目里最重的一句——
中间状态（`.staging/`、`inbox/`、日志、git 历史）都会留下痕迹，事后标记补不回来。

**代码后果**：`sensitive: true` 的字段在导入报告里被替换成 `（敏感值，不回显）`；
剥离发生在分片、静态预渲染、发布门禁三处；`audit:publish` 用**真值**当探针而不是形状匹配。

## 7. Static export is a publish action, not a daily one

**约束**：日常用 `npm start` / `npm run dev` 实时读卡；`npm run export:static` 只用于部署。

**理由**：导出会重写被 git 跟踪的 `static/data`，每次改卡都跑会制造大量无关 diff。

**代码后果**：`svelte.config.js` 在两种 adapter 之间切换；`needs-build.mjs` 存在
就是为了判断「这次改动到底需不需要重建」。`infohub/pitfalls` 第一条就是这个坑的症状。

## The meta-invariant: no second source of truth

上面七条可以归到一条更根本的：**任何信息只存一处，派生结构一律现算。**

顺着这条看，很多设计就不是巧合了：

| 设计 | 它消除的第二真源 |
| :-- | :-- |
| 没有索引文件，`kb tree` 现场扫目录 | 索引与目录的漂移 |
| `domainDir()` 从 `domain` 前缀推目录，不存层级字段 | 层级字段与目录的漂移 |
| 卡片 frontmatter 不存 `slug` / `version` / 父指针 | 派生值与内容的漂移 |
| `fidelity` + `word_count` 由采集器如实上报 | 「有正文」的假设与实际的漂移 |
| 发布门禁用真值探针，不信任「已标记」 | 标记与实际值的漂移 |
| `contentFingerprint` 忽略生命周期字段 | 「内容变了」与「只是重导」的混淆 |

**代价是每次现场计算**。`kb tree` 库大了会慢、`card-store` 要 mtime 缓存、
`domain_create` 要做往返验证。这些代价是明知的，换来的是「永远不会出现索引与实际不一致」——
而那一类故障最致命，因为它让「查不到」和「没写过」无法区分。

## Where these invariants are enforced

| 约束 | 强制点 | 违反了会怎样 |
| :-- | :-- | :-- |
| 长文本走文件 | 工具签名就不收长文本 | 转义失败，数据丢失 |
| 先 dry_run | `dry_run` 默认 `true` | 需显式传 false 才写盘 |
| 不补内容 | prompt + `check_fields()` | 只计数不丢数据，但会标出 |
| 20 张上限 | `max_updates` | 整体中止，零写入 |
| identity 单一来源 | 只读 `spec.identity` | 规则无法分叉 |
| PII 先标记 | `sensitive: true` + 三处剥离 + 真值门禁 | 门禁失败，无法发布 |
| 静态导出克制 | 两种 adapter + `needs-build` | 大量无关 diff |

注意「强制点」这一列的性质不同：前四个是**代码结构强制**（做不到就是做不到），
后三个是**流程强制**（做得到，但会被检查出来）。改代码时要分清自己在动哪一类——
把流程强制当成结构强制，会写出多余的守卫；反过来则会让约束静默失效。
