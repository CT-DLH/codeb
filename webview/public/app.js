'use strict'

const $ = (id) => document.getElementById(id)
const esc = (s) => String(s ?? '').replace(/[&<>"']/g, (c) =>
  ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]))
const fmtTime = (ts) => {
  if (!ts) return '—'
  const d = new Date(Number(ts) > 1e12 ? Number(ts) : Number(ts) * 1000)
  return isNaN(d) ? String(ts).slice(0, 19) : d.toLocaleString('zh-CN', { hour12: false })
}

let PAYLOAD = null
let coversTab = 'stale'

// 项目目录表状态。infohub 有 2.9 万个节点，不能一次全渲染成 DOM，
// 所以用「内存里放全量、展开时才渲染直接子节点」的懒渲染。
const PT = { data: null, repo: null, filter: 'all', search: '', children: null, byPath: null }

function toast(msg) {
  const t = $('toast')
  t.textContent = msg
  t.classList.add('show')
  clearTimeout(toast._t)
  toast._t = setTimeout(() => t.classList.remove('show'), 2200)
}

async function fetchJSON(url) {
  const r = await fetch(url, { cache: 'no-store' })
  if (!r.ok) throw new Error(`${r.status} ${await r.text()}`)
  return r.json()
}

function renderHeader(p) {
  $('workspace').textContent = p.workspace
  const badges = Object.entries(p.source || {}).map(([k, v]) =>
    `<span class="badge ${v === 'live' ? 'live' : 'snapshot'}" title="${k}">${k}: ${v}</span>`).join('')
  $('sourceBadges').innerHTML = badges
}

function renderKpis(p) {
  // 层数不再写死：树有多少层由各项目的 md 决定，这里只报告实际深度
  const depth = p.tree.depth || 0
  const c = p.covers || {}
  const items = [
    { label: '项目', val: p.tree.projects.length, cls: '' },
    { label: '实际层级', val: depth + ' 层', cls: '' },
    { label: '知识页', val: p.index?.pagesCount ?? '—', cls: '' },
    { label: '语义块', val: p.index?.blocksCount ?? '—', cls: '' },
    { label: 'covers 声明', val: c.coversDecl, cls: '' },
    { label: '过期声明 stale', val: c.stale?.count ?? 0, cls: c.stale?.count ? 'warn' : 'ok' },
    { label: '冲突覆盖 conflict', val: c.conflict?.count ?? 0, cls: c.conflict?.count ? 'warn' : 'ok' },
    { label: '未覆盖源码', val: c.uncovered?.count ?? 0, cls: c.uncovered?.count ? 'err' : 'ok' },
  ]
  $('kpis').innerHTML = items.map((x) =>
    `<div class="kpi ${x.cls}"><div class="val">${esc(x.val)}</div><div class="label">${x.label}</div></div>`).join('')
}

function renderLevels(p) {
  // 每层实际有几个带下级的节点，而不是固定的「第1~5层」标签
  const counts = []
  const walk = (nodes, d) => {
    counts[d] = (counts[d] || 0) + nodes.length
    for (const n of nodes) if (n.children?.length) walk(n.children, d + 1)
  }
  walk(p.tree.projects || [], 1)
  $('levels').innerHTML = counts.filter(Boolean).map((n, i) =>
    `<div class="level-chip">第${i + 1}层 <b>${n}</b></div>`).join('') +
    `<div class="level-chip depth">共 <b>${p.tree.depth || 0}</b> 层</div>`
}

function nodeHtml(node, projectName, moduleName) {
  const parts = node.parts || []
  if (!parts.length) {
    return `<div class="leaf" title="无部件数据">（待建）</div>`
  }
  const children = parts.map((part) => {
    const p = String(part.path || '')
    const isFile = /\.(md|py|ts|tsx|js)$/.test(p)
    const leaf = isFile
      ? `<div class="leaf" data-project="${esc(projectName)}" data-module="${esc(moduleName)}"
           data-path="${esc(p.replace(/^\.\//, ''))}" title="点击查看文件内容">${esc(part.name)}</div>`
      : `<div class="leaf">${esc(part.name)}</div>`
    return leaf
  }).join('')
  return `<div class="children">${children}</div>`
}

let CURRENT = null  // { path, title, content, editing }

function bindNode(el) {
  el.addEventListener('click', (e) => {
    e.stopPropagation()
    openDetail(el.dataset.file, el.dataset.title || el.textContent.trim(), el.dataset.path)
  })
}

