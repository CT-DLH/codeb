---
covers:
  - apps/web/src/components/QuestionPanel.tsx
title: Semantic block index: QuestionPanel.tsx (layer 4)
updated: 2026-11-24
---

# 语义块索引：QuestionPanel.tsx（第4层）

**源码文件**：`apps/web/src/components/QuestionPanel.tsx`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="apps/web/src/components/QuestionPanel.tsx", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| Q@48 | interface | L48-69 |  | interface Q { |
| Attempt@72 | interface | L72-79 | R20：一次作答记录。 | interface Attempt { |
| SubGradeDetail@103 | interface | L103-111 | R41：单个小问的批改明细（与后端 SubGradeDetail 同形）。 | interface SubGradeDetail { |
| fmtScore@114 | function | L114-117 | 分值展示：最多两位小数并去掉尾随 0（100 分 3 问的均分值不该显示成 33.333333333333336）。 | function fmtScore(n: number): string { |
| fmtExpected@120 | function | L120-125 | 标准答案展示：判断题的 true/false 换成「正确/错误」，其余原样（与作答按钮文案一致）。 | function fmtExpected(gradableIsJudge: boolean, raw: string): string { |
| fmtAttemptAnswer@132 | function | L132-147 | R41：作答历史的展示。一题多问存的是结构化作答 JSON，原样显示是一串 | function fmtAttemptAnswer(raw: string): string { |
| fmtTime@150 | function | L150-155 | 作答时间戳 → 「8/12 14:03」（作答历史里用，省空间）。 | function fmtTime(iso: string): string { |
| fmtTime.p@153 | arrow | L153-153 |  | const p = (n: number) => String(n).padStart(2, '0') |
| normalizeType@158 | function | L158-173 | 归一化题型：把历史导入的类型名映射到内部标准类型。 | function normalizeType(t: string): 'judge' \| 'single' \| 'multiple' \… |
| splitInlineOptions@179 | function | L179-203 | 选项兜底解析：当 options 为空但题干内嵌选项（如 “A. xxx\nB. xxx”）时， | function splitInlineOptions(content: string): { stem: string; options:… |
| FoldBlock@209 | function | L209-235 | 一个可折叠的内容块（答案 / 解析N / …）。默认折叠，点击标题展开。 | function FoldBlock({ |
| SubQuestionList@251 | function | L251-470 | R41：一题多问的小问列表 —— 可逐问作答（R29 时是纯只读的）。 | function SubQuestionList({ |
| SubQuestionList.toggle@305 | arrow | L305-314 |  | const toggle = (letter: string) => { |
| SubEdit@480 | interface | L480-489 | R29：小问的编辑态。与 SubQuestion 唯一差别是 options 在编辑器里是「每行一个」的 | interface SubEdit { |
| subToEdit@491 | function | L491-502 |  | function subToEdit(sq: SubQuestion): SubEdit { |
| editToSub@504 | function | L504-524 |  | function editToSub(s: SubEdit): SubQuestion { |
| QuestionCard@534 | function | L534-1432 | 单张题目卡片。 | export function QuestionCard({ |
| QuestionCard.togglePick@667 | arrow | L667-677 |  | const togglePick = (letter: string) => { |
| QuestionCard.blockLabel@689 | arrow | L689-690 |  | const blockLabel = (b: QuestionAnalysis, i: number): string => |
| QuestionCard.genSummary@692 | arrow | L692-706 |  | const genSummary = async () => { |
| QuestionCard.buildPatch@714 | arrow | L714-739 | 既用于真正提交，也作为「有没有实质改动」的比对基准——两处共用一个函数， 才不会出现「判断说没改、提交却写进了东西」或反过来的错位。 | const buildPatch = () => { |
| QuestionCard.baselinePatch@742 | arrow | L742-764 |  | const baselinePatch = () => { |
| QuestionCard.startEdit@767 | arrow | L767-771 |  | const startEdit = () => { |
| QuestionCard.cancelEdit@774 | arrow | L774-778 |  | const cancelEdit = () => { |
| QuestionCard.saveEdit@784 | arrow | L784-810 | R42：保存。没有实质改动就直接退出，不发 PATCH—— 每次写都会留一条修订记录，别为「点进去又点出来」留痕。 | const saveEdit = async () => { |
| QuestionCard.del@817 | arrow | L817-825 |  | const del = async () => { |
| QuestionCard.submit@827 | arrow | L827-856 |  | const submit = async () => { |
| QuestionCard.retry@859 | arrow | L859-865 |  | const retry = () => { |
| VariantFamilyBlock@1458 | function | L1458-1537 | R61-P5：变式题族块。 | function VariantFamilyBlock({ questionId }: { questionId: string }) { |
| QuestionPanel@1539 | function | L1539-1689 |  | export function QuestionPanel({ |
| QuestionPanel.toggleSubtree@1571 | arrow | L1571-1581 |  | const toggleSubtree = () => { |
| QuestionPanel.genAll@1607 | arrow | L1607-1619 |  | const genAll = async () => { |
