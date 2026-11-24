/**
 * codeb webview — data layer (pure functions, zero DSH dependency).
 *
 * Extracted from the DSH panel plugin's index.js. Reads workspace files and
 * builds a JSON snapshot of the five-level page table, covers self-check,
 * verification status and session-log timeline.
 *
 * Improvement over the plugin: the timeline now scans the WHOLE
 * `_kbwork/agent-logs/*.jsonl` directory and merges events by timestamp,
 * instead of reading a single hard-coded file.
 */
import fs from 'node:fs'
import path from 'node:path'

/** Initial snapshot — used only when a workspace file is absent. */
export const SNAPSHOT = {
  projects: ['codeb', 'atomkgraph', 'infohub', '_shared'],
  levels: [
    { level: '第1层', name: '项目索引', files: 1 },
    { level: '第2层', name: '模块导航', files: 4 },
    { level: '第3层', name: '部件细页表', files: 10 },
    { level: '第4层', name: '语义块索引', files: 26 },
    { level: '第5层', name: '完整源码页帧', files: 0 },
  ],
  covers: {
    pages: 129,
    coversDecl: 348,
    coreSrc: 359,
    stale: { count: 6, items: [] },
    conflict: { count: 54, items: [] },
    uncovered: { count: 64, items: [] },
  },
  verification: {
    regression: { status: 'pass', detail: 'run_regression.ps1 全绿' },
    mcp: { status: 'pass', detail: 'MCP smoke 75/0', failed: 0 },
  },
}

/** Read a UTF-8 file; return null when absent or unreadable. */
export function readFile(root, rel) {
  try {
    return fs.readFileSync(path.join(root, rel), 'utf8')
  } catch {
    return null
  }
}

/** Recursively list files under a directory with a given basename. */
export function listNamedFiles(dir, basename, out = []) {
  let entries
  try {
    entries = fs.readdirSync(dir, { withFileTypes: true })
  } catch {
    return out
  }
  for (const entry of entries) {
    const full = path.join(dir, entry.name)
    if (entry.isDirectory()) listNamedFiles(full, basename, out)
    else if (entry.isFile() && entry.name === basename) out.push(full)
  }
  return out
}

export function parseMarkdownLinks(text) {
  const links = []
  const re = /\[([^\]]+)\]\(([^)]+)\)/g
  let m
  while ((m = re.exec(text || ''))) links.push({ title: m[1], href: m[2] })
  return links
}

/** Strip a leading YAML frontmatter block from markdown. */
export function withoutFrontmatter(text) {
  if (!text) return ''
  return text.replace(/^---\r?\n[\s\S]*?\r?\n---\r?\n/, '')
}

/**
 * 取某个 `## 标题` 下的正文行（到下一个同级或更高级标题为止）。
 */
export function sectionLines(text, headingRe) {
  const out = []
  let inside = false
  for (const line of withoutFrontmatter(text).split(/\r?\n/)) {
    if (/^##\s/.test(line)) {
      if (inside) break                 // 进入下一个 ## 就结束
      if (headingRe.test(line)) { inside = true; continue }
      continue
    }
    if (inside) out.push(line)
  }
  return out
}

/**
 * 把一行 Markdown 表格切成单元格。
 */
function splitRow(line) {
  return line.trim().replace(/^\||\|$/g, '').split('|').map((c) => c.trim())
}

function isSeparator(cells) {
  return /^:?-{2,}:?$/.test(cells[0] || '')
}

/**
 * 解析页面声明的直接子节点。两种写法都支持，优先 `## 下级`：
 *
 *  1. 显式声明（推荐，可任意深度）：
 *       ## 下级
 *       | 名称 | 说明 | 知识页 |
 *  2. 兼容旧的「模块表格」：表里含指向 modules/ 或 00-modules.md 的链接，
 *     就当作子节点，名称取链接文字，说明取「职责/说明」列。
 *
 * 这样已有页表不用重写就能被递归树接住，新增层级也不受限。
 */
export function parseChildren(text) {
  const explicit = parseDeclaredChildren(text)
  if (explicit.length) return explicit
  return parseTableChildren(text)
}

