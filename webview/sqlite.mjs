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
export function readIndex(root) {
  if (!DatabaseSync) return null
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
