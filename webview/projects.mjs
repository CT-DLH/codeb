/**
 * 项目注册表（Web 侧）。
 *
 * 与 distill/projtree.py 的 `projects` 表是**同一张表**——不另建库，
 * 因为派生索引库已经有 repo 分区，再开一个只会让「哪个项目在哪」有两份答案。
 *
 * 读写分工：
 *   - listProjects  读表 + 补发现（repo/ 下有一级目录但没登记的）
 *   - addProject    写表 + 建 repo/<name>/knowledge/ 骨架 + 后台 scan
 *   - removeProject 只删表行，**不碰 repo/ 和磁盘**
 *
 * node:sqlite 不可用时降级为「只读发现」：能列老项目，但不能导入。
 * 那种情况下 addProject 明确报错，而不是假装成功。
 */
import fs from 'node:fs'
import path from 'node:path'
import { spawn } from 'node:child_process'

let DatabaseSync = null
try {
  ;({ DatabaseSync } = await import('node:sqlite'))
} catch {
  // Node without sqlite support — import 不可用，list 退化为纯发现。
}

const TABLE_DDL = `
CREATE TABLE IF NOT EXISTS projects (
  name       TEXT PRIMARY KEY,
  disk_path  TEXT NOT NULL,
  display    TEXT,
  source     TEXT NOT NULL,
  note       TEXT,
  created_at TEXT NOT NULL
)`

/** 扫项目名合法性的唯一口径，与 projtree.register_project 保持一致。 */
const NAME_RE = /^[a-z0-9][a-z0-9._-]*$/

function now() {
  const d = new Date()
  const p = (n) => String(n).padStart(2, '0')
  const off = -d.getTimezoneOffset()
  const sign = off >= 0 ? '+' : '-'
  const a = Math.abs(off)
  return `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())}T`
    + `${p(d.getHours())}:${p(d.getMinutes())}:${p(d.getSeconds())}`
    + `${sign}${p(Math.floor(a / 60))}${p(a % 60)}`
}

function dbFile(root) {
  return path.join(root, '_kbwork', 'codeb-index.db')
}

/** 打开可写库并确保 projects 表存在；不可用时返回 null。 */
function open(root) {
  if (!DatabaseSync) return null
  const p = dbFile(root)
  if (!fs.existsSync(p)) return null
  try {
    const db = new DatabaseSync(p)
    db.exec(TABLE_DDL)
    return db
  } catch {
    return null
  }
}

/** repo/<name>/ 下一级目录名 = 知识库里真实存在的项目。 */
function knownRepoNames(root) {
  try {
    return fs.readdirSync(path.join(root, 'repo'), { withFileTypes: true })
      .filter((e) => e.isDirectory())
      .map((e) => e.name)
      .sort()
  } catch {
    return []
  }
}