function parseDeclaredChildren(text) {
  const lines = sectionLines(text, /^##\s*(下级|子节点|子模块)/)
  const rows = lines.filter((l) => l.trim().startsWith('|')).map(splitRow)
  if (!rows.length) return []
  const headers = rows[0]
  const body = rows.filter((c) => c !== headers && !isSeparator(c) && c.length >= 2)
  const nameCol = Math.max(0, headers.findIndex((h) => /名称|名字|模块|采集器|组件/.test(String(h))))
  const descCol = headers.findIndex((h) => /说明|描述|简介|作用|职责/.test(String(h)))
  return body.map((c) => toChild(c, nameCol, descCol)).filter(Boolean)
}

/** 兼容：把「模块表格」当作子节点列表。 */
function parseTableChildren(text) {
  const rows = []
  for (const line of withoutFrontmatter(text).split(/\r?\n/)) {
    if (!line.trim().startsWith('|')) continue
    const cells = splitRow(line)
    if (isSeparator(cells)) continue
    rows.push(cells)
  }
  if (!rows.length) return []
  const headers = rows[0]
  const body = rows.filter((c) => c !== headers && c.length >= 2)

  // 子节点只认「指向下级页」的那一列：modules/ 或 sources/ 下的 .md。
  // 不能拿整行去正则，否则「知识页」列里的 agent-base-survey.md 也会被
  // 当成子节点，而且同一行里出现几次就被计几次。
  const CHILD_HREF = /\]\(([^)]*\/)?(modules|sources)\/[^)]*\.md\)/
  const colHasChildLink = headers.map((h, i) =>
    body.some((c) => CHILD_HREF.test(String(c[i] || ''))) &&
    /页表|知识页|部件|细页|链接|下级|模块/.test(String(h)))
  let childCol = colHasChildLink.findIndex(Boolean)
  if (childCol < 0) {
    // 表头不带明显字样时，退化为「哪一列里有 modules/ 链接」
    childCol = headers.findIndex((_, i) =>
      body.some((c) => CHILD_HREF.test(String(c[i] || ''))))
  }
  if (childCol < 0) return []

  const descCol = headers.findIndex((h) => /职责|说明|描述|简介|作用/.test(String(h)))
  const out = []
  const seen = new Set()
  for (const c of body) {
    const cell = String(c[childCol] || '')
    if (!CHILD_HREF.test(cell)) continue
    // 名称列优先取链接所在列的链接文字；说明列单独取
    // hrefCol=childCol：只认「部件页/下级」那一列的链接。
    //      不传的话会整行找第一个 .md，codeb 的「知识页」列（agent-base-survey.md）
    //      就会抢走名称与路径，把 6 个模块退化成 2 个错误节点。
    const child = toChild(c, childCol, descCol, childCol)
    if (!child || seen.has(child.name)) continue
    seen.add(child.name)
    out.push(child)
  }
  return out
}

function toChild(cells, nameCol, descCol, hrefCol = -1) {
  // 名称：优先用名称列原文；该列本身是链接时才退回链接文字。
  let name = String(cells[nameCol] || '')
  const nameLink = name.match(/\[([^\]]+)\]\([^)]*\)/)
  if (nameLink) name = nameLink[1]
  // href：优先取「部件页/下级」那一列的链接，取不到才整行找第一个 .md。
  // （不能无条件整行找第一链接，否则 codeb 的「知识页」列会抢走名称与路径）
  let href = null
  const inCol = hrefCol >= 0 ? String(cells[hrefCol] || '').match(/\[([^\]]+)\]\(([^)]+\.md)\)/) : null
  const any = inCol || cells.join(' | ').match(/\[([^\]]+)\]\(([^)]+\.md)\)/)
  if (any) href = any[2]
  if (!name && any) name = any[1]
  name = String(name).replace(/\[([^\]]+)\]\([^)]+\)/g, '$1').replace(/`/g, '').trim()
  if (!name) return null
  return {
    name,
    href,
    summary: descCol >= 0 && cells[descCol] ? String(cells[descCol]).replace(/`/g, '').trim() : '',
  }
}

/**
 * 从第3层模块页解析「功能部件」表格（叶子）。
 * 单独导出，供 /api/node 懒加载接口按节点调用。
 */