function renderTree(p) {
  const projects = p.tree.projects || []
  if (!projects.length) {
    $('tree').innerHTML = '<div class="empty">没有项目数据</div>'
    return
  }
  // 根节点（项目索引）
  const rootRow = `<div class="node-row" data-file="${esc(p.tree.rootFile || '')}"
      data-title="项目索引" data-path="项目索引">
      <span class="node">📇 项目索引</span>
      <span class="node-summary">${esc(p.tree.rootSummary || '')}</span></div>`
  // 递归渲染：深度由数据决定，不再假设「项目→模块→部件」
  $('tree').innerHTML = rootRow + projects.map((proj) => renderNode(proj, proj.name, 0)).join('')
  bindTree($('tree'))
}

/** 递归渲染一个节点（项目/模块/采集器/部件容器都走这里）。 */
function renderNode(node, trail, depth) {
  const hasChildren = (node.children || []).length > 0
  const hasParts = (node.parts || []).length > 0
  const file = node.file || ''
  const label = `<span class="node">${esc(node.name)}</span>` +
    (node.summary ? `<span class="node-summary">${esc(node.summary)}</span>` : '')
  const row = `<span class="node-row" data-file="${esc(file)}" data-title="${esc(node.name)}"
      data-path="${esc(trail)}" data-depth="${depth}">${label}</span>`

  if (!hasChildren && !hasParts && node.partsLoaded !== false) {
    // 叶子
    return `<div class="leaf" data-file="${esc(file)}" data-title="${esc(node.name)}"
      data-path="${esc(trail)}" data-depth="${depth}">${label}</div>`
  }

  const kids = (node.children || []).map(
    (c) => renderNode(c, `${trail} / ${c.name}`, depth + 1)).join('')
  const parts = (node.parts || []).map((part) => {
    const pfile = part.file || file
    return `<div class="leaf" data-file="${esc(pfile)}" data-title="${esc(part.name)}"
      data-path="${esc(trail + ' / ' + part.name)}" data-depth="${depth + 1}">
      ${esc(part.name)}${part.note ? ` <span class="node-summary">— ${esc(String(part.note).slice(0, 80))}</span>` : (part.sig ? ` <span class="node-sig">${esc(String(part.sig).slice(0, 60))}</span>` : '')}</div>`
  }).join('')

  let body
  if (node.partsLoaded === false && !kids) {
    body = '<div class="leaf lazy">展开加载…</div>'
  } else {
    body = kids + parts
  }
  if (!body) body = '<div class="leaf">（无下级）</div>'

  return `<details data-node="${esc(file)}" data-name="${esc(node.name)}" data-depth="${depth}">
    <summary>${row}</summary>
    <div class="children">${body}</div></details>`
}

/** 绑定点击看详情 + 懒加载子节点。 */
function bindTree(scope) {
  scope.querySelectorAll('.node-row[data-file], .leaf[data-file]').forEach(bindNode)

  scope.querySelectorAll('details[data-node]').forEach((d) => {
    d.addEventListener('toggle', async () => {
      if (!d.open || d.dataset.loaded === '1') return
      // 已经有子节点/部件（首屏全量模式）就不用再拉
      const box = d.querySelector('.children')
      if (!box || !box.querySelector('.leaf.lazy')) { d.dataset.loaded = '1'; return }
      d.dataset.loaded = '1'
      const file = d.dataset.node
      const name = d.dataset.name
      if (!file) { box.innerHTML = '<div class="leaf">（无数据）</div>'; return }
      const depth = Number(d.dataset.depth || 0) + 1
      try {
        const r = await fetchJSON('/api/node?file=' + encodeURIComponent(file) +
          '&name=' + encodeURIComponent(name))
        const trail = d.querySelector('.node-row')?.dataset.path || name
        const kids = (r.children || []).map(
          (c) => renderNode(c, `${trail} / ${c.name}`, depth)).join('')
        const parts = (r.parts || []).map((part) => {
          const pfile = part.file || file
          return `<div class="leaf" data-file="${esc(pfile)}" data-title="${esc(part.name)}"
            data-path="${esc(trail + ' / ' + part.name)}" data-depth="${depth}">
            ${esc(part.name)}${part.note ? ` <span class="node-summary">— ${esc(String(part.note).slice(0, 80))}</span>` : (part.sig ? ` <span class="node-sig">${esc(String(part.sig).slice(0, 60))}</span>` : '')}</div>`
        }).join('')
        const out = kids + parts
        box.innerHTML = out || '<div class="leaf">（无下级）</div>'
        bindTree(box)
      } catch (e) {
        box.innerHTML = '<div class="leaf">加载失败：' + esc(e.message) + '</div>'
        d.dataset.loaded = '0'
      }
    })
  })
}

