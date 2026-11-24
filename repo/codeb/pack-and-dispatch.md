---
title: Assembling context for a task, and checking it can be dispatched
covers:
  - kb.py
  - mcp/server.ts
updated: 2026-11-20
---

# Assembling context for a task, and checking it can be dispatched

两个命令，一个给干活的人、一个给派活的人：

```bash
kb pack collector/sites/                      # 执行者：装订一份册子（stdout，不落盘）
kb dispatch collector/kit/ collector/refs/    # 派发者：这批范围能不能并行
```

知识库原来的定位是「让 agent 读得快」。到这里多了一件：**让 leader 能把活切开、
把每份活该看的装订好、并且在派之前就知道会不会撞车。**

## 为什么册子不落盘

册子（`.context/<role>/<task>.md` 那一类）一旦落盘就多一份要手工同步的真源。
工单改了而册子没重新生成时，它会**静默说谎**——照着错册子开工比没有册子更糟。
所以 `kb pack` 只往 stdout 打，每次现场算。代价是每次都要重新扫一遍源码目录，
实测一次 pack 在 infohub 上约 0.3–1 秒，可以接受。

同理，`kb dispatch` 也不存任何名单：写范围互斥、共享知识、接口面全部从
`covers` 和文件系统现场算。目录会移、页会改，存下来的名单第二天就骗人。

## 取料四层与降级顺序

这才是 `pack` 的唯一设计。预算不够时**先砍最可替代的**：

| 层 | 内容 | 丢的次序 |
| :-- | :-- | :-- |
| L1 目标源码 | 单文件全文（超预算退大纲）；目录给每个文件 | **最后才丢** |
| L2 知识节 | 只取点名了目标文件的二级小节，不取整页 | 弱相关先丢，强相关后丢 |
| L3 兄弟文件大纲 | 同目录其它文件的签名 | 最先丢 |
| L4 计划 + 省略清单 | `## 计划` 小节、以及「什么没装、怎么取」 | **永不丢** |

目标源码永不先于知识层被丢，是因为「改什么」比「为什么这样改」更基础；
反过来也不对——只有源码没有约束，agent 会照着代码把那些「不要修正」的注释改掉。
所以两层都丢了的时候必须报警，见下。

### 全文还是大纲：看预算，不看行数

`OUTLINE_LINE_LIMIT = 400` 只是参考线。真正的判据是 `TARGET_BUDGET_SHARE`：
目标源码超过预算的 60% 就退大纲，按目录装订时这笔额度再按文件数均摊。

写死行数会把两种相反的情况判反：`kb.py` 1432 行给大纲，是因为它 17k tok
塞不进 13k；而 906 行的 `blob.py` 在同一个预算里给全文仍然合理。

## 配置也算源码

`collector/sites/<family>/<kind>.yaml` 这类文件是任务的**交付物本身**。
只认 `.py`/`.ts` 会让「加一个新站点」的册子里没有要照抄的样板 YAML——
第一次跑 `kb pack collector/sites/` 就踩到了：只装进 6,299 tok 知识、源码 0 块。

`CONF_EXT` 覆盖 yaml/yml/json/toml/sql，且配置**一律给全文**：
YAML 的 value 就是内容，抽签名会抽成空。

排除 `package.json` / `tsconfig.json` / `capabilities.json` 这类（`CONF_SKIP_NAMES`），
它们体积大且与具体任务无关，混进来会挤掉真要看的源码。

## 精度分档：exact / dir / none
`pack` 必须自报精度，因为 `covers` 的精度差异极大。实测 infohub
`collector/` 下 125 个代码文件里，精确到文件被认领的只有 8 个，
另外 117 个只有目录级认领。

| 档 | 含义 | 装订行为 |
| :-- | :-- | :-- |
| `exact` | 有页精确 covers 这个文件 | 只取该页命中节，排序可信 |
| `dir` | 只有页 covers 了所在目录 | 取目录页命中节，标注按目录推断 |
| `none` | 无任何页认领 | 不装知识层，打印「该补 `kb upsert`」 |

`none` 不是失败，是**产出待办**：跑一次就知道哪里缺页。

## `--no-source`：答案常常不在源码里

最高频的提问是「改 X 有哪些坑」，而这个问题的答案在知识层。

| 装订方式 | token | 源码占比 |
| :-- | :-- | :-- |
| `kb pack collector/kit/paging.py` | 6,968 | 5,204（**75%**） |
| 同上 `--no-source` | **1,764** | 0 |

为什么必须做成开关，而不是让调用方压预算：**降预算会先把知识层丢掉**
（分层顺序就是如此），所以「省钱」和「只要知识」是相反的方向，压预算办不到。

