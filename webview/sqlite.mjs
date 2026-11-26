/**
 * Optional sqlite acceleration for the webview (Node 22.5+ / 24).
 *
 * The sqlite db is a DERIVED INDEX built by `kb reindex`; Markdown remains the
 * source of truth. This module only READS the db. If it is missing or the
 * runtime lacks node:sqlite, the caller falls back to the Markdown scanner in
 * data.mjs — nothing breaks.
 */
import fs from 'node:fs'
import path from 'node:path'

let DatabaseSync = null
try {
  ;({ DatabaseSync } = await import('node:sqlite'))
} catch {
  // Node without sqlite support — graceful degradation.
}

export function dbPath(root) {
  return path.join(root, '_kbwork', 'codeb-index.db')
}

/** Read derived index facts; return null when unavailable. */
export function readIndex(root) {  if (!DatabaseSync) return null
  const p = dbPath(root)
  if (!fs.existsSync(p)) return null
  let db
  try {
    db = new DatabaseSync(p, { readOnly: true })
    const one = (sql, ...args) => db.prepare(sql).get(...args)
    const all = (sql, ...args) => db.prepare(sql).all(...args)

    const meta = {}
    for (const r of all('SELECT key, value FROM meta')) meta[r.key] = r.value

    // covers：按 repo+page_rel 分组，供前端显示"某页声明了哪些路径"
    const covers = all(
      'SELECT c.repo, c.page_rel, c.path, c.is_dir, p.title ' +
      'FROM covers c LEFT JOIN pages p ON p.repo=c.repo AND p.rel=c.page_rel'
    )
    // blocks：per-file 统计 + 总数
    const blockFiles = all(
      'SELECT file, repo, COUNT(*) AS n FROM blocks GROUP BY repo, file ORDER BY n DESC'
    )
    // stale/conflict 直接复用 webview 已有的 check_covers.py 结果；这里只给结构化补充
    return {
      meta,
      coversCount: covers.length,
      blocksCount: blockFiles.reduce((s, r) => s + Number(r.n), 0),
      blockFiles: blockFiles.map((r) => ({ file: r.file, repo: r.repo, count: Number(r.n) })),
      pagesCount: Number(meta.pages || 0),
      generatedAt: meta.generated_at || null,
      live: true,
      source: 'sqlite',
    }
  } catch {
    return null
  } finally {
    try { db?.close() } catch { /* ignore */ }
  }
}

/**
 * 复刻 kb.py 的 est_tokens：CJK 字符 1 tok，其余每 3.5 字符 1 tok，向上取整。
 * 口径必须与 CLI / MCP 一致，否则前端显示的数字和 agent 实际消耗对不上。
 */
export function estTokens(text) {
  const cjk = (text.match(/[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff\u3040-\u30ff]/g) || []).length
  return Math.ceil(cjk + (text.length - cjk) / 3.5)
}

function fmtSize(n) {
  if (n == null) return ''
  if (n < 1024) return `${n}B`
  if (n < 1024 * 1024) return `${(n / 1024).toFixed(1)}K`
  return `${(n / 1024 / 1024).toFixed(1)}M`
}

/**
 * 模拟「把整个目录表按树形文本注入 prompt」时的真实文本，
 * 格式与 `projtree tree` 的文本输出一致：缩进 + 路径 + 介绍 + 状态。
 * 深度由 path 里的 / 数决定（readProjTree 返回的是整库，未指定子树）。
 */
export function renderInjectText(nodes, repo) {
  const sorted = [...nodes].sort((a, b) => a.path.localeCompare(b.path, 'zh-CN'))
  const lines = [repo]
  for (const n of sorted) {
    const depth = n.path.split('/').length - 1
    let line = '  '.repeat(depth + 1) + n.name + (n.isDir ? '/' : '')
    if (n.size != null) line += `  (${fmtSize(n.size)})`
    if (n.purpose) line += `  — ${n.purpose}`
    if (n.state === 'stale') line += '  ⚠过期'
    else if (n.state === 'none' && !n.isDir) line += '  ·未写'
    lines.push(line)
  }
  return lines.join('\n')
}

/**
 * 目录表：project_files（扫描生成的结构） + file_notes（LLM/agent 写的介绍）。
 *
 * 两张表是分开的，这里只读。每个文件带上 noteState：
 *   fresh   note_hash === content_hash      介绍与源码一致
 *   stale   note_hash !== content_hash      源码改过，介绍可能过时
 *   none    没有介绍
 *   orphan  有介绍但文件已不在目录表里
 */
