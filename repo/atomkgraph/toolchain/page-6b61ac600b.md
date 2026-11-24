---
covers:
  - scripts/verify-r62-delete-ui.mjs
  - scripts/test-r62-delete-api.mjs
  - apps/web/src/App.tsx
  - apps/web/src/api.ts
  - packages/core/src/services/knowledge-service.ts
  - packages/core/src/llm/client.ts
  - packages/core/src/ingest/vision-ocr.ts
  - packages/core/src/ingest/vision-clean.ts
  - scripts/vision-clean.ts
  - packages/core/src/services/relink-service.ts
updated: 2026-11-20
title: Toolchain pitfalls: ten things that fail silently
---

# 工具链踩坑：会静默出错的十件事

这些教训的共同点是**它们静默出错——工具不报错，只是给你一个看起来合理但错的结果**。按踩到频率排序。

## 1. 变异测试还原绝不能用 `git checkout`

它恢复的是 **HEAD** 版本，不是「变异前」版本。对**尚未提交**的实现（`App.tsx` 那批 +271 行、状态 `M`），`git checkout` 会把它们**整体删掉**；而且因为文件确实回到 HEAD 状态、`git diff` 会**无输出**——「`git diff` 干净」这条校验会**假绿通过**，看起来完美还原而实现已经没了。

正确做法：变异前 `Copy-Item` 备份 → 还原时从备份拷回 → 判据与**变异前哈希**比（不是与 HEAD 比），并确认 `git diff --stat` **非空**。曾因这个协议错误差点毁掉整批实现，是验证方顶回来纠正的。

## 2. 并行跑同一个 UI 验证脚本会得到一片假红

两实例互相删对方的被试数据、互相污染页面。实测并发时 **10/36**，铁证是 `[1]` 报「删除按钮不存在」，而同一次运行的 `[10-结构]` 却报 `deleteBtnLeft=true`——**自相矛盾**。串行后连续多次全绿。

**UI 验证脚本必须串行跑。** 脚本虽有锁（PID 存活检测），但锁只能拦「同时开始」，**拦不住「一个已跑起来、另一个中途改源码（变异）」**——冻结/变异期间必须独占。复跑前先确认：无 `MUTATION` 标记、锁文件空闲。

## 3. 别用 `body.innerText` 判「某内容是否还在」

页面上任何地方（反馈、侧栏、聊天）都可能含该文本，尤其**结果反馈文案本身就常含被操作对象的标题**。限定容器 + 剔除已知会含该文本的节点，或改用**结构判据**（某个元素「只在某分支渲染」，它在不在就是分支切换的信号）。间歇性假阳性比稳定假红更危险。

## 4. PowerShell inline `-e` 引号嵌套必然出事

嵌套引号触发 `ParserError`。**永远先写 `.ts`/`.mjs` 文件再 `node` 跑**，不要 `pwsh -Command '...-e "..."...'` 内联。

## 5. `tsx` 转译 `page.evaluate` 里的函数时会注入 `__name` 辅助函数

浏览器环境里没有这个函数 → 运行时报 `__name is not defined`。**跑 puppeteer/playwright 脚本用 `.mjs`，别用 tsx 跑 `.ts`。**

## 6. 前端改动在 3939 上不生效

后端 3939 托管的是 `apps/web/dist` 里**已构建的 bundle**。UI 验证必须走 vite dev server（5199），且要 `--host 127.0.0.1`（vite 默认只绑 `::1`，而既有脚本都用 `127.0.0.1`）。

## 7. 读文件时队友正在写 → 读到半成品

实测两次读到 `Unexpected end of input` / `Unexpected token 'const'`，行数还在变。**行数/mtime 还在变时不要下结论。**

## 8. 队友报告不能全信

一次协作里，队友跑出全绿、exit 1 却矛盾；另一处把 `text-destructive` 按钮自己当成了错误横幅。**关键断言、变异测试、还原协议都要独立复验**——并行协作时尤其如此。

