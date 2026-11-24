# codeb — specification index

> 目标：给 LLM 维护的知识库，**结构少到不会用错，写入便宜到愿意写**。
>
> 设计细节已经全部落进知识库 `repo/codeb/`。本文件只保留**工具必须服从的硬契约**，
> 以及指向各页的索引。`kb.py` 必须服从本文件；反过来不成立。

---

## 0. 为什么本文件这么短

原先这里是一份 392 行的完整规格。它的内容和知识库重复了，而**两份设计文档必然分叉**——
分叉之后没有任何一处是权威的，读的人不知道该信哪份。

这与本项目反对 `manifest.toml` 的理由是同一条：多一个必须同步维护的真源，
就多一处会悄悄不一致的地方。所以规格正文迁进了知识库，本文件退化为索引 + 硬契约。

---

## 1. 硬契约（改动需同步改冒烟测试）

这七条是不可协商的。违反其中任何一条，工具就不是现在这个工具。

1. **根下必须有 `.codeb`**；所有页面在 `repo/` 之下。
2. **`repo/` 第一级目录 = 一个仓库**，英文名；`_shared/` 为保留名。
3. **页面文件名英文小写连字符**；**标题英文、正文中文**。
4. **唯一写入口是 `kb upsert`**，其余命令全部只读。
5. **规则只有一份实现**：`kb.py`。`mcp/server.ts` 只声明工具、校验参数、调内核。
6. **无状态**：不写数据库、不写缓存、不写索引文件，每次现场扫目录。
7. **UTF-8 / LF / 无 BOM**：读 `utf-8-sig`，写 `write_bytes(text.encode("utf-8"))`。

---

## 2. 路径（工具依赖这些位置）

```text
<root>/
├── .codeb
├── kb.py                    内核
├── mcp/server.ts            MCP 层
├── mcp/smoke.ts             端到端测试
└── repo/
    ├── _shared/             跨仓库知识
    └── <repo>/              每个仓库一个英文名目录，可按源码路径折叠
```

---

## 3. 设计正文在哪

| 主题 | 页面 |
| :-- | :-- |
| 整体是什么、三层结构 | `repo/codeb/overview` |
| 七个命令、退出码、`--body-file` | `repo/codeb/commands` |
| 页面格式、`covers` 三种匹配形态 | `repo/codeb/design/page-format` |
| 一段说明该放代码还是知识库 | `repo/codeb/design/where-knowledge-goes` |
| 怎么写一页有人读的东西 | `repo/codeb/design/writing-pages` |
| 被推翻的方案、决策理由、与旧版对照 | `repo/codeb/design/decisions` |
| 路由包：leader 点名成员集 + 每成员保真度 | `repo/codeb/route-packs-caller-declared-member-sets-and-the-fidelity-lad` |
| MCP 工具语义与写入循环 | `repo/codeb/mcp-tools` |
| MCP 协议实现细节与错误分级 | `repo/codeb/mcp-transport` |
| 实测缺陷清单（症状→原因→处理） | `repo/codeb/defects` |
| 跨仓库通用约定与环境坑 | `repo/_shared/conventions` |

用 `python kb.py tree` 看全貌，`python kb.py where <源文件>` 反查归属。

---

## 4. 尚未实现（刻意留白）

- **没有自动化检查**（漂移/覆盖/孤儿）。将来若要加，必须是独立只读命令，
  绝不参与写入路径，也绝不要求额外元数据文件——三条一起才保证它不退化成第二本账。
- **没有全文检索优化**。`kb search` 是逐行子串匹配（空白不敏感），几百页够用。
- **没有并发写保护**。两个会话同时 `kb upsert` 同一路径，后者可能覆盖前者。当前假设单会话维护。
- **没有删除/重命名命令**。直接用文件系统操作，然后跑 `kb tree` 确认没有断链。
- **没有跨仓库引用检查**。`covers` 写错路径不报错，只让 `kb where` 查不到——
  刻意的：`covers` 描述意图，不该被当作「引用的文件必须存在」的断言。

---

## 5. 验证

```bash
node mcp/smoke.ts        # 31 项断言，真实 stdio 协议，跑完自动清理
python kb.py tree        # 应能看到 codeb/ 与 infohub/ 下的折叠结构
```
