---
covers:
  - scripts/migrate-card-ids.ts
  - scripts/migrate-conflicts.ts
  - scripts/migrate-award-to-student.ts
  - scripts/migrate-tag-ids.ts
  - scripts/prepare-courses.ts
  - scripts/import-jsonl.ts
  - scripts/backfill-source-body.ts
  - scripts/backfill_timestamps.ts
updated: 2026-11-17
---

# Migrations and backfills: dry-run by default, with exceptions

迁移类脚本的共同设计是「默认只预演，`--apply` 才写盘」。这个默认值不是随便定的：它们全都**直接改 `cards/` 里的文件**，不经导入内核，没有 `_overwrite_fields` / `_replace_sections` 那套保护，也没有 `.trash/` 回收（除了 award 合并）。

但有几个脚本破了这个约定，先列出来，后面不再重复：

| 脚本 | 开关名 | 无 dry-run 的脚本 |
| :-- | :-- | :-- |
| `migrate-card-ids.ts` | `--apply` | |
| `migrate-conflicts.ts` | `--apply` | |
| `migrate-award-to-student.ts` | `--apply` | |
| `migrate-tag-ids.ts` | **`--write`** | |
| `backfill-source-body.ts` | `--apply` | |
| `backfill_timestamps.ts` | `--apply` | |
| `migrate-collected-at.mjs` | — | **无，直接写** |
| `prepare-courses.ts` | — | 写 `inbox/`，不碰卡 |
| `import-jsonl.ts` | `--write` | |

## 共同的三道保险

**幂等**。每个脚本的注释都明确写了「幂等」，且都有对应的实现手法：只补缺失字段、只填空正文、已收敛的记录不再计为待改、新 id 不是映射的键。这意味着「不确定要不要跑」的正确姿势是**先跑一遍 dry-run 看计数，再跑 `--apply`，然后再跑一次 dry-run 确认是 0**。

**先读进内存再统一写**。`migrate-card-ids` 是重命名类，它的做法是先把所有待改内容 `readFileSync` 进内存，再统一写新文件，最后才删旧文件——并且删之前检查 `!written.has(change.oldFile)`，避免「A 改名成 B、B 改名成 A」时把刚写的东西删掉。

**报告里点名**。所有脚本都不只说「改了几张」，而是列出具体是哪张卡、改了什么。`migrate-conflicts` 给 `by_reason` 分布，`migrate-award` 写 `docs/获奖名单合并.md` 报告，`migrate-card-ids` 打印前 20 条重命名并单列哈希碰撞。

## migrate-card-ids

**语义**：按领域包当前的 `card_id_pattern` 重算已有卡片的 `card_id`，并重命名文件（`card_id` 与文件名是同一个东西）。

**参数**：位置参数 = domain（默认 `thesis`），`--apply` 落盘。

**前提**：领域包必须声明 `identity`，否则 `exit 1` 打「没有声明 identity，无法重算 card_id」。

**算法**：对每张卡 `buildCardId(domain, frontmatter, spec.identity, year)` 算出 `base`。`year` 取 `collected_at` 前 4 位，没有就用当前年份。然后按 `base` 分组，**同组内按当前 id 字典序稳定分配后缀** `-2` / `-3`。这个排序键的选择是关键——用当前 id 而不是文件名或 mtime，保证第一次运行和后续运行结果一致。

**风险**：
- 这是**删除操作**。旧文件被 `rmSync`，只要有一张卡改名失败，那次运行就留下半成品。
- 哈希碰撞时后缀分配依赖「当前 id 的字典序」，所以**先跑一次别的迁移改变了 id，再跑这个，后缀可能变**。注释里写「第一次运行和后续运行结果一致」，前提是中间不动 id。
- `card_id` 只由 frontmatter 内容派生，所以同一份 frontmatter 每次算同一个 id——但也意味着**改 frontmatter 里的 identity 字段就会换 id**，进而换 URL（静态站的详情页路径是 `/domain/card_id`）。

## migrate-conflicts

**语义**：回收已经收敛的 `import_conflicts` 记录，并把 `status: 冲突` 退回 `待核实`。

