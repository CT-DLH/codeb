---
covers:
  - packages/core/src/repositories/paper-repo.ts
title: Semantic block index: paper-repo.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：paper-repo.ts（第4层）

**源码文件**：`packages/core/src/repositories/paper-repo.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="packages/core/src/repositories/paper-repo.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| PaperRow@18 | interface | L18-35 |  | interface PaperRow { |
| PaperPartRow@37 | interface | L37-46 |  | interface PaperPartRow { |
| rowToPaper@48 | function | L48-68 |  | function rowToPaper(r: PaperRow): Paper { |
| rowToPart@70 | function | L70-81 |  | function rowToPart(r: PaperPartRow): PaperPart { |
| CreatePaperInput@83 | interface | L83-99 |  | export interface CreatePaperInput { |
| UpdatePaperInput@101 | interface | L101-113 |  | export interface UpdatePaperInput { |
| CreatePaperPartInput@115 | interface | L115-122 |  | export interface CreatePaperPartInput { |
| PaperRepository@124 | class | L124-428 |  | export class PaperRepository { |
| PaperRepository.create@132 | method | L132-161 |  | create(input: CreatePaperInput): Paper { |
| PaperRepository.findByIdentityKey@169 | method | L169-175 | 按 identity_key 找已确认的卷（幂等复用用）。 | findByIdentityKey(identityKey: string): Paper \| null { |
| PaperRepository.findAllByIdentityKey@178 | method | L178-184 | 列出全部同 identity_key 的卷（含未确认），供预检展示「有一张待确认的卷」。 | findAllByIdentityKey(identityKey: string): Paper[] { |
| PaperRepository.findById@186 | method | L186-189 |  | findById(id: string): Paper \| null { |
| PaperRepository.findAll@197 | method | L197-213 | 卷列表（带统计）。 | findAll(opts: { kind?: PaperKind; ids?: string[] } = {}): PaperWithSta… |
| PaperRepository.detail@216 | method | L216-219 | 单卷详情（含大题与统计）。 | detail(id: string): PaperWithStats \| null { |
| PaperRepository.withStats@222 | method | L222-260 | 给卷补上大题列表与题数统计（活关联口径）。 | private withStats(p: Paper): PaperWithStats { |
| PaperRepository.update@262 | method | L262-284 |  | update(id: string, patch: UpdatePaperInput): Paper \| null { |
| PaperRepository.update.put@267 | arrow | L267-270 |  | const put = (col: string, v: unknown): void => { |
| PaperRepository.remove@295 | method | L295-309 | 删卷。 | remove(id: string): { removed: boolean; detached_questions: number } { |
| PaperRepository.createPart@313 | method | L313-331 | ---- 大题 ---- | createPart(input: CreatePaperPartInput): PaperPart { |
| PaperRepository.ensurePart@342 | method | L342-348 | 找（或建）某卷下的一个大题。 | ensurePart(input: CreatePaperPartInput): PaperPart { |
| PaperRepository.findParts@350 | method | L350-355 |  | findParts(paperId: string): PaperPart[] { |
| PaperRepository.findPart@357 | method | L357-362 |  | findPart(partId: string): PaperPart \| null { |
| PaperRepository.maxPaperOrder@370 | method | L370-375 | 某卷现有的最大 paper_order（全卷，不按 part）。 | maxPaperOrder(paperId: string): number { |
| PaperRepository.attachQuestions@390 | method | L390-421 | 批量挂卷 / 退卷。 | attachQuestions( |
| PaperRepository.count@424 | method | L424-427 | 库里是否已有卷（用于「录入时是否要自动建卷」的判断与前端空态）。 | count(): number { |
