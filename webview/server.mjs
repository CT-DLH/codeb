/**
 * codeb webview — zero-dependency HTTP server.
 *
 *   node webview/server.mjs [--root D:\work\project\codeb] [--port 8777]
 *
 * 页面：
 *   GET /             → public/home.html   主页：选择 / 导入项目
 *   GET /p/<name>     → public/panel.html  项目面板：只显示该项目
 *   GET /chat         → public/chat.html   对话（?repo=<name> 锁定项目）
 *
 * API：
 *   GET  /api/data         → JSON payload；?project=<name> 只返回该项目
 *   GET  /api/projects     → 项目列表（含自动发现的）
 *   POST /api/projects     → 导入 { path, name? }（后台扫描）
 *   DELETE /api/projects   → 注销登记（不动 repo/ 与磁盘）
 *   GET  /api/health       → { ok: true, root, generatedAt }
 *   GET  /api/projtree     → 项目目录表（project_files + file_notes，只读）
 *                            ?repo=codeb 指定项目；缺省取第一个
 *
 * 静态文件从 webview/public 出，只发放白名单里的名字——无路径穿越。
 * CORS 全开（本地开发工具）。
 */
import http from 'node:http'
import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'
import { execFile } from 'node:child_process'
import { promisify } from 'node:util'
import * as chatApiMod from './chat-api.mjs'
import { buildNode, buildPayload, detectRoot, parseCovers, parseParts } from './data.mjs'
import { readIndex, readProjTree } from './sqlite.mjs'
import { addProject, projectStatus, refreshNotes, refreshStructure, removeProject } from './projects.mjs'

const execFileAsync = promisify(execFile)
const HERE = path.dirname(fileURLToPath(import.meta.url))
const PUBLIC = path.join(HERE, 'public')

// --- CLI args -------------------------------------------------------------
function arg(name, fallback = null) {
  const i = process.argv.indexOf(name)
  return i >= 0 && process.argv[i + 1] ? process.argv[i + 1] : fallback
}
const ROOT = detectRoot(arg('--root', process.cwd()))
const PORT = Number(arg('--port', '8777')) || 8777
const HOST = arg('--host', '127.0.0.1')

const STATIC = {
  // 主页 = 项目选择页；项目面板在 /p/<name>（动态路由，见 handler）
  '/': ['home.html', 'text/html; charset=utf-8'],
  '/index.html': ['home.html', 'text/html; charset=utf-8'],
  '/home.html': ['home.html', 'text/html; charset=utf-8'],
  '/home.js': ['home.js', 'text/javascript; charset=utf-8'],
  '/panel.html': ['panel.html', 'text/html; charset=utf-8'],
  '/style.css': ['style.css', 'text/css; charset=utf-8'],
  '/app.js': ['app.js', 'text/javascript; charset=utf-8'],
  // ---- 对话面板（codeb 自己实现的 LLM 对话，UI 壳照 DSH 的暗色主题）----
  '/chat': ['chat.html', 'text/html; charset=utf-8'],
  '/chat.html': ['chat.html', 'text/html; charset=utf-8'],
  '/chat.css': ['chat.css', 'text/css; charset=utf-8'],
  '/chat.js': ['chat.js', 'text/javascript; charset=utf-8'],
}

// 对话 API：每个会话一个常驻 Python 引擎（见 chat-api.mjs）
const chatApi = chatApiMod.createChatApi({
  ROOT,
  PY_SCRIPT: path.join(HERE, 'chat_engine.py'),
})

function send(res, code, body, type = 'application/json; charset=utf-8', cache = 'no-store') {
  res.writeHead(code, {
    'Content-Type': type,
    'Cache-Control': cache,
    'Access-Control-Allow-Origin': '*',
  })
  res.end(body)
}

/**
 * Run _kbwork/check_covers.py to get a LIVE covers report. If it fails for
 * any reason, fall back to whatever data.mjs read (snapshot or on-disk file).
 *
 * 这个子进程要 2 秒以上（扫 690 covers + 658 源文件），而结果只在 repo/ 下的
 * Markdown 变动时才变。所以按「repo/ 下所有 .md 的最新 mtime + 文件数」做缓存键：
 * 没改过就直接复用上次结果，改过才重跑。
 */
