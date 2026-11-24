# codeb webview

一个零依赖的本地 web 面板，人工查看 codeb 项目的**多级页表**、covers 自检、
验证状态和 session 事件。数据直接来自工作区文件，刷新即可看到最新结果。

> **层级不写死**：树有几层由各项目的 Markdown 页表决定，不是固定的 5 层。
> 任何页面都可以用 `## 下级` 表格声明自己的直接子节点，前端递归渲染到任意深度。
> 例如 infohub 是 4 层：infohub → 采集模块 → 平台采集器（11 个）→ 各采集器的功能部件。

## 启动

```powershell
.\webview\start.ps1
```

或者手动：

```bash
node webview/server.mjs --root D:\work\project\codeb --port 8777
```

然后浏览器打开 **http://127.0.0.1:8777**

参数：
- `--root`：工作区根目录（默认从当前目录向上找 `repo/00-projects.md`）
- `--port`：端口（默认 8777）
- `--host`：监听地址（默认 127.0.0.1）

## 怎么声明层级

在任意页面的 Markdown 里写：

```markdown
## 下级

| 名称 | 说明 | 知识页 |
|:--|:--|:--|
| 平台采集器 | 按平台拆分的 11 个采集适配器 | [index](../collectors/index.md) |
```

- `名称` 列做节点标题，`说明` 列做副标题，`知识页` 列的 `.md` 链接决定下钻目标
- 子页面里再写 `## 下级`，就多一层；不写就是叶子
- 叶子用 `## 功能部件` 表格列出源码部件（key/类型/行号/作用）

也兼容旧的「模块表格」写法（表里含 `modules/` 或 `sources/` 链接即视为子节点）。

## 显示什么

| 区块 | 数据来源 |
|:--|:--|
| KPI | 项目数、**实际层级数**、知识页数、语义块数、covers 声明数、过期/冲突/未覆盖数 |
| 多级页表树 | `repo/00-projects.md` → 逐层 `## 下级` → `## 功能部件`，深度由数据决定 |
| covers 自检 | 服务器实时跑 `_kbwork/check_covers.py`，分 stale / conflict / uncovered 三页签 |
| 验证状态 | `_kbwork/regression_status.json` 或 `verification.json`，没有则显示快照 |
| Session 事件 | `_kbwork/agent-logs/*.jsonl` 与 `agent-traces/*.jsonl`，按时间合并 |

每个数据源在右上角有 `live` / `snapshot` 标记。`snapshot` 表示读不到真实文件时
用的内置兜底数据（首次快照），不是实时结果。

## 交互

- **多级页表树**：左侧根节点（一级·项目索引）→ 项目（二级）→ 模块（三级）→ 部件/语义块，每层都带简介卡片。
- **查看详情**：点任意节点，右侧显示该层页表的**完整 Markdown 原文**（含职责、适用场景、功能部件表、验证命令等全部细节）。
- **手动编辑**：右侧点「编辑」→ 修改 → 「保存」。保存只写 `repo/**/*.md`，写前自动备份到 `_kbwork/webview-backups/`（可回滚）；「取消」放弃修改，「打开文件」在新窗口按行号查看。
- **刷新**：重新拉取 `/api/data`，树和详情数据源都更新。

### 编辑安全

`POST /api/save` 三重校验：必须在 `ROOT/repo/` 下、扩展名 `.md`、父目录存在。路径穿越（如 `../../evil.md`）返回 403。每次保存前把原文复制到 `_kbwork/webview-backups/<路径>.<时间戳>.bak`，误改可用备份还原。

## 为什么不做成 DSH 插件界面

DSH 的 client 插件需要 `inject` 白名单，且浏览器端要 HMR/刷新才生效；
本面板是独立进程，跟 DSH 解耦——换工作区、改文件、重启都不影响 DSH 会话。

## sqlite 派生索引（可选加速）

页表数据**以 Markdown 为 source of truth**，sqlite 只是派生索引（materialized view）：
- `_kbwork/codeb-index.db`：`pages` / `covers` / `blocks` / `meta` 四表
- 重建：`python -X utf8 kb.py reindex`（stdlib sqlite3，kb.py 仍零外部依赖）
- 查询：`python -X utf8 kb.py blocks --file kb.py`、`python -X utf8 kb.py covers-check`
- webview 通过 `node:sqlite` 只读该 db（右上角 `index: sqlite` 标记）；db 不存在或 Node 不支持时自动回退到 Markdown 扫描

**修改页表 md 后要重建索引**才能在 sqlite 视图里看到变化；webview 的树/详情直接读 md，无需重建。

## 性能：三层懒加载

首屏只读必要的文件，其余按需拉取（实测 2784ms → 206ms 冷启 / 18ms 热）：

| 接口 | 内容 | 何时加载 | 耗时 |
|:--|:--|:--|:--|
| `/api/data` | 第1层项目 + 第2层模块名/简介 | 首屏 | 206ms 冷 / 18ms 热 |
| `/api/parts?file=` | 第3层某模块的部件表 | 展开该模块时 | ~15ms |
| `/api/covers` | covers 自检（跑 Python） | 首屏后异步补 | 2067ms 首次 → 36ms 缓存 |

**为什么这样分**：

- `buildTree` 默认 `lazy:true`，不读第3层那 300+ 个 md，payload 从 87.5 KB 降到 23.3 KB。
- covers 自检要起 Python 子进程扫 690 covers + 658 源文件，占原本总耗时 80%。它已改成独立接口 + 按 `repo/**/*.md` 的 mtime 键缓存，`repo/` 没改动就直接复用上次结果。
- 页面先渲染树和 KPI，covers 卡片显示「自检计算中…」再后台补齐。

## 数据更新

页面读的是磁盘文件，所以：
- agent 跑完任务 → session log 增加 → 刷新可见；
- 改了源码 → 重跑 `check_covers.py` → 刷新可见实时自检；
- 页表 md 变化 → 刷新可见新项目/模块/块。

## 文件

```
webview/
├── server.mjs          # 零依赖 HTTP 服务器
├── data.mjs            # 数据解析（从 DSH 插件抽取并改进）
├── start.ps1           # 启动脚本
├── README.md
└── public/
    ├── index.html
    ├── style.css
    └── app.js
```
