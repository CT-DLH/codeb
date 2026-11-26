# launcher: 通用本地启动器模板

把 `start.bat` 里**项目无关的骨架**抽出来固化，项目差异全部收敛到 `launcher.bat` 顶部一个 `CONFIG` 块。拷进新项目改几行就能用。

## 文件

- `launcher.bat` — 通用骨架。复制到项目根，只改顶部 `CONFIG START`～`CONFIG END` 之间的变量。
- `needs-build.mjs` — 通用新鲜度探测（可选接入）。

## 骨架做什么（七步，顺序不能变）

1. 解析 `--rebuild` / `--no-open` / `-h`。
2. `PORT` / `HOST` 默认值（env 可覆盖 config）。
3. 找 node：`where node` → 找不到退回 `NODE_FALLBACK`（为没配 PATH 的机器能双击）。
4. 判断要不要重建：`--rebuild`、或产物 `DIST_MARKER` 不存在、或探测脚本输出非 `fresh`。
5. 杀掉占用 `PORT` 的旧进程（`netstat -ano` + `taskkill`）。
6. 按需 `BUILD_CMD`，失败即停不启动。
7. 前台 `SERVE_CMD` + 按需开浏览器。

## 接入一个新项目

改 `CONFIG` 块这六个变量即可：

| 变量 | 含义 | 示例 |
| :-- | :-- | :-- |
| `APP_NAME` | 日志前缀 | `myapp` |
| `PORT` / `HOST` | 端口与绑定，默认回环 | `3000` / `127.0.0.1` |
| `NODE_FALLBACK` | 无 PATH 时的 node 兜底路径，留空则强制要 PATH | `C:\...\node.exe` |
| `BUILD_CMD` | 构建命令，产物要落到 `DIST_MARKER` | `npm run build` |
| `DIST_MARKER` | 「已构建」标记产物 | `build\index.js` |
| `PROBE_SCRIPT` | 可选新鲜度探测脚本，留空则只在产物缺失/`--rebuild` 时重建 | `scripts\needs-build.mjs` |
| `SERVE_CMD` | 前台服务命令（不后台化） | `%NODE% scripts/serve.mjs` |

## 探测脚本契约

`needs-build.mjs` 必须满足：

- stdout 打印**恰好** `fresh` 或 `stale`；
- **恒 `exit 0`**（「需要重建」不是错误，靠 stdout 传值而非退出码）；
- 产物缺失直接 `stale`。

骨架的判定是「**非 `fresh` 一律重建**」而不是「`stale` 才重建」——探测自身报错、node 异常都当重建处理。失败方向是「多构建一次」而非「少构建一次」，因为 mtime 判据总有盲区（比如没纳入 `domains/*.yaml`），20 秒重建好过看一份过期包。

`needs-build.mjs` 用法：

```
node scripts/needs-build.mjs build\handler.js src static svelte.config.js vite.config.ts package.json
```

第一个参数是 marker，后面是要比较的源/配置路径。目录会递归遍历，自动跳过 `node_modules` 和任何 `.` 开头目录（`.backup`/`.trash`/`.cache`/`.svelte-kit`）——这些目录 mtime 天天变，跟源码是否需要重建无关。

## 三条必须记住的坑（都来自 start.bat 实战）

1. **全程 ASCII-only。** `cmd.exe` 用 OEM codepage（936）解析 `.bat`，UTF-8 中文会被从字符中间截断，更糟的是含中文的行在某些 codepage 组合下让 `goto` 标签失效。需要说明的地方写英文。
2. **杀端口这步不能省。** 不杀就起一个新进程然后端口冲突，而旧进程还在服务旧产物——表现是「改了没生效」。
3. **默认绑回环。** 本地服务常带敏感真值（live 模式不剥离），`HOST` 默认 `127.0.0.1` 是安全设计；要暴露到网段必须显式 `set HOST=0.0.0.0`。浏览器会把 `0.0.0.0` 当无效地址，所以骨架开浏览器时自动换成 `127.0.0.1`。

## 已知边界

- `PROBE_SCRIPT` 留空时，只有「产物不存在」或「`--rebuild`」会触发构建，日常改源码不会自动重建。
- `SERVE_CMD` 是前台阻塞运行，`Ctrl+C` 即停。
- `BUILD_CMD` 用 `call` 调用，确保执行完返回继续往下走，不会因 npm 内部跳转提前结束脚本。