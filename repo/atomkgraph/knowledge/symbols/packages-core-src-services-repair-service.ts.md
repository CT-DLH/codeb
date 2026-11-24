---
covers:
  - packages/core/src/services/repair-service.ts
title: Semantic block index: repair-service.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：repair-service.ts（第4层）

**源码文件**：`packages/core/src/services/repair-service.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="packages/core/src/services/repair-service.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| MergeProposal@62 | interface | L62-74 |  | export interface MergeProposal { |
| RenameProposal@76 | interface | L76-81 |  | export interface RenameProposal { |
| ReparentProposal@83 | interface | L83-88 |  | export interface ReparentProposal { |
| CollapseProposal@98 | interface | L98-105 | 容器塌缩进它唯一的子节点。 | export interface CollapseProposal { |
| RewriteProposal@116 | interface | L116-130 | 原地改写一个节点的正文（第 3 步「优化节点内容」）。 | export interface RewriteProposal { |
| RepairPlanMeta@139 | interface | L139-143 |  | export interface RepairPlanMeta { |
| RepairItemResult@152 | interface | L152-158 |  | export interface RepairItemResult { |
| RepairRunResult@160 | interface | L160-167 |  | export interface RepairRunResult { |
| RepairRollbackResult@169 | interface | L169-182 |  | export interface RepairRollbackResult { |
| RawNode@184 | interface | L184-202 |  | interface RawNode { |
| QkRow@204 | interface | L204-210 |  | interface QkRow { |
| combineContent@213 | function | L213-232 | 正文叠加。子串情形直接取长的那份，避免把一段话贴两遍。 | export function combineContent( |
| minRewriteChars@235 | function | L235-237 | 改写稿的字数下限（截断护栏，不是质量判断）。 | export function minRewriteChars(basisChars: number, ratio = REWRITE_MI… |
| RelationMoveStep@241 | interface | L241-246 |  | export interface RelationMoveStep { |
| planRelationMove@256 | function | L256-277 | 合并时每条关系边该去哪 —— 纯函数，dry-run 和真跑共用同一份计划。 | export function planRelationMove( |
| stripLeadingHeading@282 | function | L282-290 | 去掉正文开头「# <title>」那一行（标题只是把节点名又说了一遍，合并后会变成第二个 H1）。 | export function stripLeadingHeading(text: string, title: string): stri… |
| RepairService@292 | class | L292-1410 |  | export class RepairService { |
| RepairService.raw@306 | method | L306-316 | 直读一行（不过滤 deleted_at）：判断成环、恢复源节点都要用。 | raw(id: string): RawNode \| null { |
| RepairService.isAncestor@319 | method | L319-329 | ancestorId 是不是 nodeId 的祖先（含自身相等返回 false）。 | isAncestor(ancestorId: string, nodeId: string): boolean { |
| RepairService.chainToRoot@332 | method | L332-343 | 从根到自己的 id 链（含自身）。 | chainToRoot(id: string): string[] { |
| RepairService.questionsOf@345 | method | L345-349 |  | private questionsOf(id: string): QkRow[] { |
| RepairService.relationsOf@351 | method | L351-353 |  | private relationsOf(id: string): Relation[] { |
| RepairService.findRelationByEnds@356 | method | L356-363 | 两点之间是否已有同类边（合并时会因此撞车）。 | private findRelationByEnds(sourceId: string, targetId: string, type: s… |
| RepairService.restoreRow@373 | method | L373-403 | 把整行还原到指定值（含 edit_count / content_hash）。 | private restoreRow( |
| RepairService.restoreRow.put@386 | arrow | L386-389 |  | const put = (col: string, v: unknown): void => { |
| RepairService.run@412 | method | L412-489 | 执行一批修复建议，一个批次一条舟。 | run(proposals: RepairProposal[], opts: { dryRun?: boolean; note?: stri… |
| RepairService.mergeInto@495 | method | L495-743 | 把源节点整体并入 keeper。顺序刻意排过： | private mergeInto( |
| RepairService.renameInto@746 | method | L746-788 | 改名消歧。标题不是「随便起」：撞车（含剥掉括注后撞车）一律拒。 | private renameInto(batchId: string, p: RenameProposal, dryRun: boolean… |
| RepairService.reparentInto@791 | method | L791-821 | 改挂父节点（修「父被删/父不存在/父链成环」）。 | private reparentInto(batchId: string, p: ReparentProposal, dryRun: boo… |
| RepairService.collapseInto@829 | method | L829-974 | 容器塌缩进唯一子节点：子上提一层顶替容器，容器（连同正文）消失。 | private collapseInto(batchId: string, p: CollapseProposal, dryRun: boo… |
| RepairService.rewriteInto@982 | method | L982-1072 | 原地改写一个节点的正文（可一并改标题）。 | private rewriteInto(batchId: string, p: RewriteProposal, dryRun: boole… |
| RepairService.rollback@1085 | method | L1085-1306 | 按批次还原。刻意分三趟： | rollback(batchId: string, opts: { dryRun?: boolean } = {}): RepairRoll… |
| RepairService.planFromReport@1316 | method | L1316-1395 | 体检报告 → 修复建议。不碰库，生成的东西要人过一眼再 apply。 | planFromReport( |
| RepairService.nearestLiveAncestor@1401 | method | L1401-1409 | 往上找第一个还活着的祖先；根都不行的话返回 null（挂到根级）。 | nearestLiveAncestor(id: string, fallbackToRoot: boolean): string \| nu… |
| brokenReasonText@1412 | function | L1412-1420 |  | function brokenReasonText(reason: string, target: string \| null): str… |
| pickContainer@1423 | function | L1423-1431 | 同一组里谁是「容器」（有子节点的那个）：父子同名时留它当分组名更有信息量。 | function pickContainer(g: DuplicateGroup, db: DB): string { |
| pickKeeper@1437 | function | L1437-1460 | 合并时保留谁：有子树的 > 正文长的 > 挂载题多的 > 建得早的。 | export function pickKeeper(ids: string[], db: DB): string { |