/** 猜源码根：frontmatter root: → 兄弟目录。与 kb.repo_roots 同序。 */
function guessDiskRoot(root, name) {
  const dir = path.join(root, 'repo', name)
  const walk = (d, depth) => {
    if (depth > 4) return null
    let entries
    try { entries = fs.readdirSync(d, { withFileTypes: true }) } catch { return null }
    for (const e of entries) {
      const full = path.join(d, e.name)
      if (e.isDirectory()) {
        const hit = walk(full, depth + 1)
        if (hit) return hit
        continue
      }
      if (!e.name.endsWith('.md')) continue
      let text = ''
      try { text = fs.readFileSync(full, 'utf8') } catch { continue }
      const m = text.split('\n', 24).join('\n').match(/^root:\s*(.+)$/m)
      if (!m) continue
      const decl = m[1].trim().replace(/^["']|["']$/g, '')
      try {
        if (fs.statSync(decl).isDirectory()) return decl
      } catch { /* 声明了但不存在，继续找 */ }
    }
    return null
  }
  const declared = walk(dir, 0)
  if (declared) return declared
  const sib = path.join(path.dirname(path.resolve(root)), name)
  try {
    return fs.statSync(sib).isDirectory() ? sib : ''
  } catch {
    return ''
  }
}

/** 每个项目的文件数 / 介绍数，来自 project_files 与 file_notes。 */
function countsOf(db, root) {
  const out = new Map()
  if (!db) return out
  const one = (sql, ...a) => {
    try { return db.prepare(sql).all(...a) } catch { return [] }
  }
  for (const r of one(
    'SELECT repo, SUM(CASE WHEN is_dir=0 THEN 1 ELSE 0 END) AS n, '
    + 'COUNT(*) AS total FROM project_files GROUP BY repo')) {
    out.set(r.repo, { files: Number(r.n) || 0, nodes: Number(r.total) || 0, notes: 0 })
  }
  for (const r of one('SELECT repo, COUNT(*) AS n FROM file_notes GROUP BY repo')) {
    const cur = out.get(r.repo) || { files: 0, nodes: 0, notes: 0 }
    cur.notes = Number(r.n) || 0
    out.set(r.repo, cur)
  }
  for (const r of one(
    'SELECT repo, scan_id, at, n_files FROM scan_log '
    + 'WHERE (repo, scan_id) IN (SELECT repo, MAX(scan_id) FROM scan_log GROUP BY repo)')) {
    const cur = out.get(r.repo) || { files: 0, nodes: 0, notes: 0 }
    cur.lastScan = r.at || ''
    out.set(r.repo, cur)
  }
  return out
}

/**
 * 列出全部项目。顺序：已登记在前，各自按名字排序。
 * `_shared` 这类下划线开头的是跨仓库共享知识，不是可进入的项目，排除。
 */
export function listProjects(root) {
  const db = open(root)
  const counts = countsOf(db, root)
  const out = new Map()

  if (db) {
    try {
      for (const r of db.prepare(
        'SELECT name,disk_path,display,source,note,created_at FROM projects ORDER BY name'
      ).all()) {
        let exists = false
        try { exists = fs.statSync(r.disk_path).isDirectory() } catch { exists = false }
        out.set(r.name, {
          name: r.name,
          display: r.display || r.name,
          disk_path: r.disk_path,
          source: r.source || 'imported',
          note: r.note || '',
          created_at: r.created_at || '',
          registered: true,
          exists,
        })
      }
    } catch { /* 表读不了就当空 */ }
    finally {
      try { db.close() } catch { /* ignore */ }
    }
  }

  // 补充：知识库里有目录但没登记的（老库升级路径）
  for (const name of knownRepoNames(root)) {
    if (out.has(name) || name.startsWith('_')) continue
    const disk = guessDiskRoot(root, name)
    out.set(name, {
      name, display: name, disk_path: disk, source: 'discovered', note: '',
      created_at: '', registered: false, exists: !!disk,
    })
  }

  return [...out.values()]
    .map((p) => {
      const c = counts.get(p.name) || {}
      const js = jobState(p.name)
      return {
        ...p,
        files: c.files || 0,
        nodes: c.nodes || 0,
        notes: c.notes || 0,
        last_scan: c.lastScan || '',
        scanning: !!js.running,
        scan_error: (!js.running && js.ok === false) ? (js.tail || '任务失败') : '',
        job: js,
      }
    })
    .sort((a, b) => (a.registered === b.registered
      ? a.name.localeCompare(b.name)
      : (a.registered ? -1 : 1)))
}

/**
 * 导入一个项目：写注册表 + 建知识页骨架 + 后台扫描。
 *
 * 扫描**必须异步**：infohub 那种规模扫一次 5 秒以上，同步会把 HTTP 请求
 * 挂死，前端只能看到转圈。这里立刻返回，前端轮询 listProjects 看文件数变化。
 */
export function addProject(root, diskPath, opts = {}) {
  const raw = String(diskPath || '').trim().replace(/^["']|["']$/g, '')
  if (!raw) return { ok: false, error: '请填写项目路径' }

  const disk = path.resolve(raw)
  let st
  try { st = fs.statSync(disk) } catch {
    return { ok: false, error: `路径不存在：${disk}` }
  }
  if (!st.isDirectory()) return { ok: false, error: `不是目录：${disk}` }

  // 名字：显式给的就用它，否则取目录名。统一小写、非法字符换成 -
  let name = String(opts.name || '').trim().toLowerCase()
  if (!name) {
    name = path.basename(disk).toLowerCase().replace(/[^a-z0-9._-]+/g, '-')
      .replace(/^-+|-+$/g, '')
  }
  if (!NAME_RE.test(name)) {
    return {
      ok: false,
      error: `项目名不合法：${name || '(空)'}。只允许小写字母/数字/._-，且以字母或数字开头`,
    }
  }

  const db = open(root)
  if (!db) {
    return { ok: false, error: 'sqlite 不可用（需要 Node 22.5+ 的 node:sqlite），无法登记项目' }
  }
  try {
    const dup = db.prepare('SELECT name, disk_path FROM projects WHERE name=?').get(name)
    if (dup && path.resolve(dup.disk_path) !== disk) {
      return {
        ok: false,
        error: `项目名 ${name} 已被占用（指向 ${dup.disk_path}）。换个名字，或用 --name 指定`,
      }
    }
    db.prepare(
      'INSERT INTO projects (name,disk_path,display,source,note,created_at) '
      + 'VALUES (?,?,?,?,?,?) '
      + 'ON CONFLICT(name) DO UPDATE SET disk_path=excluded.disk_path, '
      + 'display=excluded.display, source=excluded.source, note=excluded.note'
    ).run(name, disk, String(opts.display || name), 'imported',
      String(opts.note || ''), now())
  } catch (e) {
    return { ok: false, error: String(e?.message || e) }
  } finally {
    try { db.close() } catch { /* ignore */ }
  }

  // 知识页骨架：没有它，kb 的 tree/pack 找不到这个项目
  const scaffold = path.join(root, 'repo', name, 'knowledge')
  let scaffolded = false
  try {
    fs.mkdirSync(scaffold, { recursive: true })
    const page = path.join(scaffold, '00-modules.md')
    if (!fs.existsSync(page)) {
      fs.writeFileSync(page, [
        '---',
        `title: ${name} modules (layer 2)`,
        `root: ${disk.replace(/\\/g, '/')}`,
        `updated: ${new Date().toISOString().slice(0, 10)}`,
        'covers: []',
        '---',
        '',
        `# ${name} 模块导航（第 2 层）`,
        '',
        '> 自动创建的骨架页。补写模块表后，agent 就能从这里下钻到部件页。',
        '',
        '| 模块 | 部件页表 | 默认写范围 | 状态 |',
        '|:--|:--|:--|:--|',
        '',
      ].join('\n'), 'utf8')
      scaffolded = true
    }
  } catch (e) {
    return { ok: false, name, error: `已登记但建骨架失败：${e?.message || e}` }
  }

  // 导入后先扫结构，再 reindex（否则知识页索引里查不到这个项目）
  startJob(root, name, 'structure', [
    '-m', 'distill.projtree', '--root', disk, '--repo', name, 'scan',
  ])
  return { ok: true, name, disk_path: disk, scaffolded, scan: 'running' }
}

/** 注销登记。不删 repo/、不删磁盘、不删目录表——那都是不可逆操作。 */
export function removeProject(root, name) {
  const n = String(name || '').trim()
  if (!n) return { ok: false, error: '缺少项目名' }
  const db = open(root)
  if (!db) return { ok: false, error: 'sqlite 不可用' }
  try {
    const cur = db.prepare('DELETE FROM projects WHERE name=?').run(n)
    return cur.changes > 0
      ? { ok: true, name: n }
      : { ok: false, error: `${n} 不在注册表里` }
  } catch (e) {
    return { ok: false, error: String(e?.message || e) }
  } finally {
    try { db.close() } catch { /* ignore */ }
  }
}

/** 正在跑的任务：repo → { kind, startedAt, progress, output }。内存态，重启即清空。 */
const jobs = new Map()

/** 任务结束后的结果：repo → { ok, code, kind, finishedAt, tail }。**成功也记**，前端才能显示「上次更新于」。 */
const jobResults = new Map()

const MAX_TAIL = 4000

/**
 * 起一个后台任务。**必须异步**：
 *   - scan   infohub 那种规模 5 秒以上
 *   - fill   逐批调 LLM，364 个文件要 31 批，可能几分钟
 * 同步会把 HTTP 请求挂死，前端只能看到转圈。
 */
function startJob(root, repo, kind, argv) {
  if (jobs.has(repo)) return { ok: false, error: `${repo} 已有任务在跑` }
  const job = {
    kind, repo, startedAt: Date.now(), progress: 0, tail: '',
  }
  jobs.set(repo, job)
  jobResults.delete(repo)

  const py = resolvePython(root)
  const child = spawn(py, ['-X', 'utf8', ...argv], {
    cwd: root, stdio: ['ignore', 'pipe', 'pipe'], windowsHide: true,
  })

  const push = (buf) => {
    job.tail = (job.tail + buf.toString('utf8')).slice(-MAX_TAIL)
    // fill 会逐批打印 "[3/31] ..."，据此算进度给前端看
    const m = [...job.tail.matchAll(/\[(\d+)\/(\d+)\]/g)].pop()
    if (m) job.progress = Math.round((Number(m[1]) / Number(m[2])) * 100)
  }
  child.stdout.on('data', push)
  child.stderr.on('data', push)

  child.on('error', (e) => {
    jobs.delete(repo)
    jobResults.set(repo, { ok: false, code: -1, kind, finishedAt: Date.now(),
      tail: `启动失败：${e.message}` })
  })
  child.on('exit', (code) => {
    jobs.delete(repo)
    jobResults.set(repo, {
      ok: code === 0, code, kind, finishedAt: Date.now(), tail: job.tail.slice(-1200),
    })
  })
  return { ok: true, kind, repo, started: true }
}

/** 当前任务状态 + 上次结果，供前端轮询。 */
function jobState(repo) {
  const j = jobs.get(repo)
  if (j) {
    return {
      running: true, kind: j.kind,
      elapsed: Math.round((Date.now() - j.startedAt) / 1000),
      progress: j.progress, tail: j.tail.slice(-600),
    }
  }
  const r = jobResults.get(repo)
  if (r) {
    return {
      running: false, kind: r.kind, ok: r.ok,
      finishedAt: new Date(r.finishedAt).toISOString(), tail: r.tail,
    }
  }
  return { running: false }
}

/** 更新目录表**结构**（不调 LLM，只重新扫磁盘）。 */
export function refreshStructure(root, repo) {
  const disk = diskOf(root, repo)
  if (!disk) return { ok: false, error: `${repo} 没有可扫描的源码路径` }
  return startJob(root, repo, 'structure', [
    '-m', 'distill.projtree', '--root', disk, '--repo', repo, 'scan',
  ])
}

/** 更新目录表**说明**（调 LLM 补介绍）。只补未写的，不改已有。 */
export function refreshNotes(root, repo, opts = {}) {
  const disk = diskOf(root, repo)
  if (!disk) return { ok: false, error: `${repo} 没有可扫描的源码路径` }
  const argv = ['-m', 'distill.projtree', '--root', disk, '--repo', repo,
    'fill', '--mode', 'openai', '--only', 'missing']
  if (opts.limit) argv.push('--limit', String(Number(opts.limit)))
  return startJob(root, repo, 'notes', argv)
}

/** 从注册表或自动发现里取源码路径。 */
function diskOf(root, repo) {
  const p = listProjects(root).find((x) => x.name === repo)
  return p && p.exists ? p.disk_path : ''
}

/** 选 python：优先项目自带的 agvenv，退回系统 python。 */
function resolvePython(root) {
  const cands = [
    path.join(root, '_kbwork', 'agvenv', 'Scripts', 'python.exe'),
    path.join(root, '_kbwork', 'venv', 'Scripts', 'python.exe'),
  ]
  for (const c of cands) {
    try { if (fs.statSync(c).isFile()) return c } catch { /* next */ }
  }
  return process.platform === 'win32' ? 'python' : 'python3'
}

/**
 * 兄弟目录候选：给导入表单的 datalist 用。
 *
 * 只列「有 .git 的目录」——D:\work\project 下有 74 个目录，无差别全列
 * 等于把用户丢进一堆无关名字里。有 .git 才可能是真正的仓库。
 */
export function listSiblings(root) {
  const parent = path.dirname(path.resolve(root))
  let entries
  try { entries = fs.readdirSync(parent, { withFileTypes: true }) } catch { return [] }
  const out = []
  for (const e of entries) {
    if (!e.isDirectory() || e.name.startsWith('.')) continue
    const full = path.join(parent, e.name)
    try {
      if (!fs.statSync(path.join(full, '.git')).isDirectory()) continue
    } catch { continue }
    out.push(full)
  }
  return out.sort((a, b) => a.localeCompare(b))
}

/** 供 /api/projects 返回的整体状态。 */
export function projectStatus(root) {
  const projects = listProjects(root)
  return {
    projects,
    sqlite: !!DatabaseSync && fs.existsSync(dbFile(root)),
    scanning: [...jobs.keys()],
    siblings: listSiblings(root),
    workspace: path.resolve(root),
  }
}