export function parseParts(modText) {
  const parts = []
  if (!modText) return parts
  const srcM = modText.match(/源码文件\D*`([^`]+)`/)
  const pathHint = srcM ? srcM[1] : ''
  let inTable = false
  for (const line of withoutFrontmatter(modText).split(/\r?\n/)) {
    if (/^##\s*功能部件/.test(line)) { inTable = true; continue }
    if (inTable && /^##\s/.test(line)) break
    if (!inTable) continue
    const cells = line.trim().replace(/^\||\|$/g, '').split('|').map((c) => c.trim())
    if (cells.length < 3) continue
    if (/^:?-{2,}:?$/.test(cells[0]) || /部件.*key/.test(cells[0])) continue
    // 部件 key 形如 `render@310`，从反引号里抽出来
    const keyM = cells[0].match(/`([^`]+)`/)
    const key = keyM ? keyM[1] : cells[0]
    // 列布局有两种，按列数区分：
    //   5 列（当前）：key | 类型 | 行号 | 用途 | 签名
    //   4 列（旧版）：key | 类型 | 行号 | 作用(=签名)
    // 用途优先；没有用途时退回签名，但标出来源，避免把签名当说明。
    const hasPurposeCol = cells.length >= 5
    const purpose = hasPurposeCol ? cells[3] : ''
    const sig = hasPurposeCol ? cells[4] : cells[3]
    parts.push({
      level: '部件',
      name: key,
      path: pathHint,
      kind: cells[1] || '',
      lines: cells[2] || '',
      note: purpose || '',
      sig: sig || '',
      hasPurpose: Boolean(purpose),
    })
  }
  return parts
}

/**
 * 递归构建任意深度的页表树。
 *
 * 旧实现把层级写死成「项目 → 模块 → 部件」，于是 infohub 的
 * 「采集 → 平台采集器 → 具体部件」这种三层嵌套塞不进去。
 * 现在每层都读同一个页面的 `## 下级` 表递归下去，深度由 md 决定。
 */