**参数**：位置参数 = domain（省略 = 全部领域），`--apply`、`--json`。

**逐条判定**（`decide`），六种 reason：

| reason | 条件 | drop |
| :-- | :-- | :-- |
| `unparsed` | 解析不出字段路径或值（历史手写格式、值里带分隔符） | 否 |
| `path_missing` | 字段已从卡上撤回（`_clear`） | 是 |
| `converged` | 现值 == 记录里的「新值」 | 是 |
| `kept_kept` | 现值 == 记录里的「保留」值 | 否 |
| `open` | 第三种值 | 否 |
| `superseded` | 同一路径有多条记录，非最后一条 | 是 |

记录行格式是 `ext.x: 保留「A」，新值「B」（来源）`。`parseLine` 去掉尾部括号来源，用 `」，新值「` 当分隔符，且要求**只出现一次**——出现两次就返回 null（值本身带这个分隔符）。这是「宁可留噪声也不静默销案」的具体实现。

同一路径留最后一条（最新一次导入记的），更早的标 `superseded`。

**只有 `kept.length === 0` 时才 `delete fm.import_conflicts`**（整字段删掉，不留空数组）并把 `status` 从 `冲突` 改回 `待核实`。还有残留记录时只覆盖数组。

**幂等**：收敛过一次的卡再跑，`would_change` 为 0。

**风险**：低。它只删 `import_conflicts` 数组里的记录，不动卡片的其他字段。唯一的行为副作用是 `status` 的改写，而那个只在记录全清空时发生。

## migrate-award-to-student

**语义**：把 `cards/award/` 的获奖名单并入 `cards/student/`。

**参数**：`--apply`。默认 dry-run 只打 JSON 统计。

**判「是不是同一个人」的四个判据**（顺序不可颠倒）：

1. 学号精确相等 → 同名才并；姓名不一致 = 不同人，另建卡。
2. 遮蔽学号（前 4 + 后 3）命中完整学号 → **必须同时姓名相等**才并。
3. 没有可用学号 → 姓名唯一命中一张**没有学号的待认领卡**才并。
4. 其余一律新建。

第 2 条的注释是这份脚本里信息量最大的部分：**单独遮蔽学号会大量撞车**（3 位未知 + 上千名学生，2026-10 实测 527 条命中里只有 31 条同名），所以「学号像」不是证据。第 4 条的后果：有完整学号写 `ext.student_id`，遮蔽学号写 `ext.student_id_masked`（只作展示，不进 identity），获奖信息写 `ext.award_records`。

**`--apply` 会做的事**（`apply()`）：
- 新建学生卡（已存在同 id 则跳过）。
- 合并进现有卡（按 `award` + `year` + `department` 三元组判重，重复不追加）。
- **把每张被判定的 award 卡 `renameSync` 进 `.trash/award-merge-<stamp>/cards/`**。
- 若 `cards/award/` 空了，`rmSync` 整个目录。
- 把 `domains/award.yaml` 也 `renameSync` 进 `.trash/award-merge-<stamp>/`。
- 写 `docs/获奖名单合并.md` 报告，以及 `.trash/award-merge-<stamp>/review.jsonl`（需人工看的少数派，含姓名/遮蔽学号，不进版本库）。

**风险**：**这是这一系列里唯一会删领域包的脚本**。`domains/award.yaml` 移走之后，`award` 领域就不存在了——任何还引用它的地方（`extends`、`sources`、旧链接）都会失效。虽然文件在 `.trash/` 里可恢复，但领域一旦从导航消失就不会有人注意到。

`--apply` 之后重跑：award 目录已空，`loadAwards()` 返回 `[]`，脚本安静退出，不会二次处理。

## migrate-tag-ids

**语义**：把卡片 `tags` 里残留的「旧式点分 ID」（如 `discipline:cs.ai.nlp`）按 `_taxonomy/*.yaml` 的 `legacy_id` 改写成新单段 ID（`discipline:nlp`）。

**开关是 `--write`**，不是 `--apply`。