这条是 agent 逼出来的。原先它面对「不要贴源码」没有任何表达方式：只能装整册
7,183 tok，其中 72% 是它明确说过不要的东西。

## 知识层被挤空必须报警

预算压到 1200 时 `collector/kit/` 的知识节会被全部丢掉，只剩源码大纲。
这份册子看着完整，实际已经把「改了会静默出错」的那些约束全丢了。
所以 `pack` 此时输出 `knowledge_lost: true` 并在正文顶部写警告——
安静地交出一份残缺但整齐的册子，是这套工具最危险的失败模式。

## dispatch 查四件事

```text
✓ 写范围两两互斥      ← 非空就拒绝并行，会互相覆盖
共享知识              ← 被多个范围共同认领的页，每个包都必须装
接口面                ← 你写范围内的文件，还被哪些别人的页描述
串行点                ← 由别的脚本生成的派生文件
```

### 串行点为什么必须是全局的

`collector/capabilities.json` 由 `collector/tools/capabilities.py --write` 生成，
加任何一份站点 spec 都要重跑它。实测 `collector/` 下 **7 个子范围全都命中它**。

如果只在每张任务卡上各写一句「注意串行」，7 个 agent 会各跑一次生成器，
最后只剩一个人的结果——其余 6 个新站从能力清单里静默消失，而每个人的卡片
都说自己没错。所以 `dispatch` 把它从「各卡提醒」升级成 `serial_bottlenecks`：
同一派生物被 ≥2 个范围命中，就在全局报一次，处理办法是各 agent 只改源文件、
由 leader 在并回后统一重生成。

### 识别派生文件：要求点名生成器

只用「自动生成 / 不要手改」会大面积误报，实测三类假阳性：

- `capabilities.py` 里那行 note 字符串（**它就是生成器本身**）
- `enrich_batch.py` 的 `--plan` 说明（它吃掉别人生成的输入，自己不是产物）
- `web.py` 里「由 web 源接管，会生成…」的散文

所以判据是 `DERIVED_MARK`：**点名一个脚本 + 一个强产物词**同时出现，
且那个脚本名不能是文件自己。第三条尤其重要——生成器与产物常常同名不同后缀
（`capabilities.py` 生成 `capabilities.json`），比 stem 会把产物误判成生成器。

### 写范围之外的派生物，扫描必须有边界

找 `capabilities.json` 不能递归扫整仓：infohub 有 25 万个文件，
一次 `dispatch` 会直接挂住（实测超过 180 秒未返回）。
所以只扫两处、各非递归一层：仓库根、scope 的父目录。
聚合型产物就落在聚合层，这个假设成立且成本是 1.9 秒。

## 仓库根是坐标，不是分类

`covers` 里写的是仓库内相对路径（`collector/kit/paging.py`），
但代码在磁盘上的位置推不出来——`atomkgraph` 的代码在
`D:/work/project/knowledge_map/atomkgraph`，不与仓库同名。

实测：朴素按「知识库根的兄弟目录」推断，163 条 covers 里 49 条指向不存在的路径；
写显式映射后 223 条页级 covers 里 217 条可解析（97%）。

所以每个仓库在一个页面的 frontmatter 写一行：

```yaml
root: D:/work/project/knowledge_map/atomkgraph
```

**这与 `manifest.toml` 的区别在于它会大声失败**：坐标写错时 `pack` 立刻报
「scope 定位不到磁盘根」并列出已知的映射，而不是安静产出没有源码的册子。
分类标签没有这个性质——填错了没人看得出来。

## 实测数字

| 项 | 值 |
| :-- | :-- |
| `kb tree` 全库（81 页标题） | 949 tok |
| `pack collector/sites/` | 8,794 tok / 25 块 / 精度 exact |
| `pack collector/kit/paging.py` | 6,968 tok（414 行源码全文） |
| 同上 `--no-source` | **1,764 tok**（砍 75%） |
| `pack kb.py` | 2,552 tok（1432 行只给大纲，17k tok 全文塞不下） |
| `pack collector/kit/` 单节筛选 | 全文 8,378 → 相关小节 1,678 tok（砍 80%） |
| `pack collector/kit/` 目录源码 | 全文 32,435 → 大纲 1,251 tok（砍 96%） |
| `dispatch collector/kit/` | 162 tok（文件清单 + 接口面 + 串行点） |
| `dispatch` 7 个 collector 子范围 | 0 冲突，全部命中同一串行点 |
| 一次 `dispatch` 耗时 | 1.9 秒 |
