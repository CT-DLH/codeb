---
covers:
  - apps/web/src/components/SettingsPanel.tsx
title: Semantic block index: SettingsPanel.tsx (layer 4)
updated: 2026-11-24
---

# 语义块索引：SettingsPanel.tsx（第4层）

**源码文件**：`apps/web/src/components/SettingsPanel.tsx`  
**解析器**：`typescript`  
**第5层完整正文**：`read_block(path="apps/web/src/components/SettingsPanel.tsx", key="<name>@<line>")`  

| 语义块 key | 类型 | 行号 | 用途 | 签名 |
|:--|:--|:--|:--|:--|
| SettingsPanelProps@23 | interface | L23-28 |  | export interface SettingsPanelProps { |
| SettingsPanel@62 | function | L62-775 |  | export function SettingsPanel({ theme, setTheme, lang, setLang }: Sett… |
| SettingsPanel.patch@94 | arrow | L94-109 |  | const patch = async ( |
| SettingsPanel.setBackend@111 | arrow | L111-113 |  | const setBackend = (b: EmbedBackend): void => { |
| SettingsPanel.saveOnline@115 | arrow | L115-123 |  | const saveOnline = (): void => { |
| SettingsPanel.saveChat@128 | arrow | L128-132 | 侧边对话模型（R62）：多档列表，全量提交。 逐档的密钥输入框状态：id → 草稿值。存成 map 而不是单值， 否则同时编辑两档时后改的会覆盖前一个的输入。 | const saveChat = (): void => { |
| SettingsPanel.activateChat@142 | arrow | L142-158 | 用户很可能正在别的卡片里改着 model 名还没保存——如果走 patch， 那次 setS 会把所有未保存的编辑抹掉（切一下启用，刚打的字全没了）。 所以这里只改本地 activeId 并单独发请求 | const activateChat = (id: string): void => { |
| SettingsPanel.addChatProfile@160 | arrow | L160-176 |  | const addChatProfile = (): void => { |
| SettingsPanel.removeChatProfile@183 | arrow | L183-193 | 删除某档。与 activateChat 同理不走 patch： 删一张卡不该把别的卡里还没保存的改动一起丢掉。 提交的是当前本地列表（含未保存编辑），所以顺带把它们也存了，符合直觉。 | const removeChatProfile = (id: string): void => { |
| SettingsPanel.submitChat@200 | arrow | L200-230 | 提交档位列表但不用响应覆盖本地 state（保留未保存编辑与刚输入的 key）。 与 patch 的区别就在这里：patch 的 setS(r.settings) 适合「服务端是唯一真 | const submitChat = async ( |
| SettingsPanel.probeChat@233 | arrow | L233-256 |  | const probeChat = async (id: string): Promise<void> => { |
| SettingsPanel.runProbe@258 | arrow | L258-268 |  | const runProbe = async (): Promise<void> => { |
| SettingsPanel.runReindex@270 | arrow | L270-281 |  | const runReindex = async (): Promise<void> => { |
