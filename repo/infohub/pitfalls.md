---
covers:
  - start.bat
  - svelte.config.js
  - vite.config.ts
  - .github/workflows/deploy.yml
  - src/mcp/lib/storage.ts
  - src/lib/server/card-store.ts
  - src/lib/schemas.ts
  - scripts/migrate-card-ids.ts
  - scripts/audit-publish.ts
  - pipelines/
updated: 2026-11-18
---

# Pitfalls

按「踩到的频率」排序，不按时间。每条都写**症状**（怎么发现的）和**原因**，
因为症状相似但原因不同的坑，处理方式完全相反。

## Assuming a card edit needs a rebuild

**症状**：改了一张卡，执行 `npm run build` 等了 40 秒，或者更糟——跑了 `export:static`，
结果 `static/data` 被重写，git 里冒出一堆无关 diff。

**原因**：使用模式（`npm start` / `npm run dev`）每次请求实时读 `cards/`，改卡刷新即见。
只有改 **Svelte 组件或样式**才需要重建。`export:static` 是发布动作，不是日常动作。

**判断**：改的是 `cards/` 或 `domains/` → 刷新即可；改的是 `.svelte` / `.css` → 重建。

## Cards written, list shows zero

**症状**：MCP 写入返回成功，`cards/` 里也确实有文件，但页面上查不到。

**原因**：`domainDir()` 的映射在**两个地方各有一份**——`src/mcp/lib/storage.ts`（写）
与 `src/lib/server/card-store.ts`（读）。不一致时就是「写进 A，读取找 B」，
**不报错，只是静默为空**。

**检查**：先看写入的 domain 名（如 `info_student`）经 `domainDir()` 会映射到哪个目录，
再确认读取层用的是同一条规则。三卡制迁移后目录是三层，`domain` 是单段带前缀，这个转换只有那一处正则。

## Static export without the publish gate

**症状**：`build/` 里有敏感字段值。

**原因**：`export:static` 末尾的 `audit:publish` 是门禁，漏一条就导出失败。
但有人会跳过整条 `export:static` 只跑 `build:site`，那样门禁不执行。

**正确**：发布只用 `npm run export:static`（或别名 `npm run build`），不要拆开跑其中几步。

## Forgot to reset after a local export

**症状**：之后某次正常导出，产物里带着敏感值。

**原因**：`export:static:local` 会生成带值的静态产物。核对完必须跑 `npm run build:data` 复位。

## Bulk loading a table with per-row card_create

**症状**：几十行的材料，跑到中途失败，报转义错误。

**原因**：桥接层对 raw 代码块和长字符串的转义不可靠，实测失败 5 次。
**任何长文本写入必须走文件路径参数**，不进 `content` 参数。

**正确**：表格给 `card_import`，单条长文本给 `body_file`。

## Hand-editing domains YAML

**症状**：改完刷新，字段没生效，或者校验报错但说不清哪错。

**原因**：手改绕过了元 Schema 校验与往返验证（`domain_create` / `domain_update` 做的那些检查）。

**正确**：用 `domain_update`。它支持增删字段、改 `summary_columns`、设 `dedup_key` / `identity` / `attachments`。

## Trying to inherit two parent packs

**症状**：`extends: [person, _info]` 这种写法不生效。

**原因**：`extends` **只接受单父包**（`src/lib/schemas.ts`）。
这不是疏忽，是限制；项目的应对方式是把 `person` 的字段并入 `_info`，保留 `person` 不删以免断引用。

**正确**：字段并进需要继承的那个父包，而不是想办法多继承。

## identity template changed, card_id did not

**症状**：改了 `card_id_pattern`，新导入的卡还是旧格式 id，或者同一实体被建了第二张卡。

**原因**：模板只影响**新写入**，已有卡不会自动迁移。

**正确**：`npm run migrate:ids -- <domain> [--apply]`（默认只预演）。
模板里用 `{hash:weak}`，**不能用随机数**，否则幂等失效、重复导入会重复建卡。

## Masked student IDs used as a strong identity

**症状**：1872 行导入后合并出一堆错卡。

**原因**：公示表里的学号是**遮蔽过的**（`2023***071`），批内重复 346 组，本身不唯一。
拿它当强标识会让不同学生被合并。

**正确**：用姓名 + 学院 + 奖项 + 年度 + 学号的**弱标识组合**；强标识冲突交给工具拦进 review。

## Array fields split wrongly for multi-row entities

**症状**：「中国茶、酒文化与健康」被顿号拆成三门课。

**原因**：数组字段默认按分隔符拆。

**正确**：`split: false` 关掉拆分。多行一实体的数组字段（如未评课程、奖项）按**并集累加**。

