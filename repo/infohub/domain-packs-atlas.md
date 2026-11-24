---
covers:
  - domains/
  - domains/_base.yaml
  - domains/_collect.yaml
  - domains/_info.yaml
updated: 2026-11-17
---

# Domain packs: every pack, every field

16 个 YAML 装在 `domains/`，但它们**不是 16 个平级的包**：3 个抽象父包 + 13 个实体包。
改字段之前先看这一页，不要打开前端代码，也不要凭感觉手改 YAML。

## The inheritance tree as it actually is

```text
_base       （23 个 base_fields，根，无 domain_id）
├── _collect   abstract=true   → 5 个采集卡包
│   ├── collect_zhihu   回答 / 文章
│   ├── collect_paper   论文
│   ├── collect_github  仓库
│   ├── collect_web     其他
│   └── collect_bilibili 视频
└── _info      abstract=true   → 8 个信息卡包
    ├── info_student      本科生 / 研究生 / 毕设学生
    ├── info_mentor       导师
    ├── info_course       课程
    ├── info_thesis       任务书 / 题目 / 开题报告 / 中期检查 / 论文 / 答辩材料
    ├── info_academic     任务书 / 招生公告 / 数据接口 / 时间线
    ├── info_competition  竞赛
    ├── info_gaokao       专业 / 院校
    └── info_job          岗位 / 公司
```

**`_base.yaml` 是唯一没有 `domain_id` 的文件**——它不是领域，只是字段池。`extends` 只有两层，
不存在三级继承链：`info_student extends _info extends _base` 是读取器展开的结果，不是 YAML 里写了三条 `extends`。

`extends` **只接受单父包**（`src/lib/schemas.ts`）。`info_student` 既需要人物字段又需要来源语汇，
解决方案是「把 `person` 的字段并入 `_info`、`person` 文件保留不删」，而不是多继承。

## _base: the 23 shared fields

必填只有三个：`title` / `domain` / `collected_at`。**其余 20 个全部可选。**

| 组 | 字段 |
| :-- | :-- |
| 必填 | `title` `domain` `collected_at` |
| 服务端生成 | `card_id` `created_at` `edited_at` |
| 基本 | `object_type` `summary` `aliases` `tags` `source_type` `source_ref` `last_verified` `notes` |
| 导入溯源 | `sources`（含 file/row/fields/kind/parser/title/sections/kept_sections/attached_at）`import_conflicts` |
| 结构化补充 | `hard_requirements` `key_dates` `risks` |
| 已降级但保留 | `confidence` `status` `gaps` `next_action` |

`source_ref` 的 `placeholder` 直接写明了它的四种合法形状：原文 URL / DOI / arXiv ID / `qq://群号/消息ID` / 群消息时间与发布人。

**最后四个字段是刻意留下的负担**：注释写着「信息没有『待核实→有效→冲突→过期』的生命周期，
新鲜度由 `collected_at` 计算，这几个字段新卡可不填」。它们仍在 Schema 里，是为了让旧卡正常渲染而不是被当成未声明字段。

## _collect: only fields that are 100% filled

16 个 `ext_fields`。判断标准是实测填充率，不是重要性：

- **父包 5 个 100% 填充**：`url` `fidelity` `word_count` `author` `published_at`。
- `collector` 与 `platform` 是**两个不同概念**：`collector` 是「哪个采集器实现」，`platform` 是「采集器上报的平台名」。
  大多数情况相同（zhihu→zhihu），但 `collect_paper` 的 `platform` 可能是 `crossref` / `cnki` / `arxiv`——
  它们共用一个采集器实现，平台名仍各自保留。
- `voteup` **量纲由采集器决定**：知乎=赞数、GitHub=star、B站=播放量。所以 `collect_github.yaml`
  把 label 改成「Star」，`collect_bilibili` 改成「播放量」——同一个字段名，不同采集器语义不同。
- `fidelity` 的三档：`full` 正文完整 / `partial` 残片（字幕、摘要）/ `metadata_only` 仅元数据。

## _info: 19 fields, and the sensitive ones are deliberately absent

父包只声明「来源与冲突」这组共用语汇 + 原属 `person` 的人物字段（`name`/`name_en`/`gender`/`birth_year`/
`relation`/`school`/`major`/`academic_title`/`education_level`/`email`/`homepage`）
+ 原属 `document` 的字段（`doc_type`/`milestones`）+ 实测补出的 `research`/`browse_count`/`homepage_updated`/`roster_email`。

**`id_card` / `phone` / `address` 不在父包**，这是 2026-11-05 按实测收窄的结果：

| 字段 | 实测使用面 |
| :-- | :-- |
| `id_card` | 仅 student 47 张，其余 5 个信息卡领域全 0 |
| `phone` | student 47 / mentor 22，其余 0 |
| `address` | 仅 mentor 80 张，其余 0 |

放父包会让 course/thesis/academic/competition 也「声明」这三个字段——它们并不使用，
等于无谓扩大敏感字段声明面。**PII 面越小越好**，这是这条设计的全部理由。

