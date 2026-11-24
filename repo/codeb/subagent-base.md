---
title: The subagent base: pi-agent-core vs a 253-line loop of our own
covers:
  - distill/agent/loop.py
  - distill/agent/pi_probe.mjs
updated: 2026-11-20
---

# The subagent base: pi-agent-core vs a 253-line loop of our own

结论先给：**用 pi 的思路，不用 pi 的包。**

> 本页只对比了 pi 与自己写，**没先盘点其他基座**。全量实测见
> `codeb/agent-base-survey`——那里量了 9 个候选的真实行数与依赖，
> 结论是：单 agent 自己写，**要派子 agent 就用 `openai-agents`**。

pi-agent-core 确实能接我们的 NVIDIA 端点，工具调用也跑通了（实测 10.1 秒、2 次工具调用、
答案正确）。但它的代价是 73 个目录 / 85.6 MB `node_modules`，而我们要的能力
写出来只有 253 行、零依赖、直接 import `kb.py`。

## 实测：pi 跑通了，而且暴露了一个真实缺陷

```text
=== pi-agent-core 接 NVIDIA 实测 ===
  [tool] kb_tree({"repo":"None"})      ← 注意这个
  [done] kb_tree isError=false {"ms":518,"bytes":114}
  [tool] kb_tree({"repo":"infohub"})
  [done] kb_tree isError=false {"ms":560,"bytes":15959}
该知识库包含 1 个仓库（infohub），infohub 仓库下共有 46 页。
耗时 10097ms，触发工具调用: true
```

`"repo":"None"` 是模型把**可选参数**填成了字符串 `"None"` 而不是省略它。
pi 原样透传给工具，工具就查了一个叫 "None" 的仓库。第一次返回 114 字节
（空结果），模型自己发现不对又重调了一次。

这不是 pi 的 bug，是所有 agent 框架的共同处境：**模型会塞垃圾到可选参数里**。
差别在于谁负责吃掉它。我们的做法是每个工具入口过一个 `_s()`：

```python
def _s(v):
    if v is None: return None
    s = str(v).strip()
    return None if s.lower() in ("", "none", "null", "undefined") else s
```

一条规则挡掉五种写法。这比在 schema 里写 `"可省略"` 有用。

## 为什么不用 pi 的包：代价量化

| 项 | pi-agent-core | 自己的 loop.py |
| :-- | :-- | :-- |
| 代码 | 458 + 398 + 278 行（loop + agent + proxy） | 253 行 |
| 依赖 | 73 个目录 / 85.6 MB（pi-ai 把所有 provider 打进来） | 0（标准库 + kb.py） |
| 语言 | Node + TypeScript | Python，能直接 `import kb` |
| 工具调用成本 | 每次 spawn python 子进程 261ms | 进程内 `kb.main()` 54ms |
| 改折叠策略 | 写 `transformContext` 钩子，只能操作消息数组 | 直接改 `Ledger`，保留结构化身份 |

pi-ai 4.5 MB 解包体积里，绝大部分是 Bedrock / Google / Mistral / Copilot 的 provider。
我们只用 OpenAI-compatible 一家，这些一行都不执行，但要装、要审、要跟着升级。

而且这两个包已经改名：`@mariozechner/*` 0.73.1 装的时候 npm 直接警告
`please use @earendil-works/pi-agent-core instead going forward`。新包 1.6.0
把依赖又拆成 `pi-ai` + `pi-schema` + `pi-telemetry` 三个。

## 真正值得抄的是 abstractions，不是代码

pi 有五个设计是对的，独立于它用什么语言实现：

1. **`AgentTool` = name + parameters + execute**。没有 class 继承、没有注册表、
   没有插件生命周期。工具就是一个带 schema 的函数。
2. **失败编码进 stream，不抛异常**。`stopReason: "error"` + `errorMessage`。
   这样 UI 永远能渲染出一个完整的回合，不会卡在半截。
3. **`beforeToolCall` / `afterToolCall` 两个钩子**。前者能 `{block: true}` 拦掉调用，
   后者能整体替换 `content`。我们的折叠就挂在这个位置。
4. **工具结果必须带 `details`**（结构化），`content` 只放给模型看的文本。
   两者分开，UI 和日志才不会去解析自然语言。
5. **`tool_execution` 支持 sequential / parallel 两种模式**。
   我们的 kb 工具全是只读且互不依赖，该并行。

这五条照抄，代码自己写。253 行换 85.6 MB，划算。

## 折叠参数：不该挂在每个工具调用上

这是本次最实在的一个结论，而且**和我最初的直觉相反**。

