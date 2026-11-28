'use strict'

/**
 * 主页：项目选择 + 导入。
 *
 * 数据只有 /api/projects 一个来源。这里刻意不做「项目列表」的本地缓存——
 * 导入后要立刻看到扫描进度变化，缓存只会让界面和真相不一致。
 */

const $ = (id) => document.getElementById(id)
const esc = (s) => String(s ?? '').replace(/[&<>"']/g, (c) =>
  ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]))

let pollTimer = null

function toast(msg) {
  const t = $('toast')
  t.textContent = msg
  t.classList.add('show')
  clearTimeout(toast._t)
  toast._t = setTimeout(() => t.classList.remove('show'), 2400)
}

async function fetchJSON(url, opts) {
  const r = await fetch(url, { cache: 'no-store', ...opts })
  const d = await r.json().catch(() => ({}))
  if (!r.ok || d.ok === false) throw new Error(d.error || `${r.status}`)
  return d
}

/** 卡片的健康状态：缺源码 / 未扫描 / 扫描中 / 报错 / 正常。 */
function healthOf(p) {
  if (p.scanning) return { cls: 'warn', text: '扫描中…' }
  if (p.scan_error) return { cls: 'err', text: '扫描失败' }
  if (!p.exists) return { cls: 'err', text: '源码目录不存在' }
  if (!p.files) return { cls: 'warn', text: '未扫描' }
  return { cls: 'ok', text: '正常' }
}

function fmtTime(iso) {
  if (!iso) return '—'
  // 形如 2026-11-27T23:37:45+0800
  const m = String(iso).match(/^(\d{4})-(\d{2})-(\d{2})[T ](\d{2}):(\d{2})/)
  return m ? `${m[2]}-${m[3]} ${m[4]}:${m[5]}` : String(iso).slice(0, 16)
}

function cardNode(p) {
  const h = healthOf(p)
  const card = document.createElement('a')
  card.className = 'project-card' + (p.registered ? '' : ' unregistered')
  card.href = '/p/' + encodeURIComponent(p.name)

  const head = document.createElement('div')
  head.className = 'pc-head'
  const name = document.createElement('span')
  name.className = 'pc-name'
  name.textContent = p.display || p.name
  const badge = document.createElement('span')
  badge.className = 'pc-health ' + h.cls
  badge.textContent = h.text
  head.append(name, badge)

  const path = document.createElement('div')
  path.className = 'pc-path'
  path.textContent = p.disk_path || '（未登记源码路径）'
  path.title = p.disk_path || ''

  const stats = document.createElement('div')
  stats.className = 'pc-stats'
  const mk = (label, val) => {
    const d = document.createElement('span')
    d.className = 'pc-stat'
    d.innerHTML = `<b>${esc(val)}</b>${esc(label)}`
    return d
  }
  stats.append(
    mk('文件', p.files || 0),
    mk('已写介绍', p.notes || 0),
  )

  const foot = document.createElement('div')
  foot.className = 'pc-foot'
  foot.textContent = p.source === 'discovered'
    ? '自动发现 · 未登记源码路径'
    : `最近扫描 ${fmtTime(p.last_scan)}`

  card.append(head, path, stats, foot)
  if (p.scan_error) {
    const err = document.createElement('div')
    err.className = 'pc-error'
    err.textContent = p.scan_error
    card.append(err)
  }
  return card
}

function render(d) {
  const grid = $('projectGrid')
  const list = (d.projects || []).filter((p) => !p.name.startsWith('_'))
  grid.innerHTML = ''
  if (!list.length) {
    grid.innerHTML = '<div class="empty">还没有项目。用下面的表单导入一个仓库路径。</div>'
    return
  }
  for (const p of list) grid.append(cardNode(p))
}

let lastSig = ''

async function load(silent = false) {
  try {
    const d = await fetchJSON('/api/projects')
    // sqlite 不可用是硬故障（没法导入项目），要显眼；正常时什么都不说。
    const dbBad = !d.sqlite
    const scanning = (d.scanning || []).length
    $('hint').innerHTML = dbBad
      ? '<span class="badge snapshot" title="需要 Node 22.5+ 的 node:sqlite">sqlite 不可用</span>'
      : scanning
        ? `<span class="badge live">${scanning} 个扫描中</span>`
        : `<span class="badge snapshot">${(d.projects || []).length} 个项目</span>`
    render(d)

    // 只在「有扫描在跑」时轮询；扫描完了自动停，避免空转
    const sig = JSON.stringify((d.projects || []).map(
      (p) => [p.name, p.files, p.notes, p.scanning, p.scan_error]))
    if (sig !== lastSig) lastSig = sig
    if (scanning) {
      if (!pollTimer) {
        pollTimer = setInterval(() => load(true), 2000)
      }
    } else if (pollTimer) {
      clearInterval(pollTimer)
      pollTimer = null
    }
    if (!silent) { /* 首屏不留额外动作 */ }
  } catch (e) {
    $('projectGrid').innerHTML =
      `<div class="empty">加载失败：${esc(e.message)}</div>`
  }
}

async function doImport() {
  const btn = $('importBtn')
  const msg = $('importMsg')
  const p = ($('importPath').value || '').trim()
  const n = ($('importName').value || '').trim()
  if (!p) { msg.textContent = '请填仓库路径'; msg.className = 'import-msg err'; return }

  btn.disabled = true
  btn.textContent = '导入中…'
  msg.textContent = ''
  msg.className = 'import-msg'
  try {
    const d = await fetchJSON('/api/projects', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ path: p, name: n || undefined }),
    })
    msg.className = 'import-msg ok'
    msg.textContent = `已导入 ${d.name}`
      + (d.scaffolded ? '，已创建知识页骨架' : '')
      + (d.scan === 'running' ? '，正在后台扫描…' : '')
    $('importPath').value = ''
    $('importName').value = ''
    await load()
  } catch (e) {
    msg.className = 'import-msg err'
    msg.textContent = String(e.message || e)
  } finally {
    btn.disabled = false
    btn.textContent = '导入'
  }
}

/**
 * 兄弟目录提示：只列「有 .git 且还没导入」的目录。
 *
 * 为什么不列全部：D:\work\project 下有 74 个目录，无差别塞进 datalist
 * 等于把用户丢进一堆无关名字里。只提示可能是仓库的。
 */
async function loadHints() {
  try {
    const d = await fetchJSON('/api/projects')
    const have = new Set((d.projects || []).map((p) => p.disk_path.toLowerCase()))
    const sib = d.siblings || []
    $('siblingHints').innerHTML = sib
      .filter((s) => !have.has(s.toLowerCase()))
      .slice(0, 40)
      .map((s) => `<option value="${esc(s)}"></option>`).join('')
  } catch { /* 提示是加分项，失败不影响导入 */ }
}

$('importBtn').addEventListener('click', doImport)
$('importPath').addEventListener('keydown', (e) => { if (e.key === 'Enter') doImport() })
$('importName').addEventListener('keydown', (e) => { if (e.key === 'Enter') doImport() })
$('refreshBtn').addEventListener('click', () => { lastSig = ''; load() })

load()
loadHints()
