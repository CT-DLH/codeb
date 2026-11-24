---
covers:
  - scripts/audit-publish.ts
updated: 2026-11-17
---

# Publish gate: how audit-publish catches a leak

`scripts/audit-publish.ts` 是发布链路的最后一步，也是唯一会因为「内容不对」而失败的一步。它的判定方向与直觉相反：**不相信代码里剥过一遍**，而是拿 `cards/` 里的真值反过来去产物里找。

## 为什么判据在产物侧

敏感值的出口不止 `card-store` 一条：别的领域可能把同一个号码写进普通字段、正文里又抄了一遍、`static/data` 分片里还有一份。代码里逐条剥离等于要求每一处出口都记得剥——漏一处就公开一次，而且部署是一次性动作。

所以门禁做在产物侧：**拿 `cards/` 里标记了 `sensitive: true` 的字段真值当探针，逐个在 `build/` 里搜**。

## 探针怎么取

真值来源分两步：先按领域包算出「敏感字段路径」，再逐卡把这些路径上的值取出来。

`sensitivePathsOf(domain)` 递归走 `loadDomainSpec(domain)` 的 `extFields` 与 `baseFields`，把 `sensitive: true` 的字段收集成相对卡片对象的路径。它支持三种粒度，与 `src/lib/sensitive.ts` 同口径：

| 形态 | 路径示例 | 说明 |
| :-- | :-- | :-- |
| 顶层字段 | `ext.phone` | 最常见 |
| object 子字段 | `ext.guardian.phone` | 只标子字段不会把整列抹掉 |
| 数组项子字段 | `ext.family[].id_card` | `[]` 后缀表示「数组每一项再取」 |

路径前缀区分来源：`ext` 下的加 `ext.`，base 字段（`title`/`summary` 这类）不加前缀。

`valuesAt(card, path)` 按 `.` 逐段下钻，遇到 `[]` 后缀就把数组摊平。只收 `string` 与 `number`——布尔和对象不当探针（对象没法直接做子串匹配）。

**卡片目录必须走 `domainDir(domain)`**。三卡制迁移后目录是 `cards/<collect|info|report>/<子类型>/`，与领域名不同段。这里有一段被反复引用的历史：早先写的是 `join(CARDS_DIR, domain)`，迁移后每个领域都 `existsSync=false`，于是 `continue` 跳过，报告显示「卡片里带敏感值的 0 张」，被当成干净结果——**门禁静默失效，实测漏掉了导师电话/地址**。代码里为此留了注释，是这条路线上最贵的一个坑。

## 短值不当探针

`MIN_NEEDLE_LEN = 6`。短于 6 位的值列进 `skipped` 并从探针池剔除——「1」「3」这种值会命中任何一份 HTML 里的任意数字，噪声会淹没真正的问题。

报告会按字段分别统计：`N 张卡有值 / 长值 X 条当探针 / 短值 Y 条不扫（当探针会到处误报）`。

## 扫什么目录

`BUILD_DIR` 默认 `<root>/build`，可被 `process.argv[2]` 覆盖。

`listBuildFiles()` 先 `glob('**/*')` 拿到全部文件，再按白名单过滤：

| 归入扫描 | 理由 |
| :-- | :-- |
| `*.html` | 预渲染页面，正文与字段都在里面 |
| `*.json` | 分片、SvelteKit 的 `__data.json`、API 响应 |
| `api/` 前缀（无扩展名） | `/api/cards/{domain}/{card_id}` 预渲染成同名文件，是卡片 JSON |

| 跳过 | 理由 |
| :-- | :-- |
| `_app/` | 框架打包的 JS，不含卡片内容 |
| `pagefind/` / `_pagefind/` | 索引是 brotli 压缩的，读不出明文；它的输入就是那些 HTML，HTML 干净则索引干净 |

跳过的部分不假装扫过：报告里按顶层目录分组给出「跳过 N 个非内容文件（`_app/…`、`pagefind/…`、根目录/…）」，并明说不扫 pagefind 的原因。

## 一次正则扫全部探针

不是逐探针 `includes`，而是把去重后的探针值拼成一个 alternation 正则（`buildScanners`）：

- 纯数字/`X` 串（身份证、手机号）单独包一层 `(?<!\d)(?:…)(?!\d)`——不加边界的话 `13800001111` 会命中 `138000011112`。
- 非数字值直接 `escapeRe` 拼进去。
- 按长度降序排列，长的先匹配。

这比逐个 `includes` 快一个量级（实测从「分钟级」降到可接受）。匹配结果再 `new Set(...)` 去重，因为同一张卡的值会在 HTML、`__data.json`、分片 JSON 里各出现一次——所以报告给的是「N 个文件」，不是「N 次命中」。

## 阳性对照：让「没扫到」不等于「干净」

这是整个脚本最容易做错、也最关键的一段。

`blind` 数组：对每条探针，都要能在它**自己的卡片源文件**里扫到。做不到就进 `blind`，报告打 `阳性对照 ❌` 并强制失败。

两个细节都来自真实故障：

