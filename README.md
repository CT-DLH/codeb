# codeb

给 LLM 维护的多仓库知识库。**结构少到不会用错，写入便宜到愿意写。**

## 它解决什么问题

改了代码之后，「这段为什么这么写」的知识存在人脑和聊天记录里，下次换一个会话就没了。
把这个知识写进仓库的 Markdown 又太贵——不知道写哪、不知道有没有写过、写完了没人看。

codeb 只做三件事：

1. **让读便宜**：`kb tree` 用几十 token 看清全库，`kb read --section` 只取一节（约 150 tok）。
2. **让写便宜**：`kb upsert` 命中即更新、miss 即补充，不用想「该放哪」。
3. **让模型自己维护**：MCP 工具直接暴露上面这些能力，模型边干活边写。

## 结构

```text
.codeb              根标记（空文件）
kb.py               内核：所有规则只有这一份实现
mcp/server.ts       MCP 层：只声明工具、调内核
mcp/smoke.ts        端到端测试
distill/            离线收割历史会话：sessions.py（素材）+ distill.py（候选）
repo/
  _shared/          跨仓库知识
  codeb/            本工具自己的知识库（设计决策、MCP 用法）
  <repo>/           每个仓库一个英文名目录
    overview.md
    <topic>/        按源码路径折叠，不平铺
```

注意 `repo/codeb/`：**这个工具也给自己建了知识库**。
它记录的是「为什么这样设计」「推翻过哪些方案」，属于读代码看不出来的那部分。

**四条强制规则**：

1. 根下必须有 `.codeb`，页面都在 `repo/` 下。
2. `repo/` 第一级目录 = 一个仓库，用英文名。
3. 文件名用英文小写连字符。
4. **标题用英文，正文用中文。**

第 4 条的理由：导航输出会反复进入模型上下文，英文更省 token、不会出现同一概念三种译法；
正文是知识载体，用中文。`kb tree` 会在英文标题后附一行中文首句提示，把两者接上。

## 命令

```bash
python kb.py init                     # 建骨架
python kb.py tree                     # 下行浏览（折叠 + 中文提示）
python kb.py tree --repo infohub      # 只看一个仓库
python kb.py tree --flat              # 忽略 parent，回到纯目录树
python kb.py heads infohub/overview   # 列出所有标题
python kb.py read infohub/overview --section "Directory map"
python kb.py search 软404              # 空白不敏感
python kb.py where collector/kit/paging.py   # 上行反查
python kb.py graph                    # covers 投影成页间图：hub/孤立页/重复覆盖
python kb.py plan                     # 散落各页 ## 计划 的条目，状态现场算
python kb.py plan close P-xxx --into <页> --section <节> --body-file f.md
python kb.py pack collector/sites/     # 装订一份上下文册子（stdout，不落盘）
python kb.py pack collector/kit/paging.py --budget 8000
python kb.py pack collector/kit/paging.py --no-source   # 只要知识，不要源码（省约 75%）
python kb.py dispatch collector/kit/ collector/refs/   # 派发前查冲突
python kb.py upsert ...               # 唯一写入口
```

所有命令都支持 `--json`（MCP 层依赖它）。

### 装订上下文：给改某个模块的人一个册子

`kb pack <scope>` 现场算出一份册子：目标源码 + 点名这个文件的**知识小节** +
同目录其它文件的签名大纲 + 该模块的 `## 计划`，最后附一节「有意省略」
（什么没装、用哪条命令取回）。

```bash
python kb.py pack collector/sites/        # 8794 tok / 25 块 / 精度 exact
python kb.py pack kb.py                   # 2552 tok（1432 行只给大纲，17k 全文塞不下）
python kb.py pack collector/kit/paging.py --no-source   # 1764 tok（砍 75%）
```

不落盘，每次都重算——落盘的册子会在工单改了而没重新生成时静默说谎。

`--no-source` 是给「改这个有哪些坑」这类问题用的：源码常占总量的 75%，
而答案在知识层。它不能靠压预算实现——**降预算会先把知识层丢掉**，
所以「省钱」和「只要知识」是相反的方向。