`roster_email` 与 `ext.email` 的区别：前者来自名单表格（批量导入），后者来自教师主页/个人材料。
来源不同所以分成两个字段，否则同一张卡上两个来源的邮箱会互相覆盖。

## The 13 concrete packs at a glance

| domain_id | 中文名 | object_types | 实测卡数 |
| :-- | :-- | :-- | --: |
| `collect_zhihu` | 知乎 | 回答 / 文章 | 4658 |
| `collect_paper` | 论文 | 论文 | 4517 |
| `collect_github` | GitHub | 仓库 | 1894 |
| `collect_web` | 网页 | 其他 | 320 |
| `collect_bilibili` | B站 | 视频 | 23 |
| `info_student` | 学生名册 | 本科生 / 研究生 / 毕设学生 | 3019 |
| `info_course` | 课程大纲 | 课程 | 149 |
| `info_mentor` | 导师名录 | 导师 | 115 |
| `info_thesis` | 本科综合毕设 | 6 种材料类型 | 84 |
| `info_academic` | 学业科研 | 任务书 / 招生公告 / 数据接口 / 时间线 | 78 |
| `info_competition` | 竞赛 | 竞赛 | 64 |
| `info_gaokao` | 高考志愿 | 专业 / 院校 | 1 |
| `info_job` | 就业实习 | 岗位 / 公司 | 1 |

`report` 层与 `report_*` 领域**不存在**——`domainDir()` 支持三层，但第三层是预留位。

## identity: each pack encodes a different judgement

这是 16 份 YAML 里**唯一不能照抄**的部分。逐包看真实声明：

| 包 | strong | weak | disambiguator | card_id_pattern | fallback |
| :-- | :-- | :-- | :-- | :-- | :-- |
| `collect_zhihu` / `github` / `web` / `bilibili` | `ext.url` | — | `ext.collector_key` | `{hash:strong}` | `{hash:strong}` |
| `collect_paper` | **空** | `title` | `ext.doi` | `{hash:weak}` | `{hash:weak}` |
| `info_student` | `ext.student_id` | `ext.name` | `ext.class` `ext.major` | `{hash:strong}` | `name-{ext.name}` |
| `info_mentor` | `ext.homepage` | — | — | `{hash:strong}` | `{hash:weak}` |
| `info_course` | `ext.course_code` | `title` | — | `{ext.course_code}` | `{hash:weak}` |
| `info_competition` | `ext.competition_key` | `title` | `ext.seq` | `{hash:strong}` | `{hash:weak}` |
| `info_thesis` | `source_ref` | `title` `ext.advisor` | `ext.student_name` | `{year}-{hash:weak}` | — |
| `info_academic` | — | — | — | `{hash:weak}` | `{hash:weak}` |
| `info_gaokao` / `info_job` | **空** | `title` | — | `{hash:weak}` | `{hash:weak}` |

### Why collect_paper refuses to use DOI as a strong id

`collect_paper.yaml` 里这段注释是这一页最该记住的一条：

> 保持 `weak: [title]` 而不改 `strong: [doi]`：改强标识会重算 3605 张卡的 `card_id`，
> 而 title 弱标识已能命中同一篇。题录的 title 是最稳定的键（DOI 有时缺失，实测 87.3% 有 DOI）。

**改强标识是一次 card_id 重算**，会把已有卡全部改名、断掉外部引用。所以哪怕 DOI 更「正确」也不改。

### Why info_student's order cannot be reversed

学号本身唯一，姓名会重名。所以「有学号先按学号并卡，没学号才按姓名并卡」。
顺序反了，**同名不同学号会被合并掉**。只有姓名的材料先落成 `name-{ext.name}` 的「待认领卡」，
带学号的材料出现时自动并入，donor 原文件进 `.trash/`。

注意 `card_id_fallback` 是 `name-{ext.name}` 而不是 `{hash:weak}`——待认领卡需要**人可读**，
因为它的作用就是等人来认领。

### Why info_thesis is the only one with {year} in the pattern

`{year}-{hash:weak}`：同一份毕设材料每年重来一遍，标题会完全重复（「任务书」）。
年份进 id 才能把 2024 年的任务书和 2025 年的分开。

## derive: two chained rules, only in info_student

`ext_fields` 里声明 `derive:` 的字段**全项目只有两个**，都在 `info_student.yaml`：

```yaml
insurance_note:
  derive:
    from: body
    pattern: (?<value>该人员已在.+?规定。)
origin_region:
  derive:
    from: ext.insurance_note
    pattern: (?<value>(?<=已在)[^，]+?(?=\d*参加))
```

第二条**从第一条的结果里取**，这就是 `derive.ts` 必须按不动点迭代而不是单趟扫描的原因。
两条都用**命名组 `value`**：没有命名组时取第 1 组，再没有就取整段匹配（见 `core/sections-and-derive`）。

两个都标了 `sensitive: true`——**派生字段会被敏感标记接管**，部署边界按同一口径剥离。
如果派生字段不标 sensitive，敏感值就会从派生路径漏出去。

