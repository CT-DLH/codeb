---
covers:
  - scripts/serve-local.mjs
  - scripts/preview-server.mjs
  - scripts/needs-build.mjs
  - start.bat
updated: 2026-11-17
---

# Local server: three small scripts and a batch file

本地预览有三种入口，各自解决不同的问题，**端口与绑定地址各不相同**，混用是最常见的困惑来源。

| 入口 | 端口 | 绑定 | 服务什么 |
| :-- | :-- | :-- | :-- |
| `npm run dev` | vite 默认（5173 起） | 默认 localhost | 实时读 `cards/`，无构建 |
| `npm start` / `start.bat` | `PORT` 默认 **5478** | `HOST` 默认 **127.0.0.1** | `build/` 的 adapter-node 产物 |
| `node scripts/preview-server.mjs` | `argv[2]` 或 `PORT`，默认 **5478** | **硬编码 127.0.0.1** | `build/` 的静态文件（零依赖） |
| `npm run preview` | vite 默认 4179 | 默认 localhost | `build/`（vite 自己的 preview，不走上面两个脚本） |

`npm run preview` 与 `preview-server.mjs` 都预览 `build/`，但前者是 vite 内置的、后者是自己写的。选后者的理由是零依赖 + 能正确处理 Pagefind 的 `.pf_*` 分片 MIME。

## serve-local.mjs：adapter-node 的启动壳

做的事只有三件：

1. `process.env.HOST ??= '127.0.0.1'`——**默认只绑回环**。要局域网访问得显式设 `HOST=0.0.0.0`。这个默认值是安全设计：本地服务带敏感字段真值（`serve-local` 不剥离），不能默认暴露到网段。
2. 检查 `../build/index.js` 存在，不存在就 `console.error` + `exit 1`，提示「先跑 `npm run build:server`（或 `start.bat` 会自动构建）」。
3. `import('../build/index.js')` 动态 import 并调它的 `server` 导出。

所以它是**薄到几乎没有逻辑**的：真正的 HTTP 服务在 adapter-node 生成的 `build/index.js` 里。`PORT` 由 adapter-node 自己读（默认 3000，但 `start.bat` 会显式传 5478）。

注意它的敏感字段口径：**带值**。`build/index.js` 是 `BUILD_MODE=server` 的产物，`__BUILD_STATIC__` 为 false，`localRuntime()` 因此返回 true，`showSensitive()` 走显示分支。这是有意的——本地看的就是全字段。所以 `serve-local.mjs` 打印的那行提示写着「本地口径：敏感字段带值」。

## preview-server.mjs：零依赖静态服务器

自己写而不是用 `npx serve` 的理由全在这份脚本里：

**clean URL 映射**。`adapter-static` 把 `/domain/card_id` 输出成 `build/domain/card_id.html`。请求路径没有扩展名时先试 `X.html`，再试 `X/index.html`（`replace(/\/$/, '')` 先去掉尾斜杠）。这两步的顺序就是「详情页」与「目录页」的优先级。

**路径穿越防护**。`resolve` 之后检查 `fsPath.startsWith(BUILD_DIR)`，不满足就 403。少了这一步，`GET /../../.env` 能读到项目根的任何文件——而项目根有 `collector/.env`（LLM 凭据）。

**MIME 表**。手写的 `MIME` 对象，关键是 `.wasm` → `application/wasm`（Pagefind 的索引加载要它）和 **`.pf_*` 前缀 → `application/json`**。Pagefind 的分片文件名形如 `.pf_meta`、`.pf_fragment`——没有扩展名分隔符，`extname()` 拿到的是整个文件名，查不到 MIME 表，浏览器会因为 `application/octet-stream` 拒绝按 JSON 加载。这里专门用 `startsWith('.pf_')` 兜住。

**目录请求**。指向目录时补 `index.html`；`readFileSync` 失败（ENOENT / EISDIR / EACCES）统一 `res.writeHead(404)`，不区分——静态预览不需要区分。

它固定 `HOST = '127.0.0.1'`，**不可通过环境变量改**。要局域网访问得改代码。这与 `serve-local.mjs` 的口径不同（后者可改），因为静态预览可能带着带敏感值的 `build/`（刚跑完 `export:static:local`），硬编码是更稳的选择。

## needs-build.mjs：判断要不要重建

它回答一个问题：`build/handler.js` 是不是比源码新？

**比较的对象**（取所有这些路径下的最新 mtime，与 `build/handler.js` 比）：

- `src/` 整棵树
- `static/` 整棵树，**但排除 `static/data/`**
- `svelte.config.js` / `vite.config.ts` / `package.json` / `tsconfig.json` 四个配置文件

