---
covers:
  - sizes.py
  - package.json
updated: 2026-11-17
---

# Numbers do not belong in the knowledge base

这一页是**一条规则的说明**，不是数据。规则本身很短：

> 行数、文件数、断言数、卡片张数、耗时——**不写进页面**。要数字就跑 `python sizes.py`。
> 代码内部的常量与阈值（`max_updates` 默认值、`MAX_ANOMALIES`、分块行数）照常写，那不漂移。

## 为什么这条规则值得单独一页

这不是洁癖，是**踩过的**。写库过程中同一份文件的行数出现过四个版本：450 / 523 / 564 / 1508，
每次都是「刚查过」的，每次都不对。原因有三层：

1. **PowerShell 的 `Get-Content | Measure-Object -Line` 会静默少算**——它对末行无换行、
   对 `\r\n` 的处理与编辑器不一致。同一文件用三种 PowerShell 写法得到三个数。
2. **文件本身在动**。并行会话正在改代码，查完到写完之间数字就可能失效。
3. **知识库是多页并行写的**。两页各自记录同一文件的行数，必然分叉。

第 3 条正是本项目反对 `manifest.toml` 的理由：**多一个必须同步维护的真源，就多一处会悄悄不一致的地方**。
`covers` 不写文件是否存在、页面不写行数，是同一条原则在不同层面的应用。

## The tool

仓库根的 `sizes.py`（只用标准库）：

```bash
python sizes.py                      # 各主要目录的文件数与行数
python sizes.py --modules            # 按子系统拆开
python sizes.py src/core/ingest.ts   # 单个文件
python sizes.py src/mcp/tools/       # 单个目录
python sizes.py --json               # 机器可读
```

它刻意跳过了 `node_modules` / `cards` / `build` / `static` / `.trash` / `.backup` 等目录——
统计代码规模时，那些目录只会让数字失去意义。

行数按 LF 计（与编辑器显示一致），读 `utf-8-sig` 去掉可能的 BOM。

## What to write instead of a number

| 想表达 | 不要写 | 写 |
| :-- | :-- | :-- |
| 这个文件很大 | 「1508 行」 | 「这是全仓最重的一个文件」 |
| 这个目录很多文件 | 「125 个 py 文件」 | 「上百个 Python 文件」 |
| 测试覆盖广 | 「32 项断言」 | 列出**覆盖了哪些行为** |
| 这个脚本是巨无霸 | 「988 行」 | 「这是最长的一个入口脚本」 |
| 需要精确值 | 数字 | 「行数用 `python sizes.py <路径>` 现查」 |

「覆盖了哪些行为」永远比「几项断言」有用：前者告诉你改坏了什么会被发现，后者只是个计数。

## The three things that DO belong

### 1. 代码常量与阈值

```text
max_updates 默认 20
MAX_ANOMALIES = 50 / MAX_RISKS = 20 / MAX_CLEARS = 100
RAW_CELL_LIMIT = 60
LLM_CHUNK_LINES 默认 12
```

这些**不随提交漂移**，而且它们是语义本身——不知道 `max_updates=20` 就无法判断一次导入会不会中止。
删掉它们是删掉知识。

### 2. 带日期与条件的实测观察

```text
2026-11-16 实测：14923 张卡
实测（哈工大研究生院通知栏目）：第 1 页 20 条，list2.htm 也返回 20 条且全部重合
176 行用 16 块 ≈ 8 分钟
```

关键区别：**这是「某时某条件下的观察结果」，不是「系统的属性」**。
写的时候必须带条件，读的人才知道能不能外推。`llm-extraction` 页里那些耗时数字全部属于这一类。

### 3. 结构与机制

```text
判据是「搬到另一个站点还成立吗」
顺序固定 ① 强标识 → ② 弱标识 → ③ 新建，不可颠倒
extends 只接受单父包
```

这是知识库的**主体**，也是唯一真正稳定的部分。

## The test for whether something belongs

问一句：**代码改坏时，这句话需要跟着改吗？**

- 「`ingest.ts` 有 2231 行」→ 改一行就错，**不该写**。
- 「`matchIdentity` 的三步顺序不可颠倒，否则同名不同学号会被误并」→ 只有逻辑被推翻才需改，**该写**。
- 「`max_updates` 默认 20，超过整体中止」→ 改默认值才需改，值本身是知识，**该写**。

这个判据在 `codeb/design/where-knowledge-goes` 里有更完整的版本：一段话如果在代码改坏时不需要改，
它大概就是有价值的知识；如果代码一改它就得跟着改，那它本来就该在代码里。

## Corollary: don't record the answer to a queryable question

「这个文件多少行」「这个目录几个文件」「现在多少张卡」——这些都能一条命令查出来。
把它们抄进知识库，等于给自己加了一份会过期的副本。

**能被一条命令回答的问题，就不要用工整的中文段落回答。**