const coversCache = { key: null, value: null }

function repoMarkdownKey() {
  // 只需知道「有没有变」，用目录 mtime 链太粗（改文件不改目录 mtime），
  // 所以扫一遍 .md 的 mtime。这一步纯 fs.stat，比跑 Python 快两个量级。
  let newest = 0
  let count = 0
  const stack = [path.join(ROOT, 'repo')]
  while (stack.length) {
    const dir = stack.pop()
    let entries
    try { entries = fs.readdirSync(dir, { withFileTypes: true }) } catch { continue }
    for (const e of entries) {
      const full = path.join(dir, e.name)
      if (e.isDirectory()) { stack.push(full); continue }
      if (!e.name.endsWith('.md')) continue
      count += 1
      try {
        const st = fs.statSync(full)
        if (st.mtimeMs > newest) newest = st.mtimeMs
      } catch { /* ignore */ }
    }
  }
  return `${count}:${newest}`
}

async function liveCovers() {
  const key = repoMarkdownKey()
  if (coversCache.key === key && coversCache.value) return coversCache.value

  const pyCandidates = [
    path.join(ROOT, '_kbwork', 'agvenv', 'Scripts', 'python.exe'),
    'python',
  ]
  for (const py of pyCandidates) {
    try {
      const { stdout } = await execFileAsync(
        py,
        ['-X', 'utf8', path.join(ROOT, '_kbwork', 'check_covers.py')],
        { cwd: ROOT, timeout: 60000, maxBuffer: 8 * 1024 * 1024 },
      )
      if (stdout && /===.*\(/.test(stdout)) {
        const value = { ...parseCovers(stdout), live: true }
        coversCache.key = key
        coversCache.value = value
        return value
      }
    } catch { /* try next interpreter */ }
  }
  return null
}

const server = http.createServer(async (req, res) => {
  let url
  try {
    url = new URL(req.url, `http://${HOST}:${PORT}`)
  } catch {
    return send(res, 400, JSON.stringify({ error: 'bad url' }))
  }

  try {
    // 对话 API 优先（/api/chat*），交给 chat-api.mjs
    if (url.pathname.startsWith('/api/chat')) {
      const handled = await chatApi(req, res, url)
      if (handled) return
    }

    if (url.pathname === '/api/health') {
      return send(res, 200, JSON.stringify({ ok: true, root: ROOT, generatedAt: new Date().toISOString() }))
    }

    // ---------- 项目注册表 ----------
    // GET    列出项目（含自动发现的）
    // POST   导入一个项目 { path, name?, display?, note? }
    // DELETE 注销登记（只删表行，不动 repo/ 与磁盘）
    if (url.pathname === '/api/projects') {
      if (req.method === 'GET') {
        return send(res, 200, JSON.stringify({ ok: true, ...projectStatus(ROOT) }))
      }
      if (req.method === 'POST') {
        const chunks = []
        for await (const c of req) chunks.push(c)
        let body
        try { body = JSON.parse(Buffer.concat(chunks).toString('utf8')) }
        catch { return send(res, 400, JSON.stringify({ ok: false, error: 'invalid json' })) }
        const r = addProject(ROOT, body.path || body.disk_path, body)
        return send(res, r.ok ? 200 : 400, JSON.stringify(r))
      }
      if (req.method === 'DELETE') {
        let name = url.searchParams.get('name') || ''
        if (!name) {
          const chunks = []
          for await (const c of req) chunks.push(c)
          try { name = JSON.parse(Buffer.concat(chunks).toString('utf8')).name || '' } catch { /* 用 query */ }
        }
        const r = removeProject(ROOT, name)
        return send(res, r.ok ? 200 : 400, JSON.stringify(r))
      }
      return send(res, 405, JSON.stringify({ ok: false, error: 'method not allowed' }))
    }

    // POST /api/save — 手动编辑页表 md。安全：只写 ROOT/repo 下的 .md。
    if (url.pathname === '/api/save' && req.method === 'POST') {
      const chunks = []
      for await (const c of req) chunks.push(c)
      let body
      try { body = JSON.parse(Buffer.concat(chunks).toString('utf8')) }
      catch { return send(res, 400, JSON.stringify({ ok: false, error: 'invalid json' })) }
      const rel = String(body.path || '')
      const content = body.content
      if (typeof content !== 'string') {
        return send(res, 400, JSON.stringify({ ok: false, error: 'content must be string' }))
      }
      const target = path.resolve(ROOT, rel)
      const repoDir = path.join(ROOT, 'repo')
      // 三重校验：在 ROOT 内、在 repo/ 下、扩展名是 .md
      if (!target.startsWith(repoDir + path.sep)) {
        return send(res, 403, JSON.stringify({ ok: false, error: 'only repo/**/*.md is writable' }))
      }
      if (!target.endsWith('.md')) {
        return send(res, 403, JSON.stringify({ ok: false, error: 'only .md files are writable' }))
      }
      if (!fs.existsSync(path.dirname(target))) {
        return send(res, 400, JSON.stringify({ ok: false, error: 'parent dir missing' }))
      }
      try {
        // 写前备份到 _kbwork/webview-backups/（可回滚）
        const backup = path.join(ROOT, '_kbwork', 'webview-backups',
          rel.replace(/[\\/]/g, '__') + '.' + Date.now() + '.bak')
        fs.mkdirSync(path.dirname(backup), { recursive: true })
        if (fs.existsSync(target)) fs.copyFileSync(target, backup)
        fs.writeFileSync(target, content, 'utf8')
        return send(res, 200, JSON.stringify({ ok: true, path: rel, backup: path.relative(ROOT, backup) }))
      } catch (e) {
        return send(res, 500, JSON.stringify({ ok: false, error: String(e?.message || e) }))
      }
    }

    // 第3层部件按需加载：前端展开某模块时才请求，首屏不读这 300+ 个 md。
    if (url.pathname === '/api/parts') {
      const rel = url.searchParams.get('file') || ''
      const target = path.resolve(ROOT, rel)
      if (!target.startsWith(ROOT + path.sep)) {
        return send(res, 403, JSON.stringify({ error: 'outside workspace' }))
      }
      if (!target.endsWith('.md')) {
        return send(res, 400, JSON.stringify({ error: 'only .md' }))
      }
      let text = null
      try { text = fs.readFileSync(target, 'utf8') } catch { text = null }
      if (text === null) {
        return send(res, 200, JSON.stringify({ file: rel, parts: [], exists: false }))
      }
      return send(res, 200, JSON.stringify({
        file: rel, parts: parseParts(text), exists: true,
      }))
    }

    // covers 自检要跑 Python（2 秒级），首屏不等它——单独接口按需取。
    if (url.pathname === '/api/covers') {
      const live = await liveCovers()
      if (live) return send(res, 200, JSON.stringify(live))
      return send(res, 200, JSON.stringify({ live: false, source: 'none' }))
    }

    // 单节点按需加载：返回该页的直属下级 + 部件（层级深度由 md 决定）
    if (url.pathname === '/api/node') {
      const rel = url.searchParams.get('file') || ''
      const name = url.searchParams.get('name') || ''
      const target = path.resolve(ROOT, rel)
      if (!target.startsWith(ROOT + path.sep) || !target.endsWith('.md')) {
        return send(res, 403, JSON.stringify({ error: 'invalid path' }))
      }
      if (!fs.existsSync(target)) {
        return send(res, 200, JSON.stringify({ file: rel, children: [], parts: [], exists: false }))
      }
      const node = buildNode(ROOT, { name, file: rel, lazy: false })
      return send(res, 200, JSON.stringify({ file: rel, exists: true, ...node }))
    }

    if (url.pathname === '/api/data') {
      // 首屏只读第1、2层；部件由 /api/parts 懒加载，covers 由 /api/covers 懒加载。
      // ?project=<name> 只返回该项目的区块（项目面板用；主页不传=全部）
      const project = url.searchParams.get('project') || ''
      const payload = buildPayload(ROOT, { lazyTree: true, project })
      payload.covers = { ...payload.covers, pending: true }
      // Optional sqlite derived index (kb reindex). Never required — the
      // Markdown scan above is the fallback and remains the source of truth.
      const idx = readIndex(ROOT)
      payload.index = project && idx
        ? { ...idx, blockFiles: (idx.blockFiles || []).filter((f) => f.repo === project) }
        : (idx || { live: false, source: 'none' })
      if (idx) payload.source.index = 'sqlite'
      // Allow ?file=<path> to read an arbitrary UTF-8 file from the workspace
      // (used by the tree viewer to show a symbol page's contents).
      if (url.searchParams.has('file')) {
        const rel = url.searchParams.get('file') || ''
        const target = path.resolve(ROOT, rel)
        if (!target.startsWith(ROOT + path.sep) && target !== ROOT) {
          return send(res, 403, JSON.stringify({ error: 'outside workspace' }))
        }
        let content = null
        try { content = fs.readFileSync(target, 'utf8') } catch { content = null }
        return send(res, 200, JSON.stringify({ path: rel, content, exists: content !== null }))
      }
      return send(res, 200, JSON.stringify(payload))
    }

    // ---------- 目录表维护（两个按钮的后端）----------
    // refresh=structure  重新扫磁盘（不调 LLM，秒级）
    // refresh=notes      调 LLM 补写介绍（分钟级，逐批进行）
    // 都异步：同步会把请求挂死，前端只能看转圈。
    if (url.pathname === '/api/projtree/refresh' && req.method === 'POST') {
      const chunks = []
      for await (const c of req) chunks.push(c)
      let body
      try { body = JSON.parse(Buffer.concat(chunks).toString('utf8')) }
      catch { return send(res, 400, JSON.stringify({ ok: false, error: 'invalid json' })) }
      const repo = String(body.repo || '')
      const kind = String(body.kind || 'structure')
      if (!repo) return send(res, 400, JSON.stringify({ ok: false, error: '缺少 repo' }))
      const fn = kind === 'notes' ? refreshNotes : refreshStructure
      const r = fn(ROOT, repo, body)
      return send(res, r.ok ? 200 : 409, JSON.stringify(r))
    }


    // 只读；改介绍走 CLI（python -m distill.projtree note），避免前端误写结构。
    if (url.pathname === '/api/projtree') {
      const repo = url.searchParams.get('repo') || null
      const tree = readProjTree(ROOT, repo)
      if (!tree) {
        return send(res, 200, JSON.stringify({
          live: false, source: 'none', repos: [], repo: null,
          nodes: [], orphans: [], stats: null,
        }))
      }
      return send(res, 200, JSON.stringify(tree))
    }

    // ---------- 页面路由 ----------
    // /            主页：选择项目
    // /p/<name>    项目面板：只显示该项目
    // 必须在 STATIC 精确匹配之前拦，否则 /p/xxx 会落到 404。
    const pMatch = url.pathname.match(/^\/p\/([^/]+)\/?$/)
    if (pMatch) {
      const name = decodeURIComponent(pMatch[1])
      const fp = path.join(PUBLIC, 'panel.html')
      if (!fs.existsSync(fp)) {
        return send(res, 404, JSON.stringify({ error: 'missing panel.html' }))
      }
      return send(res, 200, fs.readFileSync(fp), 'text/html; charset=utf-8')
    }

    const staticFile = STATIC[url.pathname]
    if (staticFile) {
      const [name, type] = staticFile
      const fp = path.join(PUBLIC, name)
      if (!fs.existsSync(fp)) {
        return send(res, 404, JSON.stringify({ error: `missing ${name}` }))
      }
      const text = fs.readFileSync(fp)
      return send(res, 200, text, type)
    }

    return send(res, 404, JSON.stringify({ error: 'not found' }))
  } catch (err) {
    return send(res, 500, JSON.stringify({ error: String(err?.message || err) }))
  }
})

server.listen(PORT, HOST, () => {
  console.log(`codeb webview → http://${HOST}:${PORT}`)
  console.log(`workspace      → ${ROOT}`)
  console.log('press Ctrl+C to stop')
})
