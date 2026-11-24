---
covers:
  - scripts/test-ingest.ts
title: Semantic block index: test-ingest.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：test-ingest.ts（第4层）

**源码文件**：`scripts/test-ingest.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="scripts/test-ingest.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| dump@121 | function | L121-130 | 失败时打印的取证值。JSON.stringify 对函数/undefined 返回 undefined，直接 .slice 会炸—— | function dump(v: unknown): string { |
| check@131 | function | L131-139 |  | function check(name: string, cond: boolean, extra?: unknown): void { |
| eq@140 | function | L140-142 |  | function eq<T>(name: string, actual: T, expected: T): void { |
| OneQuestionDoc@150 | interface | L150-152 |  | interface OneQuestionDoc { |
| filler@307 | arrow | L307-307 |  | const filler = (n: number): string => '设函数连续可导，求证存在一点使导数等于区间端点的平均变化率。'… |
| fakeDrift@402 | arrow | L402-410 | 假模型：故意把题干改写掉。真模型不会稳定复现改写行为，只能靠注入。 | const fakeDrift: ChatFn = async () => ({ |
| fakeOk@422 | arrow | L422-437 | 对照组：照抄原文 → 不许误标（否则「全部标红」也能让 3-13 通过，等于没测） | const fakeOk: ChatFn = async () => ({ |
| mkFakeAligned@459 | arrow | L459-470 |  | const mkFakeAligned = (n: number): ChatFn => async () => ({ |
| fakeVision@701 | arrow | L701-712 |  | const fakeVision = async (_file: string, o: VisionOcrOptions): Promise… |
| boom@764 | arrow | L764-766 | 失败语义：requireOcr 必须抛，不 require 必须降级留 warning 且保留原文本 | const boom = async (): Promise<VisionOcrResult> => { |
| mkQ@796 | arrow | L796-803 | 跨块去重：分块 overlap 会让边界题被抽两遍（一次残片、一次完整） | const mkQ = (content: string, detail = '块1 #1'): ExtractedQuestion => … |
| fakeOverlap@836 | arrow | L836-845 |  | const fakeOverlap: ChatFn = async () => { |
| mkNew@929 | arrow | L929-937 |  | const mkNew = (content: string): ExtractedQuestion => ({ |
| fakeChat@938 | arrow | L938-941 |  | const fakeChat = (reply: unknown, counter?: { n: number }): ChatFn => … |
| throwChat@1040 | arrow | L1040-1042 | 模型报错不能拖垮整批：这一题按新建处理，后面的题照常判 | const throwChat: ChatFn = async () => { |
| mkDecision@1054 | arrow | L1054-1066 |  | const mkDecision = ( |
| alias@1186 | arrow | L1186-1186 |  | const alias = (id: string): string => buildKnowledgeOutline(ldb).byId.… |
| mkChat@1228 | arrow | L1228-1232 |  | const mkChat = (picks: unknown): ChatFn => async () => ({ |
| boom@1303 | arrow | L1303-1305 | 变异：catch 里不记 judge_failed / 不留原因 → 11-10 红 | const boom: ChatFn = async () => { |
| err@1566 | arrow | L1566-1571 |  | const err = (code: string, msg: string, status?: number): Error => { |
| flaky@1575 | arrow | L1575-1579 |  | const flaky = async (): Promise<string> => { |
| bad@1594 | arrow | L1594-1597 |  | const bad = async (): Promise<string> => { |
| timing@1609 | arrow | L1609-1612 |  | const timing = async (): Promise<string> => { |
| netFlaky@1634 | arrow | L1634-1638 |  | const netFlaky = async (): Promise<string> => { |
| walkArp@1815 | arrow | L1815-1820 |  | const walkArp = (nodes: typeof arpTree): void => { |
| eq16@1893 | arrow | L1893-1894 |  | const eq16 = (name: string, actual: unknown, expected: unknown): void … |
| fakeChat@1979 | arrow | L1979-1996 |  | const fakeChat: ChatFn = async (_cfg, messages) => { |
| fakeVision19@2241 | arrow | L2241-2255 |  | const fakeVision19 = async (_f: string, o: { pages?: number[] }) => ({ |
| map20@2338 | arrow | L2338-2351 | --- 跨页连续性：模型给标记，代码做对撞 --- | const map20 = (rows: Array<[number, Partial<PageTranscript>]>): Map<nu… |
| fakeVision20@2409 | arrow | L2409-2435 |  | const fakeVision20 = async (_f: string, o: VisionOcrOptions): Promise<… |
| fakeVisionAuto@2507 | arrow | L2507-2532 |  | const fakeVisionAuto = async (_f: string, o: VisionOcrOptions): Promis… |
| fakeVisionManual@2549 | arrow | L2549-2573 |  | const fakeVisionManual = async (_f: string, o: VisionOcrOptions): Prom… |
| fakeAny@2646 | arrow | L2646-2670 |  | const fakeAny = (log: number[][]) => async (_f: string, o: VisionOcrOp… |
| sn@2693 | arrow | L2693-2699 | ═══ §21 结构整形（R46）：折叠冗余包装层 / 平铺分组 ═══ 真实形态都取自第一章实测：1.1.5 在五个分类方式外面多包了一层「网络分类维度」； 1.1.6 把 11 个性能指标全部平铺 | const sn = (title: string, content = '', children: SplitNode[] = []): … |
| titlesOf@2700 | arrow | L2700-2701 |  | const titlesOf = (nodes: SplitNode[]): string[] => |
| fakeShape@2702 | arrow | L2702-2706 |  | const fakeShape = (reply: string, calls: string[] = []): ChatFn => |
| shapeErr@2942 | function | L2942-2951 | 坏输出一律显式失败，由调用方降级（静默返回空树 = 整节知识点消失） | async function shapeErr(raw: string, truncated = false): Promise<strin… |
| nodesOf@3010 | arrow | L3010-3016 |  | const nodesOf = (topic: string) => |
| chat22@3017 | arrow | L3017-3028 |  | const chat22: ChatFn = async (_cfg, messages) => { |
| ok@3022 | arrow | L3022-3022 |  | const ok = (content: string) => ({ content, finish_reason: 'stop', tru… |
| alignSuite@3159 | function | L3159-3277 | §23 标题对齐：只改标题，不改正文；编号/清单/容器类型三道校验都得拦得住 | async function alignSuite(): Promise<void> { |
| alignSuite.mk@3161 | arrow | L3161-3162 |  | const mk = (title: string, content = '正文', children?: SplitNode[]): Sp… |
| alignSuite.fake@3186 | arrow | L3186-3186 |  | const fake = (content: string) => async () => ({ content, finish_reaso… |
| alignSuite.spy@3231 | arrow | L3231-3234 |  | const spy = async () => { |
| alignIntegration@3281 | function | L3281-3364 | §24 接线：planUnifiedIngest 要在「库里已有内容」时先对齐再合并（不是只在单测里能用） | async function alignIntegration(): Promise<void> { |
| alignIntegration.chat24@3314 | arrow | L3314-3329 | 拆解只给一个原子点，标题故意换了个说法（第二轮提取就是这样） | const chat24: ChatFn = async (_cfg, messages) => { |
| alignIntegration.ok@3317 | arrow | L3317-3317 |  | const ok = (content: string) => ({ content, finish_reason: 'stop', tru… |
| fakeFailOne@3382 | arrow | L3382-3393 |  | const fakeFailOne: ChatFn = async (_c, _m, o) => { |
| testSheetLlm@3495 | function | L3495-3615 | 真实事故（第4章 4.2 节）：OCR 把「10.」读成「30.」，超出 maxSkip 被当续行， 整道题并进上一题 → 习题侧 69 道、答案侧 72 道，08/10/18 三条答案成孤儿。 协议 | async function testSheetLlm() { |
| testSheetLlm.stub@3504 | arrow | L3504-3518 | 模型只抄锚点。题号被 OCR 读成 30 也一样照抄，程序照样能按内容切出来。 | const stub = async (): Promise<{ content: string }> => ({ |
| testSheetLlm.ghost@3537 | arrow | L3537-3550 | 锚点在原文里搜不到 → 丢弃并计数，绝不拿模型文本顶上 | const ghost = async (): Promise<{ content: string }> => ({ |
| testSheetLlm.wsStub@3556 | arrow | L3556-3560 | 白空格被模型改动（换行→空格）时仍应定位成功 | const wsStub = async (): Promise<{ content: string }> => ({ |
| testSheetLlm.noAns@3565 | arrow | L3565-3569 | 有答案节却一条都没配上 → 降级，让正则接手 | const noAns = async (): Promise<{ content: string }> => ({ |
| testSheetLlm.counting@3575 | arrow | L3575-3578 |  | const counting = async (): Promise<{ content: string }> => { |
| testSheetLlm.wrongLetter@3592 | arrow | L3592-3605 | 真实失效（2026-11-20 操作系统第2章）：原文答案节是 43. D， 模型给的锚点却是 43. A —— 它没照抄，而是按自己的计算填了它认为的答案。 整串锚点永远搜不到，但题号那半截 | const wrongLetter = async (): Promise<{ content: string }> => ({ |
| testVisionGuards@3622 | function | L3622-3872 | ══════════════════════════════════════════════════════════ 31. 视觉清洗的产物校验与去重 ════════════════════════ | async function testVisionGuards(): Promise<void> { |
| testVisionGuards.throws@3683 | arrow | L3683-3690 | --- 覆盖率校验 --- | const throws = (fn: () => void): boolean => { |
| testKeyPool@3874 | function | L3874-3941 |  | async function testKeyPool(): Promise<void> { |
| testAnswerSplit@3948 | function | L3948-3976 |  | async function testAnswerSplit(): Promise<void> { |
| testTextClean@3978 | function | L3978-3989 |  | async function testTextClean(): Promise<void> { |