### 派发：切开之前先看会不会撞车

```bash
python kb.py dispatch collector/kit/ collector/refs/ collector/sites/
```

查四件事：写范围两两是否冲突、哪些知识页被多个范围共享、接口面（改签名要通知谁）、
串行点（由别的脚本生成的派生文件）。

实测 `collector/` 下 7 个子范围写范围全部互斥，但**全部命中同一个串行点**
`collector/capabilities.json`——加任何一份站点 spec 都要重跑 `capabilities.py --write`。
7 个 agent 各跑一次，最后只剩一个人的结果，其余 6 个新站从能力清单里静默消失。
所以这条从「各卡提醒」升级成全局 `serial_bottlenecks`：各 agent 只改源文件，
由 leader 在并回后统一重生成。

### 仓库根写在 frontmatter 的 `root:`

`covers` 写的是仓库内相对路径，但代码在磁盘上的位置推不出来
（`atomkgraph` 在 `knowledge_map/` 下面）。所以在一个页面的 frontmatter 写一行：

```yaml
root: D:/work/project/knowledge_map/atomkgraph
```

它是**坐标不是分类**：写错时 `pack` 立刻报「定位不到磁盘根」并列出已知映射，
而分类标签填错了没人看得出来。实测这让可解析的 covers 从 114/163 提升到 217/223。

### 计划：散落在各页，状态不写进文件

计划不是独立文档，条目就写在该模块对应页面的 `## 计划` 小节里：

```
- [ ] P-<slug> 一句话说清改什么 — done: <锚点>
```

**只允许 `[ ]` 和 `[-]`，写了 `[x]` 会被拒收。** 「已实现」是关于代码的断言，
只能由代码本身证实；手写 `[x]` 会在功能被回退或从未落地时静默骗人。
锚点三种：`path a.py, b/`、``grep kb.py `正则` ``、`none`（进 manual 交人判）。

`kb plan` 输出四桶：`open` 待做、`partial` 做了一半、`manual` 需人判、
`stale` **代码里已存在 → 该收编进知识后删条目**。

关闭必须走 `kb plan close`，它强制**先写知识、成功后才删条目**。只删行会丢掉
「为什么当初要做它」，而那是计划里唯一读代码读不出来的部分。

### 多会话写入是安全的

`kb.py` 的写入有全库文件锁 + `os.replace` 原子替换，覆盖整个「读→改→写」。

这是补过一个真实缺陷：早期没有锁，实测 20 个并发写同一页的不同小节，
**20 个全部报成功，最终只剩 8 个小节，静默丢 12 个**。加锁后 40×3 轮并发 0 丢失。

两个必须知道的边界：

- 锁是**建议锁**，只约束同样走 `kb.py` 的进程。直接改 `.md` 不受保护，
  所以写入必须始终保持单一入口。
- Windows 上 `os.replace` 与并发读取会双向撞 `PermissionError`（共享冲突），
  写端与读端都已加重试吸收。

### 写入

```bash
# 新建：topic 决定折叠到哪个子目录
python kb.py upsert --repo infohub --topic collector --title "L1 primitives" \
  --covers collector/kit/ --body "正文..."

# 命中：替换某一节（该节不存在时自动追加）
python kb.py upsert infohub/collector/l1-primitives --section "Testing" --body "..."

# 命中：追加到文末
python kb.py upsert infohub/collector/l1-primitives --append --body "..."
```

## 接入 MCP

项目根的 `.mcp.json` 已经写好，把里面那段粘到你的 MCP 客户端即可：

```json
{
  "mcpServers": {
    "codeb": {
      "command": "node",
      "args": ["D:/work/project/codeb/mcp/server.ts"],
      "env": { "PYTHONIOENCODING": "utf-8" }
    }
  }
}
```

需要 Node 24+（能直接跑 `.ts`，**没有构建步骤**）。
Python 解释器默认取 `python`，可用环境变量 `KB_PYTHON` 覆盖。

