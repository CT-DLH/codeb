---
covers:
  - docs/16-模型可用性与延迟实践.md
updated: 2026-11-18
title: NVIDIA model availability and latency: 85 models, 12 usable
---

# NVIDIA 模型可用性与延迟实测：85 个模型只 12 个能出正文

NVIDIA 模型可用性与延迟实测（实测日期 2026-11-04，端点 `https://integrate.api.nvidia.com/v1`，OpenAI 兼容）。权威源 `docs/16-模型可用性与延迟实测.md`（183 行）。原始数据 `.cache/nvidia-*.md` / `.cache/pipeline-e2e.md` / `.cache/live-ingest.md`。

## 一句话结论

**`.env` 五个角色全部可用**，但 `LLM_SPLIT_MODEL` 配的 `minimax-m3.1-flash` 是可用模型里最慢、最不稳的一个；**`nvidia/nemotron-3.5-bolt-e4b` 在抽题/抽知识点/可视化/视觉四条链路上全部通过且最快**——唯一「全科满分」模型。

## 目录 ≠ 能用：85 个里只有 12 个能出正文

`GET /v1/models` 返回 85 个模型（公开商品目录，与账号调用权限无关）。逐个真打后：

- 可用 12（真回了正文）
- 空正文 8（模型活着，但预算被思维链吃光，正文为 null，finish_reason 仍 `stop`）
- 不可用 40（404 `Function '<uuid>': Not found for account '<账号>'`）
- 未测 25（安全分类/版面解析/检索/语音，通用 chat 探针无意义）

**三态输出**：把空正文单独统计，别记成「模型坏了」误删好模型。

## 两档延迟实测（60 个通用对话候选）

轻档（`max_tokens 1024`，问「用一句话解释单点故障」）：12/60 能出正文；其中 8 个通过重档真抽题。重档（项目真抽题 prompt，`max_tokens 8192`，判「JSON 合法且 ≥3 题」）。

| 模型 | 轻档 | 重档 | 结论 |
|---|---|---|---|
| `nvidia/nemotron-3.5-bolt-e4b` | ✅ 1.7s | ✅ **21.5s** | 最快且稳，四链路全通 |
| `poolside/laguna-xs-2.1` | ✅ 4.2s | ✅ **5.2s** | 抽题最快，但知识点链路吐坏 JSON |
| `nvidia/nemotron-3-ultra-550b-a55b` | ✅ 1.1s | ✅ 14.0s | 稳，知识点偏慢 |
| `nvidia/nemotron-3-nano-omni-…-reasoning` | ✅ 2.8s | ✅ 18.0s | 推理模型，知识点烧光预算 |
| `meta/muse-glimmer-30b` | ✅ 29.2s | ✅ 62.3s | — |
| `z-ai/glm-5.3-flash` | ✅ 19.7s | ✅ 68.6s | 视觉最好，文字链路偏慢 |
| `nvidia/nemotron-3.5-super-vl-120b-a12b` | ✅ 8.0s | ✅ 75.4s | — |
| `mistralai/mistral-large-4-1t-a52b` | ✅ 21.2s | ✅ 80.8s | — |
| `meta/llama-3.2-90b-vision-instruct` | ✅ 3.8s | ❌ 240s 超时 | 轻档能答，重档撑不住 |
| `deepseek-ai/deepseek-v4.1-flash` | ✅ 18.7s | ❌ 空正文 | reasoning 806 字吃光预算 |
| `google/diffusiongemma-26b-a4b-it` | ✅ 0.8s | ❌ 400 | 不支持该请求形态 |
| `stepfun-ai/step-5-preview` | ✅ 77.5s | ❌ 空正文 | 轻档已 77.5s |
| 其余 48 | ❌ | — | 40 个 404 账号无权 + 90s 超时 |

两个关键点：抽题过 ≠ 知识点过（`laguna` 抽题最快但知识点吐坏 JSON；`nano-omni` 抽题正常但知识点被思维链烧光）。**两个链路必须分开验收**。

## 真实流水线端到端（5 题卷子 + 2 节讲义）

| 模型 | 抽题（5题） | 抽知识点（2节） |
|---|---|---|
| `minimax-m3.1-flash`（现役） | ✅ 13.7s | ✅ 130.6s（18 节点） |
| `nvidia/nemotron-3.5-bolt-e4b` | ✅ **7.8s** | ✅ **20.1s**（6 节点） |
| `poolside/laguna-xs-2.1` | ✅ 7.7s | ❌ `LLM_BAD_JSON`：坏控制字符 |
| `nano-omni reasoning` | ✅ 16.0s | ❌ `LLM_EMPTY`：reasoning 12593 字吃光预算 |
| `nemotron-3-ultra-550b` | ✅ 26.0s | ✅ 129.6s（6 节点） |
| `z-ai/glm-5.3-flash` | ✅ 112.3s | ❌ 356.2s 后 0 节点 |

现役 `minimax` 是完成的三个里最慢：抽题比 `bolt` 慢 1.8 倍，知识点慢 6.5 倍（130.6s vs 20.1s）。

## HTTP 全链路（正在运行的 3939，当前 `.env`）