## 9. `data.parent_id` vs `data.knowledge.parent_id`

`GET /api/knowledge/:id` 返回 `{knowledge,...}`，`parent_id` 在 `data.knowledge.parent_id`。读错形状 → 恒 undefined → 三条断言**连正确实现也被判失败**。假红比漏报更容易误导人去「修」本来正确的代码。

## 10. 第一次变异尝试可能测的不是你以为的东西

把软删改成硬删，直接 `DELETE FROM knowledge` 会被**外键约束挡住并抛错** → HTTP 500，row 其实没删掉 → 「行仍存在」的断言反而**绿**了。那测的是「FK 挡住了硬删」，不是「硬删语义」。改 `foreign_keys=OFF` 让硬删真的成功，才得到正确的红。**验证方主动放弃了第一次结果，没拿它当证据。**

## 长耗时 LLM 调用：超时不是硬上限，但 undici 会抢先掐断

### 现象

视觉转录单页要 100~2000s，请求频繁报 `请求超过 290000ms`。290000 = 290s，看着像某个写死的上限，**其实不是**。

### 真正的原因：两层超时，undici 的默认值抢先

Node 内置 `fetch` 底层是 undici，它有自己的 **`headersTimeout`，默认 300s**，而且**不受 `AbortSignal` 控制**——你给 `fetch(..., { signal })` 设 600s，undici 仍会在 300s 时先抛 `UND_ERR_HEADERS_TIMEOUT`。

所以 `fetchWithTimeout` 里的 `budget` 要区分两种情况：

```ts
const budget = d ? ms : Math.min(ms, capMs ?? 290_000)
```

有自定义 dispatcher（`d`）时用完整 `ms`；没有时压到 290s——**不是限制业务，是别让 undici 先掐断而报出误导性的错误**。

### 解法：自建 Agent，把 headersTimeout 抬上去

`packages/core/src/llm/client.ts` 的 `longLivedDispatcher()`：懒加载单例 `new Agent({ headersTimeout: 900_000, bodyTimeout: 900_000, connectTimeout: 60_000 })`，然后用 **undici 自己的 `fetch`** 带上 `dispatcher`。

**关键坑**：**不能给 Node 全局 `fetch` 传 `dispatcher`**，会报 `UND_ERR_INVALID_ARG`。必须用 undici 模块导出的 `fetch`，它才认这个参数。实测：

```
1) DEFAULT_VISION_TIMEOUT_MS = 600000
2) dispatcher headersTimeout = 900000
3) 全局 dispatcher headersTimeout = (默认 300000)
```

`packages/core/package.json` 本来就声明了 `undici ^8.12.3`，不用新装。

### 错误码要翻译成人话

`UND_ERR_HEADERS_TIMEOUT` 归到 `LLM_TIMEOUT`，消息写"请求超过 Nms 没有响应"。原始错误码对使用者没有意义，只会让人以为是网络坏了。

### 顺带一条：`.env` 里的 `LLM_TIMEOUT_MS` 是无效的

这个变量加了又删——超时由调用点的 `timeoutMs` 决定，`LLM_TIMEOUT_MS` 不参与任何计算，改了不会有任何效果。**要调超时改调用点或 `AKG_VISION_TIMEOUT_MS`。**

## 相关源码位置

| 关注点 | 文件 |
| --- | --- |
| LLM 客户端、超时、dispatcher、模型轮换 | `packages/core/src/llm/client.ts` |
| 单页视觉转录（渲染、缓存、并发） | `packages/core/src/ingest/vision-ocr.ts` |
| 清洗成结构化 Markdown、批量、大纲 | `packages/core/src/ingest/vision-clean.ts` |
| 视觉转录 CLI（`--pages` / `--out` / `--batch-size` / `--concurrency`） | `scripts/vision-clean.ts` |