function partLeaf(part, mod) {
  const file = part.file || mod?.file || ''
  return `<div class="leaf" data-file="${esc(file || '')}" data-title="${esc(part.name)}">
    ${esc(part.name)}${part.note ? ` <span class="node-summary">— ${esc(String(part.note).slice(0, 80))}</span>` : (part.sig ? ` <span class="node-sig">${esc(String(part.sig).slice(0, 60))}</span>` : '')}</div>`
}

async function openDetail(path, title, trail) {
  if (!path) { toast('该节点没有对应 md 文件'); return }
  $('detailTitle').innerHTML = `${esc(title)} <span class="hint">${esc(path)}</span>`
  // 面包屑：层级路径由数据给出，长度随项目结构变化
  const crumbs = String(trail || title).split(' / ').filter(Boolean)
  $('detailMeta').innerHTML = crumbs.map((c, i) =>
    `<span class="crumb ${i === crumbs.length - 1 ? 'cur' : ''}">${esc(c)}</span>`
  ).join('<span class="crumb-sep">›</span>') +
    `<div class="crumb-file">${esc(path)}</div>`
  $('detailMsg').textContent = ''
  $('detailActions').style.display = 'flex'
  try {
    const res = await fetchJSON('/api/data?file=' + encodeURIComponent(path))
    if (!res.exists) { $('detailView').innerHTML = '<div class="empty">文件不存在</div>'; return }
    CURRENT = { path, title, content: res.content, editing: false }
    renderDetailView()
  } catch (e) {
    $('detailView').innerHTML = `<div class="empty">加载失败：${esc(e.message)}</div>`
  }
}

function renderDetailView() {
  if (!CURRENT) return
  const isEdit = CURRENT.editing
  $('detailView').style.display = isEdit ? 'none' : 'block'
  $('detailEditor').style.display = isEdit ? 'block' : 'none'
  $('editBtn').style.display = isEdit ? 'none' : 'inline-block'
  $('saveBtn').style.display = isEdit ? 'inline-block' : 'none'
  $('cancelBtn').style.display = isEdit ? 'inline-block' : 'none'
  if (isEdit) {
    $('detailEditor').value = CURRENT.content
  } else {
    // 简单 md 高亮（标题/引用）
    const html = CURRENT.content.split('\n').map((line) => {
      const x = esc(line)
      if (/^#\s/.test(line)) return `<div class="md-h1">${x}</div>`
      if (/^##\s/.test(line)) return `<div class="md-h2">${x}</div>`
      if (/^>/.test(line)) return `<div class="md-quote">${x}</div>`
      return `<div>${x}</div>`
    }).join('')
    $('detailView').innerHTML = html
  }
}

function showFile(path, content) {
  const lines = String(content).split('\n')
  const body = lines.map((l, i) =>
    `<div><span style="color:var(--muted);display:inline-block;width:42px;text-align:right;margin-right:10px">${i + 1}</span>${esc(l)}</div>`).join('')
  const win = window.open('', '_blank')
  if (!win) { toast('请允许弹出窗口'); return }
  win.document.write(`<!doctype html><html><head><meta charset="utf-8"><title>${esc(path)}</title>
    <style>body{background:#0f1420;color:#dbe3f0;font:12px/1.5 Consolas,monospace;padding:16px}
    h3{color:#5b9dff;font-family:sans-serif}</style></head><body>
    <h3>${esc(path)} (${lines.length} 行)</h3><pre style="white-space:pre-wrap">${body}</pre></body></html>`)
  win.document.close()
}

function bindDetailActions() {
  $('editBtn').addEventListener('click', () => {
    if (!CURRENT) return
    CURRENT.editing = true
    renderDetailView()
    $('detailMsg').textContent = ''
  })
  $('cancelBtn').addEventListener('click', () => {
    if (!CURRENT) return
    CURRENT.editing = false
    renderDetailView()
    $('detailMsg').textContent = ''
  })
  $('saveBtn').addEventListener('click', async () => {
    if (!CURRENT) return
    const content = $('detailEditor').value
    try {
      const r = await fetch('/api/save', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ path: CURRENT.path, content }),
      })
      const data = await r.json()
      if (!r.ok || !data.ok) throw new Error(data.error || r.statusText)
      CURRENT.content = content
      CURRENT.editing = false
      renderDetailView()
      $('detailMsg').className = 'detail-msg ok'
      $('detailMsg').textContent = `已保存 ${CURRENT.path}（备份：${data.backup || '—'}）`
      toast('保存成功')
    } catch (e) {
      $('detailMsg').className = 'detail-msg err'
      $('detailMsg').textContent = '保存失败：' + e.message
    }
  })
  $('rawBtn').addEventListener('click', () => {
    if (!CURRENT) return
    showFile(CURRENT.path, CURRENT.content)
  })
}

