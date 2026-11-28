'use strict'

/* ==========================================================================
   codeb 对话面板前端
   
   职责边界（这是「借用 DSH 的 UI 壳、功能自己实现」的落点）：
     前端  → 只管渲染、会话切换、SSE 消费。零业务逻辑。
     后端  → chat-api.mjs 管进程，chat_engine.py 管上下文与 agent loop。
   
   会话状态：前端内存 + 后端 Python 进程 + sqlite 落盘（webview/chat-store.mjs）。
   刷新页面会从 sqlite 恢复会话列表与消息，点侧栏会话即可继续。
   ========================================================================== */

const $ = (id) => document.getElementById(id)
const el = (tag, cls) => { const e = document.createElement(tag); if (cls) e.className = cls; return e }

/* ─────────────────────────────── 状态 */
const S = {
  sessions: [],          // [{id, title, repo, model, ctxTokens, messages:[], sections:[]}]
  activeId: null,
  streaming: false,
  trajectory: [],        // 当前会话的工具调用轨迹
  models: [],            // 从 /api/chat/models 拉
  defaultModel: '',
  repos: [],             // 从 /api/chat/repos 拉（repo_roots 的磁盘视角）
  cot: false,            // 是否让模型输出思考链（顶栏开关）
  ctxMode: 'aggregated', // 上下文页签视图：aggregated | raw
}

/**
 * 默认仓库：从 ?repo= 读（项目面板点「对话」时带过来），否则 codeb。
 *
 * 不读的话，从 infohub 面板进对话会静默问成 codeb——
 * 界面在说「infohub 的对话」，装进上下文的却是别的项目。
 */
const repo = (() => {
  const q = new URLSearchParams(location.search).get('repo')
  return q || 'codeb'
})()
/** ?repo= 给了就锁定，切仓库入口禁用（见 repoBtn 的 onclick）。 */
const LOCKED_REPO = !!new URLSearchParams(location.search).get('repo')
const DEFAULT_TREE_DEPTH = 3

/* ─────────────────────────────── 工具函数 */
const esc = (s) => String(s ?? '').replace(/[&<>"']/g, (c) =>
  ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]))

let toastTimer = null
function toast(msg) {
  const t = $('toast')
  t.textContent = msg
  t.classList.add('show')
  clearTimeout(toastTimer)
  toastTimer = setTimeout(() => t.classList.remove('show'), 2200)
}

function fmtTok(n) {
  if (!n || n < 0) return '0'
  if (n < 1000) return String(n)
  return (n / 1000).toFixed(n < 10000 ? 1 : 0) + 'k'
}

function active() {
  return S.sessions.find((s) => s.id === S.activeId) || null
}

/* ─────────────────────────────── 极简 markdown 渲染
   不引第三方库（本项目零依赖原则）。只覆盖模型实际会输出的语法：
   围栏代码块、行内代码、标题、粗体、列表、表格、引用、段落。
   顺序很重要：先抠出代码块占位，避免块内内容被后续规则破坏。 */
