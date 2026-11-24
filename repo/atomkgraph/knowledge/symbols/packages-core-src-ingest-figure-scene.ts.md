---
covers:
  - packages/core/src/ingest/figure-scene.ts
title: Semantic block index: figure-scene.ts (layer 4)
updated: 2026-11-24
---

# 语义块索引：figure-scene.ts（第4层）

**源码文件**：`packages/core/src/ingest/figure-scene.ts`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="packages/core/src/ingest/figure-scene.ts", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| FigureScene@40 | interface | L40-44 |  | export interface FigureScene { |
| SceneProblem@46 | interface | L46-49 |  | export interface SceneProblem { |
| scenePrompt@61 | function | L61-87 | 场景图提示词。 | export function scenePrompt(canvas: { w: number; h: number }, caption?… |
| num@90 | function | L90-93 | 数字归一：接受字符串数字、保留一位小数、拒绝 NaN/Infinity。 | function num(v: unknown): number \| null { |
| str@95 | function | L95-97 |  | function str(v: unknown): string \| undefined { |
| parseFigureScene@105 | function | L105-191 | 解析模型给的场景图。 | export function parseFigureScene(raw: string, canvas: { w: number; h: … |
| esc@194 | arrow | L194-195 |  | const esc = (s: string): string => |
| renderSceneSvg@204 | function | L204-278 | 场景图 → 自包含 SVG。 | export function renderSceneSvg(scene: FigureScene): string { |
| round@280 | function | L280-282 |  | function round(n: number): number { |
| sceneTexts@285 | function | L285-292 | 场景图里所有要显示的文字（框内 label、独立 text、括号/圆 label），用于逐字召回校验。 | export function sceneTexts(scene: FigureScene): string[] { |
| sceneAudit@295 | function | L295-317 | 坐标越界 / 图元过少的体检。越界不致命（overflow 只是被裁掉），但必须报出来。 | export function sceneAudit(scene: FigureScene): string[] { |
| textBox@320 | function | L320-329 | 文字方框的粗估：CJK 按 1em、ASCII 按 0.55em（不引字体度量库，够用来查重叠）。 | export function textBox(t: { s: string; x: number; y: number; anchor: … |
| textOverlaps@339 | function | L339-364 | 查文字重叠。 | export function textOverlaps(scene: FigureScene): Array<[string, strin… |
| sceneCanvas@367 | function | L367-370 | 画布尺寸：宽固定 1000，高按原图比例。 | export function sceneCanvas(imgW: number, imgH: number, width = 1000):… |