function renderVerification(p) {
  const v = p.verification || {}
  const items = [
    ['回归', v.regression],
    ['MCP', v.mcp],
  ].filter(([, x]) => x).map(([name, x]) => {
    const st = String(x.status || 'unknown')
    const cls = /pass|ok|0|green/i.test(st) ? 'pass' : 'fail'
    return `<div class="vitem ${cls}"><div class="st">${esc(name)}: ${esc(st)}</div>
      <div class="d">${esc(x.detail || '')}</div></div>`
  }).join('')
  $('verification').innerHTML = items || '<div class="empty">无验证数据</div>'
}

function renderCovers(p) {
  const c = p.covers || {}
  const tabs = [['stale', '过期'], ['conflict', '冲突'], ['uncovered', '未覆盖']]
  $('coversTabs').innerHTML = tabs.map(([k, name]) =>
    `<button data-tab="${k}" class="${coversTab === k ? 'active' : ''}">${name} (${c[k]?.count ?? 0})</button>`).join('')
  $('coversTabs').querySelectorAll('button').forEach((b) =>
    b.addEventListener('click', () => { coversTab = b.dataset.tab; renderCovers(PAYLOAD) }))

  const items = c[coversTab]?.items || []
  $('coversList').innerHTML = items.length
    ? items.map((x) => `<div class="row" title="${esc(x)}">${esc(x)}</div>`).join('')
    : '<div class="empty">该类无问题（或只显示前 40 条）</div>'
}

function renderTimeline(p) {
  const evs = p.timeline || []
  $('logMeta').textContent = `${p.logFiles || 0} 个日志文件 · 显示前 ${evs.length} 条`
  $('timeline').innerHTML = evs.length
    ? evs.map((e) => `<div class="ev"><span class="ts">${esc(fmtTime(e.ts))}</span>
        <span class="etype">${esc(e.event || e.type || '')}</span>
        <span class="edetail">${esc(e.detail || '')}</span></div>`).join('')
    : '<div class="empty">无事件（跑了 agent 任务后会出现）</div>'
}

// ---------- 项目目录表 ----------
function ptBuildIndex(t) {
  const byPath = new Map()
  const children = new Map()
  for (const n of t.nodes || []) {
    byPath.set(n.path, n)
    const par = n.parent || ''
    if (!children.has(par)) children.set(par, [])
    children.get(par).push(n)
  }
  // 目录在前，文件在后；再按名字排
  for (const arr of children.values()) {
    arr.sort((a, b) => (b.isDir - a.isDir) || a.name.localeCompare(b.name, 'zh-CN'))
  }
  PT.byPath = byPath
  PT.children = children
}

function ptVisible(n) {
  if (PT.filter === 'stale' && !(n.state === 'stale')) return false
  if (PT.filter === 'missing' && n.isDir) return false
  if (PT.filter === 'missing' && n.state !== 'none') return false
  if (PT.filter === 'noted' && (n.isDir || !n.purpose)) return false
  if (PT.search) {
    const q = PT.search.toLowerCase()
    const hay = (n.path + ' ' + (n.purpose || '')).toLowerCase()
    if (!hay.includes(q) && !String(n.path).toLowerCase().includes(q)) return false
  }
  return true
}

function ptHasVisibleDesc(path, seen = new Set()) {
  if (seen.has(path)) return false
  seen.add(path)
  const kids = PT.children.get(path) || []
  for (const k of kids) {
    if (ptVisible(k)) return true
    if (k.isDir && ptHasVisibleDesc(k.path, seen)) return true
  }
  return false
}