function renderMarkdown(text) {
  if (!text) return ''
  const blocks = []
  let s = String(text)

  // 1. 围栏代码块 → 占位符（此时 code 还是原文，esc 一次是对的）
  s = s.replace(/```([\w+-]*)\n?([\s\S]*?)```/g, (_, lang, code) => {
    const i = blocks.length
    blocks.push(`<pre><code>${esc(code.replace(/\n$/, ''))}</code></pre>`)
    return `\u0000CB${i}\u0000`
  })

  // 2. 行内代码 → 占位符。**必须在 esc 之前**：
  // 放在 esc 之后的话，code 已经是 `&quot;` 形态，再 esc 一次就成
  // `&amp;quot;`，页面上会把实体原样显示出来（实测踩到）。
  const inlines = []
  s = s.replace(/`([^`\n]+)`/g, (_, code) => {
    const i = inlines.length
    inlines.push(`<code>${esc(code)}</code>`)
    return `\u0000IC${i}\u0000`
  })

  // 3. 转义剩下的（代码块与行内代码已抠成占位符，不会二次转义）
  s = esc(s)

  // 4. 表格
  s = s.replace(/(^\|.*\|[ \t]*\n\|[\s:|-]+\|[ \t]*\n(?:\|.*\|[ \t]*(?:\n|$))+)/gm, (tbl) => {
    const lines = tbl.trim().split('\n')
    const cells = (ln) => ln.replace(/^\||\|$/g, '').split('|').map((c) => c.trim())
    const head = cells(lines[0])
    const body = lines.slice(2).map(cells)
    const th = head.map((c) => `<th>${c}</th>`).join('')
    const trs = body.map((r) => `<tr>${r.map((c) => `<td>${c}</td>`).join('')}</tr>`).join('')
    return `\u0000TB<table><thead><tr>${th}</tr></thead><tbody>${trs}</tbody></table>TB\u0000`
  })

  // 5. 标题
  s = s.replace(/^######\s+(.+)$/gm, '<h3>$1</h3>')
  s = s.replace(/^#####\s+(.+)$/gm, '<h3>$1</h3>')
  s = s.replace(/^####\s+(.+)$/gm, '<h3>$1</h3>')
  s = s.replace(/^###\s+(.+)$/gm, '<h3>$1</h3>')
  s = s.replace(/^##\s+(.+)$/gm, '<h2>$1</h2>')
  s = s.replace(/^#\s+(.+)$/gm, '<h1>$1</h1>')

  // 6. 粗体 / 斜体
  s = s.replace(/\*\*([^*\n]+)\*\*/g, '<strong>$1</strong>')
  s = s.replace(/(?<![*\w])\*([^*\n]+)\*(?!\w)/g, '<em>$1</em>')

  // 7. 引用
  s = s.replace(/^&gt;\s?(.+)$/gm, '<blockquote>$1</blockquote>')

  // 8. 列表：连续的行包成一个 <ul>/<ol>
  s = s.replace(/(?:^[ \t]*[-*+]\s+.+(?:\n|$))+/gm, (blk) => {
    const items = blk.trim().split('\n')
      .map((l) => l.replace(/^[ \t]*[-*+]\s+/, '').trim())
      .filter(Boolean)
    return `<ul>${items.map((i) => `<li>${i}</li>`).join('')}</ul>`
  })
  s = s.replace(/(?:^[ \t]*\d+[.)]\s+.+(?:\n|$))+/gm, (blk) => {
    const items = blk.trim().split('\n')
      .map((l) => l.replace(/^[ \t]*\d+[.)]\s+/, '').trim())
      .filter(Boolean)
    return `<ol>${items.map((i) => `<li>${i}</li>`).join('')}</ol>`
  })

  // 9. 段落：空行分段，段内换行转 <br>
  const blocksOut = s.split(/\n{2,}/).map((seg) => {
    const t = seg.trim()
    if (!t) return ''
    if (/^<(h[123]|ul|ol|table|blockquote|pre|div)/.test(t)) return t
    if (/^\u0000TB/.test(t)) return t
    if (/^\u0000CB/.test(t)) return t
    return `<p>${t.replace(/\n/g, '<br>')}</p>`
  }).filter(Boolean)
  s = blocksOut.join('\n')

  // 10. 还原占位符
  s = s.replace(/\u0000TB([\s\S]*?)TB\u0000/g, (_, t) => t)
  s = s.replace(/\u0000CB(\d+)\u0000/g, (_, i) => blocks[Number(i)] || '')
  s = s.replace(/\u0000IC(\d+)\u0000/g, (_, i) => inlines[Number(i)] || '')

  return s
}

/* ─────────────────────────────── SSE 解析
   fetch + ReadableStream 手解 SSE。不用 EventSource：
   那只能用 GET，而我们要 POST 带 body。 */
async function* sseStream(url, body, signal) {
  const resp = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
    signal,
  })
  if (!resp.ok) {
    let detail = ''
    try { detail = (await resp.text()).slice(0, 400) } catch { /* ignore */ }
    throw new Error(`HTTP ${resp.status} ${detail}`)
  }
  const reader = resp.body.getReader()
  const dec = new TextDecoder()
  let buf = ''
  for (;;) {
    const { done, value } = await reader.read()
    if (done) break
    buf += dec.decode(value, { stream: true })
    let idx
    while ((idx = buf.indexOf('\n\n')) >= 0) {
      const frame = buf.slice(0, idx)
      buf = buf.slice(idx + 2)
      for (const line of frame.split('\n')) {
        if (!line.startsWith('data: ')) continue
        const json = line.slice(6)
        try { yield JSON.parse(json) } catch { /* 跳过坏帧 */ }
      }
    }
  }
}

/* ─────────────────────────────── 会话管理 */
function newSession(opts = {}) {
  const id = 's-' + Date.now().toString(36) + Math.random().toString(36).slice(2, 6)
  // 新会话继承「当前会话的模型与仓库」：换项目时用户刚点过一次，
  // 不该每开一个新会话都要再选一遍。
  const prev = active()
  const s = {
    id,
    title: opts.title || '新会话',
    repo: opts.repo || prev?.repo || repo,
    model: opts.model || prev?.model || S.defaultModel || '',
    ctxTokens: 0,
    sections: [],
    messages: [],      // [{role, text, tools:[]}]
    ready: false,
    treeDepth: opts.tree_depth ?? DEFAULT_TREE_DEPTH,
    files: opts.files || [],
    routeSpecs: opts.route_specs || [],
    custom: opts.custom || [],
    cot: opts.cot ?? S.cot,
    llmHistory: [],        // LLM 原始 history（含 tool_call_id），持久化用
  }
  S.sessions.unshift(s)
  S.activeId = id
  S.trajectory = []
  renderSessions()
  renderMessages()
  renderTrajectory()
  renderContext()
  return s
}

function switchSession(id) {
  if (S.streaming) { toast('这一轮还没结束'); return }
  S.activeId = id
  S.trajectory = []
  const s = active()
  if (s) {
    // 轨迹从消息里的 tools 重建（刷新后仍可看）
    for (const m of s.messages) {
      for (const t of (m.tools || [])) S.trajectory.push({ ...t, msgRole: m.role })
    }
  }
  renderSessions()
  renderMessages()
  renderTrajectory()
  renderContext()
}

async function deleteSession(id) {
  const i = S.sessions.findIndex((s) => s.id === id)
  if (i < 0) return
  try {
    await fetch('/api/chat/close', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_id: id }),
    })
  } catch { /* 后端没起也无妨 */ }
  try { await fetch('/api/chat/session', { method: 'DELETE',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ id }) }) } catch { /* ignore */ }
  S.sessions.splice(i, 1)
  if (S.activeId === id) {
    S.activeId = S.sessions[0]?.id || null
    S.trajectory = []
  }
  if (!S.sessions.length) newSession()
  else {
    renderSessions(); renderMessages(); renderTrajectory(); renderContext()
  }
}

/* ─────────────────────────────── 渲染：会话列表 */
function renderSessions() {
  const box = $('sessionList')
  box.innerHTML = ''
  if (!S.sessions.length) {
    box.innerHTML = '<div class="session-empty">还没有会话</div>'
    return
  }
  for (const s of S.sessions) {
    const item = el('div', 'session-item' + (s.id === S.activeId ? ' active' : ''))
    const title = el('span', 'session-title')
    title.textContent = s.title
    title.title = s.title
    const del = el('button', 'session-del')
    del.innerHTML = '<svg viewBox="0 0 16 16" width="12" height="12"><path d="M4 4l8 8M12 4l-8 8" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>'
    del.title = '删除会话'
    del.onclick = (e) => { e.stopPropagation(); deleteSession(s.id) }
    item.append(title, del)
    item.onclick = () => openSavedSession(s.id)
    box.append(item)
  }
}

/* ─────────────────────────────── 渲染：消息 */
function msgNode(m) {
  const node = el('div', 'msg msg-' + m.role)
  const role = el('div', 'msg-role')
  role.textContent = m.role === 'user' ? '你' : 'AI'
  const body = el('div', 'msg-body')

  // 思考链：可折叠，默认收起；照 DSH ReasoningRow 的形态。
  if (m.cot) {
    const row = el('details', 'cot-row' + (m.pending ? ' running' : ''))
    const sum = el('summary')
    const chev = el('span', 'cot-chevron')
    chev.textContent = '▶'
    const label = el('span', 'cot-label')
    label.textContent = '思考'
    const brief = el('span', 'cot-summary')
    const first = (m.cot || '').split('\n').find((l) => l.trim()) || ''
    brief.textContent = first.replace(/\*\*/g, '').slice(0, 80)
    sum.append(chev, label, brief)
    if (m.pending) {
      const run = el('span', 'cot-running')
      run.textContent = '思考中…'
      sum.append(run)
    }
    const bodyEl = el('div', 'cot-body')
    bodyEl.textContent = m.cot
    row.append(sum, bodyEl)
    body.append(row)
  }

  if (m.tools && m.tools.length) {
    const wrap = el('div', 'tools')
    for (const t of m.tools) wrap.append(toolCard(t))
    body.append(wrap)
  }

  // 工具轮次提示：模型可能连着跑十几轮工具才说第一句话（实测一次 25 轮），
  // 那期间不给动静，用户看到的就是「发完消息，界面空白几十秒」。
  if (m.pending && m.tools && m.tools.length && !m.text) {
    const still = m.tools.filter((t) => t.state === 'running')
    const tip = el('div', 'tools-status')
    tip.textContent = still.length
      ? `正在执行 ${still.map((t) => t.name).join('、')}…`
      : `已完成 ${m.tools.length} 次工具调用，正在汇总…`
    body.append(tip)
  }

  const text = el('div', 'msg-text')
  if (m.role === 'assistant') text.innerHTML = renderMarkdown(m.text || '')
  else text.textContent = m.text || ''
  if (m.pending) text.insertAdjacentHTML('beforeend', '<span class="cursor"></span>')
  body.append(text)

  // 每轮 token 用量（DSH TurnUsagePanel 的轻量版）
  if (m.role === 'assistant' && m.usage && !m.pending) {
    const bar = el('div', 'usage-bar')
    const u = m.usage
    const inTok = u.prompt_tokens ?? u.input_tokens
    const outTok = u.completion_tokens ?? u.output_tokens
    const reasonTok = (u.completion_tokens_details?.reasoning_tokens
      ?? u.output_tokens_details?.reasoning_tokens)
    const bits = []
    if (inTok != null) bits.push(`输入 ${fmtTok(inTok)}`)
    if (outTok != null) bits.push(`输出 ${fmtTok(outTok)}`)
    if (reasonTok != null) bits.push(`思考 ${fmtTok(reasonTok)}`)
    if (bits.length) {
      const pill = el('span', 'usage-pill')
      pill.textContent = bits.join(' · ')
      bar.append(pill)
    }
    if (bar.childElementCount) body.append(bar)
  }

  if (m.error) {
    const err = el('div', 'msg-error')
    err.textContent = m.error
    body.append(err)
  }

  // 消息操作行：复制 + 分支（对齐 DSH MessageIconActions）
  if (!m.pending) {
    const acts = el('div', 'msg-actions')
    const copy = el('button', 'msg-act')
    copy.textContent = '复制'
    copy.title = '复制这条消息'
    copy.onclick = async () => {
      try {
        await navigator.clipboard.writeText(m.text || '')
        copy.textContent = '已复制'
        setTimeout(() => { copy.textContent = '复制' }, 1500)
      } catch { toast('复制失败') }
    }
    acts.append(copy)
    // 分支只在完成的 transcript 上可用（DSH 也是这条规则）
    const branch = el('button', 'msg-act')
    branch.textContent = '分支'
    branch.title = '从这条消息分叉出新会话'
    branch.onclick = () => branchFrom(m)
    acts.append(branch)
    body.append(acts)
  }

  node.append(role, body)
  return node
}

/** 工具调用卡片：折叠态给「名字 + 参数摘要 + token + 状态点」，
    展开态给完整的请求参数与返回正文。
    为什么默认收起：一次分析常调 3-8 个工具，全展开会把回答顶出屏幕；
    DSH 也是这个默认。 */
function toolCard(t) {
  const card = el('div', 'tool-card' + (t.open ? ' open' : ''))
  const head = el('div', 'tool-card-head')

  const caret = el('span', 'tool-caret')
  caret.textContent = '▶'

  const state = el('span', 'tool-state ' + (t.state || 'running'))
  const name = el('span', 'tool-card-name')
  name.textContent = t.name
  const args = el('span', 'tool-card-args')
  args.textContent = t.argsText || ''
  args.title = t.argsText || ''
  const tok = el('span', 'tool-card-tok')
  tok.textContent = t.tokens ? fmtTok(t.tokens) + ' tok' : ''

  head.append(caret, state, name, args, tok)

  const bodyEl = el('div', 'tool-card-body')
  if (t.args && Object.keys(t.args).length) {
    const lab = el('span', 'tool-body-label')
    lab.textContent = '请求参数'
    const txt = el('div', 'tool-body-text')
    txt.textContent = JSON.stringify(t.args, null, 2)
    bodyEl.append(lab, txt)
  }
  if (t.result) {
    const lab = el('span', 'tool-body-label')
    lab.textContent = '返回' + (t.repeat ? '（重复调用已拦下）' : '')
    const txt = el('div', 'tool-body-text')
    txt.textContent = t.result.length > 4000 ? t.result.slice(0, 4000) + '\n…（已截断）' : t.result
    bodyEl.append(lab, txt)
  }
  if (!bodyEl.childElementCount) {
    bodyEl.textContent = t.state === 'running' ? '执行中…' : '（无内容）'
  }

  head.onclick = (e) => {
    e.stopPropagation()
    const open = card.classList.toggle('open')
    t.open = open
  }

  card.append(head, bodyEl)
  return card
}

function renderMessages() {
  const box = $('messages')
  const s = active()
  box.innerHTML = ''
  if (!s || !s.messages.length) {
    box.append(welcomeNode())
    return
  }
  for (const m of s.messages) box.append(msgNode(m))
  scrollBottom()
}

function welcomeNode() {
  const w = el('div', 'welcome')
  w.innerHTML = `
    <div class="welcome-icon">◈</div>
    <h2>codeb 对话</h2>
    <p>目录树已预装进上下文，模型先看项目结构再决定读什么。</p>
    <ul class="welcome-tips">
      <li>问「这个项目的路由 LLM 链路是什么样」</li>
      <li>问「<code>kb.py</code> 里 <code>cmd_route</code> 怎么降档」</li>
      <li>问「有几处调用了 <code>est_tokens</code>」——会走 <code>grep_count</code></li>
    </ul>`
  return w
}

function scrollBottom() {
  const box = $('messages')
  requestAnimationFrame(() => { box.scrollTop = box.scrollHeight })
}

/* 原始态：真实发给 LLM 的 messages 数组，逐条原样展示。
   与聚合态同源（都来自 context 事件），但这里**不分段、不排序、不省略**：
   tool_calls / tool_call_id 都保留，折叠的占位符也照实际发出的显示。 */
function renderContextRaw(s, raw, sum, list) {
  for (const b of $('ctxModes').querySelectorAll('.ctx-mode')) {
    b.classList.toggle('active', b.dataset.mode === 'raw')
  }
  if (!s || !raw || !raw.length) {
    sum.innerHTML = ''
    list.innerHTML = '<div class="traj-empty">发一条消息后显示原始 messages</div>'
    return
  }
  const totalTok = raw.reduce((a, m) => a + (m.tokens || 0), 0)
  const sysTok = raw.find((m) => m.role === 'system')?.tokens || 0
  sum.innerHTML = `
    <div class="ctx-kpi"><div class="v">${fmtTok(totalTok)}</div><div class="l">messages 合计</div></div>
    <div class="ctx-kpi"><div class="v">${fmtTok(sysTok)}</div><div class="l">system</div></div>
    <div class="ctx-kpi"><div class="v">${raw.length}</div><div class="l">条消息</div></div>
    <div class="ctx-kpi"><div class="v">${s.ready ? '就绪' : '待初始化'}</div><div class="l">状态</div></div>`

  list.innerHTML = ''
  for (const m of raw) {
    const card = el('div', 'raw-msg')
    const head = el('div', 'raw-msg-head')
    const idx = el('span', 'raw-idx')
    idx.textContent = '#' + m.idx
    const role = el('span', 'raw-role ' + (m.role || 'unknown'))
    role.textContent = m.role || '?'
    const note = el('span', 'raw-note')
    if (m.tool_calls) note.textContent = `${m.tool_calls.length} 个 tool_calls`
    else if (m.tool_call_id) note.textContent = `tool_call_id: ${String(m.tool_call_id).slice(0, 18)}`
    const tok = el('span', 'raw-tok')
    tok.textContent = fmtTok(m.tokens || 0) + ' tok'
    head.append(idx, role, note, tok)

    const bodyEl = el('div', 'raw-msg-body')
    const pre = document.createElement('pre')
    pre.textContent = m.content || '（空）'
    bodyEl.append(pre)
    if (m.tool_calls) {
      const lab = el('div', 'raw-tc-label')
      lab.textContent = 'tool_calls（真实发给 LLM 的 JSON）'
      const tpre = document.createElement('pre')
      tpre.textContent = JSON.stringify(m.tool_calls, null, 2)
      bodyEl.append(lab, tpre)
    }
    head.onclick = () => card.classList.toggle('open')
    card.append(head, bodyEl)
    list.append(card)
  }
}

/* ─────────────────────────────── 渲染：上下文页签
   这一页展示的是「下一轮真正要发给模型的东西」，不是内部记账。
   分段按 token 降序，每段可展开看正文。
*/
function renderContext() {
  const s = active()
  const sum = $('ctxSummary')
  const list = $('ctxSections')
  // 两种视图：原始态（真实 messages 顺序）与聚合态（按语义分段）。
  const raw = s?.raw
  if (S.ctxMode === 'raw') {
    renderContextRaw(s, raw, sum, list)
    return
  }
  if (!s) {
    sum.innerHTML = ''
    list.innerHTML = '<div class="traj-empty">没有会话</div>'
    return
  }

  const bd = s.breakdown
  if (!bd) {
    sum.innerHTML = `
      <div class="ctx-kpi"><div class="v">${fmtTok(s.ctxTokens || 0)}</div>
        <div class="l">上下文 tok</div></div>
      <div class="ctx-kpi"><div class="v">${s.ready ? '就绪' : '待初始化'}</div>
        <div class="l">状态</div></div>`
    list.innerHTML = '<div class="traj-empty">发一条消息后显示完整内容</div>'
    return
  }

  for (const b of $('ctxModes').querySelectorAll('.ctx-mode')) {
    b.classList.toggle('active', b.dataset.mode === 'aggregated')
  }
  const parts = bd.parts || []
  const maxTok = Math.max(...parts.map((p) => p.tokens || 0), 1)
  const segs = parts.length
  sum.innerHTML = `
    <div class="ctx-kpi"><div class="v">${fmtTok(bd.total)}</div><div class="l">每轮发送总量</div></div>
    <div class="ctx-kpi"><div class="v">${fmtTok(bd.system_tokens)}</div><div class="l">系统提示词</div></div>
    <div class="ctx-kpi"><div class="v">${fmtTok(bd.tools_tokens)}</div><div class="l">工具定义</div></div>
    <div class="ctx-kpi"><div class="v">${segs}</div><div class="l">分段</div></div>`

  list.innerHTML = ''
  if (!parts.length) {
    list.innerHTML = '<div class="traj-empty">上下文是空的</div>'
    return
  }

  // 按 token 降序：先看最贵的那块（通常是工具定义或工具结果）
  const ordered = [...parts].sort((a, b) => (b.tokens || 0) - (a.tokens || 0))

  for (const p of ordered) {
    const card = el('div', 'ctx-part' + (p.foldable ? ' foldable' : ''))

    const head = el('div', 'ctx-part-head')
    const caret = el('span', 'ctx-caret')
    caret.textContent = '▶'
    const kind = el('span', 'ctx-kind ' + (p.kind || ''))
    kind.textContent = p.kind || 'sec'
    const label = el('span', 'ctx-label')
    label.textContent = p.label
    label.title = p.label
    const barWrap = el('span', 'ctx-barwrap')
    const bar = el('div', 'ctx-bar')
    bar.style.width = Math.max(2, (p.tokens / maxTok) * 100) + '%'
    barWrap.append(bar)
    const tok = el('span', 'ctx-tok')
    tok.textContent = fmtTok(p.tokens) + ' tok'
    head.append(caret, kind, label, barWrap, tok)

    const body = el('div', 'ctx-part-body')
    if (p.note) {
      const note = el('div', 'ctx-note')
      note.textContent = p.note
      body.append(note)
    }

    // 子项：每个都带「看正文」按钮
    for (const c of p.children || []) {
      const row = el('div', 'ctx-child' + (c.folded ? ' folded' : ''))
      const cname = el('span', 'ctx-child-label')
      cname.textContent = c.label
      cname.title = c.label

      if (c.params) {
        const ps = el('span', 'ctx-child-sub')
        ps.textContent = '(' + c.params.join(', ') + ')'
        cname.append(ps)
      }
      if (c.folded) {
        const badge = el('span', 'ctx-badge ')
        badge.textContent = '已折叠'
        cname.append(badge)
      }
      const ctok = el('span', 'ctx-child-tok')
      ctok.textContent = fmtTok(c.tokens) + ' tok'

      const showBtn = el('button', 'ctx-show')
      showBtn.textContent = '看正文'
      showBtn.onclick = (e) => {
        e.stopPropagation()
        const pre = row.querySelector('.ctx-child-body')
        if (pre) { pre.remove(); showBtn.textContent = '看正文'; return }
        const preEl = document.createElement('pre')
        preEl.className = 'ctx-child-body'
        preEl.textContent = c.content || '（空）'
        row.append(preEl)
        showBtn.textContent = '收起'
      }

      row.append(cname, ctok, showBtn)
      body.append(row)
    }

    // 没有子项的段（例如 raw），直接给正文
    if (!(p.children || []).length && p.content) {
      const preEl = document.createElement('pre')
      preEl.className = 'ctx-child-body'
      preEl.textContent = p.content
      body.append(preEl)
    }

    head.onclick = () => card.classList.toggle('open')
    card.append(head, body)
    list.append(card)
  }
}

/* ─────────────────────────────── 渲染：轨迹页签 */
function renderTrajectory() {
  const box = $('trajList')
  box.innerHTML = ''
  if (!S.trajectory.length) {
    box.innerHTML = '<div class="traj-empty">还没有工具调用</div>'
    return
  }
  for (const t of S.trajectory) {
    const item = el('div', 'traj-item')
    const head = el('div', 'traj-head')
    const name = el('span', 'traj-name')
    name.textContent = t.name
    const args = el('span', 'traj-args')
    args.textContent = t.argsText || ''
    args.title = t.argsText || ''
    const tok = el('span', 'traj-tok')
    tok.textContent = t.tokens ? fmtTok(t.tokens) + ' tok' : ''
    head.append(name, args, tok)
    item.append(head)
    if (t.result) {
      const res = el('div', 'traj-result')
      res.textContent = t.result.length > 1200 ? t.result.slice(0, 1200) + '…' : t.result
      item.append(res)
    }
    box.append(item)
  }
}

/* ─────────────────────────────── 下拉菜单
   一个通用组件，模型 / 工作目录共用：
     openDropdown(anchor, {items, activeId, onPick, searchable, foot})
   items: [{id, label, sub, meta, star, active}]
*/
let dropdownState = null

function openDropdown(anchor, opts) {
  const dd = $('dropdown')
  dropdownState = { ...opts, anchor }

  // 定位到按钮下方，右对齐
  const r = anchor.getBoundingClientRect()
  dd.style.display = 'flex'
  dd.style.minWidth = Math.max(320, Math.min(480, r.width + 200)) + 'px'
  const ddW = dd.offsetWidth || 360
  let left = r.right - ddW
  left = Math.max(8, Math.min(left, window.innerWidth - ddW - 8))
  dd.style.left = left + 'px'
  dd.style.top = (r.bottom + 6) + 'px'

  anchor.classList.add('open')

  const search = $('dropdownSearch')
  search.value = ''
  search.style.display = opts.searchable === false ? 'none' : ''
  search.placeholder = opts.searchPlaceholder || '搜索…'
  search.oninput = () => renderDropdownList(search.value)
  if (opts.searchable !== false) setTimeout(() => search.focus(), 0)

  $('dropdownFoot').textContent = opts.foot || ''
  $('dropdownFoot').style.display = opts.foot ? '' : 'none'

  renderDropdownList('')
  requestAnimationFrame(() => search.focus())
}

function closeDropdown() {
  const dd = $('dropdown')
  dd.style.display = 'none'
  if (dropdownState?.anchor) dropdownState.anchor.classList.remove('open')
  dropdownState = null
}

function renderDropdownList(query) {
  if (!dropdownState) return
  const list = $('dropdownList')
  list.innerHTML = ''
  const q = String(query || '').trim().toLowerCase()
  const items = dropdownState.items.filter((it) => {
    if (!q) return true
    return (it.label + ' ' + (it.id || '') + ' ' + (it.sub || '')).toLowerCase().includes(q)
  })
  if (!items.length) {
    const empty = el('div', 'dropdown-empty')
    empty.textContent = q ? '没有匹配项' : '没有可选项'
    list.append(empty)
    return
  }
  for (const it of items) {
    const row = el('div', 'dropdown-item' + (it.active ? ' active' : ''))
    const main = el('div', 'dropdown-item-main')
    const title = el('div', 'dropdown-item-title')
    if (it.star) {
      const st = el('span', 'star')
      st.textContent = '★'
      st.title = '推荐'
      title.append(st)
    }
    const nm = el('span')
    nm.textContent = it.label
    title.append(nm)
    main.append(title)
    if (it.sub) {
      const sub = el('div', 'dropdown-item-sub')
      sub.textContent = it.sub
      sub.title = it.sub
      main.append(sub)
    }
    row.append(main)
    if (it.meta) {
      const meta = el('div', 'dropdown-item-meta')
      meta.textContent = it.meta
      row.append(meta)
    }
    row.onclick = async () => {
      closeDropdown()
      try { await dropdownState.onPick(it) } catch (e) { toast(String(e?.message || e)) }
    }
    list.append(row)
  }
}

async function loadModels() {
  try {
    const r = await fetch('/api/chat/models', { cache: 'no-store' })
    const d = await r.json()
    if (d.ok) {
      S.models = d.models || []
      S.defaultModel = d.default || ''
    }
  } catch { /* 保底：没有清单也能用后端默认模型 */ }
}

async function loadRepos() {
  try {
    const r = await fetch('/api/chat/repos', { cache: 'no-store' })
    const d = await r.json()
    if (d.ok) S.repos = d.repos || []
  } catch { /* ignore */ }
}

function showModelPicker() {
  const s = active()
  if (!s) return
  const cur = s.model || S.defaultModel
  openDropdown($('modelBtn'), {
    searchPlaceholder: '搜索模型…',
    foot: 'webview/models.json · 可手工编辑',
    items: S.models.map((m) => ({
      id: m.id,
      label: m.label,
      sub: m.note || m.id,
      star: m.recommended,
      meta: m.context_window ? fmtTok(m.context_window) : '',
      active: m.id === cur,
    })),
    onPick: async (it) => {
      // 允许在对话中途换模型：只影响后续调用，不动已有上下文
      await setModel(s, it.id)
    },
  })
}

function showRepoPicker() {
  const s = active()
  if (!s) return
  openDropdown($('repoBtn'), {
    searchPlaceholder: '搜索仓库…',
    foot: '仓库清单由 repo_roots() 实时扫描 · 切换会重建上下文',
    items: S.repos.map((r) => ({
      id: r.name,
      label: r.name,
      sub: `${r.dir} · ${r.files} 个源码文件`,
      active: r.name === s.repo,
    })),
    onPick: async (it) => {
      if (it.id === s.repo) return
      await switchRepo(s, it.id)
    },
  })
}

async function setModel(s, model) {
  if (!model || model === s.model) return
  if (s.ready) {
    const r = await fetch('/api/chat/model', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_id: s.id, model }),
    })
    const d = await r.json()
    if (!d.ok) throw new Error(d.error || '切换模型失败')
    s.model = d.model || model
  } else {
    s.model = model
  }
  renderTop()
  toast(`模型 → ${S.models.find((m) => m.id === s.model)?.label || s.model}`)
}

async function switchRepo(s, repoNames) {
  // 切仓库 = 重建上下文（目录树换了），但**保留对话历史**：
  // 用户常常是「在 A 项目问完，去 B 项目问相关的事」。
  // 历史留着，新的目录树重新装订，旧工具结果自然被折叠掉。
  if (S.streaming) { toast('这一轮还没结束'); return }
  const prev = s.repo
  s.repo = repoNames
  s.ready = false
  s.sections = []
  s.ctxTokens = 0
  try {
    await ensureReady(s)
    renderTop(); renderContext()
    toast(`工作目录 → ${repoNames}（上下文已重建）`)
  } catch (e) {
    s.repo = prev
    throw e
  }
}
function renderCotToggle() {
  const b = $('cotToggle')
  if (b) b.setAttribute('aria-pressed', S.cot ? 'true' : 'false')
}

function renderTop() {
  const s = active()
  const m = S.models.find((x) => x.id === (s?.model || S.defaultModel))
  const modelLabel = m?.label || s?.model || '—'
  $('modelBtnLabel').textContent = modelLabel
  $('modelBtn').title = `模型：${s?.model || S.defaultModel || '—'}（点击切换）`
  $('repoBtnLabel').textContent = s?.repo || repo
  if (LOCKED_REPO) {
    // 锁定态看起来就是个标签，不是可点的选择器
    $('repoBtn').classList.add('locked')
    $('repoBtn').title = `从项目面板进入，锁定在 ${repo}（回主页换项目）`
  }
  $('ctxChip').textContent = fmtTok(s?.ctxTokens || 0) + ' tok'
  $('topTitle').textContent = s?.title || 'codeb 对话'

  // 发送 / 停止 双态
  const sendBtn = $('sendBtn')
  sendBtn.classList.toggle('stopping', S.streaming)
  sendBtn.title = S.streaming ? '停止生成' : '发送'
  $('sendIcon').style.display = S.streaming ? 'none' : ''
  $('stopIcon').style.display = S.streaming ? '' : 'none'

  $('composerHint').textContent = S.streaming
    ? '模型思考中…（可点停止）'
    : (s?.ready ? '就绪' : '待发送首条消息')
  renderCotToggle()
}

/* ─────────────────────────────── 会话初始化（懒：首条消息时）
   为什么懒：目录树扫描 + token 估算要几百毫秒，
   用户可能只是想看一眼面板。 */
async function ensureReady(s) {
  if (s.ready) return
  const resp = await fetch('/api/chat/init', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      session_id: s.id,
      repo: s.repo,
      tree_depth: s.treeDepth,
      files: s.files,
      route_specs: s.routeSpecs,
      custom: s.custom,
      model: s.model || S.defaultModel || '',
      cot: s.cot,
      llmHistory: s.llmHistory || [],
    }),
  })
  const data = await resp.json()
  if (!resp.ok || !data.ok) throw new Error(data.error || `初始化失败 HTTP ${resp.status}`)
  s.ready = true
  s.model = data.model || s.model || S.defaultModel
  s.ctxTokens = data.context_tokens || 0
  s.sections = data.sections || []
  s.breakdown = data.breakdown || null
  s.raw = data.raw || []
  renderTop(); renderContext()
}

/* ─────────────────────────────── 停止 / 发送 */
async function onSendClick() {
  if (S.streaming) return stopGeneration()
  return send()
}

async function stopGeneration() {
  const s = active()
  if (!s) return
  try {
    await fetch('/api/chat/stop', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_id: s.id }),
    })
    $('composerHint').textContent = '正在停止…'
  } catch (e) {
    toast('停止失败：' + String(e?.message || e))
  }
}

/* ─────────────────────────────── 发消息 */
async function send() {
  const s = active()
  const input = $('input')
  const text = input.value.trim()
  if (!s || !text || S.streaming) return

  input.value = ''
  autoGrow()

  // 首条消息当标题
  if (s.messages.length === 0) {
    s.title = text.length > 28 ? text.slice(0, 28) + '…' : text
    renderSessions()
  }

  const userMsg = { role: 'user', text }
  const asMsg = { role: 'assistant', text: '', cot: '', tools: [], pending: true }
  s.messages.push(userMsg, asMsg)
  S.trajectory = []
  S.streaming = true
  renderMessages()
  renderTop()

  try {
    await ensureReady(s)
  } catch (e) {
    asMsg.pending = false
    asMsg.error = String(e?.message || e)
    S.streaming = false
    renderMessages(); renderTop()
    return
  }

  const asNode = () => {
    // 每次渲染后节点会重建，取最后一个 assistant
    const nodes = $('messages').querySelectorAll('.msg-assistant')
    return nodes[nodes.length - 1]
  }

  try {
    for await (const ev of sseStream('/api/chat', {
      session_id: s.id,
      message: text,
    })) {
      if (ev.type === 'tool_call') {
        asMsg.tools.push({
          name: ev.name,
          argsText: compactArgs(ev.args),
          args: ev.args,          // 完整参数，卡片展开时显示
          state: 'running',
        })
        S.trajectory.push({
          name: ev.name, argsText: compactArgs(ev.args), args: ev.args,
          state: 'running',
        })
        repaintAssistant(asMsg)
        renderTrajectory()
      } else if (ev.type === 'tool_result') {
        const t = [...asMsg.tools].reverse().find((x) => x.name === ev.name && x.state === 'running')
        if (t) {
          t.state = ev.repeated ? 'done' : 'done'
          t.result = ev.result || ''
          t.tokens = ev.tokens || 0
          t.repeat = !!ev.repeated
        }
        const tr = [...S.trajectory].reverse().find((x) => x.name === ev.name && x.state === 'running')
        if (tr) {
          tr.state = 'done'; tr.result = ev.result || ''; tr.tokens = ev.tokens || 0
          tr.repeat = !!ev.repeated
        }
        repaintAssistant(asMsg)
        renderTrajectory()
      } else if (ev.type === 'cot') {
        asMsg.cot = (asMsg.cot || '') + (ev.text || '')
        repaintAssistant(asMsg)
      } else if (ev.type === 'token') {
        asMsg.text += ev.text || ''
        repaintAssistant(asMsg)
      } else if (ev.type === 'done') {
        asMsg.text = ev.answer || asMsg.text
        if (ev.cot) asMsg.cot = ev.cot
        asMsg.pending = false
        if (ev.usage) asMsg.usage = ev.usage
        asMsg.stopped = !!ev.stopped
        asMsg.tools.forEach((t) => { if (t.state === 'running') t.state = 'done' })
        S.trajectory.forEach((t) => { if (t.state === 'running') t.state = 'done' })
        if (ev.context_tokens) s.ctxTokens = ev.context_tokens
        repaintAssistant(asMsg)
        renderTrajectory()
      } else if (ev.type === 'stopping') {
        $('composerHint').textContent = '正在停止…'
      } else if (ev.type === 'error') {
        asMsg.pending = false
        asMsg.error = ev.message || '未知错误'
        repaintAssistant(asMsg)
      }
    }
  } catch (e) {
    asMsg.pending = false
    asMsg.error = String(e?.message || e)
    repaintAssistant(asMsg)
  } finally {
    S.streaming = false
    renderTop()
    // 这一轮结束后同步一次上下文构成：工具结果、折叠状态都变了，
    // 面板不刷新的话显示的还是上一轮的内容
    refreshContext()
    // 每轮结束把 LLM 原始 history + 展示消息一起落盘。
    // 失败不打扰用户（内存里还在，下一轮会再试）。
    persistActiveSession(asMsg).catch(() => {})
  }
}

function compactArgs(args) {
  if (!args || typeof args !== 'object') return ''
  const parts = []
  for (const [k, v] of Object.entries(args)) {
    let vs = typeof v === 'string' ? v : JSON.stringify(v)
    if (vs.length > 46) vs = vs.slice(0, 46) + '…'
    parts.push(`${k}=${vs}`)
  }
  return parts.join(' ')
}

function repaintAssistant(asMsg) {
  const nodes = $('messages').querySelectorAll('.msg-assistant')
  const node = nodes[nodes.length - 1]
  if (node && asMsg) node.replaceWith(msgNode(asMsg))
  else { renderMessages(); return }
  scrollBottom()
  renderTop()
}

/* ─────────────────────────────── 输入框自动增高 */
function autoGrow() {
  const t = $('input')
  t.style.height = 'auto'
  t.style.height = Math.min(t.scrollHeight, 200) + 'px'
}

/* ─────────────────────────────── 页签切换 */
function switchTab(name) {
  for (const b of $('topTabs').querySelectorAll('.tab')) {
    b.classList.toggle('active', b.dataset.tab === name)
  }
  $('paneChat').classList.toggle('active', name === 'chat')
  $('paneContext').classList.toggle('active', name === 'context')
  $('paneTrajectory').classList.toggle('active', name === 'trajectory')
  if (name === 'context') refreshContext()
}

async function refreshContext() {
  const s = active()
  if (!s || !s.ready) { renderContext(); return }
  try {
    const r = await fetch(`/api/chat/context?session_id=${encodeURIComponent(s.id)}`)
    const d = await r.json()
    if (d.ok && d.breakdown) {
      s.breakdown = d.breakdown
      s.raw = d.raw || s.raw || []
      s.sections = d.sections || s.sections
      s.ctxTokens = d.total_tokens || s.ctxTokens
      renderContext(); renderTop()
    }
  } catch { /* 保底：保留旧数据 */ }
}

/* ─────────────────────────────── 分支
   从某条消息复制出一个新会话前缀。LLM history 由服务端从分叉点那条
   assistant 的 llm 里取（不是整条会话最后一条），这样分支才真的是分支。 */
async function branchFrom(m) {
  if (S.streaming) { toast('这一轮还没结束'); return }
  const src = active()
  if (!src) return
  const seq = src.messages.indexOf(m)
  if (seq < 0) return
  const newId = 's-' + Date.now().toString(36) + Math.random().toString(36).slice(2, 6)
  try {
    const r = await fetch('/api/chat/fork', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        source_id: src.id, up_to_seq: seq, new_id: newId,
        title: (src.title || '会话') + ' · 分支',
      }),
    })
    const d = await r.json()
    if (!d.ok) { toast('分支失败：' + (d.error || '')); return }
    // 重新读回分支会话（服务端已建好库记录）
    const rr = await fetch('/api/chat/session?id=' + encodeURIComponent(newId))
    const dd = await rr.json()
    if (!dd.ok) { toast('读取分支失败'); return }
    const br = {
      id: newId, title: dd.session.title, repo: dd.session.repo,
      model: dd.session.model || S.defaultModel || '',
      ctxTokens: 0, sections: [],
      messages: (dd.messages || []).map((x) => ({
        role: x.role, text: x.text || '', cot: x.cot || '',
        tools: x.tools || [], error: x.error || '', stopped: !!x.stopped,
        usage: x.usage || {}, llm: x.llm || [], pending: false,
      })),
      ready: false, treeDepth: dd.session.tree_depth || DEFAULT_TREE_DEPTH,
      files: [], routeSpecs: [], custom: [], cot: !!dd.session.cot,
      createdAt: dd.session.created_at,
    }
    const withLlm = [...br.messages].reverse().find((x) => x.llm && x.llm.length)
    br.llmHistory = withLlm ? withLlm.llm : []
    S.sessions.unshift(br)
    switchSession(newId)
    await ensureReady(br)
    renderTop(); renderContext()
    toast('已从这条消息分叉')
  } catch (e) {
    toast('分支失败：' + String(e?.message || e))
  }
}

/* ─────────────────────────────── 会话持久化
   每轮 done 后把 LLM history + 展示消息写进 sqlite；
   刷新页面从 sqlite 恢复列表，点某个会话即重连并灌回 history。 */
async function persistActiveSession(lastAsMsg) {
  const s = active()
  if (!s) return
  // 拉一次权威 LLM history（含 tool_call_id），只有常驻进程里有
  let llmHistory = s.llmHistory || []
  try {
    const r = await fetch('/api/chat/history', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_id: s.id }),
    })
    const d = await r.json()
    if (d.ok && Array.isArray(d.history)) {
      llmHistory = d.history
      s.llmHistory = d.history
    }
  } catch { /* 后端没起也无妨 */ }
  const createdAt = s.createdAt || Date.now()
  try {
    await fetch('/api/chat/session', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        id: s.id, title: s.title, repo: s.repo, model: s.model,
        cot: s.cot, tree_depth: s.treeDepth, created_at: createdAt,
        messages: s.messages.map((m) => ({
          role: m.role, text: m.text || '', cot: m.cot || '',
          tools: m.tools || [], error: m.error || '', stopped: !!m.stopped,
          usage: m.usage || {},
          llm: m.role === 'assistant' && m === lastAsMsg ? llmHistory : [],
        })),
      }),
    })
  } catch { /* 落盘失败不影响使用 */ }
}

async function loadSavedSessions() {
  try {
    const r = await fetch('/api/chat/sessions')
    const d = await r.json()
    if (!d.ok || !Array.isArray(d.sessions) || !d.sessions.length) return false
    // 逐条拉完整消息。会话不多（个人使用），一次性恢复即可，
    // 省去「点开才加载」的复杂状态。
    for (const saved of d.sessions) {
      let messages = []
      try {
        const rr = await fetch('/api/chat/session?id=' + encodeURIComponent(saved.id))
        const dd = await rr.json()
        if (dd.ok) messages = (dd.messages || []).map((m) => ({
          role: m.role, text: m.text || '', cot: m.cot || '',
          tools: m.tools || [], error: m.error || '', stopped: !!m.stopped,
          usage: m.usage || {}, llm: m.llm || [], pending: false,
        }))
      } catch { /* 单条失败不影响其它 */ }
      const withLlm = [...messages].reverse().find((m) => m.llm && m.llm.length)
      S.sessions.push({
        id: saved.id,
        title: saved.title || '新会话',
        repo: saved.repo || repo,
        model: saved.model || S.defaultModel || '',
        ctxTokens: 0,
        sections: [],
        messages,
        llmHistory: withLlm ? withLlm.llm : [],
        ready: false,
        treeDepth: saved.tree_depth || DEFAULT_TREE_DEPTH,
        files: [], routeSpecs: [], custom: [],
        cot: !!saved.cot,
        createdAt: saved.created_at,
      })
    }
    return true
  } catch { return false }
}

async function openSavedSession(id) {
  const s = S.sessions.find((x) => x.id === id)
  if (!s) return
  // 消息已在 boot 时全量恢复；这里只需切换并（首次）建上下文
  switchSession(id)
  try {
    await ensureReady(s)
    renderTop(); renderContext()
  } catch (e) {
    toast('连接会话失败：' + String(e?.message || e))
  }
}

/* ─────────────────────────────── 启动 */
async function boot() {
  // 先从 sqlite 恢复历史会话；有就默认打开最近的一条，没有再新建。
  // 早先是先 newSession 再异步 load，结果新会话和历史会话同时在场、
  // active 指向被异步覆盖，界面闪一下——现在串行，状态只有一个来源。
  const hadSaved = await loadSavedSessions()
  let first
  if (hadSaved && S.sessions.length) {
    first = S.sessions[0]
    S.activeId = first.id
    // 轨迹从消息里的 tools 重建
    S.trajectory = []
    for (const m of first.messages) {
      for (const t of (m.tools || [])) S.trajectory.push({ ...t, msgRole: m.role })
    }
  } else {
    first = newSession()
  }

  // 开局就把上下文建起来：用户打开页面往往第一件事就是点「上下文」看装了什么。
  ensureReady(first).then(() => {
    renderTop(); renderContext()
  }).catch(() => { /* 留给首条消息重试 */ })

  $('newChatBtn').onclick = () => {
    if (S.streaming) { toast('这一轮还没结束'); return }
    const s = newSession()
    ensureReady(s).then(() => { renderTop(); renderContext() }).catch(() => {})
    $('input').focus()
  }

  // panelLink 现在是 <a href="/">，浏览器原生跳转即可，
  // 不再绑 onclick——否则会和默认行为重复触发，也丢掉中键/右键复制地址。

  // 发送 / 停止 双态
  $('sendBtn').onclick = onSendClick

  // 思考链开关：切换当前会话与默认值，下次新建会话继承
  $('cotToggle').onclick = async () => {
    S.cot = !S.cot
    const s = active()
    if (s) {
      s.cot = S.cot
      // 会话已初始化时，Python 进程里的 cot 开关还停在 init 那一刻。
      // 必须推过去，否则翻了开关也照样不出 reasoning。失败只提示，
      // 不回滚：本地状态已经改了，下次新建会话仍会继承。
      if (s.ready) {
        try {
          await fetch('/api/chat/cot', {
            method: 'POST', headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ session_id: s.id, cot: s.cot }),
          })
        } catch { toast('思考链开关未能同步到当前会话，下一条消息可能不生效') }
      }
    }
    renderCotToggle()
  }

  // 选择器
  $('modelBtn').onclick = (e) => {
    e.stopPropagation()
    if ($('dropdown').style.display !== 'none') { closeDropdown(); return }
    showModelPicker()
  }
  $('repoBtn').onclick = (e) => {
    e.stopPropagation()
    // 从项目面板带 ?repo= 进来时锁死仓库：在 infohub 的对话里切到 codeb，
    // 页签和上下文说的就是两个项目了，比不给切更容易出错。
    if (LOCKED_REPO) { toast('当前对话锁定在 ' + repo + '，回主页换项目'); return }
    if ($('dropdown').style.display !== 'none') { closeDropdown(); return }
    showRepoPicker()
  }

  // 点外部 / Esc 关闭下拉
  document.addEventListener('click', (e) => {
    if ($('dropdown').style.display === 'none') return
    if ($('dropdown').contains(e.target)) return
    closeDropdown()
  })
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && $('dropdown').style.display !== 'none') {
      closeDropdown()
      e.stopPropagation()
    }
  })

  const input = $('input')
  input.addEventListener('input', autoGrow)
  input.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      if (S.streaming) return
      send()
    }
  })

  for (const b of $('topTabs').querySelectorAll('.tab')) {
    b.onclick = () => switchTab(b.dataset.tab)
  }

  for (const b of $('ctxModes').querySelectorAll('.ctx-mode')) {
    b.onclick = () => { S.ctxMode = b.dataset.mode; renderContext() }
  }

  $('reloadCtxBtn').onclick = async () => {
    await refreshContext()
    toast('已刷新')
  }

  $('attachBtn').onclick = () => toast('上下文配置：改 chat_engine.py 的 init 参数，或调 /api/chat/init')

  renderTop()
  renderSessions()
  renderMessages()
  renderTrajectory()
  renderContext()
  input.focus()

  // 清单异步加载（不阻塞首屏）
  Promise.all([loadModels(), loadRepos()]).then(() => {
    const s = active()
    if (s && !s.model) s.model = S.defaultModel
    renderTop()
    renderContext()
  })
}

document.addEventListener('DOMContentLoaded', boot)