我先按「每个工具调用都带 `retain` 参数」建模，量出来的账是：

```text
A. 折叠参数的固定税（每请求）
  10 个工具，最小写法 (+31 字符/工具) : 89 tok
  10 个工具，带描述写法(+80 字符/工具) : 372 tok
```

89 tok 看着可以接受。但把一条真实轨迹（10 个块、8 轮）跑完，逐块判断
「这个决定模型真的比工具定义更知道吗」，结果是 **10 个里只有 2 个需要模型**：

| 块 | 该留几轮 | 谁最清楚 |
| :-- | :-- | :-- |
| `kb_tree` | 0 | 工具定义完全知道：导航用一次就够 |
| `kb_where` | 0 | 工具定义知道：结果被后续 read 覆盖 |
| `kb_pack`（任务书） | ∞ | **调用者**（leader 派单时）知道 |
| `kb_read` 检查清单 | 3 | 工具定义可猜 |
| `kb_read` 样板 | 2 | ★ 只有模型知道写完没写完 |
| `bash cat` 参照物 | 1 | 工具定义可猜 |
| `kb_upsert` 确认 | 2 | 工具定义知道：审计线索 |
| `kb_pack`（验收书） | ∞ | **调用者**知道 |
| `bash test` | 1 | ★ 模型知道：测试输出常要反复看 |

8 个静态、2 个动态。让模型每轮重算那 8 个，付的是**每次请求的 reasoning**，
而本会话实测 reasoning 约 250 tok/次（694.9 KB / 708 次调用）。

所以最终设计：

- **折叠轮数写在工具定义里**（`Tool.fold_rounds`），一次声明、全轮生效。零 schema 税。
- **只给输出真正无界的工具留 `retain` 覆盖**。实测只有 3 个：`kb_pack`
  （预算决定大小）、`bash`（命令决定）、`kb_search`（命中数决定）。
  其余 7 个的输出大小由输入决定，改默认值就够。
- schema 税从 10×89 降到 3×89。

## 一个必须记住的坑：`fold_rounds=0` 的语义

第一版写成 `if self.n - b.born >= k`，`k=0` 时 `age` 也是 0，
于是**刚加进来的块在同一轮就被折掉了**。模型从头到尾没读到过内容，
于是反复重调同一个工具：

```text
  [1] kb_tree({}) -> 9185 tok
      折叠 1 块：kb_tree#2
  [2] kb_tree({}) -> 9185 tok
      折叠 1 块：kb_tree#3
  ... 连续 6 轮全是 kb_tree，最终上下文 139 tok
```

判据必须是 `age > k`，给 born 那一轮留一次被读的机会。改完：

```text
  [1] kb_tree({}) -> 3433 tok
轮数 2 · 工具调用 1 · 最终上下文 3502 tok · 折叠 0 块
```

**折叠得太早比不折叠更贵**：不是省了 token，是让 agent 丢了信息然后重做一遍。
这条只有真跑才会发现——静态看代码 `>=` 和 `>` 都像对的。

## 第二个坑：给模型看的东西不要用 JSON

同一个 `kb tree`：

| 格式 | 字符 | token |
| :-- | :-- | :-- |
| 文本 | 7,465 | **3,433** |
| `--json` | 27,350 | **9,185** |

**2.7 倍。** MCP 层必须用 JSON（它有结构化消费者：客户端要解析 `stats`、`items`），
但工具内部喂给模型的那一份一律用文本。JSON 的大括号、引号、重复键名
（`"rel":` 出现 80 次）全是白付的钱。

这条以前没暴露，因为 MCP 层的消费者一直是程序。一旦工具结果直接进模型上下文，
格式化选择立刻变成成本项。

## 保留与取回：折叠的前提是能取回

折叠不是二选一。墓碑（只剩 id + 取回命令）能省 100%，留前 200 tok 能省 97.7%，
但 `kb_pack` 的 8,794 tok 里有 5,204 是**要照抄的 YAML 全文**——
留个开头保不住那个。所以任务书只有两种状态：整块在，或墓碑 + 一条命令取回。

`Ledger` 因此保留每条结果的 `(tool, key, born)` 结构化身份，
`folded` 字典存原文。`kb.recall("<key>")` 取回。这也是为什么不能只靠
pi 的 `transformContext`——它拿到的只是一个消息数组，键一旦折进字符串里就找不回来了。

## 静默失败：agent 循环放大了每一个「不说话」的错误

这是把工具交给 agent 之后最贵的一类问题。真人用户看到「0 页」会自己去翻文档；
agent 不会——它会**换一个参数再试**，因为「空结果」和「名字打错了」在它看来一样。