**排除 `static/data` 是有意的**：那个目录里是 `build:data` 的产物（万级分片），每次 `build:data` 都会把它们全部重写。如果算进 mtime，跑过一次 `build:data` 之后永远判「stale」，`start.bat` 每次都要白等一次 `build:server`。而 `build/handler.js` 是 `railway/` 那条服务端入口的产物，它**不读** `static/data`（在线模式实时读卡），所以那些文件的改动确实不需要重建。

**故意不看的**：`cards/`。在线模式每次请求实时读卡，改卡刷新即见，不需要重建。把它算进 mtime 会让每次改一张卡都触发一场分钟级的构建。

**输出与退出码**：打印 `fresh` 或 `stale`，**恒 `exit 0`**。`build/handler.js` 不存在时直接 `stale`。这是给 shell 用的：靠 stdout 的值判断，不靠退出码——因为「需要重建」不是错误。

`static/` 的遍历用递归 walk 且**跳过 `node_modules` 与以 `.` 开头的目录**（`.backup` / `.trash` / `.cache` / `.svelte-kit`）。这点很关键：`static/data` 之外还可能有人往里放 `.backup`，那些目录的 mtime 天天变。

## start.bat：把三件事串起来

批处理做的事，顺序不能变：

1. 解析 `--rebuild`（强制重建）与 `--no-open`（不自动开浏览器）。
2. 定 `PORT`（默认 5478）与 `HOST`（默认 127.0.0.1）。
3. 找 node。找不到就用写死的兜底路径——这是为了在**没配 PATH 的机器**上也能双击运行。
4. 杀掉占用该端口的旧进程（`netstat -ano` 找 PID → `taskkill`）。这一步不做的话，脚本会起一个新的然后端口冲突，而旧进程还在服务着旧产物——表现是「改了没生效」。
5. 调 `needs-build.mjs`，**只有输出恰好是 `fresh` 才跳过构建**。任何其他输出（包括脚本自身报错、node 找不到）都当 `stale` 处理。
6. `npm run build:server`。
7. `node scripts/serve-local.mjs`，需要时开浏览器。

**第 5 步的判定是「非 fresh 一律重建」而不是「stale 才重建」**，这是有意的取舍：注释里那句话是「多花 20 秒，好过看一份过期的包」。`needs-build.mjs` 的 mtime 判据有已知盲区（比如改了 `domains/*.yaml`——`domains/` 不在它的比较列表里），失败方向应该是「多构建一次」而不是「少构建一次」。

`OPEN_HOST` 的处理：如果 `HOST` 是 `0.0.0.0`，浏览器要开 `127.0.0.1` 而不是 `0.0.0.0`（后者在某些浏览器里会被当成无效地址）。

**整个批处理只用 ASCII**。中文注释在 OEM codepage（936）下会被按不同编码解读，`echo` 出来是乱码，更糟的是含中文的行在某些 codepage 组合下会被 cmd 解析错，导致跳转标签失效。所以这个文件里一个非 ASCII 字符都没有，需要说明的地方写英文。

## 三种入口怎么选

| 场景 | 用哪个 | 理由 |
| :-- | :-- | :-- |
| 改卡片内容，想立刻看 | `npm run dev` | 不构建，每请求实时读盘 |
| 改 Svelte 组件或路由 | `npm run dev` | 有 HMR |
| 验证「部署出去长什么样」 | `npm run export:static` 然后 `preview-server.mjs` | 走完整链路 + 静态产物 + 门禁 |
| 验证敏感字段渲染对不对 | `npm run export:static:local` 然后 `preview-server.mjs` | 带值口径，能看到真字段 |
| 日常本地使用（带值、要快） | `start.bat` | 带值 + 自动判断重建 + 自动开浏览器 |
| 只想看构建产物，不想装依赖 | `node scripts/preview-server.mjs` | 零依赖 |

一个容易踩的点：`start.bat` / `npm start` 服务的是 **server 形态**，`preview-server.mjs` 服务的是 **static 形态**。同一个 `build/` 目录里两套产物文件名不同（`index.js` + `handler.js` vs `index.html` + 分片），所以**不能拿 `start.bat` 验静态导出的结果**——它服务的是另一份东西。要验静态导出，必须先跑 `export:static` 再起 `preview-server.mjs`。

另一条：静态导出后 `build/` 里同时有 server 与 static 两套产物（`build/server/` + `build/client/` 或 `index.html`，取决于最后一次构建的模式）。`needs-build.mjs` 只看 `handler.js`，所以它对「静态产物是不是新的」完全无感——那是两套不同的新鲜度问题。
