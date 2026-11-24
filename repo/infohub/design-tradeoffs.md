---
covers:
  - src/core/ingest.ts
  - src/core/normalize.ts
  - src/core/derive.ts
  - src/mcp/lib/dedup.ts
  - src/lib/sensitive.ts
---

# Design tradeoffs

这一页记录「为什么选 A 不选 B」。看代码只能看到结果，看不到被否掉的方案和否掉的理由。

## Loose first: only three required fields

`title` / `domain` / `collected_at`。其余全部可选。

**理由**：一条信息 = 一句话 + 一个领域 + 采集时间，就应该是合法卡片。
把 `confidence` / `status` 降级为可选，新鲜度改由 `collected_at` 自动算（超 90 天在详情页标「可能过时」）。
未声明字段（Agent 随手加的 `ext.临时备注`）**原样保留**，只在构建时警告，前端兜底渲染到「其他」分组。

**代价**：放弃结构完整性。这是有意识的——它是检索系统，不是知识管理系统。

## Dedup without embeddings

用精确/包含匹配 + 打分，规则见 `写入通道`。

**理由**：可解释（报告里能说清为什么判为重复）、可离线、零依赖、幂等。
**代价**：同义改写会漏。缓解方式是 `aliases` 字段人工补。

## Merges never overwrite silently

值不同就保留双方 + 记 `import_conflicts` + `status: 冲突`。

**理由**：两个来源说法不同，很可能是不同时点的真实差异（名额分配、职称晋升），
自动取「新的」或「全的」会丢信息。
**代价**：冲突要人工收敛（`migrate:conflicts` 可回收已收敛的）。

## Prefer card_append over update plus commit

原来的写入是「读取版本 → 暂存 → 提交」三步，带乐观锁。
采集场景（看到一条新信息就挂上去）用不着这套，改用 `card_append` 直接追加小节。
**乐观锁机制保留**，但大多数场景不再需要。

## Unified blank semantics

`null` / `""` / `[]` / `{}` 一律视为未填（`src/lib/blank.ts`），渲染时整行跳过，不产生空行。

**理由**：导入的材料里这四种空值混用，如果分别对待，每个消费方都要写四遍判断。

## Body sections: append only

`card_attach` 把附件正文挂到已有卡时，**正文已有同名小节就保留原样**。
`sources[].kind=attachment` 记下 `sections`（实际追加）与 `kept_sections`（被保留）。

**理由**：附件质量不一定强于人工写过的正文。覆盖会丢掉人工整理的内容。
**代价**：同一小节可能出现两份叙述，需要人工合并。

## Lifecycle fields excluded from the fingerprint

`writeCardFile` 用**忽略这两个键**的内容指纹判定是否变化。

**理由**：否则同一份材料重复导入会不断刷新 `edited_at`，把「今天改过」刷成噪音，
git 历史也会被无意义的修改淹没。

## Sensitive fields stripped at three exits

领域包 `sensitive: true` 的字段值只留在 `cards/`。剥离发生在三处：分片（`build:data`）、
静态预渲染、以及门禁。**不需要任何环境变量**——本地运行实时读本机卡片，值照常显示。

`INFOHUB_SENSITIVE` 只是显式覆盖：`=0` 让本地服务预演发布口径，`=1` 让静态产物带值供本地核对。

**本地服务默认只绑 `127.0.0.1`**：本地口径带值，绑全网卡等于把号码送到局域网（显式设 `HOST` 才改）。

## The publish gate probes with real values

`audit:publish` 不是「扫形状」，而是**拿 `cards/` 里标记字段的真实值当探针去扫 `build/`**，命中即失败。

**理由**：形状匹配（如手机号正则）会漏掉不符合格式的敏感值，也会误伤正常数字。
用真值扫是唯一不会漏的办法。实测它还顺手抓到了三件别的问题（见 `docs/敏感信息.md`）。

## Three-tier card layout

`cards/<collect|info|report>/<子类型>/`，`domain` 名是 `collect_paper` 这种带前缀的单段。

`src/mcp/lib/storage.ts` 的 `domainDir()` 与 `src/lib/server/card-store.ts` 的口径**必须一致**。
不一致的症状是「卡片写进 A，读取找 B」，列表里 0 张——这个 bug 不会报错，只会静默为空。

`report` 层目前**目录与领域都不存在**，是为将来的报告类卡片预留的位置。
