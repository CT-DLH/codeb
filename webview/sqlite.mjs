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

    const repos = db.prepare(
      'SELECT repo, COUNT(*) AS n FROM project_files GROUP BY repo ORDER BY repo').all()
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

    return { repos, repo: want, nodes, orphans, stats, scan, live: true,
             source: 'sqlite' }
  } catch {
    return null
  } finally {
    try { db?.close() } catch { /* ignore */ }
  }
}