## split: false — the only three array fields that must not be split

`awards`（单项奖）、`unrated_courses`（未评课程）、`award_records`（奖助记录），全在 `info_student.yaml`。

默认数组字段按 `[,，;；、\n]+` 拆。但这三个是「多行一实体」的数组，拆了会出事：

> 「中国茶、酒文化与健康」被顿号拆成三门课。

`award_records` 是对象数组（`award`/`year`/`level`/`department`/`sequence`），拆了结构直接崩。
**新增「一行里含分隔符的数组字段」时必须显式写 `split: false`。**

## attachments: only info_thesis has it

`info_thesis` 是全项目唯一声明 `attachments` 的包：

```yaml
attachments:
  enabled: true
  match_by: [title]
  accept: [.docx]
  parser: task-book
  on_missing: quarantine     # 匹配不到卡 → 进隔离区
  on_ambiguous: review       # 匹配到多张 → 进人工复核
  body_section_map:          # 附件小节名 → 卡片小节名
    主要内容与技术指标: 主要研究内容
    技术指标与主要内容: 主要研究内容
    主要内容: 主要研究内容
    ...
```

`body_section_map` 的**三个键映射到同一个值**不是冗余：教师写任务书时这三种标题都常见，
归并到同一个卡片小节，前端才能展示成一段。`on_missing` / `on_ambiguous` 是两种不同的失败处置，
不能合并成一个 `on_error`——「没找到卡」和「找到多张卡」需要的动作相反。

## 字段级元数据的全部可用键

从 16 份 YAML 实际出现过的键汇总（不是从代码推测）：

| 键 | 作用 | 出现处 |
| :-- | :-- | :-- |
| `label` | 表头中文名 / 详情页标签 | 几乎全部 |
| `type` | `string` / `number` / `array` / `object` | 全部 |
| `required` | 仅 `_base` 三个必填，其余全 false | 全部 |
| `order` | 详情页与列表排序 | 采集包与 student 用得最多 |
| `format` | `url` / `date` / `badge` / `ref` | 见下 |
| `filterable` | 列表页可筛选 | 多数包 |
| `enum` | 取值白名单 | `status` `confidence` `relation` `task_state` |
| `value_labels` | 枚举值的中文显示名 | 采集包的 `kind` / `fidelity` / `collector` |
| `sensitive` | 部署边界剥离 | 8 个字段（见上） |
| `split` | `false` 关闭数组拆分 | student 的 3 个字段 |
| `placeholder` | 录入提示 | `source_ref` |
| `server_generated` | 不接受手填 | `card_id` `created_at` `edited_at` |
| `derive` | 从正文/字段正则取值 | student 的 2 个字段 |
| `fields` | object 的子字段声明 | `salary` / `key_links` / `sources` |
| `item` | array 的元素类型 | 所有数组字段 |

`format` 的四种渲染方式：`url` 渲染成可点链接、`date` 按日期格式、`badge` 渲染成彩色标签（用于枚举）、
`ref` 渲染成参考资料条目（`info_competition` 的 `refs`）。

## Changing a pack: three traps

1. **不要手改 YAML**，用 `domain_update`。手改绕过元 Schema 校验与往返验证，
   出错时报错信息说不清哪一行错。详见 `infohub/mcp/domain-pack-api`。
2. **删 `object_types` 前先看占用**：仍被卡片使用的类型会警告并给出占用卡数，删空会报错。
   `info_thesis` 有 6 个类型，删错一个就有一批卡失去类型。
3. **改 `identity` 是一次历史数据迁移**，不是配置修改。改完必须跑
   `npm run migrate:ids -- <domain> [--apply]`，默认只预演。`{hash:weak}` **不能用随机数**，
   否则幂等失效、重复导入会重复建卡。

## 命名前缀为什么是 info_ 和 collect_

`domain` 是**单段带前缀**（`info_student`），不是 `person/student` 这种嵌套。原因是三层卡片布局：

```text
domain = info_student   →   cards/info/student/<card_id>.md
domain = collect_paper  →   cards/collect/paper/<card_id>.md
```

**注意第二段是把前缀剥掉后的剩余部分，不是完整 domain 名。** 实测目录是 `cards/info/student`，
不是 `cards/info/info_student`。

实现只有一行正则（`src/mcp/lib/storage.ts` 的 `domainDir()`）：

```ts
const m = /^(collect|info|report)_(.+)$/.exec(domain);
return m ? join(CARDS_DIR, m[1], m[2]) : join(CARDS_DIR, domain);
```

前缀就是层，这样 `domain` 一个字符串就能同时表达「哪一层」和「哪个领域」，不需要第二个字段。
**没有前缀的 domain 会退化成 `cards/<domain>` 两层**，这条 fallback 是给未迁移的旧数据留的。

这行正则在 `src/mcp/lib/storage.ts`（写）与 `src/lib/server/card-store.ts`（读）**各有一份**。
不一致的症状是「写进 A，读取找 B」，列表里 0 张，且**不报错**。
