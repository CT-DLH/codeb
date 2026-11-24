---
covers:
  - cards/
updated: 2026-11-17
---

# What a card file actually looks like

前面几页讲「怎么写入」「字段怎么定义」，这一页讲**落到磁盘上到底是什么形状**。
改读取层、写迁移脚本、排查渲染问题时先看这里，比逐个翻卡片文件快。

## The full shape, from a real card

`cards/info/student/200110101.md` 的原文（未删节）：

```markdown
---
title: 刘雨晨
domain: info_student
collected_at: '2026-10-26'
object_type: 本科生
ext:
  student_id: '200110101'
  name: 刘雨晨
  class: 20级计算机1班
  eval_term: 2025-2026-1
  unrated_courses:
    - 机器学习
  faculty: 计算机科学与技术学院
  enroll_class: 计算机科学与技术
card_id: "200110101"
sources:
  - file: 25秋未评价学生名单-信息学部（本科）(1).xlsx
    row: '348'
    fields:
      - ext.eval_term
      - title
      - ext.name
      - ext.student_id
      - ext.class
      - ext.faculty
      - ext.enroll_class
      - ext.unrated_courses
created_at: '2026-10-27T13:33:48.000Z'
edited_at: '2026-10-27T13:33:48.000Z'
---
## 来源

- 25秋未评价学生名单-信息学部（本科）(1).xlsx · 第 348 行
```

三个结构事实值得单独说：

1. **`ext` 是一个嵌套对象**，不是把 `ext_student_id` 这种扁平键铺在顶层。
   YAML 里的 `ext_fields.student_id` 在卡片里就是 `ext.student_id`。
2. **`title` / `domain` / `collected_at` / `object_type` / `card_id` / `sources` / `created_at` / `edited_at` 都在顶层**，
   和 `ext` 平级。它们是 base 字段或服务端字段，不属于任何领域包。
3. **正文既可能是模板生成的，也可能是附件挂来的**。上面这张卡正文只有「来源」一节，
   因为材料本身没正文；下面 thesis 卡就是另一种形态。

## Two body shapes: generated vs attached

### 采集卡：正文常常是空的或极简

`cards/collect/zhihu/00001155.md` 的正文只有一行链接：

```markdown
## 原文位置

[原文链接](https://zhuanlan.zhihu.com/p/88290363)
```

它的 `ext.fidelity: metadata_only`、`ext.word_count: 0` —— **正文没抓到**。
这三个信号是对齐的：`fidelity` 说「仅元数据」，`word_count` 说 0，正文就只有链接。

所以「卡片没有正文」不代表写入失败，可能是采集器诚实地报告了 `metadata_only`。
排查时先看 `fidelity`，不要直接怀疑写入通道。

### 有附件的卡：正文由多个小节拼成

`cards/info/thesis/2026-06109a74.md` 的 `sources` 有**两条**记录，第二条是附件：

```yaml
sources:
  - file: 综合毕设.xlsx
    row: '46'
    fields: [ext.contact_email, ext.advisor, ...]
  - kind: attachment
    file: raw/综合毕设指导书/47至50/本科生综合设计（论文）任务书 - 顾术实-1.docx
    parser: task-book
    title: 基于地形与任务跨模态语义补全的月面通信策略研究
    sections:
      - 立题的目的和意义
      - 本研究将围绕以下3个核心内容展开
      - 进度安排
      - 同组设计者及分工
    kept_sections: []
    attached_at: '2026-10-25'
```

`kind` 缺席的那条是表格行，`kind: attachment` 那条是附件。
两条的 `file` 指向完全不同的位置（一个在导入用的 xlsx，一个在 `raw/` 里的原始 docx）。

`sections` 记下**实际追加了哪些小节**，`kept_sections` 记下**哪些小节因为正文已有而保留原样**。
这张卡 `kept_sections` 是空数组——说明这次挂载没有和人工正文冲突。

## Why sources[] is the audit trail

`sources[].fields` 是一个**字段名列表**，不是值。它回答的问题是「这个卡上的字段分别是谁写的」。
上例 thesis 卡里，`ext.advisor` 来自 xlsx 第 46 行，而正文小节来自 docx 附件。

这个设计让「合并不静默覆盖」可追溯：值不同时保留双方并记 `import_conflicts`，
而 `sources` 说明两个值的出处。没有它，冲突行只能写成「保留 A，新值 B」，看不出谁是谁。

同一份材料同一行的多次写入会**合并成一条**（`fields` 取并集）；
不同行/不同文件各留一条。所以 `sources` 的条数等于「有多少份材料碰过这张卡」，不是「被写过多少次」。

## The lifecycle pair

`created_at` 首次落盘，`edited_at` **只在内容真正变化时更新**。

判据是 `contentFingerprint()`（`src/mcp/lib/storage.ts`）：frontmatter **忽略 `created_at` 与 `edited_at` 这两个键**、
键序无关、再加正文，一起算 sha256。

为什么必须忽略这两个键：否则同一份材料重复导入会不断刷新 `edited_at`，
把「今天改过」刷成噪音，git 历史被无意义的修改淹没。这是 `infohub/design-tradeoffs` 里
「Lifecycle fields excluded from the fingerprint」的实现侧。

`card_id` 字段也写在 frontmatter 里，**和文件名相同**。读取层优先用 `frontmatter.card_id`，
文件名只是兜底（`String(record.frontmatter.card_id ?? basename(file, '.md'))`）。
迁移改名时这两处都要动，只改文件名会让 `card_id` 与文件名不一致。

## 那三种 YAML 引号是刻意留的

观察上面的真实卡片，会发现引号用法不统一：

| 写法 | 出现处 | 原因 |
| :-- | :-- | :-- |
| `'2026-10-26'` | `collected_at`、`row` | 不加引号 YAML 会解析成日期/数字，字段类型就变了 |
| `"200110101"` | `card_id` | 学号形如数字，不加引号会被解析成整数、丢前导零 |
| `'https://...'` | `ext.url` | 冒号后跟空格会被误认为映射 |

这不是书写疏忽，是 `gray-matter` 序列化的结果。**手改卡片时不要把这些引号「清理」掉**——
清理掉之后 `row: 348` 从字符串变成数字，`fields` 比对就会失败。

## A minimal valid card

最省的合法卡片只有四个顶层键加正文：

```markdown
---
title: 某条信息
domain: info_job
collected_at: '2026-11-17'
---
正文。
```

`ext` 可以整个不存在（读取层按 `?? {}` 兜底），`sources` 也可以不写（手工录入场景）。
这就是「宽松优先」的实际形态：三个必填字段之外的**一切**都可选。

## What is NOT in the file

- **没有 `id` 之外的索引字段**。没有 `slug`、没有 `type_id`、没有父节点指针。
  层级全部由 `domain` 前缀 + 目录位置推出来。
- **没有 `updated_by` / `version`**。`card_update` + `card_commit` 的乐观锁靠 `revision`
  （内容哈希）在**调用期间**校验，不落盘。
- **没有标签表、没有分类表**。`tags` 是 frontmatter 里的字符串数组，聚合靠读取层现算。

这三条「没有」是同一个决定：**卡片文件是唯一真源，任何派生结构都不落盘**。
加一个索引字段，就多一处会和实际漂移的地方。