实测四个任务跑了三轮才收敛，每一轮都挖出一个静默失败：

### 1. `--repo` 给错名字 → rc=0 输出「0 页」

`kb tree --repo collector/kit` 返回「0 页 · 标题共约 0 tok」，退出码 0。
agent 以为 infohub 是空仓库，于是去翻 `codeb`，再翻全库，4 轮全废。

`kb where` 更危险：它输出「没有页面覆盖 X」，而 agent 的下一步正是
**据此新建一页**——静默失败直接导致重复页。

修法：三个命令（tree / where / search）统一在入口校验，rc=2，并印出可用仓库名。

**但只印仓库名不够。** agent 拿到「可用：_shared, atomkgraph, codeb, infohub」
之后仍然去试 `--repo codeb`——它真正缺的信息是「collector 是 infohub 的子目录」。
所以错误里必须做**路径归属推断**，直接给出替代命令：

```text
没有名为 collector/kit 的仓库。可用：_shared, atomkgraph, codeb, infohub
  collector/kit 是 infohub 仓库下的子目录，不是仓库。
  要看这个子目录：kb dispatch collector/kit/   （文件清单 + 谁在描述它，约 115 tok）
  要看它的源码上下文：kb pack collector/kit/
```

改完这一条，同一个任务从 4 轮降到 1 轮。

### 2. 错误写 stderr，工具只捕获 stdout

`kb.py` 把错误打到 stderr，agent 的工具包装只接了 stdout，于是模型拿到的
是 `kb 退出码 2`——信息量等于零。它当然继续瞎猜。

**错误信息本身就是工具输出的一部分。** 必须原样交给模型，否则等于没有报错。

### 3. `kb_dispatch` 说「6 个代码文件」却不列出来

agent 问的正是「这个目录下有哪些文件」，而信息明明已经算出来了。
结果同一个调用重复 3 次（2 次被去重拦下）。

这条的教训比 bug 本身重要：**算出来的信息不给，等于没算。** 说话省下的
47 tok，代价是三轮重试。

### 4. 模型把 `.py` 路径传给 `kb_read`

「读这个文件」和「读描述这个文件的页」在模型看来是一件事。
`kb_read` 回「页面不存在」它不会想到换工具——实测先去 `kb_tree` 绕两圈。

修在 `pick_page`（所有读路径的公共出口），一次覆盖 read / heads / find：

```text
页面不存在：collector/kit/paging.py
  这是一个代码路径，不是知识页：
    看源码 + 相关知识：kb pack collector/kit/paging.py
    只看相关知识：      kb pack collector/kit/paging.py --no-source
    描述它的页：infohub/collector/architecture, infohub/collector/kit-api, ...
```

### 加一个去重闸

同样的参数调第二次，结果必然一样。实测「约束类」任务把 `kb_dispatch`
同一个参数调了 3 次——它不是想重试，是**没意识到上次已经回答过**（因为
答案里缺它要的那一项）。再执行一遍只会膨胀上下文，所以直接拦下并提示
「换工具或换参数」。

这一条是兜底：它不能替代把错误说清楚，只能止住浪费。

## `--no-source`：问题的答案常常不在源码里

最高频的提问是「改 X 有哪些坑」。真实数据：

| 装订方式 | token | 源码占比 |
| :-- | :-- | :-- |
| `kb pack collector/kit/paging.py` | 6,968 | 5,204（75%） |
| 同上 `--no-source` | **1,764** | 0 |

坑全在那 1,764 tok 里（`paging.py 的候选形状与原因码` 1,189 tok 直接点名了这个文件）。
而 agent 原先无法表达「我只要知识层」：降预算会**先把知识丢光**（分层顺序如此），
挤压源码额度又没开关。

实测加了这个开关之后，agent 在「不要贴源码」的问法下自己选对了：

```text
[3] kb_pack({"scope": "collector/kit/paging.py", "no_source": true}) -> 1962 tok
```

而在「我要照着加一种新翻页判断」的问法下它选的是装源码——这个判断它做对了。

## 落地

- `distill/agent/loop.py` — 300 行，零依赖，`python distill/agent/loop.py`
- `distill/agent/pi_probe.mjs` — 对照实验，装 pi 只为验证它能不能接 NVIDIA
- `distill/agent/run_tasks.py` — 四个真实任务的回归套件，跑完打印「有错误的任务：N/4」
- 工具层直接 `import kb`，进程内调用，54ms/次
- 冒烟测试 75 项（`node mcp/smoke.ts`），其中 6 项专盯上面这几条静默失败