工具清单：`tree`（通用树，view=kb 架构树 / view=source 源码目录树）/ `kb_read` / `kb_heads` / `kb_search` / `kb_where` / `kb_upsert`。
`tree` 的 kb 视图即旧的 `kb_tree`，默认视图不变。

## 收割历史会话（distill/）

上面的调用顺序假设「在场的那个 agent 会主动写」。**它不会**——写入对未来会话才有回报，
对当前任务只有成本，而且"收工前记得写"里的收工时刻对 agent 不可观测。

`distill/` 是这条缺口的兜底，离线跑，把历史会话里的知识捞出来：

```bash
python distill/sessions.py material --cwd codeb -o _kbwork/materials.jsonl
python distill/sessions.py report   --cwd codeb -o _kbwork/report.md
python distill/distill.py --materials _kbwork/materials.jsonl --report _kbwork/candidates.md
python distill/distill.py --materials _kbwork/materials.jsonl --id 1 --apply   # 才落库
```

它只产出**候选**，落盘仍走 `kb upsert` 这个唯一写入口。六道闸门决定一条候选能不能写：
`kb where` 去重、路径必须真实存在、骨架正文与审计线索默认拒绝落库、
**正文里提到的文件必须能在磁盘上核到**、**正文不能是占位符/模板空壳**。

后两道是必要的：实测模型会把"这类项目通常怎么实现"当成"这个项目就是这样"，
一次就编出 9 个不存在的模块。没编路径但整页是 `[工具文件名 5]` 这类占位填充的也一样要拦。
证据不足时正确结果是 0 条可落库，而不是硬凑一页——噪音页比缺页更糟。

### LLM 配置

`--llm` 默认 `nvidia`，配置**复用 infohub 那一份**，不复制也不要另建：

- 真源 `D:\work\project\infohub\collector\.env`，键名 `ZHIHU_LLM_*`
  （base_url `https://integrate.api.nvidia.com/v1`，
  model `nvidia/nemotron-3.5-lightning-30b-a3b`）
- 只读 `ZHIHU_LLM_*`，因为该文件还有 BILI_COOKIE / XHS_COOKIE 等无关凭据
- 必须传 `chat_template_kwargs.enable_thinking=false`：推理型 Nemotron 不关 thinking
  会先吐 `reasoning_content` 把 `max_tokens` 吃光，`content` 变成空串
- `--llm none` 可离线只出线索；`--verbose` 打印失败原因

详见 `repo/codeb/distill/`。

## 验证

```bash
node mcp/inspect.ts    # 打印握手结果与八个工具的入参（排查客户端配置问题先跑它）
node mcp/smoke.ts      # 75 项断言，走真实 stdio 协议，跑完自己清理
```

## 调用顺序（重要）

```text
1. tree（view=kb）        看清全库（约 971 tok）；看源码目录用 tree view=source
2. kb_where <源码路径>     这次要改的东西归谁管？
3. 有命中 → kb_read <页> --section    确认现有内容
   无命中 → kb_read <最相关的页>       看邻居怎么写的
4. kb_upsert              按上一步结果更新或新建
```

**第 2 步不能跳。** 跳过就会产出重复页，而重复页一旦出现，两页都不再权威。

要**派活**给别人时，顺序换成：

```text
1. kb_dispatch <范围A> <范围B> ...   能不能并行、会撞什么
2. kb_pack <范围>                    给每个执行者装订各自那一份
```

详细说明见知识库：`repo/codeb/connect-client`、`repo/codeb/pack-and-dispatch`。

## 设计文档

`DESIGN.md` 是规格。工具必须服从它，反过来不成立。

## 依赖

- Python 3.11+（只用标准库，无需安装任何包）
- Node 24+（仅 MCP 层需要）
- `distill/sessions.py` 解码 `.zstd` 会话需要 `zstandard`（已装则自动用；
  没有则退回 `zstd` CLI，用文件重定向而不是管道）
- `distill/distill.py` 调 NVIDIA 走标准库 `urllib`，**不引入 openai SDK**
