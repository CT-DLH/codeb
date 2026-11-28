/**
 * codeb 对话 API：把 webview/chat_engine.py 接进 webview/server.mjs。
 *
 * 设计：**每个会话一个常驻 Python 进程**。为什么不每个请求起一次：
 *   1. 上下文要跨轮保留（目录树 + 折叠账本），起一次就全丢
 *   2. 目录树扫描 + token 估算要几百毫秒，每轮重算纯浪费
 *
 * 协议：NDJSON over stdin/stdout（见 chat_engine.py 头部注释）。
 *
 * 路由：
 *   POST /api/chat/init     { repo, tree_depth, files[], route_specs[], custom[] }
 *                           → { ok, session_id, model, context_tokens, sections[] }
 *   POST /api/chat          { session_id, message }
 *                           → text/event-stream（每条 data: 一个 NDJSON 事件）
 *   POST /api/chat/reset    { session_id } → { ok }
 *   GET  /api/chat/context?session_id= → { sections[], system_tokens, total_tokens }
 *   POST /api/chat/close    { session_id } → { ok }
 */
import { spawn } from 'node:child_process'
import fs from 'node:fs'
import path from 'node:path'
import * as chatStore from './chat-store.mjs'

/** 找一个可用的 Python。优先项目自带的 agvenv。 */
function pythonCandidates(root) {
  return [
    path.join(root, '_kbwork', 'agvenv', 'Scripts', 'python.exe'),
    path.join(root, '_kbwork', 'agvenv', 'bin', 'python'),
    'python',
  ]
}

/** 一次 NDJSON 子进程 + 行分发。 */
class PyProc {
  constructor(exe, script, cwd) {
    // **必须带 -u**：Python 的 stdout 接到管道时会开全缓冲（不是行缓冲），
    // 于是 emit() 里的 flush() 也救不了——实测不加 -u 时 spawn 出来
    // 6 秒内一个字都收不到，init 直接超时。这是 Windows 管道下的实测行为。
    this.proc = spawn(exe, ['-X', 'utf8', '-u', script], {
      cwd, stdio: ['pipe', 'pipe', 'pipe'], windowsHide: true,
    })
    this.buf = ''
    this.pending = []      // 等待中的行消费者 [{ resolve, timer }]
    this.lines = []        // 早到还没人取的行（send 与 nextLine 之间的竞态窗口）
    this.stderr = ''
    this.alive = true

    this.proc.stdout.setEncoding('utf8')
    this.proc.stdout.on('data', (chunk) => this._onData(chunk))
    this.proc.stderr.setEncoding('utf8')
    this.proc.stderr.on('data', (c) => {
      this.stderr += c
      if (this.stderr.length > 8000) this.stderr = this.stderr.slice(-8000)
      if (process.env.KB_CHAT_DEBUG) console.error(`[py ${this.proc.pid}] stderr: ${String(c).slice(0, 400)}`)
    })
    this.proc.on('spawn', () => {
      if (process.env.KB_CHAT_DEBUG) console.error(`[py ${this.proc.pid}] spawned`)
    })
    this.proc.on('exit', () => {
      this.alive = false
      this.lines.length = 0     // 死进程的残留行不能再被读到
      // 唤醒所有等待者，避免请求永远挂着
      for (const w of this.pending.splice(0)) {
        clearTimeout(w.timer)
        w.reject(new Error(`Python 退出：${this.stderr.trim().slice(-500) || '无输出'}`))
      }
    })
    this.proc.on('error', (e) => {
      this.alive = false
      for (const w of this.pending.splice(0)) {
        clearTimeout(w.timer)
        w.reject(new Error(`Python 起不来：${e.message}`))
      }
    })
  }