export function readProjTree(root, repo = null) {
  if (!DatabaseSync) return null
  const p = dbPath(root)
  if (!fs.existsSync(p)) return null
  let db
  try {
    db = new DatabaseSync(p, { readOnly: true })
    const has = (t) => {
      try { return !!db.prepare(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?").get(t) } catch { return false }
    }
    if (!has('project_files')) return null

    // 只数文件，不数目录节点：798 是「762 文件 + 36 目录」的行数，
    // 拿它当文件数会让人以为 codeb 有 798 个文件（实际只有 762）。
    const repos = db.prepare(
      'SELECT repo, SUM(CASE WHEN is_dir=0 THEN 1 ELSE 0 END) AS n ' +
      'FROM project_files GROUP BY repo ORDER BY repo').all()
      .map((r) => ({ repo: r.repo, count: Number(r.n) }))
    const want = repo || (repos[0] && repos[0].repo)
    if (!want) return { repos, repo: null, nodes: [], stats: null }

    const rows = db.prepare(`
      SELECT f.path, f.parent_path, f.is_dir, f.name, f.ext, f.size,
             f.content_hash, n.purpose, n.detail, n.note_hash, n.source,
             n.updated_at
        FROM project_files f
        LEFT JOIN file_notes n ON n.repo = f.repo AND n.path = f.path
       WHERE f.repo = ?
       ORDER BY f.is_dir DESC, f.path`).all(want)

    const nodes = rows.map((r) => {
      let state = 'none'
      if (r.is_dir) state = ''
      else if (r.purpose && r.note_hash && r.content_hash)
        state = r.note_hash === r.content_hash ? 'fresh' : 'stale'
      else if (r.purpose) state = 'fresh'
      return {
        path: r.path,
        parent: r.parent_path || '',
        name: r.name,
        isDir: !!r.is_dir,
        ext: r.ext || null,
        size: r.size == null ? null : Number(r.size),
        purpose: r.purpose || null,
        detail: r.detail || null,
        source: r.source || null,
        updatedAt: r.updated_at || null,
        state,
      }
    })

    // 孤儿：有介绍但结构表里没有这个文件
    let orphans = []
    if (has('file_notes')) {
      orphans = db.prepare(`
        SELECT n.path, n.purpose, n.source, n.updated_at
          FROM file_notes n
          LEFT JOIN project_files f ON f.repo = n.repo AND f.path = n.path
         WHERE n.repo = ? AND f.path IS NULL`).all(want)
        .map((r) => ({ path: r.path, purpose: r.purpose || null,
                       source: r.source || null, updatedAt: r.updated_at || null }))
    }

    const files = nodes.filter((n) => !n.isDir)
    const stats = {
      dirs: nodes.length - files.length,
      files: files.length,
      noted: files.filter((n) => n.purpose).length,
      stale: files.filter((n) => n.state === 'stale').length,
      missing: files.filter((n) => n.state === 'none').length,
      orphans: orphans.length,
    }
    const last = db.prepare(
      'SELECT scan_id, method, elapsed_ms FROM scan_log WHERE repo=? ' +
      'ORDER BY scan_id DESC LIMIT 1')
    let scan = null
    try {
      const r = last.get(want)
      if (r) scan = { id: r.scan_id, method: r.method, ms: Number(r.elapsed_ms) }
    } catch { /* scan_log 不存在时忽略 */ }

    // 注入成本：模拟把整个目录表按树形文本塞进 prompt，口径同 kb.est_tokens。
    // 三档口径，避免「加介绍反而更少」这种反直觉显示：
    //   tokens        完整树 = 缩进树 + 介绍 + 状态标记（agent 实际看到的）
    //   tokensTree    仅树 = 缩进 + 文件名/目录名，不含介绍和大小
    //   tokensPaths   仅路径清单 = 每行一个完整相对路径（另一种常见注入方式）
    // 三者覆盖不同注入方式，让人知道「换种格式能省多少」。
    const injectText = renderInjectText(nodes, want)
    const tokens = estTokens(injectText)
    const treeLines = [want]
    for (const n of nodes) {
      const depth = n.path.split('/').length - 1
      treeLines.push('  '.repeat(depth + 1) + n.name + (n.isDir ? '/' : ''))
    }
    const tokensTree = estTokens(treeLines.join('\n'))
    const pathLines = [want, ...nodes.map((n) => n.path)]
    const tokensPaths = estTokens(pathLines.join('\n'))
    const tokenStats = {
      tokens,                                  // 完整树 + 介绍 + 状态
      tokensTree,                              // 仅树形结构
      tokensPaths,                             // 仅路径清单
      chars: injectText.length,
      files: files.length,
      noted: files.filter((n) => n.purpose).length,
      perFile: files.length ? Math.round(tokens / files.length) : 0,
      model: 'kb.est_tokens（CJK 1tok/字，其余 3.5字符/tok）',
    }

    return { repos, repo: want, nodes, orphans, stats, scan,
             tokens: tokenStats, live: true, source: 'sqlite' }
  } catch {
    return null
  } finally {
    try { db?.close() } catch { /* ignore */ }
  }
}