function ptStateHtml(n) {
  if (n.isDir) return ''
  if (n.state === 'stale') return '<span class="pt-state stale">过期</span>'
  if (n.state === 'fresh' && n.purpose) return '<span class="pt-state fresh">新鲜</span>'
  return '<span class="pt-state none">未写</span>'
}

function ptSize(size) {
  if (size == null) return ''
  if (size < 1024) return `<span class="pt-size">${size}B</span>`
  if (size < 1024 * 1024) return `<span class="pt-size">${(size / 1024).toFixed(1)}K</span>`
  return `<span class="pt-size">${(size / 1024 / 1024).toFixed(1)}M</span>`
}

function ptFileHtml(n) {
  const ext = n.ext ? `<span class="pt-ext">${esc(n.ext)}</span>` : ''
  const purpose = n.purpose
    ? `<span class="pt-purpose" title="${esc(n.purpose)}">— ${esc(n.purpose)}</span>`
    : ''
  return `<div class="pt-file" data-path="${esc(n.path)}">
    <span class="pt-name">${esc(n.name)}</span>${ext}${ptSize(n.size)}
    ${ptStateHtml(n)}${purpose}</div>`
}

function ptDirHtml(n, depth) {
  // 过滤模式下，若整个子树都不可见，这个目录本身也不显示
  if ((PT.filter !== 'all' || PT.search) && !ptVisible(n) && !ptHasVisibleDesc(n.path)) {
    return ''
  }
  const kids = PT.children.get(n.path) || []
  const nKids = kids.length
  if (!nKids) {
    return `<div class="pt-file" data-path="${esc(n.path)}">
      <span class="pt-name pt-dir">${esc(n.name)}/</span>
      <span class="pt-purpose">（空目录）</span></div>`
  }
  return `<details data-ptpath="${esc(n.path)}" ${depth < 1 ? 'open' : ''}>
    <summary><span class="pt-dir">${esc(n.name)}/</span>
      <span class="pt-size">${nKids}</span></summary>
    <div class="pt-children"></div></details>`
}

function ptRenderChildren(parent, box, depth) {
  let kids = (PT.children.get(parent) || []).filter(ptVisible)
  // 过滤模式下，把「自己不可见但后代可见」的目录也带上
  if (PT.filter !== 'all' || PT.search) {
    const extra = (PT.children.get(parent) || []).filter(
      (k) => k.isDir && !kids.includes(k) && ptHasVisibleDesc(k.path))
    kids = kids.concat(extra)
    kids.sort((a, b) => (b.isDir - a.isDir) || a.name.localeCompare(b.name, 'zh-CN'))
  }
  if (!kids.length) {
    box.innerHTML = '<div class="pt-empty">（无匹配项）</div>'
    return
  }
  const html = kids.map((k) => k.isDir ? ptDirHtml(k, depth) : ptFileHtml(k)).join('')
  box.innerHTML = html || '<div class="pt-empty">（无匹配项）</div>'
}

function renderProjTreeRoot() {
  if (!PT.data || !PT.data.live) {
    $('ptTree').innerHTML = '<div class="pt-empty">目录表未生成：先跑 python -m distill.projtree scan</div>'
    $('ptRepos').innerHTML = ''
    $('ptKpis').innerHTML = ''
    return
  }
  const t = PT.data
  if (!PT.repo || !t.repos.some((r) => r.repo === PT.repo)) {
    PT.repo = t.repo || (t.repos[0] && t.repos[0].repo)
  }
  $('ptRepos').innerHTML = t.repos.map((r) =>
    `<button data-repo="${esc(r.repo)}" class="${r.repo === PT.repo ? 'active' : ''}">${esc(r.repo)} (${r.count})</button>`).join('')
  $('ptRepos').querySelectorAll('button').forEach((b) =>
    b.addEventListener('click', () => {
      PT.repo = b.dataset.repo
      fetchJSON('/api/projtree?repo=' + encodeURIComponent(PT.repo)).then((d) => {
        PT.data = d
        ptBuildIndex(d)
        renderProjTreeRoot()   // KPI（含 token）与仓库按钮也要跟着刷新
      })
    }))

  const s = t.stats || {}
  const tk = t.tokens || {}
  const fmtTok = (n) => n == null ? '—' : n.toLocaleString('zh-CN')
  $('ptKpis').innerHTML = `
    <div class="pt-kpi">目录<b>${s.dirs ?? '—'}</b></div>
    <div class="pt-kpi">文件<b>${s.files ?? '—'}</b></div>
    <div class="pt-kpi ok">已写介绍<b>${s.noted ?? '—'}</b></div>
    <div class="pt-kpi warn">过期<b>${s.stale ?? '—'}</b></div>
    <div class="pt-kpi">未写<b>${s.missing ?? '—'}</b></div>
    ${s.orphans ? `<div class="pt-kpi warn">孤儿<b>${s.orphans}</b></div>` : ''}
    <div class="pt-kpi tok" title="整棵树含介绍+状态，注入 prompt 的估算成本">注入上下文<b>${fmtTok(tk.tokens)} tok</b></div>
    <div class="pt-kpi tok" title="仅树形结构，无介绍">纯树形<b>${fmtTok(tk.tokensTree)} tok</b></div>
    <div class="pt-kpi tok" title="每行一个完整路径">纯路径<b>${fmtTok(tk.tokensPaths)} tok</b></div>
    <div class="pt-kpi tok" title="平均每文件">每文件<b>~${fmtTok(tk.perFile)} tok</b></div>`

  renderProjTree()
}