  _onData(chunk) {
    this.buf += chunk
    let i
    while ((i = this.buf.indexOf('\n')) >= 0) {
      const line = this.buf.slice(0, i).trim()
      this.buf = this.buf.slice(i + 1)
      if (!line) continue
      if (process.env.KB_CHAT_DEBUG) {
        console.error(`[py ${this.proc.pid}] recv ${line.slice(0, 120)} (pending=${this.pending.length})`)
      }
      const w = this.pending.shift()
      if (w) {
        clearTimeout(w.timer)
        w.resolve(line)
      } else {
        // 没人等着：**先存下来，不能丢**。
        // 调用方是「先 send 再 nextLine」，而引擎可能比 nextLine 的注册还快
        // （加了 -u 之后 init_ok 常常是几毫秒就到）。早先这里是直接丢弃，
        // 于是 init 永远等不到那一行，120 秒后超时——而 /model 反而「成功」了，
        // 因为它读到的正是这条被剩下的 init_ok。
        this.lines.push(line)
      }
    }
  }

  /** 等下一行 NDJSON。 */
  nextLine(timeoutMs = 240000) {
    // 先看有没有早到的行
    if (this.lines.length) return Promise.resolve(this.lines.shift())
    return new Promise((resolve, reject) => {
      const timer = setTimeout(() => {
        const idx = this.pending.indexOf(entry)
        if (idx >= 0) this.pending.splice(idx, 1)
        reject(new Error(`等 LLM 响应超时（${Math.round(timeoutMs / 1000)}s）`))
      }, timeoutMs)
      const entry = { resolve, reject, timer }
      this.pending.push(entry)
    })
  }

  send(obj) {
    if (!this.alive) throw new Error('Python 进程已退出')
    const line = JSON.stringify(obj) + '\n'
    const ok = this.proc.stdin.write(line)
    if (process.env.KB_CHAT_DEBUG) {
      console.error(`[py ${this.proc.pid}] send ${obj.action} ok=${ok} pending=${this.pending.length} lines=${this.lines.length}`)
    }
  }

  kill() {
    this.alive = false
    try { this.proc.kill() } catch { /* ignore */ }
  }
}

/** 读请求体。 */
function readBody(req, limit = 4 * 1024 * 1024) {
  return new Promise((resolve, reject) => {
    const chunks = []
    let size = 0
    req.on('data', (c) => {
      size += c.length
      if (size > limit) { reject(new Error('请求体过大')); req.destroy(); return }
      chunks.push(c)
    })
    req.on('end', () => {
      const raw = Buffer.concat(chunks).toString('utf8')
      if (!raw) return resolve({})
      try { resolve(JSON.parse(raw)) } catch (e) { reject(new Error('不是合法 JSON')) }
    })
    req.on('error', reject)
  })
}

/** 读模型清单。每次现读，改 models.json 后刷新页面即生效。 */
function loadModels(root) {
  const p = path.join(root, 'webview', 'models.json')
  const fallback = {
    default: 'nvidia/nemotron-3.5-super-vl-120b-a12b',
    models: [{
      id: 'nvidia/nemotron-3.5-super-vl-120b-a12b',
      label: 'Nemotron 3.5 Super VL 120B',
      recommended: true,
    }],
    source: 'fallback',
  }
  try {
    const raw = fs.readFileSync(p, 'utf8')
    const data = JSON.parse(raw)
    if (!Array.isArray(data.models) || !data.models.length) return fallback
    // 过滤掉没 id 的项，注释字段不透出
    const models = data.models
      .filter((m) => m && typeof m.id === 'string' && m.id.trim())
      .map((m) => ({
        id: String(m.id).trim(),
        label: String(m.label || m.id).trim(),
        note: String(m.note || ''),
        recommended: !!m.recommended,
        context_window: Number(m.context_window) || 0,
      }))
    if (!models.length) return fallback
    const def = data.default && models.some((m) => m.id === data.default)
      ? data.default : models[0].id
    return { default: def, models, source: p }
  } catch {
    return fallback
  }
}

/** 列出可用仓库。**只列 repo_roots() 认可的仓库**，不列父目录的所有文件夹。
 *
 * 为什么必须收窄：cv 实测把 D:\work\project 下 74 个文件夹全列出来，
 * 其中 60+ 个根本没有知识页、装不出目录树——选中后上下文是空的，
 * 而界面看着像成功。**界面能选的东西必须真的能用**。
 *
 * kb.repo_roots 的判定是两条：
 *   1. repo/*.md 的 frontmatter 写了 root: → 用那个路径
 *   2. 没写的话退回「知识库根的兄弟目录」
 * 这里用同样的两条，并额外要求「目录存在」。
 */