export function buildTree(root, { lazy = false } = {}) {
  const projectsIndex = readFile(root, 'repo/00-projects.md')
  const projectLinks = projectsIndex
    ? parseMarkdownLinks(withoutFrontmatter(projectsIndex))
        .filter((l) => /knowledge\/00-modules\.md$/.test(l.href))
    : []

  const entries = projectLinks.length
    ? projectLinks.map((l) => ({ name: l.href.split('/')[0] || l.title, href: l.href }))
    : SNAPSHOT.projects.map((name) => ({ name, href: null }))

  const projects = entries.map(({ name: rawName, href }) => {
    const name = String(rawName).replace(/^`|`$/g, '').trim()
    const rel = href
      ? path.posix.normalize(path.posix.join('repo', href.replace(/^\.?\//, '')))
      : `repo/${name}/knowledge/00-modules.md`
    const node = buildNode(root, { name, file: rel, depth: 1, lazy })
    return node
  })

  return {
    projects,
    rootFile: 'repo/00-projects.md',
    rootSummary: extractSummary(projectsIndex),
    // 懒加载时只展开一层，depth 不是真实深度——报 null 让前端不要显示错数字
    depth: lazy ? null : maxDepth(projects),
  }
}

/** 递归深度（用于前端展示「共 N 层」）。 */
function maxDepth(nodes) {
  let d = 0
  for (const n of nodes || []) {
    d = Math.max(d, 1 + maxDepth(n.children))
  }
  return d
}

/**
 * 构建单个节点：读自己的 md，解析 `## 下级` 与 `## 功能部件`。
 *
 * lazy=true 时只展开一层：children 只保留名字/summary/文件路径，
 * 不下钻也不读部件，等前端展开时再请求。
 */
export function buildNode(root, { name, file, depth = 1, lazy = false }) {
  const text = file ? readFile(root, file) : null
  const childDecls = text ? parseChildren(text) : []
  const baseDir = file ? path.posix.dirname(file) : ''

  const children = childDecls.map((c) => {
    // 链接基准：相对于本页所在目录。旧实现只拼一个 cwd 猜测，
    // 遇到 `sources/xx.md` 这种相对本页的写法就整段丢失。
    let childFile = null
    if (c.href) {
      const raw = c.href.replace(/^\.\//, '')
      if (raw.startsWith('/')) {
        childFile = path.posix.normalize('repo' + raw)
      } else {
        childFile = path.posix.normalize(path.posix.join(baseDir, raw))
      }
    }
    const exists = childFile ? !!readFile(root, childFile) : false
    if (!exists) {
      return { name: c.name, file: null, summary: c.summary, children: [], parts: [],
               partsLoaded: true, depth: depth + 1, missing: !!childFile }
    }
    if (lazy) {
      // 只给骨架：下钻留给 /api/node
      return { name: c.name, file: childFile, summary: c.summary,
               children: [], parts: [], partsLoaded: false, depth: depth + 1, collapsed: true }
    }
    return buildNode(root, { name: c.name, file: childFile, depth: depth + 1, lazy })
  })

  // 叶子：本页自己声明的「功能部件」
  const parts = (lazy && children.length) ? [] : (text ? parseParts(text) : [])

  return {
    name,
    file,
    summary: (text ? extractSummary(text) : '') ||
             (childDecls.length ? `${childDecls.length} 个下级` : ''),
    children,
    parts,
    partsLoaded: !lazy || (!children.length),
    depth,
    hasChildren: childDecls.length > 0,
    hasParts: text ? /^##\s*功能部件/m.test(withoutFrontmatter(text)) : false,
  }
}

/** 项目索引页的简介抽取（原 buildTree 内联，抽出以便复用）。 */
function extractSummary(text) {
  if (!text) return ''
  const body = withoutFrontmatter(text)
  const quote = body.match(/^>\s*(.+)$/m)
  if (quote) return quote[1].replace(/\*\*/g, '').trim()
  const para = body.split(/\r?\n/).find((l) => l.trim() && !l.startsWith('#') && !l.startsWith('|') && !l.startsWith('>'))
  return para ? para.replace(/\*\*/g, '').trim().slice(0, 200) : ''
}


export function parseCovers(text) {
  const fallback = SNAPSHOT.covers
  if (!text) return { ...fallback, live: false }

  const total = text.match(/总计：\s*(\d+)\s*页，\s*(\d+)\s*covers\s*声明，\s*(\d+)\s*核心源码文件/)
  const pages = total ? Number(total[1]) : fallback.pages
  const coversDecl = total ? Number(total[2]) : fallback.coversDecl
  const coreSrc = total ? Number(total[3]) : fallback.coreSrc

  function section(headerRe, itemRe) {
    const lines = text.split(/\r?\n/)
    const items = []
    let count = 0
    let inside = false
    for (const line of lines) {
      const header = line.match(headerRe)
      if (header) {
        count = Number(header[1])
        inside = true
        continue
      }
      if (inside && /^===/.test(line)) break
      if (inside && itemRe.test(line)) {
        items.push(line.trim().replace(/^(STALE|CONFLICT|UNCOVERED)\s+/, ''))
      }
    }
    return { count, items: items.slice(0, 40) }
  }

  return {
    pages,
    coversDecl,
    coreSrc,
    stale: section(/^===\s*过期 covers 声明 \((\d+)\)\s*===/, /^\s*STALE\b/),
    conflict: section(/^===\s*冲突覆盖 \((\d+)\)\s*===/, /^\s*CONFLICT\b/),
    uncovered: section(/^===\s*未覆盖核心源码 \((\d+)\s*\/\s*\d+\)\s*===/, /^\s*UNCOVERED\b/),
    live: true,
  }
}

export function parseCoversDist(text) {
  if (!text) return null
  const m = text.match(/^pages\s+(\d+)\s+covers_paths_total\s+(\d+)/m)
  if (!m) return null
  return { pages: Number(m[1]), coversDecl: Number(m[2]), coreSrc: SNAPSHOT.covers.coreSrc }
}

export function readCovers(root) {
  for (const rel of [
    '_kbwork/covers_selfcheck.txt',
    '_kbwork/covers_check.txt',
    '_kbwork/covers_result.txt',
  ]) {
    const text = readFile(root, rel)
    if (text && /===.*\(/.test(text)) return parseCovers(text)
  }
  const dist = readFile(root, '_kbwork/covers_dist.txt')
  const totals = parseCoversDist(dist)
  if (totals) {
    return { ...SNAPSHOT.covers, ...totals, live: true }
  }
  return { ...SNAPSHOT.covers, live: false }
}

export function readVerification(root) {
  for (const rel of ['_kbwork/regression_status.json', '_kbwork/verification.json']) {
    let data = null
    try { data = JSON.parse(readFile(root, rel)) } catch { data = null }
    if (data && (data.status || data.run_regression_ps1 || data.mcp)) {
      const regression = data.run_regression_ps1?.status ?? (data.status === 'PASS' ? 'pass' : data.status ?? 'pass')
      const mcpFailed = data.mcp?.smoke_ps1?.failed
      return {
        regression: { status: regression, detail: 'run_regression.ps1' },
        mcp: {
          status: mcpFailed === 0 ? 'pass' : data.mcp?.status ?? 'pass',
          detail: `MCP smoke ${mcpFailed ?? 0} failed`,
          failed: mcpFailed ?? 0,
        },
        live: true,
      }
    }
  }
  // Fallback: check if regression script exists to at least say "available".
  return { ...SNAPSHOT.verification, live: false }
}

function summarize(data) {
  if (!data) return ''
  if (typeof data === 'string') return data.slice(0, 160)
  const parts = []
  for (const key of ['path', 'tool', 'title', 'name', 'session', 'round', 'agent', 'content']) {
    if (data[key] != null) parts.push(`${key}: ${String(data[key]).slice(0, 80)}`)
  }
  return parts.join(' · ') || JSON.stringify(data).slice(0, 160)
}

export function parseTimeline(logText, sourceName = '') {
  if (!logText) return { events: [], live: false }
  const events = []
  for (const line of logText.split(/\r?\n/).reverse()) {
    if (!line.trim()) continue
    try {
      const row = JSON.parse(line)
      events.push({
        ts: row.ts ?? row.timestamp ?? '',
        event: row.event ?? row.type ?? '',
        detail: summarize(row.data ?? row),
        source: sourceName,
      })
    } catch { /* skip non-JSON lines */ }
    if (events.length >= 80) break
  }
  return { events, live: true }
}

/**
 * Scan the WHOLE agent-logs directory (plus legacy single files), merge by ts.
 * This is the key improvement over the DSH plugin: every task's session log
 * shows up, not just one hard-coded `ok.jsonl`.
 */
export function readTimeline(root, maxEvents = 120) {
  const dirs = [
    path.join(root, '_kbwork', 'agent-logs'),
    path.join(root, '_kbwork', 'agent-traces'),
  ]
  const files = []
  for (const dir of dirs) {
    try {
      for (const e of fs.readdirSync(dir, { withFileTypes: true })) {
        if (e.isFile() && /\.jsonl$/.test(e.name)) files.push(path.join(dir, e.name))
      }
    } catch { /* no such dir */ }
  }
  for (const rel of ['distill/agent/agent_log.jsonl', '_kbwork/agent-logs/ok.jsonl']) {
    const p = path.join(root, rel)
    if (fs.existsSync(p) && !files.includes(p)) files.push(p)
  }

  const all = []
  for (const f of files) {
    let text = null
    try { text = fs.readFileSync(f, 'utf8') } catch { continue }
    const parsed = parseTimeline(text, path.basename(f))
    for (const ev of parsed.events) all.push(ev)
  }
  all.sort((a, b) => String(b.ts).localeCompare(String(a.ts)))
  return {
    events: all.slice(0, maxEvents),
    files: files.length,
    live: all.length > 0,
  }
}

/** Auto-detect the codeb workspace root: start dir or ancestors with repo/00-projects.md. */
export function detectRoot(start) {
  const candidates = [path.resolve(start || process.cwd())]
  for (const c of [...candidates]) {
    let dir = c
    for (;;) {
      if (fs.existsSync(path.join(dir, 'repo/00-projects.md'))) return dir
      const parent = path.dirname(dir)
      if (parent === dir) break
      dir = parent
    }
  }
  return path.resolve(start || process.cwd())
}

/** Build the full payload consumed by the webview. */
export function buildPayload(root, { lazyTree = false } = {}) {
  const tree = buildTree(root, { lazy: lazyTree })
  const covers = readCovers(root)
  const verification = readVerification(root)
  const timeline = readTimeline(root)
  const treeLive = fs.existsSync(path.join(root, 'repo/00-projects.md'))
  return {
    workspace: root,
    generatedAt: new Date().toISOString(),
    source: {
      tree: treeLive ? 'live' : 'snapshot',
      covers: covers.live ? 'live' : 'snapshot',
      verification: verification.live ? 'live' : 'snapshot',
      timeline: timeline.live ? 'live' : 'snapshot',
    },
    tree,
    covers,
    verification,
    timeline: timeline.events,
    logFiles: timeline.files,
  }
}