三条红线写在文件头，且都有对应的自检夹具：

1. **严格限定在 tags 数组值内**。只认三种形态：顶层 `tags:`、`ext:` 下缩进的 `tags:`、academic 内联 JSON 的 `"tags": [...]`。`discipline:` / `topic:` 也是普通 frontmatter 字段名/值，**绝不做全局字符串替换**——夹具 `fixtureField` 里 `title: discipline:cs.ai.nlp` 这种必须一字不动，`r4.changes.length === 0`。
2. 默认 dry-run。
3. 映射真源是 loader 的 `legacyToId`，且**去掉根节点恒等映射**（`from !== to` 才算迁移）。新 ID 不是映射的键，所以对已是新 ID 的卡重跑天然命中 0 处。

实现是纯文本行扫描（`migrateText` 纯函数），不是 YAML 反序列化再序列化。理由是后一种会把 8000+ 张卡的 YAML 全部重排（键序、引号风格、缩进），产生整仓 diff。代价是要自己处理引号风格：`rebuildValue` 按原值是否是 `"` / `'` 包裹来决定新值的引号。

脚本自带离线自检夹具（跑一次就打印了几条 check、几条失败），不碰 cards/ 目录，只验迁移逻辑本身没被改坏。`failures.length` 时 `exitCode = 1`。

**风险**：中。它改的是**卡片文本**，如果某个 tags 数组的形态不在识别范围内（比如 flow 风格的 `tags: [discipline:a, discipline:b]` 单行 YAML），那些值不会被迁移，也不会报告——报告只说「0 处待迁移」。

## migrate-collected-at.mjs

**语义**：给缺 `collected_at` 的卡补值。字段改造后 `collected_at` 成为必填。

**没有 dry-run，没有 `--apply`，跑就写。**

取值顺序：有 `last_verified` 且形如 `YYYY-MM-DD` → 用它；否则取文件 mtime 的日期部分。

实现是**正则 + 纯文本插入**，不是 gray-matter 往返：`raw.replace(/^(---\r?\n[\s\S]*?)(\r?\n---)/, '$1\ncollected_at: "..."$2')`，插到 frontmatter 末尾。理由是避免重新序列化整个 YAML（同 `migrate-tag-ids`）。

**风险**：低-中。`pickField` / `hasField` 用的正则 `^${key}:\s*['"]?([^'"\n]+)['"]?\s*$` 只匹配**顶层**标量字段，`collected_at` 若已存在于嵌套结构里不会被识别为「已有」，会重复插入。实际风险很小（该字段本来就是顶层）。

硬编码只扫 `cards/` 下**一层**子目录（`readdirSync(CARDS_DIR)` → `statSync(dir).isDirectory()`）。三卡制后卡片在 `cards/<collect|info|report>/<子类型>/`，这个脚本现在只会扫到 `collect` / `info` / `report` 三个目录并因为里面没有 `.md` 而什么都不做——**静默失效，不报错**。

## backfill-source-body

**语义**：给正文为空的卡生成最小「来源」小节，数据来自 `frontmatter.sources`。

**参数**：位置参数 = domain（默认 `thesis`），`--apply`。

正文内容由 `buildSourceBody(sources)` 生成（在 `src/core/ingest.ts`）。只填空正文，已有正文的一律不动。打印前 10 条预览。

**风险**：低。但它**只处理一个领域**（位置参数只有一个），且默认值 `thesis` 在三卡制后已不是有效领域名（应是 `info_thesis`），不带参数跑会得到「共 0 张卡」而不是报错。

## backfill_timestamps

**语义**：从 git 历史回填 `created_at` / `edited_at`。

**参数**：`--domain X`、`--apply`。

**口径**：
- 只补缺失字段，已有值一律不动（新写入的时间比事后推算的更可信）。
- `created_at` = 该文件第一次进 git 的提交时间，`edited_at` = 最后一次改动。
- 没有 git 历史的卡（未跟踪）退回文件 mtime，报告里单独计 `from_mtime`。
- **只在 frontmatter 末尾追加两行**，不重新序列化整份 YAML——否则上万张卡全部改写。