function listRepos(root) {
  const out = []
  const seen = new Map()

  const add = (name, dir) => {
    if (!name || !dir || seen.has(name)) return
    let st
    try { st = fs.statSync(dir) } catch { return }
    if (!st.isDirectory()) return
    seen.set(name, { name, dir })
  }

  // ---- 规则 1：repo/ 下的页面 frontmatter 声明了 root: ----
  const repoDir = path.join(root, 'repo')
  try {
    const walk = (dir, depth) => {
      if (depth > 4) return
      let entries
      try { entries = fs.readdirSync(dir, { withFileTypes: true }) } catch { return }
      for (const e of entries) {
        const full = path.join(dir, e.name)
        if (e.isDirectory()) { walk(full, depth + 1); continue }
        if (!e.name.endsWith('.md')) continue
        let text = ''
        try { text = fs.readFileSync(full, 'utf8') } catch { continue }
        // 只看 frontmatter 前 20 行里的 root:
        const head = text.split('\n', 24).join('\n')
        const m = head.match(/^root:\s*(.+)$/m)
        if (!m) continue
        const declared = m[1].trim().replace(/^["']|["']$/g, '')
        // 仓库名取页面所在的一级目录名
        const rel = path.relative(repoDir, full).split(path.sep)
        const name = rel[0] === '00-projects.md' ? path.basename(declared) : rel[0]
        add(name, path.resolve(declared))
      }
    }
    walk(repoDir, 0)
  } catch { /* 无 repo/ */ }

  // ---- 规则 2：知识库根的兄弟目录（补齐规则 1 漏掉的）----
  // 只补「repo/ 下确实有同名目录」的那些，不是无差别扫父目录。
  try {
    const parent = path.dirname(root)
    for (const e of fs.readdirSync(repoDir, { withFileTypes: true })) {
      if (!e.isDirectory() || e.name.startsWith('.')) continue
      add(e.name, path.join(parent, e.name))
    }
  } catch { /* ignore */ }

  // ---- 补文件数（用于菜单里给「多大」的提示）----
  const SKIP = new Set(['node_modules', 'dist', '.git', '_kbwork', '__pycache__',
    '.venv', 'venv', '.cache', 'build', 'target', '.next', '.nuxt', 'vendor'])
  const countFiles = (dir) => {
    let n = 0
    const stack = [[dir, 0]]
    while (stack.length) {
      const [cur, depth] = stack.pop()
      if (depth > 9) continue
      let entries
      try { entries = fs.readdirSync(cur, { withFileTypes: true }) } catch { continue }
      for (const e of entries) {
        if (e.isDirectory()) {
          if (!SKIP.has(e.name) && !e.name.startsWith('.')) {
            stack.push([path.join(cur, e.name), depth + 1])
          }
        } else if (/\.(py|ts|tsx|js|jsx|mjs|cjs|go|rs|java|rb|php|vue|svelte)$/.test(e.name)) {
          n += 1
        }
      }
    }
    return n
  }

  for (const r of seen.values()) {
    out.push({ name: r.name, dir: r.dir, files: countFiles(r.dir) })
  }
  return out.sort((a, b) => a.name.localeCompare(b.name))
}

function sendJSON(res, code, obj) {
  const body = JSON.stringify(obj)
  res.writeHead(code, {
    'Content-Type': 'application/json; charset=utf-8',
    'Cache-Control': 'no-store',
    'Access-Control-Allow-Origin': '*',
  })
  res.end(body)
}

/**
 * 构造聊天 API。
 * @returns {(req, res, url) => Promise<boolean>} 返回 true 表示已处理
 */
export function createChatApi({ ROOT, PY_SCRIPT }) {
  /** sid → { py, exe, busy, sections, model, repo } */
  const sessions = new Map()
  let pyExe = null

  function resolvePython() {
    if (pyExe) return pyExe
    for (const c of pythonCandidates(ROOT)) {
      if (c === 'python') { pyExe = c; return c }  // 交给 PATH，起不来会在 spawn error 里报
      if (fs.existsSync(c)) { pyExe = c; return c }
    }
    pyExe = 'python'
    return pyExe
  }

  async function ensureSession(sid, initOpts) {
    let s = sessions.get(sid)
    if (s && s.py.alive) return s

    const py = new PyProc(resolvePython(), PY_SCRIPT, ROOT)
    s = { py, busy: false, sections: [], model: '', repo: initOpts?.repo || 'codeb' }
    sessions.set(sid, s)

    py.send({
      action: 'init',
      root: ROOT,
      repo: initOpts?.repo || 'codeb',
      tree_depth: initOpts?.tree_depth ?? 3,
      route_specs: initOpts?.route_specs || [],
      files: initOpts?.files || [],
      custom: initOpts?.custom || [],
      model: initOpts?.model || '',
      cot: !!initOpts?.cot,
      // 恢复历史：init 之后、首条 chat 之前由 chat_engine 灌回。
      // llmHistory 是前端存的 LLM 原始消息（含 tool_call_id），
      // 展示用的 messages 不能替代它——那是两回事。
      history: initOpts?.llmHistory || [],
    })
    const line = await py.nextLine(120000)
    let obj
    try { obj = JSON.parse(line) } catch { throw new Error(`初始化返回不是 JSON：${line.slice(0, 300)}`) }
    if (obj.type === 'error') throw new Error(obj.message || '初始化失败')
    if (obj.type !== 'init_ok') throw new Error(`初始化异常：${line.slice(0, 300)}`)

    s.sections = obj.sections || []
    s.model = obj.model || ''
    s.repo = obj.repo || s.repo
    s.init = obj
    return s
  }

  // 进程退出时清理
  process.on('exit', () => { for (const s of sessions.values()) s.py.kill() })

  return async function handleChat(req, res, url) {
    const p = url.pathname

    // ---------- 会话历史持久化 ----------
    // 这几个路由不带 session_id 进程语义，纯读写 sqlite，放在 chatApi 里
    // 只是为了共用 ROOT 与 sendJSON；不碰常驻 Python 进程。
    if (p === '/api/chat/sessions' && req.method === 'GET') {
      return sendJSON(res, 200, { ok: true, sessions: chatStore.listSessions(ROOT) }), true
    }
    if (p === '/api/chat/session' && req.method === 'GET') {
      const id = url.searchParams.get('id') || ''
      const d = chatStore.loadSession(ROOT, id)
      return sendJSON(res, 200, d ? { ok: true, ...d } : { ok: false, error: '没有这个会话' }), true
    }
    if (p === '/api/chat/session' && req.method === 'POST') {
      let body
      try { body = await readBody(req) } catch (e) { return sendJSON(res, 400, { ok: false, error: e.message }), true }
      const r = chatStore.saveSession(ROOT, body)
      return sendJSON(res, r.ok ? 200 : 500, r), true
    }
    if (p === '/api/chat/session' && req.method === 'DELETE') {
      let body = {}
      try { body = await readBody(req) } catch { /* ignore */ }
      const id = String(body.id || url.searchParams.get('id') || '')
      const r = chatStore.deleteSession(ROOT, id)
      return sendJSON(res, r.ok ? 200 : 500, r), true
    }
    if (p === '/api/chat/fork' && req.method === 'POST') {
      let body
      try { body = await readBody(req) } catch (e) { return sendJSON(res, 400, { ok: false, error: e.message }), true }
      const srcId = String(body.source_id || '')
      const upToSeq = Number(body.up_to_seq)
      const newId = String(body.new_id || '')
      if (!srcId || !newId || !Number.isInteger(upToSeq)) {
        return sendJSON(res, 400, { ok: false, error: 'source_id / new_id / up_to_seq 必填' }), true
      }
      const r = chatStore.forkSession(ROOT, srcId, upToSeq, newId, body.title)
      return sendJSON(res, r.ok ? 200 : 500, r), true
    }

    // ---------- 模型清单 ----------
    if (p === '/api/chat/models') {
      return sendJSON(res, 200, { ok: true, ...loadModels(ROOT) }), true
    }

    // ---------- 仓库清单（自动更新）----------
    if (p === '/api/chat/repos') {
      return sendJSON(res, 200, { ok: true, repos: listRepos(ROOT) }), true
    }

    // ---------- 切换思考链（已初始化的会话） ----------
    if (p === '/api/chat/cot' && req.method === 'POST') {
      let body = {}
      try { body = await readBody(req) } catch { /* 用默认 */ }
      const sid = String(body.session_id || 'default')
      const s = sessions.get(sid)
      if (!s || !s.py.alive) return sendJSON(res, 200, { ok: true, cot: !!body.cot }), true
      try {
        s.py.send({ action: 'cot', cot: !!body.cot })
        const line = await s.py.nextLine(15000)
        const obj = JSON.parse(line)
        return sendJSON(res, 200, { ok: true, ...obj }), true
      } catch (e) {
        return sendJSON(res, 500, { ok: false, error: String(e?.message || e) }), true
      }
    }

    // ---------- 导出 LLM history（持久化用） ----------
    if (p === '/api/chat/history' && req.method === 'POST') {
      let body = {}
      try { body = await readBody(req) } catch { /* 用默认 */ }
      const sid = String(body.session_id || 'default')
      const s = sessions.get(sid)
      if (!s || !s.py.alive) return sendJSON(res, 200, { ok: true, history: [] }), true
      try {
        s.py.send({ action: 'history' })
        const line = await s.py.nextLine(15000)
        const obj = JSON.parse(line)
        return sendJSON(res, 200, { ok: true, history: obj.history || [] }), true
      } catch (e) {
        return sendJSON(res, 500, { ok: false, error: String(e?.message || e) }), true
      }
    }

    // ---------- 停止当前生成 ----------
    if (p === '/api/chat/stop' && req.method === 'POST') {
      let body = {}
      try { body = await readBody(req) } catch { /* 用默认 */ }
      const sid = String(body.session_id || 'default')
      const s = sessions.get(sid)
      if (!s || !s.py.alive) return sendJSON(res, 200, { ok: false, error: '会话不存在' }), true
      try {
        // 只发 stop 指令，**不杀进程**：停止要保留已生成内容与上下文
        s.py.send({ action: 'stop' })
        return sendJSON(res, 200, { ok: true }), true
      } catch (e) {
        return sendJSON(res, 500, { ok: false, error: String(e?.message || e) }), true
      }
    }

    // ---------- 切换模型 ----------
    if (p === '/api/chat/model' && req.method === 'POST') {
      let body = {}
      try { body = await readBody(req) } catch { /* 用默认 */ }
      const sid = String(body.session_id || 'default')
      const model = String(body.model || '')
      const s = sessions.get(sid)
      if (!s || !s.py.alive) return sendJSON(res, 200, { ok: false, error: '会话不存在' }), true
      try {
        s.py.send({ action: 'model', model })
        const line = await s.py.nextLine(15000)
        const obj = JSON.parse(line)
        if (obj.type === 'model_ok') s.model = obj.model
        return sendJSON(res, 200, { ok: true, ...obj }), true
      } catch (e) {
        return sendJSON(res, 500, { ok: false, error: String(e?.message || e) }), true
      }
    }

    // ---------- 初始化 / 新建会话 ----------
    if (p === '/api/chat/init' && req.method === 'POST') {
      let body
      try { body = await readBody(req) } catch (e) { return sendJSON(res, 400, { ok: false, error: e.message }), true }
      const sid = String(body.session_id || `s-${Date.now().toString(36)}`)
      const old = sessions.get(sid)
      if (old) { old.py.kill(); sessions.delete(sid) }
      try {
        const s = await ensureSession(sid, body)
        sendJSON(res, 200, {
          ok: true, session_id: sid, repo: s.repo, model: s.model,
          cot: s.init?.cot ?? !!initOpts?.cot,
          history_restored: s.init?.history_restored ?? 0,
          context_tokens: s.init?.context_tokens ?? 0,
          system_tokens: s.init?.system_tokens ?? 0,
          tools_tokens: s.init?.tools_tokens ?? 0,
          sections: s.sections,
          // breakdown 要一起透传：前端上下文面板靠它展示「真正发出去的内容」。
          // 早先这里只挑了几个字段，面板就只能显示目录树，看不到系统提示词和工具定义。
          breakdown: s.init?.breakdown ?? null,
          raw: s.init?.raw ?? [],
        })
      } catch (e) {
        sendJSON(res, 500, { ok: false, error: String(e?.message || e) })
      }
      return true
    }

    // ---------- 发消息（SSE 流式）----------
    if (p === '/api/chat' && req.method === 'POST') {
      let body
      try { body = await readBody(req) } catch (e) { return sendJSON(res, 400, { ok: false, error: e.message }), true }
      const sid = String(body.session_id || 'default')
      const message = String(body.message || '').trim()
      if (!message) return sendJSON(res, 400, { ok: false, error: '消息为空' }), true

      let s
      try {
        s = await ensureSession(sid, body)
      } catch (e) {
        return sendJSON(res, 500, { ok: false, error: String(e?.message || e) }), true
      }
      if (s.busy) return sendJSON(res, 409, { ok: false, error: '这一轮还没结束' }), true

      s.busy = true
      res.writeHead(200, {
        'Content-Type': 'text/event-stream; charset=utf-8',
        'Cache-Control': 'no-cache, no-transform',
        'Connection': 'keep-alive',
        'X-Accel-Buffering': 'no',
        'Access-Control-Allow-Origin': '*',
      })
      res.write(': connected\n\n')

      // **必须用 res 的 close 检测客户端断开，不能用 req 的**：
      // req 的 'close' 在请求体读完时就触发（我们刚 readBody 完），
      // 用它会把「正常请求」误判成「客户端走了」，导致整轮被跳过。
      let clientGone = false
      res.on('close', () => { if (!res.writableEnded) clientGone = true })

      try {
        s.py.send({ action: 'chat', message })
        // 一轮 = 若干事件，直到 done / error。
        // 客户端中途走了也必须**读到底**：NDJSON 是共享的流，
        // 留下未消费的行会被下一轮当成自己的事件，上下文就错位了。
        for (;;) {
          const line = await s.py.nextLine(300000)
          let obj
          try { obj = JSON.parse(line) } catch { continue }
          if (!clientGone) {
            try { res.write(`data: ${JSON.stringify(obj)}\n\n`) } catch { clientGone = true }
          }
          if (obj.type === 'done' || obj.type === 'error') break
        }
      } catch (e) {
        if (!clientGone) {
          try {
            res.write(`data: ${JSON.stringify({ type: 'error', message: String(e?.message || e) })}\n\n`)
          } catch { /* ignore */ }
        }
      } finally {
        s.busy = false
        try { if (!res.writableEnded) res.end() } catch { /* ignore */ }
      }
      return true
    }

    // ---------- 上下文构成 ----------
    if (p === '/api/chat/context') {
      const sid = url.searchParams.get('session_id') || 'default'
      const s = sessions.get(sid)
      if (!s || !s.py.alive) return sendJSON(res, 200, { ok: false, error: '会话不存在' }), true
      try {
        s.py.send({ action: 'context' })
        const line = await s.py.nextLine(15000)
        sendJSON(res, 200, { ok: true, ...JSON.parse(line) })
      } catch (e) {
        sendJSON(res, 500, { ok: false, error: String(e?.message || e) })
      }
      return true
    }

    // ---------- 重置 / 关闭 ----------
    if (p === '/api/chat/reset' && req.method === 'POST') {
      let body = {}
      try { body = await readBody(req) } catch { /* 用默认 */ }
      const sid = String(body.session_id || 'default')
      const s = sessions.get(sid)
      if (s) { try { s.py.send({ action: 'reset' }) } catch { /* ignore */ } }
      return sendJSON(res, 200, { ok: true }), true
    }

    if (p === '/api/chat/close' && req.method === 'POST') {
      let body = {}
      try { body = await readBody(req) } catch { /* 用默认 */ }
      const sid = String(body.session_id || 'default')
      const s = sessions.get(sid)
      if (s) { s.py.kill(); sessions.delete(sid) }
      return sendJSON(res, 200, { ok: true }), true
    }

    // ---------- 会话列表（服务端视角）----------
    if (p === '/api/chat/sessions') {
      const list = [...sessions.entries()].map(([sid, s]) => ({
        session_id: sid, repo: s.repo, model: s.model, busy: s.busy,
        alive: s.py.alive, sections: s.sections.length,
      }))
      return sendJSON(res, 200, { ok: true, sessions: list }), true
    }

    return false
  }
}
