/**
 * codeb webview — zero-dependency HTTP server.
 *
 *   node webview/server.mjs [--root D:\work\project\codeb] [--port 8777]
 *
 * Routes:
 *   GET /            → public/index.html
 *   GET /style.css   → public/style.css
 *   GET /app.js      → public/app.js
 *   GET /api/data    → JSON payload (data.mjs + live covers self-check)
 *   GET /api/health  → { ok: true, root, generatedAt }
 *
 * Static files are served from webview/public. Only those three names are
 * served — no path traversal. CORS is open (local dev tool).
 */
import http from 'node:http'
import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'
import { execFile } from 'node:child_process'
import { promisify } from 'node:util'
import { buildNode, buildPayload, detectRoot, parseCovers, parseParts } from './data.mjs'
import { readIndex } from './sqlite.mjs'

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
  '/': ['index.html', 'text/html; charset=utf-8'],
  '/index.html': ['index.html', 'text/html; charset=utf-8'],
  '/style.css': ['style.css', 'text/css; charset=utf-8'],
  '/app.js': ['app.js', 'text/javascript; charset=utf-8'],
}

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
    if (url.pathname === '/api/health') {
      return send(res, 200, JSON.stringify({ ok: true, root: ROOT, generatedAt: new Date().toISOString() }))
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
      const payload = buildPayload(ROOT, { lazyTree: true })
      payload.covers = { ...payload.covers, pending: true }
      // Optional sqlite derived index (kb reindex). Never required — the
      // Markdown scan above is the fallback and remains the source of truth.
      const idx = readIndex(ROOT)
      payload.index = idx || { live: false, source: 'none' }
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
