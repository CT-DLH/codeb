---
covers:
  - console/public/console.js
title: Semantic block index: console.js (layer 4)
updated: 2026-11-24
---

# 语义块索引：console.js（第4层）

**源码文件**：`console/public/console.js`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="console/public/console.js", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| $@4 | arrow | L4-4 |  | const $ = (selector) => document.querySelector(selector); |
| $$@5 | arrow | L5-5 |  | const $$ = (selector) => Array.from(document.querySelectorAll(selector… |
| esc@38 | arrow | L38-39 |  | const esc = (value) => |
| fmtTime@41 | arrow | L41-45 |  | const fmtTime = (iso) => { |
| fmtSize@47 | arrow | L47-52 |  | const fmtSize = (bytes) => { |
| fmtDuration@54 | arrow | L54-59 |  | const fmtDuration = (start, end) => { |
| api@61 | function | L61-73 |  | async function api(path, options = {}) { |
| setBadge@75 | function | L75-78 |  | function setBadge(element, label, tone = '') { |
| showNotice@80 | function | L80-83 |  | function showNotice(target, message, tone = 'err') { |
| showTab@87 | function | L87-102 |  | function showTab(name, updateHash = true) { |
| loadOverview@106 | function | L106-179 |  | async function loadOverview() { |
| renderProgress@181 | function | L181-206 |  | function renderProgress(progress) { |
| applyBars@209 | function | L209-213 | CSP 不允许内联 style 属性，进度宽度用 CSSOM 赋值 | function applyBars() { |
| renderLastRun@215 | function | L215-225 |  | function renderLastRun(lastRun, report) { |
| renderNotes@227 | function | L227-236 |  | function renderNotes(collector, db) { |
| loadTasks@240 | function | L240-244 |  | async function loadTasks(probe = false) { |
| pendingLabel@246 | function | L246-250 |  | function pendingLabel(task) { |
| fillTaskSelect@253 | function | L253-259 | 常驻任务下拉框：只在候选集合变了才重建，否则轮询会把正在选的项冲掉 | function fillTaskSelect(tasks) { |
| renderTasks@261 | function | L261-313 |  | function renderTasks(data) { |
| saveIdle@315 | function | L315-340 |  | async function saveIdle(event) { |
| idleAction@342 | function | L342-354 |  | async function idleAction(url, body, button) { |
| currentMode@358 | function | L358-361 |  | function currentMode() { |
| currentStage@363 | function | L363-365 |  | function currentStage() { |
| syncMode@367 | function | L367-375 |  | function syncMode() { |
| collectForm@377 | function | L377-400 |  | function collectForm() { |
| validateForm@402 | function | L402-407 |  | function validateForm(mode, body) { |
| renderPreflight@409 | function | L409-464 |  | function renderPreflight(data) { |
| runPreflight@466 | function | L466-479 |  | async function runPreflight(silent = false) { |
| startRun@481 | function | L481-504 |  | async function startRun(event) { |
| exportLibrary@506 | function | L506-518 |  | async function exportLibrary() { |
| siteForm@522 | function | L522-530 |  | function siteForm() { |
| renderSitePreflight@532 | function | L532-564 |  | function renderSitePreflight(data) { |
| runSitePreflight@566 | function | L566-575 |  | async function runSitePreflight() { |
| startSiteRun@577 | function | L577-598 |  | async function startSiteRun(event) { |
| loadArticles@602 | function | L602-621 |  | async function loadArticles(page) { |
| renderArticles@623 | function | L623-645 |  | function renderArticles() { |
| renderPager@647 | function | L647-664 |  | function renderPager() { |
| renderPager.button@653 | arrow | L653-654 |  | const button = (label, target, options = {}) => |
| openArticle@666 | function | L666-700 |  | async function openArticle(key) { |
| loadJobs@704 | function | L704-709 |  | async function loadJobs() { |
| renderActiveJobs@711 | function | L711-734 |  | function renderActiveJobs(active) { |
| renderJobsTable@736 | function | L736-758 |  | function renderJobsTable(jobs) { |
| jobHeader@760 | function | L760-778 |  | function jobHeader(meta) { |
| openJob@780 | function | L780-810 |  | async function openJob(id) { |
| lineText@812 | function | L812-817 |  | function lineText(line) { |
| updateJobLog@819 | function | L819-825 |  | function updateJobLog() { |
| updateJobStatus@827 | function | L827-839 |  | function updateJobStatus(job) { |
| subscribeJob@841 | function | L841-863 |  | function subscribeJob(id) { |
| closeStream@865 | function | L865-870 |  | function closeStream() { |
| openDrawer@874 | function | L874-879 |  | function openDrawer(title, html) { |
| closeDrawer@881 | function | L881-886 |  | function closeDrawer() { |
| fillSelect@890 | function | L890-896 |  | function fillSelect(select, entries, placeholder) { |
| init@898 | function | L898-1019 |  | async function init() { |