// 给一批新创建的 <details> 绑定展开事件。
// 关键：toggle 事件不冒泡，不能在容器上做事件委托；
// 每次 ptRenderChildren 生成新的子目录后，必须对新节点再绑一次。
// 之前只在 renderProjTree 里绑了顶层，所以点 agent/ 没反应。
function ptBindDirs(scope) {
  scope.querySelectorAll('details[data-ptpath]').forEach((d) => {
    if (d.dataset.bound) return
    d.dataset.bound = '1'
    d.addEventListener('toggle', () => {
      if (d.open) ptFillDir(d)
    })
    // 初始就 open 的目录不会可靠触发 toggle，主动填一次
    if (d.open) ptFillDir(d)
  })
}

function ptFillDir(d) {
  const box = d.querySelector('.pt-children')
  if (!box || box.dataset.loaded) return
  box.dataset.loaded = '1'
  ptRenderChildren(d.dataset.ptpath, box, 1)
  // 新生成的子目录也要绑事件，否则点它们没反应
  ptBindDirs(box)
}

function renderProjTree() {
  $('ptTree').innerHTML = ''
  ptRenderChildren('', $('ptTree'), 0)
  ptBindDirs($('ptTree'))
}

function bindProjTree() {
  $('ptFilters').querySelectorAll('button').forEach((b) =>
    b.addEventListener('click', () => {
      PT.filter = b.dataset.filter
      $('ptFilters').querySelectorAll('button').forEach((x) =>
        x.classList.toggle('active', x === b))
      renderProjTree()
    }))
  $('ptSearch').addEventListener('input', (e) => {
    PT.search = e.target.value.trim()
    renderProjTree()
  })
}

function render(p) {
  PAYLOAD = p
  renderHeader(p)
  renderKpis(p)
  renderLevels(p)
  renderTree(p)
  renderVerification(p)
  renderCovers(p)
  renderTimeline(p)
}

async function load() {
  try {
    const p = await fetchJSON('/api/data')
    render(p)
    toast('已刷新 ' + new Date().toLocaleTimeString('zh-CN'))
    // covers 自检要跑 Python（秒级），不阻塞首屏——先把页面画出来，再补。
    $('coversList').innerHTML = '<div class="empty">自检计算中…</div>'
    fetchJSON('/api/covers').then((c) => {
      if (!c || c.live === false) {
        $('coversList').innerHTML = '<div class="empty">covers 自检不可用</div>'
        return
      }
      PAYLOAD.covers = c
      PAYLOAD.source.covers = 'live'
      renderCovers(PAYLOAD)
    }).catch(() => {
      $('coversList').innerHTML = '<div class="empty">covers 自检失败</div>'
    })
    // 目录表按需单独取：它可能很大（infohub 2.9 万节点），不阻塞首屏。
    fetchJSON('/api/projtree').then((d) => {
      PT.data = d
      PT.repo = d.repo || PT.repo
      ptBuildIndex(d)
      renderProjTreeRoot()
    }).catch((e) => {
      $('ptTree').innerHTML = `<div class="pt-empty">目录表加载失败：${esc(e.message)}</div>`
    })
  } catch (e) {
    $('tree').innerHTML = `<div class="empty">加载失败：${esc(e.message)}</div>`
    toast('加载失败：' + e.message)
  }
}

$('refreshBtn').addEventListener('click', load)
bindDetailActions()
bindProjTree()
load()