`gitHistory()` 用一次 `git log --reverse --format=__C__%aI --name-only -- cards` 拿到所有文件的首次与末次提交，避免逐文件 fork。`maxBuffer` 开到 512MB，因为全库的 path 输出量很大。

`insertKeys` 是个脆弱点：它靠 `raw.slice(0, raw.length - content.length)` 切出 frontmatter 部分，再 `lastIndexOf('---')` 找闭合标记。这依赖 gray-matter 返回的 `content` 是 `raw` 的后缀——一般成立，但正文里如果有会被 gray-matter 处理掉的东西（比如开头被吞掉的空行），偏移就错了，那时返回 `null` 并计入 `parse_errors`。这是**静默跳过**而不是崩，所以报告里的 `parse_errors` 要真的看一眼。

`domainDir(domain)` 在这里是必须的：注释明说「三卡制后领域名与目录不同段，`--domain info_mentor` 会去找 `cards/info_mentor`（不存在）」。目录不存在时 `exit 2`（注意是 2，不是 1）。

**风险**：低。只加两个字段，不改原有内容。唯一实质影响是给所有卡引入 `created_at` / `edited_at`——`writeCardFile` 之后会把这两个字段当生命周期字段排除在「内容指纹」之外，但这里是直接 `writeFileSync`，不经过 `writeCardFile`，所以指纹会变一次。

## prepare-courses

**语义**：课程大纲目录 → `inbox/courses.jsonl`（一行一门课），再交给 `card_import` 落盘。

**参数**：位置参数 `[源目录] [输出 jsonl]`，默认 `raw/课程大纲` → `inbox/courses.jsonl`。

**三种输入各自处理**：
- `.doc`（Word 97 二进制）：先经 Word COM 批量转成 docx 并缓存（`inbox/.course-docx/`），转换按**内容 md5 去重**。
- `.docx` / `.pdf`：直接走 `src/core/parsers`。
- `.har`、压缩包：不是课程材料，报告里列为 unsupported。

**两层去重**：
1. 内容完全相同（md5）只保留一份，同组按格式优先级 `{.docx: 0, .pdf: 1, .doc: 2}` 再按路径长度挑最优。
2. 同一课程代码的不同文档（简介 + 教学大纲）各出一行，由领域包 `identity.strong = ext.course_code` 在 `card_import` 里合并成一张卡。

字段映射是硬编码的 `META_TO_FIELD`：`课程代码` → `ext.course_code`、`学分` → `ext.credits`、`总学时` → `ext.hours_total` 等十个中文字段名。改领域包不会改这里。

输出两个文件：`inbox/courses.jsonl` 与 `inbox/courses-report.txt`（含跳过、失败、同码多文档分组）。

**破坏性**：写 `inbox/`（gitignore），调用 Word COM（外部进程），不碰 `cards/`。

## import-jsonl

**语义**：`card_import` 是 MCP 工具，命令行里没有入口。这个脚本是固定下来的本地 runner。

**参数**：`<jsonl> <domain> [--write] [--merge] [--max-updates N]`。

默认 `dry_run: false` 的反面——`dry_run: !write`，即**默认预演**，只有显式 `--write` 才落盘。`--merge` 映射成 `strategies: {on_duplicate: 'merge'}`。

它起一个真实 stdio MCP server（`node node_modules/tsx/dist/cli.mjs src/mcp/server.ts`），通过 SDK 调 `card_import`。`MCP_TIMEOUT_MS` 环境变量可覆盖 SDK 的默认 60s——批量导入一轮就是几千行读写，默认超时会在服务端写完之前掐断客户端。

报告的呈现做了裁剪：`sample` / `anomalies` / `risks` / `columns` / `clears` 这些大字段不直接进输出，`anomalies` 按 type 分组计数后只打非 `duplicate` 的前 8 条。这是给人和 LLM 读的输出，不是给机器解析的。

**风险**：`--write` 时走内核，有安全阀（`max_updates` 超了 `ok: false`，一张都不写）。默认不带 `--write` 完全安全。