## PDF imported as a table, columns misaligned

**症状**：`pdftotext` 出来的表格列对不齐，数据串列。

**原因**：PDF 表格没有真正的列结构，得**逐页定列**。

**正确**：`pdftotext -table` 加逐页定列。公示类材料不用先由 AI 拆成 jsonl，可以直连 `card_import`。

## Long-run collection blowing the context budget

**症状**：LLM 加工时超上下文，或输出质量崩塌。

**原因**：导师卡的「科研论文」小节中位数 2.8 万字，整段 body 会超预算，
还会让模型拿论文列表编简介。

**正确**：用 `source_sections` 只取需要的正文小节。关联原文超预算时**按相关性挑块，不许从头截**——
实测从头截 2 万字只保住 63% 关键行，按「命中词数 / √块长」挑块，8 千字就能到 100%。

## Placeholder text sent to the model as material

**症状**：生成的简介是漂亮但空洞的一句话。

**原因**：主页抓来的「个人简介」有一批是占位（「主页未提供个人简介栏目。」12 字、网址 11 字）。
拿它请求模型，等于用「不补内容」这条硬规则换一句漂亮话。

**正确**：`source_min_chars` 厚度闸——小节正文合计不够就不请求模型，直接跳过。
字数只算小节正文，不算 `### 小节名` 标题行。

## README drifting from the code

2026-11-16 实测，README 里这些数字已经落后：

| README 说 | 实际 |
| :-- | :-- |
| 3479 张卡片 | **14923** |
| student 1179 张 | **3019** |
| 21 个 MCP 工具 | **24** 个 |
| 领域名 `person`/`thesis`/`job` | `info_*` / `collect_*` 带前缀 |

另外 README 第 31 行有一行目录树被误插进了正文（`采集迁移.md` 那行），是编辑事故。
**遇到数字冲突时以代码和实测为准，不要信 README。**

## Config option wired, data path not

## 配置开关接上了，数据通路没接上

最贵的一类 bug：配置开关被读取、被判断、被写进日志，**但它本该携带的数据从来没送到消费方**。开关看起来生效了，实际只是让流程走了另一条同样空洞的分支。

实测（`scripts/batch_llm.ts` 的 `source_sections`）：配置解析对了、小节也按名字取出来了、`source_min_chars` 厚度闸还照着它算字数——但拼 user 消息的那行写的是

```ts
const userText = source || sourceSections ? sourceVal : '请按系统提示输出 JSON。';
```

`sourceSections` 在这行里只是**判断条件**，真正送出去的是 `sourceVal`（`source` 字段的值）。于是当配置只给了 `source_sections` 时，`sourceVal` 是空串，模型收到的是那句兜底话术。整批输出看起来「像是模型编的」，其实是模型**没收到任何材料**。

判据：**凡是「新增了一个取材料的来源」，都要亲眼确认材料出现在发送给模型的字符串里**。看三点：① 取数函数返回值非空；② 该值被赋给 user 消息变量（不是只出现在条件里）；③ 日志/预演里能看出材料长度。三者缺一就是这类 bug。

同一个道理适用于「闸计数的口径」：`readSectionsWithSize` 返回 `chars` 时**只算正文、不算 `### 小节名` 标题行**——否则厚度闸会把一节空内容判成「够厚」，又是一个接通了但量错的例子。

## 用 PowerShell 读写 JSON 配置会静默改坏文件

`Get-Content x.json | ConvertFrom-Json | ConvertTo-Json` 做配置改写会**破坏原始结构**：对象键序变化、单元素数组被压成标量、深嵌套被重排。改完看起来是合法 JSON，配置却已经不等价了。

同理，PowerShell 的 `.ps1` 里含中文时，脚本内容可能被按错误编码读入，中文小节名变成乱码——而小节名正是 `source_sections` 的匹配键，于是「取不到材料」又不报错。

口径：**改 JSON 用 Node**（`JSON.parse` / `JSON.stringify`），做批量分析用 `.mjs` 而不是 `.ps1`。PowerShell 只负责发起命令，不负责处理带结构的文本内容。

## A guard passing is not evidence the output is right

`grounding` 证明的是「输出里的每个词都能在材料里找到」，**不证明材料是对的**。源字段本身是连写残片、截断标题或拼写错误时，模型忠实抄写就会一路绿灯。

所以「输出看着荒谬却过闸」的正确反应是**去看源字段**，不是调阈值。反过来，为了让几张卡过闸而放宽全局阈值，就是把闸的价值一次作废（被拦下的样本通常正是它的证据）。正确兜底是人工核写那几张：`card_batch` + `note` 写明「闸拦下的原因 + 人工依据」，复盘时能区分模型写的与人写的。