| 步骤 | 结果 | 耗时 |
|---|---|---|
| `POST /api/ingest/extract` 抽题 | ✅ 5/5 题 | **14.8s** |
| `POST /api/ingest/apply` 落库 | ✅ created=5 | 0.0s |
| `POST /api/questions/rollback-batch` 回滚 | ✅ deleted=5 | 0.0s |
| `POST /api/ingest/extract-knowledge` 知识点 | ✅ 13 节点 / 2 节 | **92.3s** |
| `GET /api/search` 语义检索 | ✅ 3 条命中 | **5.6s** |

五步全绿：现役配置能干活。抽题不会编造答案（有答案 0/5，符合预期——R30 曾出现 10/10 全编，现已被 prompt 约束住）。

## 其余三个角色

| 角色 | 配置 | 实测 | 判定 |
|---|---|---|---|
| 视觉 `LLM_VISION_MODEL` | `z-ai/glm-5.3-flash` | 42.6s / 21.3s，转写 717~718 字，JSON 合法 | ✅ 可用 |
| 视觉（备选） | `nvidia/nemotron-3.5-bolt-e4b` | **18.7s / 18.8s**，转写 548~603 字 | ✅ 比现役快一倍 |
| 可视化 `LLM_VIZ_MODEL` | `nvidia/nemotron-3.5-bolt-e4b` | 2/2 成功，**151.7 / 159.6s**，14~21KB HTML，doctype+script 齐、无外链 | ✅ 可用 |
| 向量 `EMBEDDING_MODEL` | `nvidia/nemotron-3-embed-1b` | 单条 0.9s，**批量 8 条 3.0s**，2048 维 | ✅ 可用 |

### 向量模型的批量差异（易踩）

| 模型 | 单条 | 批量 8 条 |
|---|---|---|
| `nemotron-3-embed-1b`（现役） | ✅ 0.9s / 2048 维 | ✅ **3.0s / 8 条** |
| `nemotron-3.5-embed-1b` | ✅ 0.4s / 2048 维 | ❌ HTTP 500 |
| `nemotron-3.5-embed-8b` | ✅ 0.6s / 4096 维 | ❌ HTTP 500 |

新版 embed 模型单条能过、**批量直接 500**。`embedTexts` 正是按批调用，重建索引时这条差异直接变成失败。**不要因为「model 更新」就换掉现役 embed**。

可视化曾出一次 `HTTP 503 content safety screening is temporarily unavailable`（85.4s 时），随后重试成功。NVIDIA 侧安全筛服务抖动，属于瞬时故障，按重试策略处理（`classifyTransient` 已把 5xx 归为可重试）。

## 方法学警示：限流会伪装成「模型不可用」

本轮最重要的教训。压测到后半程 `minimax` 开始返回 HTTP 400，另一批模型报 `fetch failed (ENOTFOUND/ECONNRESET)` 和 90s 超时，看起来像「一批模型同时坏掉」，实际是连续压测导致 HTTP 429。**冷却约 90 秒后单独重试，4 个模型全部 200 正常。**

所以：
- 成功率是「压力下的下限」，不是模型真实水平。单发隔离重测时 `minimax` 5 次里 4 次成功。
- 不要把连续实测的失败直接归因到模型，先看是不是 429、是不是自己打出来的。
- 失败重试是必需的（`--retry-failed` 把「上游瞬时抖动」与「确定性拒绝」分开：404 重试也过不了，超时/429 重试常常就过了）。
- 限流期间延迟数字偏大（排队 > 推理），不完全可比。

## 建议

1. **`LLM_SPLIT_MODEL` 换成 `nvidia/nemotron-3.5-bolt-e4b`**（现配 `minimax-m3.1-flash`）。
2. **`LLM_VISION_MODEL` 可考虑换成 `bolt-e4b`**（18.7s vs 42.6s）。现役 `glm-5.3-flash` 转写字数更多，若更看重识别完整度则保留。
3. **`EMBEDDING_MODEL` 维持 `nvidia/nemotron-3-embed-1b`**，不要换成 3.5 系列（批量 500）。
4. **`LLM_VIZ_MODEL` 维持 `bolt-e4b`**：2/2 成功，150s+ 属正常，与 `GEN_TIMEOUT_MS=600_000` 匹配。
5. **抽题与知识点用同一模型的假设需要复核**：两者对模型要求不同，若拆成两个配置，知识点更该用 `bolt-e4b`。
6. **批量压测要留间隔**，别把压测结论当模型质量结论。生产侧重试策略（`RETRY_ATTEMPTS`：network 5 / server 4 / timeout 2）对 429 已有覆盖。

## 复现命令

```bash
pnpm run bench:nvidia:scan        # 目录全量扫描（85个，并发8，约1分钟）——三态分
pnpm run bench:nvidia:chat -- --retry-failed   # 60个通用对话模型两档实测，约25分钟
pnpm run bench:nvidia -- --tasks extract --repeat 2  # 真 prompt/真参数按角色延迟
pnpm run bench:pipeline -- --models env.split,bolt,laguna  # 真实流水线端到端横向比较
pnpm run bench:live               # 按当前 .env 打真 server（需 server:3939 在跑）
```

> 压测期间若出现批量失败，先冷却 90 秒再单发复测，别急着换模型。
