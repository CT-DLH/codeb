---
covers:
  - docs/09-Phase0验证方案.md
updated: 2026-11-18
title: Phase 0 validation: three goals and the keep-or-drop rule
---

# Phase 0 验证方案：三个验证目标与抛弃/沉淀原则

Phase 0 快速验证方案。权威源 `docs/09-Phase0验证方案.md`（43 行）。目标：用最少代码确认核心假设能否成立，**不写正式框架代码**，验证通过后再按第七节推进。

## 9.1 验证目标

| 优先级 | 验证内容 | 成功标准 | 失败后果 |
|---|---|---|---|
| **P0** | AI 拆解质量 | 输入 2 章教材，拆出的原子点粒度一致、层级合理、能出题 | 项目不成立，需重新设计拆解策略 |
| **P1** | 图谱渲染性能 | 1 万合成节点，WebGL 方案帧率 ≥ 30fps | 降低指标或换渲染方案 |
| **P2** | SM-2 复习闭环 | 答对/答错后正确更新复习间隔，到期提醒正常触发 | 换 FSRS 或自定义算法 |

## 9.2 验证方式：脚本先行，全栈后跟

**阶段 0（3–5 天）：纯脚本验证**

技术栈仅 TypeScript + LLM SDK + 各模块 npm 包。**不涉及 React、Node 服务、数据库。**

```
scripts/
  test-split.ts      # 读 Markdown → 调 LLM 拆解 → 输出 JSON → 人工评审
  test-embed.ts      # 试 embedding API 成本、延迟、限流
  gen-synthetic.ts   # 生成 N 个假节点 → 喂给 sigma.js 测帧率
  test-sm2.ts        # 用 sm-2 npm 包跑一轮复习模拟
```

**阶段 1（5–7 天）：最小全栈竖线**

只做：录入一个知识点 → 存 SQLite → 前端列表显示 → 能编辑。图谱先不做。

## 9.3 抛弃 vs 沉淀

| 类型 | 内容 | 处理 |
|---|---|---|
| **抛弃型** | 脚本验证代码、合成数据生成器 | 验证完删除 |
| **沉淀型** | 数据模型 schema、拆解 prompt、掌握度公式 | 验证期即按最终设计写，不偷懒 |
| **可复用** | sm-2/fsrs npm 包、sigma.js React 封装 | 直接进正式代码 |