1. **路径口径**：`card` 记的是「项目根相对路径」（`cards/info/mentor/001.md`），所以对照时 `join(ROOT, card)`。再套一层 `CARDS_DIR` 会拼成 `cards/cards/info/...` 而读不到，阳性对照全盲。注释里还专门写了「用 `relative()` 而不是切片：ROOT 的结尾形态（有无尾斜杠）决定切片偏移」。
2. **对照用重新解析而不是原文子串**：`matter(text).data` 再 `JSON.stringify`，然后 `includes(value)`。因为 YAML 会给值加引号、转义，原文里搜不到不代表探针坏了。

`unreadable` 计数：扫产物时任何文件读取失败都 +1（只打印第一条错误）。读不到就等于没验过，必须阻断——不能让「一个文件都没扫」伪装成「扫了很干净」。

## 两种模式与 INFOHUB_SENSITIVE 三态

脚本跑在 tsx 里，探不到 vite 注入的 `__BUILD_STATIC__`（`localRuntime()` 返回 false），所以**默认就是部署口径**。`INFOHUB_SENSITIVE` 是显式覆盖，判定走 `src/lib/sensitive.ts` 的 `showSensitive()`：环境变量存在时按 `TRUTHY = {1, true, yes, on}` 判真，存在就压过形态默认。

| `INFOHUB_SENSITIVE` | `show` | 判定 | 失败条件 |
| :-- | :-- | :-- | :-- |
| 未设 | false | 剥离（部署口径） | 任一探针值在 `build/` 里**找得到** → `leaked.size > 0` |
| `=0`（或 `false`/`no`/`off`） | false | 同上，与未设完全一致 | 同上 |
| `=1` | true | 显示（本地核对口径） | 有探针但**找不到** → 有值没进产物（标记生效了但渲染漏了字段） |

`=0` 与未设行为一致这件事是有意的：`=0` 的用途是「让本地服务预演发布口径」（`serve-local.mjs` 那一侧），而对本脚本来说它只是把默认值显式写出来。

显示模式下还多一条保护：`needleValues.size === 0` 时输出「没有任何敏感值可验（先标记字段并导入数据）」，**不算失败**——因为「没数据可验」和「数据丢了」是两回事，但前者会让后者永远测不出来。所以 `export:static:local` 必须是「先导入过带敏感值的数据」再跑才有效。

## 具体判定与退出码

```
unverified = blind.length > 0 || unreadable > 0
failed = unverified
           ? true
           : show ? (needleValues.size > 0 && 有值找不到)
                  : leaked.size > 0
if (failed) process.exit(1)
```

三条失败路径，语义各不相同：

| 失败原因 | 含义 | 处理 |
| :-- | :-- | :-- |
| 探针读不到（`blind`） | 体检本身不可信 | 先修路径口径，别读结论 |
| 产物文件读不到（`unreadable`） | 同上 | 查权限/句柄 |
| 剥离模式命中泄漏 | 真的漏了 | 判是标记漏了、还是同一串号写进了正文/别的领域 |
| 显示模式值缺失 | 标记生效但数据丢了 | 查渲染链路 |

成功路径不打退出码（0）。

`BUILD_DIR` 不存在时先 `exit 1`，提示「先跑 npm run build」。

## 报告形态

不打探针原值——报告是要被读进对话的，回显就等于泄漏。`mask()` 只给形状：`${前 2 字符}…${末 1 字符}（N 位）`。

输出分六段：模式行、领域包标记字段清单、卡片与探针计数（按字段分组）、扫描/跳过文件数、阳性对照结论、结果。命中时每条给「哪张卡 · 遮蔽值 · N 个文件 · 例如 <首个文件>」。

## 实测抓到过的问题

- **导师电话/地址**：三卡制迁移后 `join(CARDS_DIR, domain)` 全部指向不存在的目录，门禁静默失效，这两列值一路进了产物而报告显示干净。修复方式是改用 `domainDir()`，并加了阳性对照。
- **未标记号码的噪声**：早期版本把「任意 18 位 / 11 位数字串」也当判定对象，采集正文里的文章 ID、徽章里的服务器 ID 全被误判成手机号。现在**只看标记字段**，未标记的号码不参与判定（材料里的 PII 靠「先在领域包标 `sensitive` 再导入」兜住，采集正文另用 `npm run scan:pii` 在落卡前扫）。
- **`static/data` 分片里的值**：分片直接进站点产物，与页面走同一条边界，所以 `build-data.ts` 里 `redactCard` 必须用 `structuredClone`——`card.ext` 与 `result.data.ext` 是同一个引用，就地删字段会连本次校验用的对象一起改掉。

## 当前标记了哪些字段


标记清单不在这里抄一份——它是领域包的产物，抄下来就是第二真源。查法：

```
grep -n "sensitive:\s*true" domains/*.yaml
```

2026-11-17 实测的结果（带日期，记录当时的覆盖面）：

| 领域包 | 字段 |
| :-- | :-- |
| `info_mentor` | `ext.phone`、`ext.address` |
| `info_student` | `ext.email`、`ext.id_card`、`ext.phone`、`ext.insurance_note`、`ext.origin_region` |
| `_info`（父包） | `ext.roster_email` |

`info_student` 的两个派生字段（`insurance_note` / `origin_region`）也标了敏感——提取出来的推断值同样是隐私。

`audit:publish` 每次运行的第一段报告就是「领域包标记字段 N 个：…」，那是唯一实时的清单。
